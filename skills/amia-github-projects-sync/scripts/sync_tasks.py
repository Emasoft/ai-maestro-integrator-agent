#!/usr/bin/env python3
"""
GitHub Task Synchronisation Script
Syncs task lists with GitHub Projects using the gh CLI
"""

import sys
import json
import subprocess
import argparse
import re
from pathlib import Path
from typing import Any

# Import thresholds from lib module (canonical source of truth)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
from lib.thresholds import TechnicalTimeouts, GitHubThresholds  # type: ignore[import-not-found]

TIMEOUTS = TechnicalTimeouts()
GH_THRESHOLDS = GitHubThresholds()


class GitHubProjectSync:
    """Handles synchronisation of tasks to GitHub Projects"""

    def __init__(self, repo: str | None = None, project_number: int | None = None):
        self.repo = repo
        self.project_number = project_number

    def check_gh_cli(self) -> bool:
        """Check if gh CLI is installed and authenticated"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                check=False,
                timeout=TIMEOUTS.API,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def get_origin_remote(self) -> str | None:
        """Get the GitHub repo from git remotes"""
        try:
            # Try 'origin' first
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=False,
                timeout=TIMEOUTS.GIT,
            )
            if result.returncode == 0:
                return self._parse_github_url(result.stdout.strip())

            # If no origin, get first remote
            result = subprocess.run(
                ["git", "remote"],
                capture_output=True,
                text=True,
                check=False,
                timeout=TIMEOUTS.GIT,
            )
            if result.returncode == 0 and result.stdout.strip():
                remote_name = result.stdout.strip().split("\n")[0]
                result = subprocess.run(
                    ["git", "remote", "get-url", remote_name],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=TIMEOUTS.GIT,
                )
                if result.returncode == 0:
                    return self._parse_github_url(result.stdout.strip())

            return None
        except Exception as e:
            print(f"Error getting remote: {e}", file=sys.stderr)
            return None

    def _parse_github_url(self, url: str) -> str | None:
        """Parse GitHub URL to owner/repo format"""
        # Handle HTTPS URLs
        https_match = re.search(r"github\.com[/:]([^/]+/[^/]+?)(\.git)?$", url)
        if https_match:
            return https_match.group(1).rstrip(".git")

        # Handle SSH URLs
        ssh_match = re.search(r"git@github\.com:([^/]+/[^/]+?)(\.git)?$", url)
        if ssh_match:
            return ssh_match.group(1).rstrip(".git")

        return None

    def list_projects(self, repo: str) -> list[dict[str, Any]]:
        """List all projects for a repository"""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "project",
                    "list",
                    "--owner",
                    repo.split("/")[0],
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=TIMEOUTS.COMMAND,
            )
            projects: Any = json.loads(result.stdout)
            result_list: list[dict[str, Any]] = (
                projects.get("projects", []) if isinstance(projects, dict) else projects
            )
            return result_list
        except subprocess.CalledProcessError as e:
            print(f"Error listing projects: {e.stderr}", file=sys.stderr)
            return []
        except (json.JSONDecodeError, subprocess.TimeoutExpired):
            print("Error parsing project list", file=sys.stderr)
            return []

    def get_first_project(self, repo: str) -> int | None:
        """Get the first available project number for a repo"""
        projects = self.list_projects(repo)
        if projects and len(projects) > 0:
            # Return the number from the first project
            number = projects[0].get("number")
            return int(number) if number is not None else None
        return None

    def create_issue(
        self, repo: str, title: str, body: str = "", labels: list[str] | None = None
    ) -> str | None:
        """Create a GitHub issue and return its URL"""
        try:
            cmd = [
                "gh",
                "issue",
                "create",
                "--repo",
                repo,
                "--title",
                title,
                "--body",
                body or "",
            ]

            if labels:
                cmd.extend(["--label", ",".join(labels)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=TIMEOUTS.COMMAND,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            error_msg = (
                e.stderr
                if isinstance(e, subprocess.CalledProcessError)
                else f"Timeout after {TIMEOUTS.COMMAND}s"
            )
            print(f"Error creating issue: {error_msg}", file=sys.stderr)
            return None

    def add_issue_to_project(
        self, project_number: int, issue_url: str, owner: str
    ) -> bool:
        """Add an issue to a project"""
        try:
            subprocess.run(
                [
                    "gh",
                    "project",
                    "item-add",
                    str(project_number),
                    "--owner",
                    owner,
                    "--url",
                    issue_url,
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=TIMEOUTS.COMMAND,
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            error_msg = (
                e.stderr
                if isinstance(e, subprocess.CalledProcessError)
                else f"Timeout after {TIMEOUTS.COMMAND}s"
            )
            print(f"Error adding issue to project: {error_msg}", file=sys.stderr)
            return False

    def sync_tasks(self, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Sync tasks to GitHub

        Args:
            tasks: List of dicts with 'title' and optional 'body', 'labels'

        Returns:
            Dict with sync results
        """
        if not self.check_gh_cli():
            return {
                "success": False,
                "error": "gh CLI not installed or not authenticated. Run: gh auth login",
            }

        # Determine repo
        if not self.repo:
            self.repo = self.get_origin_remote()
            if not self.repo:
                return {
                    "success": False,
                    "error": "Could not determine GitHub repository. Please specify --repo owner/repo",
                }

        # Determine project
        if not self.project_number:
            self.project_number = self.get_first_project(self.repo)
            if not self.project_number:
                return {
                    "success": False,
                    "error": f"No projects found for {self.repo}. Please create a project or specify --project-number",
                }

        owner = self.repo.split("/")[0]
        synced_tasks: list[dict[str, Any]] = []
        failed_tasks: list[dict[str, Any]] = []

        for task in tasks:
            title = task.get("title")
            if not title:
                failed_tasks.append({"task": task, "error": "No title provided"})
                continue

            body = task.get("body", "")
            labels_raw = task.get("labels")
            labels: list[str] | None = (
                labels_raw if isinstance(labels_raw, list) else None
            )

            # Create issue
            issue_url = self.create_issue(self.repo, title, body, labels)
            if not issue_url:
                failed_tasks.append({"task": task, "error": "Failed to create issue"})
                continue

            # Add to project
            if self.add_issue_to_project(self.project_number, issue_url, owner):
                synced_tasks.append({"task": task, "issue_url": issue_url})
            else:
                failed_tasks.append(
                    {
                        "task": task,
                        "error": "Issue created but failed to add to project",
                        "issue_url": issue_url,
                    }
                )

        return {
            "success": True,
            "repo": self.repo,
            "project_number": self.project_number,
            "synced_tasks": synced_tasks,
            "failed_tasks": failed_tasks,
        }


