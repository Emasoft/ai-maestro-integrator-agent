---
name: amia-github-integration
description: "Use when integrating GitHub Projects. Trigger with GitHub sync, label setup, or PR workflow requests. Loaded by ai-maestro-integrator-agent-main-agent."
license: Apache-2.0
compatibility: Requires GitHub CLI version 2.14 or higher, GitHub account with write permissions to target repositories, and basic Git knowledge. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub Integration Dispatcher

## Overview

Routes GitHub integration tasks to specialized skills (PRs, Projects V2, Kanban, worktrees, API, multi-user, batch).

## Prerequisites

- GitHub CLI 2.14+ authenticated (`gh auth status`)
- Write permissions on target repository
- Setup details: [prerequisites-and-setup](references/prerequisites-and-setup.md):
    - Table of Contents
    - Use-Case TOC
    - Initial Setup Requirements
      - Installing GitHub CLI
      - Verifying GitHub CLI Version
    - GitHub CLI Authentication
      - Step 1: Execute Authentication
      - Step 2: Choose Authentication Method
      - Step 3: Grant Permissions
      - Step 4: Initial Verification
    - Verify Authentication
    - Re-authentication
    - Troubleshooting Authentication
      - Problem: "Command not found: gh"
      - Problem: "Not logged into any GitHub hosts"
      - Problem: "HTTP 401: Bad credentials"
      - Problem: "Resource not accessible by integration"
    - Security Best Practices
    - Next Steps

## Instructions

1. Confirm auth: `gh auth status` (CLI 2.14+ required).
2. Route by task type:
   - **PRs** --> `amia-github-pr-workflow`
   - **Projects V2** --> `amia-github-projects-sync`
   - **Kanban** --> `amia-kanban-orchestration`
   - **Worktrees** --> `amia-git-worktree-operations`
   - **API ops** --> [api-operations](references/api-operations.md):
       - Table of Contents
       - 1.1 Executing GitHub Issue Operations
         - 1.1.1 Creating issues with labels, milestones, and assignees
         - 1.1.2 Updating issue metadata (title, body, labels)
         - 1.1.3 Managing issue lifecycle (close, reopen, transfer)
       - 1.2 Executing GitHub Pull Request Operations
         - 1.2.1 Creating PRs from branches
         - 1.2.2 Managing PR reviewers and assignees
         - 1.2.3 Submitting PR reviews (approve, request changes, comment)
         - 1.2.4 Merging PRs with different strategies
       - 1.3 Executing GitHub Projects V2 Operations
         - 1.3.1 Adding items to project boards
         - 1.3.2 Moving items between columns
         - 1.3.3 Updating custom field values via GraphQL
         - 1.3.4 Batch updating project items
       - 1.4 Managing Conversation Threads on Issues and PRs
         - 1.4.1 Posting comments and replies
         - 1.4.2 Marking threads as resolved
         - 1.4.3 Locking and unlocking conversations
       - 1.5 Handling GitHub API Rate Limits
         - 1.5.1 Checking rate limit status before operations
         - 1.5.2 Implementing exponential backoff on rate limit errors
         - 1.5.3 Queuing non-urgent operations during limit pressure
         - 1.5.4 Handling GraphQL-specific point-based rate limits
       - 1.6 Running Quality Gates Before API Operations
         - 1.6.1 Gate 1: Verifying authentication status
         - 1.6.2 Gate 2: Verifying repository and project permissions
         - 1.6.3 Gate 3: Verifying resource existence (issue, PR, label, milestone)
         - 1.6.4 Gate 4: Validating state before state-changing operations
         - 1.6.5 Gate 5: Pre-flight rate limit check
       - 1.7 Coordinating API Operations via AI Maestro
         - 1.7.1 Receiving API operation requests
         - 1.7.2 Sending operation results back to requesting agent
         - 1.7.3 Message format for API requests and responses
       - 1.8 Step-by-Step API Operation Workflow
         - 1.8.1 Receiving and parsing operation request
         - 1.8.2 Running all quality gates in sequence
         - 1.8.3 Preparing and executing API call with retry logic
         - 1.8.4 Processing and validating API response
         - 1.8.5 Logging operation to audit file
         - 1.8.6 Reporting result to orchestrator or callback agent
       - 1.9 Using GitHub CLI and GraphQL Tools
         - 1.9.1 Common gh CLI commands for issues and PRs
         - 1.9.2 Using gh api for raw REST API calls
         - 1.9.3 Executing GraphQL mutations for Projects V2
         - 1.9.4 Parsing JSON responses with jq
       - Summary
   - **Multi-user** --> [multi-user-workflow](references/multi-user-workflow.md):
       - Table of Contents
       - Use-Case TOC
         - Part 1: Setup and Configuration
         - Part 2: Operations and Troubleshooting
       - Overview
         - Why Multiple Identities?
         - Identity Components
       - Quick Start
         - 1. Generate SSH Key for Secondary Account
         - 2. Add Key to GitHub
         - 3. Configure SSH Host Alias
         - 4. Authenticate Secondary Account with gh CLI
         - 5. Configure Repository for Secondary Identity
       - Key Files and Locations
       - Common Commands Quick Reference
       - See Also
3. Batch ops: preview first (`gh issue list --label X --state open`), then execute.
4. Verify result: `gh issue view <N>` or `gh pr status`.
5. On errors: see the detailed guide in Resources.

### Checklist

Copy this checklist and track your progress:

- [ ] GitHub CLI 2.14+ installed
- [ ] `gh auth status` confirms authentication
- [ ] Task type identified (PR / Projects V2 / Kanban / Worktree / API / Multi-User / Batch)
- [ ] Routed to correct specialized skill or reference
- [ ] Batch ops: dry-run preview completed before execution
- [ ] Operation executed and result verified

## Output

| Operation | Output |
|-----------|--------|
| Routing | Name of specialized skill to invoke |
| Batch ops | Summary of affected items and changes applied |
| Automation scripts | JSON/Markdown reports via `--output-file` |
| Verification | `gh` CLI confirmation of current state |

> **Output discipline:** All scripts support `--output-file <path>`. Use it in automated workflows to minimize token consumption.

## Error Handling

Non-zero exit codes on failure; check stderr and the detailed guide in Resources.

## Examples

### Example: Bulk add label to open bug issues

```bash
# Preview affected issues
gh issue list --label "bug" --state open --json number,title \
  --jq '.[] | "\(.number): \(.title)"'

# Apply label
gh issue list --label "bug" --state open --json number \
  --jq '.[].number' | xargs -I {} gh issue edit {} --add-label "priority:critical"

# Verify
gh issue view 15 --json labels --jq '.labels[].name'
```

---

**Skill Version:** 2.0.0 | **Last Updated:** 2026-02-05

## Resources

Full reference: [detailed-guide](references/detailed-guide.md):
  - Decision Tree: Which Skill to Use?
    - Pull Requests
    - Projects V2 Sync
    - Kanban Board Operations
    - Git Worktrees
    - GitHub API Operations
    - Multiple GitHub Identities
  - Batch Operations
    - Batch Label Operations
    - Automation Scripts
  - Error Handling
  - Extended Examples
    - Route to PR skill
    - Bulk add label to bug issues
    - Projects V2 sync
  - First-Time Setup
  - Changelog
  - Reference Documents Index
