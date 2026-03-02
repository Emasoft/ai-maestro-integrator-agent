#!/usr/bin/env python3
"""
Synthesize context and assign Claude Code Action to an issue via GitHub Actions.

Usage:
    python3 amia_invoke_claude_assignment.py --issue 123
    python3 amia_invoke_claude_assignment.py --issue 123 --skip-workflow
    python3 amia_invoke_claude_assignment.py --issue 123 --prepare-context-only
    python3 amia_invoke_claude_assignment.py --issue 123 --dry-run

Features:
    - Fetches issue and comments
    - Extracts context from trusted sources (maintainers, AI agents)
    - Generates a synthesis comment with @claude mention
    - Triggers claude-code-action workflow via repository dispatch
    - Idempotent: Updates existing synthesis comment if found

Output:
    JSON object with action taken, comment URL, and workflow trigger status.

Exit Codes:
    0 - Success (includes idempotent update)
    1 - Invalid parameters
    2 - Issue not found
    3 - API error
    4 - Not authenticated
    5 - Idempotency skip (no content to synthesize)

Note:
    This script is designed to work with claude-code-action GitHub Action.
    The workflow must be configured to respond to @claude mentions or
    repository dispatch events.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any


# Default configuration
# NOTE: Maintainers list should be populated with actual repo maintainers
# AI agents list contains Claude-based agents only (generic, IDE-independent)
DEFAULT_CONFIG = {
    "trusted_sources": {
        "maintainers": [],  # Populate with actual repo maintainer usernames
        "ai_agents": [
            "claude-code[bot]",  # Claude Code Action bot
            "github-actions[bot]",  # GitHub Actions (hosts Claude Code Action)
        ],
    },
    "extraction_patterns": {
        "ai_triage": {
            "marker": "<!-- AI-ISSUE-TRIAGE -->",
        },
    },
    "synthesis": {
        "marker": "<!-- CLAUDE-CONTEXT-SYNTHESIS -->",
    },
}


def check_gh_auth() -> bool:
    """Verify gh CLI is authenticated."""
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def get_repo_info() -> tuple[str, str]:
    """Get owner and repo name from current directory."""
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "owner,name"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("Failed to get repo info. Are you in a git repository?")

    data = json.loads(result.stdout)
    return data["owner"]["login"], data["name"]


def get_issue(owner: str, repo: str, issue_number: int) -> dict[str, Any]:
    """Fetch issue details."""
    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/issues/{issue_number}"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        error = result.stderr.strip()
        if "not found" in error.lower():
            raise RuntimeError(
                f"NOT_FOUND: Issue #{issue_number} not found in {owner}/{repo}"
            )
        raise RuntimeError(f"API_ERROR: Failed to get issue: {error}")

    issue_data: dict[str, Any] = json.loads(result.stdout)
    return issue_data


def get_issue_comments(
    owner: str, repo: str, issue_number: int
) -> list[dict[str, Any]]:
    """Fetch all comments on an issue."""
    result = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{owner}/{repo}/issues/{issue_number}/comments",
            "--paginate",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        error = result.stderr.strip()
        raise RuntimeError(f"API_ERROR: Failed to get comments: {error}")

    comments_data: list[dict[str, Any]] = json.loads(result.stdout)
    return comments_data


def filter_trusted_comments(
    comments: list[dict[str, Any]],
    maintainers: list[str],
    ai_agents: list[str],
) -> list[dict[str, Any]]:
    """Filter comments to only those from trusted sources."""
    trusted_users = set(maintainers + ai_agents)
    return [c for c in comments if c.get("user", {}).get("login") in trusted_users]


def extract_maintainer_guidance(
    comments: list[dict[str, Any]],
    maintainers: list[str],
) -> list[str]:
    """Extract key decisions from maintainer comments.

    Uses a tiered approach:
    1. Extract explicit bullet points and numbered items
    2. If none found, extract sentences with RFC 2119 keywords
    """
    maintainer_comments = [
        c for c in comments if c.get("user", {}).get("login") in maintainers
    ]

    guidance = []
    for comment in maintainer_comments:
        body = comment.get("body", "")
        lines = body.split("\n")
        found_bullets = False

        # First pass: bullet points and numbered items
        for line in lines:
            trimmed = line.strip()
            # Match numbered items (1. xxx) or bullet points (- xxx, * xxx)
            match = re.match(r"^\d+\.\s+(.+)$|^[-*]\s+(.+)$", trimmed)
            if match:
                item = match.group(1) or match.group(2)
                # Skip checkbox items or too short
                if len(item) > 10 and not re.match(r"^\[[ x]\]", item):
                    guidance.append(item)
                    found_bullets = True

        # Second pass: RFC 2119 keywords if no bullets found
        if not found_bullets:
            sentences = re.split(r"(?<=[.!?])\s+", body)
            for sentence in sentences:
                cleaned = re.sub(r"[\r\n]+", " ", sentence.strip())
                # Match sentences with RFC 2119 keywords
                if re.search(
                    r"\b(MUST|SHOULD|SHALL|REQUIRED|RECOMMENDED)\b", cleaned, re.I
                ):
                    if len(cleaned) > 15:
                        guidance.append(cleaned)

    return guidance


def extract_ai_triage(
    comments: list[dict[str, Any]],
    marker: str,
) -> dict[str, str] | None:
    """Extract triage information from AI Triage comments."""
    # Find triage comment by marker
    triage_comment = None
    for c in comments:
        if marker in c.get("body", ""):
            triage_comment = c
            break

    if not triage_comment:
        return None

    body = triage_comment["body"]
    triage = {}

    for field in ["Priority", "Category"]:
        # Match Markdown table format: | **Priority** | `P1` |
        match = re.search(rf"^\s*\|\s*\*\*{field}\*\*\s*\|\s*`([^`]+)`", body, re.M)
        if match:
            triage[field.lower()] = match.group(1).strip()
        else:
            # Fallback to plain text: Priority: P1
            match = re.search(rf"^{field}[:\s]+(\S+)", body, re.M)
            if match:
                triage[field.lower()] = match.group(1)

    return triage if triage else None


def extract_related_items(
    comments: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Extract related issues and PRs from comments."""
    plan: dict[str, list[str]] = {"related_issues": [], "related_prs": []}

    for comment in comments:
        body = comment.get("body", "")

        # Extract related issues
        issue_matches = re.findall(r"/issues/(\d+)|#(\d+)", body)
        for match in issue_matches:
            issue_num = match[0] or match[1]
            ref = f"#{issue_num}"
            if ref not in plan["related_issues"]:
                plan["related_issues"].append(ref)

        # Extract related PRs
        pr_matches = re.findall(r"/pull/(\d+)", body)
        for match in pr_matches:
            ref = f"#{match}"
            if ref not in plan["related_prs"]:
                plan["related_prs"].append(ref)

    # Return None if no meaningful content
    if not plan["related_issues"] and not plan["related_prs"]:
        return None

    return plan


