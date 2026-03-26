# GitHub Integration Dispatcher -- Detailed Guide

## Table of Contents

- [Decision Tree: Which Skill to Use?](#decision-tree-which-skill-to-use)
- [Pull Requests](#pull-requests)
- [Projects V2 Sync](#projects-v2-sync)
- [Kanban Board Operations](#kanban-board-operations)
- [Git Worktrees](#git-worktrees)
- [GitHub API Operations](#github-api-operations)
- [Multiple GitHub Identities](#multiple-github-identities)
- [Batch Operations](#batch-operations)
- [Batch Label Operations](#batch-label-operations)
- [Automation Scripts](#automation-scripts)
- [Error Handling](#error-handling)
- [Extended Examples](#extended-examples)
- [First-Time Setup](#first-time-setup)
- [Changelog](#changelog)

## Decision Tree: Which Skill to Use?

Use this decision tree to route to the appropriate specialized skill.

### Pull Requests

**Use skill: `amia-github-pr-workflow`**

Covers:

- Creating pull requests linked to issues
- PR status monitoring and CI/CD integration
- Merge strategies (squash, merge commit, rebase)
- Auto-merge configuration
- PR workflow automation

### Projects V2 Sync

**Use skill: `amia-github-projects-sync`**

Covers:

- Bidirectional synchronization between agent tasks and GitHub Projects V2
- Creating and configuring project boards
- Status column management (Backlog, Todo, In Progress, AI Review, Human Review, Merge/Release, Done, Blocked)
- Custom field configuration (Priority, Due Date, Effort)
- Automation rules (auto-add, auto-archive, status transitions)
- Conflict resolution and sync health monitoring

### Kanban Board Operations

**Use skill: `amia-kanban-orchestration`**

Covers:

- Managing the 9-label classification system (feature, bug, refactor, test, docs, performance, security, dependencies, workflow)
- Issue lifecycle management across Kanban columns
- Label-based filtering and reporting
- Kanban-specific automation patterns

### Git Worktrees

**Use skill: `amia-git-worktree-operations`**

Covers:

- Creating and managing Git worktrees for parallel feature development
- Worktree-based PR workflows
- Cleanup and maintenance of worktrees

### GitHub API Operations

**See reference: `references/api-operations.md`**

Covers:

- Direct GitHub API calls (REST and GraphQL)
- Authentication methods (token, app, OAuth)
- Rate limiting and pagination
- Webhook configuration
- Advanced query patterns
- Quality gates before API operations
- Coordinating API operations via AI Maestro

### Multiple GitHub Identities

**See reference: `references/multi-user-workflow.md`**

Covers:

- SSH key setup for multiple accounts
- SSH host aliases configuration
- GitHub CLI multi-account authentication
- Identity switching and repository configuration
- Using the `gh_multiuser.py` script for automated identity management

## Batch Operations

When you need to perform operations that span multiple GitHub areas (e.g., bulk label changes across issues AND PRs, or cross-project synchronization).

### Batch Label Operations

**Reference:** `references/batch-operations.md`

Use when:

- Updating labels on multiple issues simultaneously
- Bulk closing stale issues
- Filtering by multiple criteria (label + status + assignee + date)
- Previewing changes before executing (dry-run mode)
- Creating audit trails for batch operations

Quick example:

```bash
# Bulk add label to all open issues with "feature" label
gh issue list --label "feature" --state open --json number --jq '.[].number' | \
  xargs -I {} gh issue edit {} --add-label "priority:high"
```

### Automation Scripts

**Reference:** `references/automation-scripts.md`

Available scripts:

- `sync-projects-v2.py` -- Sync GitHub Projects V2 with agent tasks
- `bulk-label-assignment.py` -- Bulk assign labels at scale
- `monitor-pull-requests.py` -- Monitor PR status and CI/CD failures
- `bulk-create-issues.py` -- Import issues from CSV/JSON
- `generate-project-report.py` -- Generate project status reports

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `gh: command not found` | GitHub CLI not installed or not in PATH | Install with `brew install gh` (macOS) or see `references/prerequisites-and-setup.md` |
| `HTTP 401 - Bad credentials` | Auth token expired or revoked | Re-authenticate: `gh auth login` then verify: `gh auth status` |
| `HTTP 403 - Resource not accessible` | Insufficient permissions | Request write access from repo owner; check token scopes (`repo`, `project`) |
| `HTTP 422 - Validation Failed` | Invalid field values (non-existent label, malformed project field) | Verify label: `gh label list`; check project fields: `gh project field-list` |
| `API rate limit exceeded` | Too many API calls | Wait for reset (`gh api rate-limit`); use GraphQL to batch queries |
| `Could not resolve to a Project` | Wrong project number or different org | Verify: `gh project list --owner <org>` |
| `xargs: gh: terminated by signal 13` | Pipe broken during batch op | Re-run with smaller batches or add error handling: `xargs -I {} sh -c 'gh issue edit {} --add-label "label" \|\| true'` |

## Extended Examples

### Route to PR skill

You receive: "Create a PR for the feature branch and link it to issue #42."
This is a Pull Request task. Invoke `amia-github-pr-workflow`:

```bash
gh pr create --base main --head feature-branch --title "Implement feature X" \
  --body "Closes #42" --assignee "@me"
```

### Bulk add label to bug issues

```bash
# Step 1: Preview affected issues (dry-run)
gh issue list --label "bug" --state open --json number,title \
  --jq '.[] | "\(.number): \(.title)"'

# Step 2: Apply the label change
gh issue list --label "bug" --state open --json number --jq '.[].number' | \
  xargs -I {} gh issue edit {} --add-label "priority:critical"

# Step 3: Verify a sample issue
gh issue view 15 --json labels --jq '.labels[].name'
```

### Projects V2 sync

You receive: "Sync the agent task board with the GitHub Project for repository X."
Invoke `amia-github-projects-sync`:

```bash
# Verify the project exists first
gh project list --owner Emasoft --format json

# Then follow the amia-github-projects-sync skill instructions
uv run python scripts/sync-projects-v2.py --repo Emasoft/repo-x --project 3 --direction bidirectional
```

## First-Time Setup

```bash
# Install GitHub CLI
brew install gh   # macOS
# or see https://cli.github.com/manual/installation for other platforms

# Authenticate
gh auth login

# Verify authentication
gh auth status
```

For detailed setup instructions, see `references/prerequisites-and-setup.md`.

## Changelog

- 2.0.0: Refactored as thin dispatcher to specialized skills, removed duplicated content
- 1.2.0: Added cross-platform `gh_multiuser.py` script with configuration-driven identity management
- 1.1.0: Added Multi-User Workflow reference for owner/developer identity separation

---

## Reference Documents Index

Content moved from SKILL.md during trim (2026-03-08).

**Setup and Auth:**

- `references/prerequisites-and-setup.md` -- GitHub CLI installation and authentication
- `references/multi-user-workflow.md` -- Managing multiple GitHub identities
- `references/single-account-workflow.md` -- Single account setup

**Operations:**

- `references/api-operations.md` -- REST/GraphQL API operations, rate limits, quality gates
- `references/batch-operations.md` -- Bulk filtering, label ops, batch updates
- `references/automation-scripts.md` -- Python scripts for sync, bulk labels, monitoring, reports
- `references/projects-v2-operations.md` -- Projects V2 specific operations
- `references/pull-request-management.md` -- PR management details
- `references/issue-management.md` -- Issue lifecycle management

**Guides and Troubleshooting:**

- `references/troubleshooting.md` -- Common issues and solutions
- `references/core-concepts.md` -- Core concepts overview
- `references/implementation-guide.md` -- Full implementation guide

**Templates:**

- `references/template-bug-report.md` -- Bug report template
- `references/template-pull-request.md` -- PR template
- `references/template-docs-issue.md` -- Documentation issue template

**Resources:**

- `references/account-strategy-decision-guide.md`
- `references/automation-scripts.md`
- `references/batch-operations.md`
- `references/core-concepts.md`
- ...and 35 more in `references/`