def parse_markdown_tasks(content: str) -> list[dict[str, str]]:
    """
    Parse markdown content for task list items
    Supports:
    - [ ] Task title
    - [x] Completed task (skipped)
    """
    tasks: list[dict[str, str]] = []
    lines = content.split("\n")

    for line in lines:
        # Match uncompleted tasks: - [ ] or * [ ]
        if re.match(r"^[\s]*[-*]\s+\[\s\]\s+", line):
            title = re.sub(r"^[\s]*[-*]\s+\[\s\]\s+", "", line).strip()
            if title:
                tasks.append({"title": title})

    return tasks


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronise tasks to GitHub Projects")
    parser.add_argument("--repo", "-r", help="GitHub repository (owner/repo format)")
    parser.add_argument(
        "--project-number", "-p", type=int, help="GitHub Project number"
    )
    parser.add_argument(
        "--tasks-file", "-f", help="File containing tasks (markdown format)"
    )
    parser.add_argument(
        "--task",
        "-t",
        action="append",
        help="Individual task title (can be used multiple times)",
    )
    parser.add_argument("--json-tasks", help="JSON string of tasks array")

    args = parser.parse_args()

    # Gather tasks from various sources
    tasks: list[dict[str, Any]] = []

    if args.tasks_file:
        try:
            with open(args.tasks_file, encoding="utf-8") as f:
                content = f.read()
                tasks.extend(parse_markdown_tasks(content))
        except FileNotFoundError:
            print(f"Error: File {args.tasks_file} not found", file=sys.stderr)
            sys.exit(1)

    if args.task:
        for task_title in args.task:
            tasks.append({"title": task_title})

    if args.json_tasks:
        try:
            json_tasks: Any = json.loads(args.json_tasks)
            if isinstance(json_tasks, list):
                tasks.extend(json_tasks)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON tasks: {e}", file=sys.stderr)
            sys.exit(1)

    if not tasks:
        print(
            "Error: No tasks provided. Use --tasks-file, --task, or --json-tasks",
            file=sys.stderr,
        )
        sys.exit(1)

    # Perform sync
    syncer = GitHubProjectSync(repo=args.repo, project_number=args.project_number)
    results = syncer.sync_tasks(tasks)

    # Output results
    print(json.dumps(results, indent=2))

    if not results["success"]:
        sys.exit(1)

    if results["failed_tasks"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
