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
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any


# Configuration
WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
WATCHED_BRANCHES = {"main", "master", "develop"}
# SC-P1-003: Maximum allowed request body size (1 MB)
MAX_CONTENT_LENGTH = 1_048_576
EMASOFT_DIR = Path(os.environ.get("EMASOFT_DIR", str(Path.home() / ".emasoft")))
LOG_DIR = EMASOFT_DIR / "webhook_logs"
AIMAESTRO_API = os.environ.get("AIMAESTRO_API", "http://localhost:23000")
# SC-P2-003: Validate AIMAESTRO_API must point to localhost to prevent SSRF
from urllib.parse import urlparse as _urlparse
_parsed_api = _urlparse(AIMAESTRO_API)
if _parsed_api.hostname not in ("localhost", "127.0.0.1", "::1"):
    print("ERROR: AIMAESTRO_API must point to localhost for security", file=sys.stderr)
    sys.exit(1)


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
        # CC-XP-012: Use urllib instead of subprocess curl for cross-platform compat
        req = urllib.request.Request(
            f"{AIMAESTRO_API}/api/messages",
            data=payload.encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except (OSError, urllib.error.URLError) as e:
        print(f"WARNING: Failed to send AI Maestro notification: {e}", file=sys.stderr)


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
    """Verify GitHub webhook HMAC-SHA256 signature.

    SC-P1-002: The secret is now required at startup, so it will never be empty
    when this function is called during normal server operation. The guard is
    kept as defence-in-depth for any future call-site that bypasses the startup
    check.
    """
    if not secret:
        # Defence-in-depth: reject if secret is somehow missing at runtime
        return False

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
        # SC-P1-003: Enforce maximum content length to prevent memory exhaustion
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid Content-Length")
            return
        if content_length > MAX_CONTENT_LENGTH:
            self.send_response(413)
            self.end_headers()
            self.wfile.write(
                f"Payload too large (max {MAX_CONTENT_LENGTH} bytes)".encode()
            )
            return

        # Read payload with bounded size even if Content-Length header is absent
        # or was tampered with (defence-in-depth)
        payload_bytes = self.rfile.read(min(content_length, MAX_CONTENT_LENGTH))

        # Verify signature
        signature = self.headers.get("X-Hub-Signature-256", "")
        # Explicitly reject requests with no signature header before HMAC comparison
        if not signature:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"Missing X-Hub-Signature-256 header")
            return
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


def run_server(port: int = 9000, bind: str = "127.0.0.1") -> None:
    """Run webhook server.

    SC-P1-002: Refuses to start if GITHUB_WEBHOOK_SECRET is not configured.
    SC-P1-004: Binds to 127.0.0.1 by default (localhost only). Pass --bind
    0.0.0.0 explicitly if the server must be reachable from outside (e.g.
    behind a reverse proxy).
    """
    # SC-P1-002: Require webhook secret at startup
    if not WEBHOOK_SECRET:
        print(
            "ERROR: GITHUB_WEBHOOK_SECRET environment variable is not set.\n"
            "The webhook server refuses to start without a shared secret.\n"
            "Set it with: export GITHUB_WEBHOOK_SECRET='your-secret-here'",
            file=sys.stderr,
        )
        sys.exit(1)

    server = HTTPServer((bind, port), WebhookHandler)
    print(f"Webhook server running on {bind}:{port}")
    server.serve_forever()


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitHub CI webhook handler")
    parser.add_argument("--port", type=int, default=9000, help="Server port")
    parser.add_argument(
        "--bind",
        default="127.0.0.1",
        help="Address to bind to (default: 127.0.0.1, use 0.0.0.0 for all interfaces)",
    )
    parser.add_argument(
        "--test", type=Path, help="Test with JSON file instead of running server"
    )

    args = parser.parse_args()

    if args.test:
        # Test mode: process a JSON file
        with open(args.test, encoding="utf-8") as f:
            payload = json.load(f)
        event_type = payload.pop("_event_type", "workflow_run")
        success, msg = handle_github_webhook(event_type, payload)
        print(f"{'OK' if success else 'FAILED'}: {msg}")
    else:
        run_server(args.port, bind=args.bind)
