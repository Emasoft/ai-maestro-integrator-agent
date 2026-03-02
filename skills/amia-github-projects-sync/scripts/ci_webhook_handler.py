#!/usr/bin/env python3
"""GitHub CI webhook handler for integrator-agent.

Receives GitHub webhook events and forwards relevant notifications
to the orchestrator via AI Maestro messaging.

Handles:
- workflow_run (CI pass/fail)
- check_run (individual check results)
- pull_request (PR events)
- issues (issue state changes)
- push (commits to watched branches)
"""

import hashlib
import hmac
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any


# Configuration
WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
WATCHED_BRANCHES = {"main", "master", "develop"}
EMASOFT_DIR = Path.cwd() / ".emasoft"
LOG_DIR = EMASOFT_DIR / "webhook_logs"
AIMAESTRO_API = os.environ.get("AIMAESTRO_API", "http://localhost:23000")


def atomic_write_json(data: Any, path: Path) -> None:
    """Write JSON atomically using a temp file and rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, str(path))
    except BaseException:
        os.unlink(tmp)
        raise


def _send_maestro_message(subject: str, message: str, priority: str = "normal") -> None:
    """Send a notification via the AI Maestro REST API."""
    payload = json.dumps({
        "subject": subject,
        "priority": priority,
        "content": {"type": "notification", "message": message},
    })
    try:
        subprocess.run(
            ["curl", "-s", "-X", "POST", f"{AIMAESTRO_API}/api/messages",
             "-H", "Content-Type: application/json", "-d", payload],
            capture_output=True, timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass


def handle_github_webhook(event_type: str, payload: dict[str, Any]) -> tuple[bool, str]:
    """Process a GitHub webhook event and send AI Maestro notification."""
    action = payload.get("action", "")
    repo = payload.get("repository", {}).get("full_name", "unknown")
    summary = f"{event_type}"
    if action:
        summary += f".{action}"
    summary += f" on {repo}"
    _send_maestro_message(f"GitHub: {event_type}", summary)
    return True, summary


def notify_ci_failure(workflow: str, run_id: str, branch: str, error_summary: str) -> None:
    """Notify AI Maestro about a CI failure."""
    _send_maestro_message(
        f"CI Failure: {workflow}",
        f"Workflow '{workflow}' (run {run_id}) failed on {branch}: {error_summary}",
        priority="high",
    )


def notify_task_blocked(task_id: str, reason: str, issue_number: int | None = None) -> None:
    """Notify AI Maestro about a blocked task."""
    msg = f"Task {task_id} blocked: {reason}"
    if issue_number:
        msg += f" (issue #{issue_number})"
    _send_maestro_message(f"Blocked: {task_id}", msg, priority="high")


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    if not secret:
        return True  # Skip verification if no secret configured

    expected = (
        "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    )

    return hmac.compare_digest(expected, signature)


def log_webhook(event_type: str, payload: dict[str, Any], result: str) -> None:
    """Log webhook event for debugging."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"{timestamp}_{event_type}.json"

    atomic_write_json(
        {
            "event_type": event_type,
            "timestamp": timestamp,
            "result": result,
            "payload_summary": {
                "action": payload.get("action"),
                "sender": payload.get("sender", {}).get("login"),
                "repository": payload.get("repository", {}).get("full_name"),
            },
        },
        log_file,
    )


class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP handler for GitHub webhooks."""

    def do_POST(self) -> None:
        # Read payload
        content_length = int(self.headers.get("Content-Length", 0))
        payload_bytes = self.rfile.read(content_length)

        # Verify signature
        signature = self.headers.get("X-Hub-Signature-256", "")
        if not verify_signature(payload_bytes, signature, WEBHOOK_SECRET):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"Invalid signature")
            return

        # Parse event
        event_type = self.headers.get("X-GitHub-Event", "unknown")
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return

        # Handle event
        _, message = handle_github_webhook(event_type, payload)

        # Additional handling for specific events
        self._handle_additional_events(event_type, payload)

        # Log
        log_webhook(event_type, payload, message)

        # Respond
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "message": message}).encode())

    def _handle_additional_events(
        self, event_type: str, payload: dict[str, Any]
    ) -> None:
        """Handle additional event types not covered by base handler."""

        if event_type == "check_run":
            check = payload.get("check_run", {})
            conclusion = check.get("conclusion")
            name = check.get("name", "unknown")

            if conclusion == "failure":
                notify_ci_failure(
                    workflow=name,
                    run_id=str(check.get("id")),
                    branch=check.get("head_sha", "")[:8],
                    error_summary=check.get("output", {}).get(
                        "summary", "Check failed"
                    ),
                )

        elif event_type == "issues":
            action = payload.get("action")
            issue = payload.get("issue", {})

            if action == "labeled":
                label = payload.get("label", {}).get("name", "")
                if label == "blocked":
                    notify_task_blocked(
                        task_id=f"GH-{issue.get('number')}",
                        reason=issue.get("title", "Issue blocked"),
                        issue_number=issue.get("number"),
                    )

        elif event_type == "push":
            ref = payload.get("ref", "")
            branch = ref.replace("refs/heads/", "")

            if branch in WATCHED_BRANCHES:
                # Notify of push to watched branch
                commits = payload.get("commits", [])
                if commits:
                    pusher = payload.get("pusher", {}).get("name", "unknown")
                    _send_maestro_message(
                        f"Push to {branch}",
                        f"{len(commits)} commit(s) pushed to {branch} by {pusher}",
                        priority="low",
                    )

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """Suppress default logging — intentionally ignores all parameters."""


def run_server(port: int = 9000) -> None:
    """Run webhook server."""
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"Webhook server running on port {port}")
    server.serve_forever()


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitHub CI webhook handler")
    parser.add_argument("--port", type=int, default=9000, help="Server port")
    parser.add_argument(
        "--test", type=Path, help="Test with JSON file instead of running server"
    )

    args = parser.parse_args()

    if args.test:
        # Test mode: process a JSON file
        with open(args.test) as f:
            payload = json.load(f)
        event_type = payload.pop("_event_type", "workflow_run")
        success, msg = handle_github_webhook(event_type, payload)
        print(f"{'OK' if success else 'FAILED'}: {msg}")
    else:
        run_server(args.port)