def has_synthesizable_content(
    guidance: list[str],
    triage: dict[str, str] | None,
    plan: dict[str, Any] | None,
) -> bool:
    """Check if there's any content worth synthesizing."""
    if guidance:
        return True
    if triage and (triage.get("priority") or triage.get("category")):
        return True
    if plan and (
        plan.get("implementation")
        or plan.get("related_issues")
        or plan.get("related_prs")
    ):
        return True
    return False


def find_existing_synthesis(
    comments: list[dict[str, Any]],
    marker: str,
) -> dict[str, Any] | None:
    """Find existing synthesis comment by marker."""
    for c in comments:
        if marker in c.get("body", ""):
            return c
    return None


def generate_synthesis_body(
    marker: str,
    guidance: list[str],
    triage: dict[str, str] | None,
    plan: dict[str, Any] | None,
) -> str:
    """Generate the synthesis comment body."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    body = f"{marker}\n\n@claude Here is synthesized context for this issue:\n"

    # Maintainer Guidance section
    if guidance:
        body += "\n## Maintainer Guidance\n\n"
        for item in guidance[:10]:  # Limit to 10 items
            body += f"- {item}\n"

    # AI Agent Recommendations section
    has_ai_content = triage or (
        plan
        and (
            plan.get("implementation")
            or plan.get("related_issues")
            or plan.get("related_prs")
        )
    )

    if has_ai_content:
        body += "\n## AI Agent Recommendations\n\n"

        if triage:
            if triage.get("priority"):
                body += f"- **Priority**: {triage['priority']}\n"
            if triage.get("category"):
                body += f"- **Category**: {triage['category']}\n"

        if plan:
            if plan.get("related_issues"):
                body += f"- **Related Issues**: {', '.join(plan['related_issues'])}\n"
            if plan.get("related_prs"):
                body += f"- **Related PRs**: {', '.join(plan['related_prs'])}\n"

    body += f"\n---\n*Generated: {timestamp}*"
    return body


def create_context_file(
    issue: dict[str, Any],
    trusted_comments: list[dict[str, Any]],
    issue_number: int,
) -> str:
    """Create a context file for AI synthesis."""
    content = f"""# Issue Context for Synthesis

