# PR Metadata Reference

This document explains how to retrieve and interpret GitHub Pull Request metadata using the integrator-agent scripts.

## Table of Contents

- 1. PR Metadata JSON Structure
  - 1.1 Core identification fields (number, title, state)
  - 1.2 Author and assignee information
  - 1.3 Branch and merge information
  - 1.4 Labels, milestones, and projects
  - 1.5 Review and approval status
- 1. Extracting Specific Fields
  - 2.1 Getting PR title and description
  - 2.2 Finding the source and target branches
  - 2.3 Checking mergeable status and conflicts
  - 2.4 Listing reviewers and their decisions
- 1. Common Metadata Queries
  - 3.1 Is this PR ready to merge?
  - 3.2 Who needs to approve this PR?
  - 3.3 What labels are applied?

---

## 1. PR Metadata JSON Structure

When you run `amia_get_pr_context.py`, the script returns a JSON object containing comprehensive PR metadata. This section explains each field.

### 1.1 Core Identification Fields

These fields uniquely identify the PR and its current state.

```json
{
  "number": 123,
  "title": "Add user authentication feature",
  "state": "OPEN",
  "url": "https://github.com/owner/repo/pull/123",
  "isDraft": false,
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-16T14:22:00Z"
}
```

**Field Definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `number` | integer | The PR number (used in URLs and references) |
| `title` | string | The PR title as displayed in GitHub |
| `state` | string | Current state: `OPEN`, `CLOSED`, or `MERGED` |
| `url` | string | Full URL to the PR on GitHub |
| `isDraft` | boolean | True if PR is marked as draft (not ready for review) |
| `createdAt` | string | ISO 8601 timestamp when PR was created |
| `updatedAt` | string | ISO 8601 timestamp of last activity |

**State Values Explained:**

- `OPEN`: PR is open and can be reviewed, commented on, or merged
- `CLOSED`: PR was closed without merging (abandoned or rejected)
- `MERGED`: PR was successfully merged into the target branch

### 1.2 Author and Assignee Information

Information about who created the PR and who is responsible for it.

```json
{
  "author": {
    "login": "developer-username",
    "name": "Developer Name",
    "email": "developer@example.com"
  },
  "assignees": [
    {
      "login": "reviewer1",
      "name": "First Reviewer"
    },
    {
      "login": "reviewer2",
      "name": "Second Reviewer"
    }
  ]
}
```

**Field Definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `author.login` | string | GitHub username of PR creator |
| `author.name` | string | Display name (may be null if not set) |
| `author.email` | string | Public email (may be null if private) |
| `assignees` | array | List of users assigned to the PR |

**Usage Example - Extract Author:**

```bash
# Using jq to extract author login
python3 amia_get_pr_context.py --pr 123 | jq -r '.author.login'
```

### 1.3 Branch and Merge Information

Details about source and target branches and merge status.

```json
{
  "headRefName": "feature/user-auth",
  "baseRefName": "main",
  "headRepository": {
    "owner": "contributor",
    "name": "repo-fork"
  },
  "baseRepository": {
    "owner": "original-owner",
    "name": "repo"
  },
  "mergeable": "MERGEABLE",
  "mergeStateStatus": "CLEAN",
  "potentialMergeCommit": {
    "oid": "abc123def456..."
  }
}
```

**Field Definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `headRefName` | string | Source branch name (the branch with changes) |
| `baseRefName` | string | Target branch name (where changes will be merged) |
| `headRepository` | object | Repository containing the source branch |
| `baseRepository` | object | Repository containing the target branch |
| `mergeable` | string | Merge status: `MERGEABLE`, `CONFLICTING`, or `UNKNOWN` |
| `mergeStateStatus` | string | Detailed merge state (see below) |

**Mergeable Status Values:**

- `MERGEABLE`: No conflicts, PR can be merged
- `CONFLICTING`: Merge conflicts exist, must be resolved
- `UNKNOWN`: GitHub is still calculating merge status

**Merge State Status Values:**

