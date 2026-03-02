# Creating Worktrees: Standard Creation Flow

## Overview

This document covers the standard 6-step flow for creating git worktrees systematically and safely.

## Table of Contents

1. [STEP 1: Check Registry for Conflicts](#step-1-check-registry-for-conflicts)
2. [STEP 2: Determine Naming Based on Purpose](#step-2-determine-naming-based-on-purpose)
3. [STEP 3: Allocate Ports If Needed](#step-3-allocate-ports-if-needed)
4. [STEP 4: Create Git Worktree](#step-4-create-git-worktree)
5. [STEP 5: Register in Registry](#step-5-register-in-registry)
6. [STEP 6: Setup Environment](#step-6-setup-environment)

---

## STEP 1: Check Registry for Conflicts

**Purpose**: Prevent duplicate worktree names and port conflicts.

**Action**: Before creating any worktree, check the registry file to ensure:
- The worktree name is not already in use
- The ports you plan to allocate are not already assigned
- The target branch is not already checked out in another worktree

**Command**:
```bash
# Check if worktree name exists
cat .worktree-registry.json | jq -r '.worktrees[].path' | grep "review-GH-42"

# Check if port is in use
cat .worktree-registry.json | jq -r '.worktrees[].ports[]' | grep "3001"
```

**What "registry" means**: The registry is a JSON file (`.worktree-registry.json`) in the main repository root that tracks all active worktrees, their paths, branches, ports, and metadata.

**What "conflict" means**: A conflict occurs when:
- Two worktrees have the same name
- Two worktrees try to use the same port number
- The same branch is checked out in multiple worktrees (git prevents this)

---

## STEP 2: Determine Naming Based on Purpose

**Purpose**: Use consistent naming conventions so worktrees are self-documenting.

**Action**: Choose the appropriate naming pattern based on what the worktree will be used for.

**Naming Patterns**:

| Purpose | Pattern | Example |
|---------|---------|---------|
| PR Review | `review-GH-{number}` | `review-GH-42` |
| Feature Development | `feature-{name}` | `feature-user-profiles` |
| Bug Fix | `bugfix-GH-{number}-{desc}` | `bugfix-GH-55-crash` |
| Testing | `test-{type}-{target}` | `test-integration-api` |
| Hotfix | `hotfix-{desc}` | `hotfix-security-patch` |
| Experiment | `exp-{name}` | `exp-new-architecture` |

**Why use these patterns**: Consistent naming allows you to:
- Identify the purpose of a worktree at a glance
- Link worktrees to GitHub issues/PRs automatically
- Sort and filter worktrees programmatically
- Avoid naming conflicts

---

## STEP 3: Allocate Ports If Needed

**Purpose**: Assign unique port numbers for services that need to run in the worktree.

**Action**: If the worktree will run services (web servers, databases, APIs), allocate ports now.

**When to allocate ports**:
- Yes: Web applications that run dev servers
- Yes: API services
- Yes: Database services
- Yes: Microservices
- No: Simple bug fixes without running services
- No: Documentation-only changes
- No: Quick code reviews without testing

**Port allocation rules**:
1. Start from base port 3000 and increment
2. Check registry to avoid conflicts
3. Allocate at least 2 ports per worktree (app + API)
4. Reserve ports immediately, before creating worktree

**Example port allocation**:
```bash
# Main repository uses: 3000 (app), 3001 (API)
# First worktree gets: 3002 (app), 3003 (API)
# Second worktree gets: 3004 (app), 3005 (API)
```

See [Port Allocation Strategy](./creating-worktrees-part3-port-allocation.md) for complete details.

---

## STEP 4: Create Git Worktree

**Purpose**: Actually create the worktree directory and check out the branch.

**Action**: Use the `git worktree add` command with the appropriate options.

**Basic syntax**:
```bash
git worktree add <path> <branch-or-commit>
```

**What each part means**:
- `<path>`: Where the worktree directory will be created (relative or absolute path)
- `<branch-or-commit>`: What to check out (branch name, commit hash, or tag)

**Location convention**: Create worktrees as **siblings** to the main repository, not inside it:
```
project/
├── main-repo/          # Main repository
├── review-GH-42/       # Worktree (sibling)
├── feature-auth/       # Worktree (sibling)
└── bugfix-GH-55/       # Worktree (sibling)
```

**Why use sibling directories**:
- Keeps worktrees isolated from main repo
- Prevents accidental commits in wrong directory
- Makes cleanup easier
- Avoids .gitignore complications

**Example commands**:
```bash
# Create from existing remote branch
git worktree add ../review-GH-42 origin/feature/new-auth

# Create new branch
git worktree add ../feature-user-profiles -b feature/user-profiles

# Create from specific commit
git worktree add ../bugfix-GH-55-crash abc123def

# Create detached HEAD (for quick inspection)
git worktree add ../inspect-commit --detach abc123def
```

**Verification**: After creation, verify the worktree exists:
```bash
# List all worktrees
git worktree list

# Check specific worktree
ls -la ../review-GH-42
```

---

## STEP 5: Register in Registry

**Purpose**: Record the worktree in the central registry for tracking and management.

**Action**: Add an entry to `.worktree-registry.json` with all relevant metadata.

**Registry entry structure**:
```json
{
  "worktrees": [
    {
      "name": "review-GH-42",
      "path": "../review-GH-42",
      "branch": "feature/new-auth",
      "purpose": "review",
      "ports": [3002, 3003],
      "github_issue": 42,
      "created": "2025-12-31T10:30:00Z",
      "status": "active",
      "notes": "Reviewing authentication refactor PR"
    }
  ]
}
```

**What each field means**:
- `name`: The worktree identifier (matches directory name)
- `path`: Relative path from main repo to worktree
- `branch`: Git branch checked out in worktree
- `purpose`: Type of worktree (review, feature, bugfix, test, etc.)
- `ports`: Array of allocated port numbers
- `github_issue`: Linked GitHub issue/PR number (optional)
- `created`: ISO 8601 timestamp of creation
- `status`: Current state (active, archived, stale)
- `notes`: Human-readable description

**How to add registry entry**:
```bash
# Using jq to add entry (recommended)
jq '.worktrees += [{
  "name": "review-GH-42",
  "path": "../review-GH-42",
  "branch": "feature/new-auth",
  "purpose": "review",
  "ports": [3002, 3003],
  "github_issue": 42,
  "created": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
  "status": "active",
  "notes": "Reviewing authentication refactor PR"
}]' .worktree-registry.json > .worktree-registry.tmp.json && \
mv .worktree-registry.tmp.json .worktree-registry.json
```

**Manual alternative**: Edit `.worktree-registry.json` directly with a text editor, but be careful with JSON syntax.

---

## STEP 6: Setup Environment

**Purpose**: Prepare the worktree for actual work by installing dependencies and configuring the environment.

**Action**: Navigate to the worktree and run setup commands.

See [Environment Setup](./creating-worktrees-part4-environment-setup.md) for complete instructions.

**Quick setup checklist**:
- [ ] Navigate to worktree directory
- [ ] Install dependencies
- [ ] Copy/configure environment files
- [ ] Run database migrations (if applicable)
- [ ] Build assets (if applicable)
- [ ] Verify tests pass

---

## Related Documentation

- [Purpose-Specific Creation Patterns](./creating-worktrees-part2-purpose-patterns.md)
- [Port Allocation Strategy](./creating-worktrees-part3-port-allocation.md)
- [Environment Setup](./creating-worktrees-part4-environment-setup.md)
- [Commands Reference and Checklist](./creating-worktrees-part5-commands-checklist.md)
- [Troubleshooting](./creating-worktrees-part6-troubleshooting.md)