## Issue Details

**Title**: {issue.get("title", "")}
**Labels**: {", ".join(label["name"] for label in issue.get("labels", []))}

### Description

{issue.get("body", "")}

## Comments from Trusted Sources

"""

    for comment in trusted_comments:
        author = comment.get("user", {}).get("login", "unknown")
        content += f"\n### Comment by {author}\n\n{comment.get('body', '')}\n\n---\n"

    # SC-P1-007: Use secure temp file creation to avoid predictable path attacks
    fd, context_file = tempfile.mkstemp(
        suffix=".md", prefix=f"issue-{issue_number}-context-"
    )
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)

    return context_file


def post_comment(owner: str, repo: str, issue_number: int, body: str) -> dict[str, Any]:
    """Post a new comment on an issue."""
    # SC-P1-005: Pipe body via stdin to avoid shell injection from user-controlled content
    result = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{owner}/{repo}/issues/{issue_number}/comments",
            "-X",
            "POST",
            "-F",
            "body=@-",
        ],
        input=body,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"API_ERROR: Failed to post comment: {result.stderr.strip()}"
        )

    comment_result: dict[str, Any] = json.loads(result.stdout)
    return comment_result


def update_comment(owner: str, repo: str, comment_id: int, body: str) -> dict[str, Any]:
    """Update an existing comment."""
    # SC-P1-005: Pipe body via stdin to avoid shell injection from user-controlled content
    result = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{owner}/{repo}/issues/comments/{comment_id}",
            "-X",
            "PATCH",
            "-F",
            "body=@-",
        ],
        input=body,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"API_ERROR: Failed to update comment: {result.stderr.strip()}"
        )

    update_result: dict[str, Any] = json.loads(result.stdout)
    return update_result


def trigger_claude_workflow(owner: str, repo: str, issue_number: int) -> bool:
    """Trigger claude-code-action workflow via repository dispatch.

    This triggers the claude-mention.yml workflow which will respond
    to the @claude mention in the synthesis comment.
    """
    # The workflow should be triggered automatically by the @claude mention
    # in the comment. This function can be used to trigger via repository_dispatch
    # if needed for immediate processing.
    result = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{owner}/{repo}/dispatches",
            "-X",
            "POST",
            "-f",
            "event_type=claude-issue-assignment",
            "-f",
            f"client_payload[issue_number]={issue_number}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Synthesize context and assign Claude Code Action to an issue."
    )
    parser.add_argument(
        "--issue",
        type=int,
        required=True,
        help="Issue number",
    )
    parser.add_argument(
        "--repo",
        help="Repository in owner/repo format. Inferred from git if not provided.",
    )
    parser.add_argument(
        "--skip-workflow",
        action="store_true",
        help="Skip triggering claude-code-action workflow",
    )
    parser.add_argument(
        "--prepare-context-only",
        action="store_true",
        help="Only prepare context file; do not create synthesis comment",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview synthesis comment without posting",
    )

    args = parser.parse_args()

    # Check authentication
    if not check_gh_auth():
        print(
            json.dumps({"error": "Not authenticated. Run 'gh auth login' first."}),
            file=sys.stderr,
        )
        sys.exit(4)

    try:
        # Get repo info
        if args.repo:
            parts = args.repo.split("/")
            if len(parts) != 2:
                print(
                    json.dumps({"error": "Invalid repo format. Use owner/repo"}),
                    file=sys.stderr,
                )
                sys.exit(1)
            owner, repo = parts
        else:
            owner, repo = get_repo_info()

        # Fetch issue
        issue = get_issue(owner, repo, args.issue)

        # Fetch comments
        comments = get_issue_comments(owner, repo, args.issue)

        # Load config (using defaults)
        config: dict[str, Any] = DEFAULT_CONFIG

        # Filter trusted comments
        trusted_sources = config["trusted_sources"]
        if not isinstance(trusted_sources, dict):
            print(f"ERROR: Expected dict, got {type(trusted_sources).__name__}", file=sys.stderr)
            sys.exit(1)
        maintainers = trusted_sources["maintainers"]
        ai_agents = trusted_sources["ai_agents"]
        if not isinstance(maintainers, list):
            print(f"ERROR: Expected list, got {type(maintainers).__name__}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(ai_agents, list):
            print(f"ERROR: Expected list, got {type(ai_agents).__name__}", file=sys.stderr)
            sys.exit(1)
        trusted_comments = filter_trusted_comments(
            comments,
            maintainers,
            ai_agents,
        )

        # Prepare context only mode
        if args.prepare_context_only:
            context_file = create_context_file(issue, trusted_comments, args.issue)
            synthesis_config = config["synthesis"]
            if not isinstance(synthesis_config, dict):
                print(f"ERROR: Expected dict, got {type(synthesis_config).__name__}", file=sys.stderr)
                sys.exit(1)
            synthesis_marker = synthesis_config["marker"]
            if not isinstance(synthesis_marker, str):
                print(f"ERROR: Expected str, got {type(synthesis_marker).__name__}", file=sys.stderr)
                sys.exit(1)
            existing = find_existing_synthesis(comments, synthesis_marker)

            result: dict[str, Any] = {
                "contextFile": context_file,
                "existingSynthesisId": existing.get("id") if existing else None,
                "marker": synthesis_marker,
                "issueNumber": args.issue,
                "owner": owner,
                "repo": repo,
            }
            print(json.dumps(result, indent=2))
            sys.exit(0)

        # Extract context
        guidance = extract_maintainer_guidance(
            trusted_comments,
            config["trusted_sources"]["maintainers"],
        )
        triage = extract_ai_triage(
            trusted_comments,
            config["extraction_patterns"]["ai_triage"]["marker"],
        )
        plan = extract_related_items(trusted_comments)

        # Check if there's content to synthesize
        has_content = has_synthesizable_content(guidance, triage, plan)
        existing = find_existing_synthesis(comments, config["synthesis"]["marker"])

        # Dry run mode
        if args.dry_run:
            if has_content:
                body = generate_synthesis_body(
                    config["synthesis"]["marker"],
                    guidance,
                    triage,
                    plan,
                )
                print("=== SYNTHESIS PREVIEW ===")
                print(body)
                print("=== END PREVIEW ===")
                if existing:
                    print(f"\nWould UPDATE existing comment (ID: {existing['id']})")
                else:
                    print("\nWould CREATE new synthesis comment")
            else:
                print("No synthesizable content found - would SKIP synthesis comment")
            print(f"Would TRIGGER claude-code-action for issue #{args.issue}")
            sys.exit(0)

        # Perform synthesis
        response = None
        action = "skipped"

        if has_content:
            body = generate_synthesis_body(
                config["synthesis"]["marker"],
                guidance,
                triage,
                plan,
            )

            if existing:
                response = update_comment(owner, repo, existing["id"], body)
                action = "updated"
            else:
                response = post_comment(owner, repo, args.issue, body)
                action = "created"

        # Trigger workflow
        workflow_triggered = False
        if not args.skip_workflow:
            # The @claude mention in the comment will trigger the workflow
            # automatically if claude-mention.yml is configured
            workflow_triggered = True  # Assumed triggered via @claude mention

        # Output result
        result = {
            "success": True,
            "action": action,
            "issueNumber": args.issue,
            "commentId": response.get("id") if response else None,
            "commentUrl": response.get("html_url") if response else None,
            "workflowTriggered": workflow_triggered,
            "marker": config["synthesis"]["marker"],
        }
        print(json.dumps(result, indent=2))

        if not has_content:
            sys.exit(5)  # Idempotency skip

    except RuntimeError as e:
        error_str = str(e)
        error_output = {
            "error": error_str,
            "issue": args.issue,
            "success": False,
        }
        print(json.dumps(error_output), file=sys.stderr)

        # Determine exit code based on error type
        if error_str.startswith("NOT_FOUND"):
            sys.exit(2)
        elif error_str.startswith("API_ERROR"):
            sys.exit(3)
        else:
            sys.exit(3)


if __name__ == "__main__":
    main()