- `CLEAN`: All checks passed, no conflicts, ready to merge
- `UNSTABLE`: Some checks failed but no conflicts
- `DIRTY`: Merge conflicts present
- `BLOCKED`: Protected branch rules prevent merge
- `BEHIND`: Target branch has new commits, needs rebase/update
- `HAS_HOOKS`: Waiting for merge queue or hooks

### 1.4 Labels, Milestones, and Projects

Organizational metadata for tracking and categorization.

```json
{
  "labels": [
    {"name": "enhancement", "color": "a2eeef"},
    {"name": "ai-review", "color": "fbca04"}
  ],
  "milestone": {
    "title": "v2.0 Release",
    "dueOn": "2024-02-01T00:00:00Z",
    "state": "OPEN"
  },
  "projectCards": [
    {
      "project": {"name": "Q1 Roadmap"},
      "column": {"name": "AI Review"}
    }
  ]
}
```

**Field Definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `labels` | array | List of labels applied to PR |
| `labels[].name` | string | Label text |
| `labels[].color` | string | Hex color code (without #) |
| `milestone` | object | Associated milestone (null if none) |
| `milestone.title` | string | Milestone name |
| `milestone.dueOn` | string | Due date (null if not set) |
| `projectCards` | array | Project board associations |

### 1.5 Review and Approval Status

Information about code review status and decisions.

```json
{
  "reviewDecision": "APPROVED",
  "reviews": [
    {
      "author": {"login": "senior-dev"},
      "state": "APPROVED",
      "submittedAt": "2024-01-16T09:00:00Z",
      "body": "LGTM! Nice work on the tests."
    },
    {
      "author": {"login": "security-team"},
      "state": "CHANGES_REQUESTED",
      "submittedAt": "2024-01-15T16:30:00Z",
      "body": "Please add input validation."
    }
  ],
  "reviewRequests": [
    {"login": "tech-lead"}
  ]
}
```

**Field Definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `reviewDecision` | string | Overall review status (see below) |
| `reviews` | array | List of submitted reviews |
| `reviews[].state` | string | Review state: `APPROVED`, `CHANGES_REQUESTED`, `COMMENTED`, `DISMISSED`, `PENDING` |
| `reviewRequests` | array | Users who have been requested to review but haven't yet |

**Review Decision Values:**

- `APPROVED`: Required approvals met
- `CHANGES_REQUESTED`: At least one reviewer requested changes
- `REVIEW_REQUIRED`: Waiting for required reviews
- `null`: No review requirements configured

---

## 2. Extracting Specific Fields

This section shows how to extract commonly needed information from PR metadata.

### 2.1 Getting PR Title and Description

The PR description is stored in the `body` field, which contains markdown text.

```bash
# Get just the title
python3 amia_get_pr_context.py --pr 123 | jq -r '.title'

# Get the description/body
python3 amia_get_pr_context.py --pr 123 | jq -r '.body'

# Get both formatted
python3 amia_get_pr_context.py --pr 123 | jq -r '"Title: \(.title)\n\nDescription:\n\(.body)"'
```

**Example Output:**

```
Title: Add user authentication feature

Description:
## Summary
This PR adds JWT-based authentication to the API.

## Changes
- Added auth middleware
- Created login/logout endpoints
- Added user session management

## Testing
- Added unit tests for auth module
- Manual testing with Postman collection
```

### 2.2 Finding the Source and Target Branches

Understanding which branches are involved is essential for context.

```bash
# Get source branch (where changes are)
python3 amia_get_pr_context.py --pr 123 | jq -r '.headRefName'
# Output: feature/user-auth

# Get target branch (where changes will go)
python3 amia_get_pr_context.py --pr 123 | jq -r '.baseRefName'
# Output: main

# Get both in context
python3 amia_get_pr_context.py --pr 123 | jq -r '"\(.headRefName) → \(.baseRefName)"'
# Output: feature/user-auth → main
```

**For Cross-Repository PRs (Forks):**

```bash
# Check if PR is from a fork
python3 amia_get_pr_context.py --pr 123 | jq -r '
  if .headRepository.owner != .baseRepository.owner
  then "Fork PR: \(.headRepository.owner)/\(.headRepository.name):\(.headRefName) → \(.baseRepository.owner)/\(.baseRepository.name):\(.baseRefName)"
  else "Same-repo PR: \(.headRefName) → \(.baseRefName)"
  end'
```

### 2.3 Checking Mergeable Status and Conflicts

Before attempting to merge, always check the merge status.

```bash
# Quick merge status check
python3 amia_get_pr_context.py --pr 123 | jq -r '.mergeable'

# Detailed merge state
python3 amia_get_pr_context.py --pr 123 | jq -r '.mergeStateStatus'

# Full merge readiness report
python3 amia_get_pr_context.py --pr 123 | jq -r '
  "Mergeable: \(.mergeable)
   State: \(.mergeStateStatus)
   Draft: \(.isDraft)
   Review: \(.reviewDecision // "none")"'
```

**Interpreting Results:**

| mergeable | mergeStateStatus | Meaning |
|-----------|------------------|---------|
| MERGEABLE | CLEAN | Ready to merge, all good |
| MERGEABLE | UNSTABLE | Can merge but some checks failed |
| MERGEABLE | BEHIND | Need to update branch first |
| MERGEABLE | BLOCKED | Branch protection rules prevent merge |
| CONFLICTING | DIRTY | Must resolve conflicts |
| UNKNOWN | * | Wait and retry, GitHub is computing |

### 2.4 Listing Reviewers and Their Decisions

Get a clear picture of review status.

```bash
# List all reviewers and their states
python3 amia_get_pr_context.py --pr 123 | jq -r '
  .reviews[] | "\(.author.login): \(.state)"'

# Example output:
# senior-dev: APPROVED
# security-team: CHANGES_REQUESTED

# List pending review requests
python3 amia_get_pr_context.py --pr 123 | jq -r '
  .reviewRequests[].login'

# Get summary
python3 amia_get_pr_context.py --pr 123 | jq -r '
  "Approvals: \([.reviews[] | select(.state == "APPROVED")] | length)
   Changes Requested: \([.reviews[] | select(.state == "CHANGES_REQUESTED")] | length)
   Pending Requests: \(.reviewRequests | length)"'
```

---

## 3. Common Metadata Queries

### 3.1 Is This PR Ready to Merge?

A PR is ready to merge when all these conditions are met:

```bash
python3 amia_get_pr_context.py --pr 123 | jq -r '
  {
    not_draft: (.isDraft == false),
    no_conflicts: (.mergeable == "MERGEABLE"),
    approved: (.reviewDecision == "APPROVED" or .reviewDecision == null),
    state_clean: (.mergeStateStatus == "CLEAN")
  } |
  if .not_draft and .no_conflicts and .approved and .state_clean
  then "READY TO MERGE"
  else "NOT READY: \([to_entries[] | select(.value == false) | .key] | join(", "))"
  end'
```

### 3.2 Who Needs to Approve This PR?

```bash
# Get pending reviewers
python3 amia_get_pr_context.py --pr 123 | jq -r '
  "Waiting for review from: \(.reviewRequests | map(.login) | join(", "))"'

# Get reviewers who requested changes (need re-review)
python3 amia_get_pr_context.py --pr 123 | jq -r '
  "Need to address changes from: \([.reviews[] | select(.state == "CHANGES_REQUESTED") | .author.login] | join(", "))"'
```

### 3.3 What Labels Are Applied?

```bash
# List all labels
python3 amia_get_pr_context.py --pr 123 | jq -r '.labels[].name'

# Check for specific label
python3 amia_get_pr_context.py --pr 123 | jq -r '
  if any(.labels[]; .name == "ai-review")
  then "Has ai-review label"
  else "Does not have ai-review label"
  end'

# Get labels as comma-separated list
python3 amia_get_pr_context.py --pr 123 | jq -r '.labels | map(.name) | join(", ")'
```
