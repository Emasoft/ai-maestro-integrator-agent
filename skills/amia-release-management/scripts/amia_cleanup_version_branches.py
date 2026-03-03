#!/usr/bin/env python3
"""AMIA Release Management - Version Branch Cleanup Script.

PURPOSE:
This script identifies and provides commands to delete version branches
that collide with release tags, which causes HTTP 300 errors in the
auto-updater.

BACKGROUND:
When both a branch and tag share the same name (e.g., "v2.6.5"), GitHub's
API returns HTTP 300 (Multiple Choices) when requesting tarball downloads.
This breaks the auto-updater for users on older versions.

The recommended code fix is to use explicit "refs/tags/" prefix, but
users on older versions can't update until the branch/tag collision is
resolved.

SAFETY:
This script DOES NOT delete anything automatically. It only prints commands
that the repository maintainer can review and execute manually.
"""

import re
import subprocess
import sys

# ANSI colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"

VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+$")


def run_git(*args: str) -> list[str]:
    """Run a git command and return non-empty stripped lines."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    print(f"{BLUE}╔════════════════════════════════════════════════════════════════╗{NC}")
    print(f"{BLUE}║            AMIA - Version Branch Cleanup Tool                  ║{NC}")
    print(f"{BLUE}╔════════════════════════════════════════════════════════════════╗{NC}")
    print()

    print(f"{YELLOW}Analyzing repository for version collisions...{NC}")
    print()

    # Get all version tags
    tags = [t for t in run_git("tag") if VERSION_RE.match(t)]
    tags.sort(key=lambda v: [int(x) for x in v.lstrip("v").split(".")])

    # Get all local version branches
    local_branches = {
        b
        for b in run_git("branch", "--format=%(refname:short)")
        if VERSION_RE.match(b)
    }

    # Get all remote version branches (strip "origin/" prefix)
    remote_branches = set()
    for b in run_git("branch", "-r", "--format=%(refname:short)"):
        name = b.removeprefix("origin/")
        if VERSION_RE.match(name):
            remote_branches.add(name)

    # Find collisions
    colliding_branches: list[str] = []

    print(f"{BLUE}═══════════════════════════════════════════════════════════════{NC}")
    print(f"{BLUE}COLLISION ANALYSIS{NC}")
    print(f"{BLUE}═══════════════════════════════════════════════════════════════{NC}")
    print()

    for tag in tags:
        if tag in local_branches:
            print(f"{RED}⚠️  COLLISION FOUND:{NC} Tag {GREEN}{tag}{NC} collides with {RED}local branch{NC}")
            if tag not in colliding_branches:
                colliding_branches.append(tag)

        if tag in remote_branches:
            print(f"{RED}⚠️  COLLISION FOUND:{NC} Tag {GREEN}{tag}{NC} collides with {RED}remote branch{NC}")
            if tag not in colliding_branches:
                colliding_branches.append(tag)

    print()

    if not colliding_branches:
        print(f"{GREEN}✓ No collisions found!{NC}")
        print(f"{GREEN}  All version tags are unique.{NC}")
        print()
        return 0

    print(f"{BLUE}═══════════════════════════════════════════════════════════════{NC}")
    print(f"{BLUE}CLEANUP COMMANDS{NC}")
    print(f"{BLUE}═══════════════════════════════════════════════════════════════{NC}")
    print()
    print(f"{YELLOW}The following commands will delete colliding branches:{NC}")
    print()
    print(f"{RED}⚠️  WARNING: Review these carefully before executing!{NC}")
    print()

    for branch in colliding_branches:
        print(f"{YELLOW}# Delete local and remote branch: {branch}{NC}")
        if branch in local_branches:
            print(f"git branch -D {branch}")
        if branch in remote_branches:
            print(f"git push origin --delete {branch}")
        print()

    print(f"{BLUE}═══════════════════════════════════════════════════════════════{NC}")
    print(f"{BLUE}RECOMMENDATIONS{NC}")
    print(f"{BLUE}═══════════════════════════════════════════════════════════════{NC}")
    print()
    print(f"{GREEN}1.{NC} Review the commands above carefully")
    print(f"{GREEN}2.{NC} Verify that these branches are no longer needed")
    print(f"{GREEN}3.{NC} Check if any open PRs reference these branches")
    print(f"{GREEN}4.{NC} Execute the commands manually (copy/paste)")
    print(f"{GREEN}5.{NC} After cleanup, users on old versions can update successfully")
    print()
    print(f"{YELLOW}WHY THIS MATTERS:{NC}")
    print("  • Users on older versions get HTTP 300 errors when updating")
    print("  • GitHub API can't distinguish between branch and tag with same name")
    print("  • The recommended fix uses explicit refs/tags/ prefix in API calls")
    print("  • But users need to update first - creating a chicken/egg problem")
    print()
    print(f"{YELLOW}BEST PRACTICE GOING FORWARD:{NC}")
    print(f"  • Use {GREEN}release tags{NC} (vX.Y.Z) for versioned releases")
    print(f"  • Use {GREEN}feature branches{NC} (feature/xxx) for development")
    print("  • Never create branches with version tag names")
    print()

    print(f"{BLUE}═══════════════════════════════════════════════════════════════{NC}")
    print(f"{BLUE}SUMMARY{NC}")
    print(f"{BLUE}═══════════════════════════════════════════════════════════════{NC}")
    print()
    print(f"  Total version tags: {GREEN}{len(tags)}{NC}")
    print(f"  Colliding branches: {RED}{len(colliding_branches)}{NC}")
    print()

    if colliding_branches:
        print(f"{YELLOW}Action required: Execute cleanup commands above{NC}")
        print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
