---
name: amia-github-integration
description: "Use when integrating GitHub Projects. Trigger with GitHub sync, label setup, or PR workflow requests. Loaded by ai-maestro-integrator-agent-main-agent."
license: MIT
compatibility: Requires GitHub CLI version 2.14 or higher, GitHub account with write permissions to target repositories, and basic Git knowledge. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: amia-api-coordinator
context: fork
user-invocable: false
---

# GitHub Integration Dispatcher

## Overview

Routes GitHub integration tasks to specialized skills (PRs, Projects V2, Kanban, worktrees, API, multi-user, batch).

## Prerequisites

- GitHub CLI 2.14+ authenticated (`gh auth status`)
- Write permissions on target repository
- Setup details: [prerequisites-and-setup](references/prerequisites-and-setup.md)

## Instructions

1. Confirm auth: `gh auth status` (CLI 2.14+ required).
2. Route by task type:
   - **PRs** --> `amia-github-pr-workflow`
   - **Projects V2** --> `amia-github-projects-sync`
   - **Kanban** --> `amia-kanban-orchestration`
   - **Worktrees** --> `amia-git-worktree-operations`
   - **API ops** --> [api-operations](references/api-operations.md)
   - **Multi-user** --> [multi-user-workflow](references/multi-user-workflow.md)
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

- [prerequisites-and-setup](references/prerequisites-and-setup.md) — GitHub CLI install, auth, and troubleshooting
  - [Initial Setup Requirements](#initial-setup-requirements)
    - [Installing GitHub CLI](#installing-github-cli)
    - [Verifying GitHub CLI Version](#verifying-github-cli-version)
  - [GitHub CLI Authentication](#github-cli-authentication)
    - [Step 1: Execute Authentication](#step-1-execute-authentication)
    - [Step 2: Choose Authentication Method](#step-2-choose-authentication-method)
    - [Step 3: Grant Permissions](#step-3-grant-permissions)
    - [Step 4: Initial Verification](#step-4-initial-verification)
  - [Verify Authentication](#verify-authentication)
  - [Re-authentication](#re-authentication)
  - [Troubleshooting Authentication](#troubleshooting-authentication)
    - [Problem: "Command not found: gh"](#problem-command-not-found-gh)
    - [Problem: "Not logged into any GitHub hosts"](#problem-not-logged-into-any-github-hosts)
    - [Problem: "HTTP 401: Bad credentials"](#problem-http-401-bad-credentials)
    - [Problem: "Resource not accessible by integration"](#problem-resource-not-accessible-by-integration)
  - [Security Best Practices](#security-best-practices)
  - [Next Steps](#next-steps)

- [api-operations](references/api-operations.md) — Detailed API operations (issue/PR/project CRUD)
  - 1.1 [Executing GitHub Issue Operations](#11-executing-github-issue-operations)
    - 1.1.1 Creating issues with labels, milestones, and assignees
    - 1.1.2 Updating issue metadata (title, body, labels)
    - 1.1.3 Managing issue lifecycle (close, reopen, transfer)
  - 1.2 [Executing GitHub Pull Request Operations](#12-executing-github-pull-request-operations)
    - 1.2.1 Creating PRs from branches
    - 1.2.2 Managing PR reviewers and assignees
    - 1.2.3 Submitting PR reviews (approve, request changes, comment)
    - 1.2.4 Merging PRs with different strategies
  - 1.3 [Executing GitHub Projects V2 Operations](#13-executing-github-projects-v2-operations)
    - 1.3.1 Adding items to project boards
    - 1.3.2 Moving items between columns
    - 1.3.3 Updating custom field values via GraphQL
    - 1.3.4 Batch updating project items
  - 1.4 [Managing Conversation Threads on Issues and PRs](#14-managing-conversation-threads-on-issues-and-prs)
    - 1.4.1 Posting comments and replies
    - 1.4.2 Marking threads as resolved
    - 1.4.3 Locking and unlocking conversations
  - 1.5 [Handling GitHub API Rate Limits](#15-handling-github-api-rate-limits)
    - 1.5.1 Checking rate limit status before operations
    - 1.5.2 Implementing exponential backoff on rate limit errors
    - 1.5.3 Queuing non-urgent operations during limit pressure
    - 1.5.4 Handling GraphQL-specific point-based rate limits
  - 1.6 [Running Quality Gates Before API Operations](#16-running-quality-gates-before-api-operations)
    - 1.6.1 Gate 1: Verifying authentication status
    - 1.6.2 Gate 2: Verifying repository and project permissions
    - 1.6.3 Gate 3: Verifying resource existence (issue, PR, label, milestone)
    - 1.6.4 Gate 4: Validating state before state-changing operations
    - 1.6.5 Gate 5: Pre-flight rate limit check
  - 1.7 [Coordinating API Operations via AI Maestro](#17-coordinating-api-operations-via-ai-maestro)
    - 1.7.1 Receiving API operation requests
    - 1.7.2 Sending operation results back to requesting agent
    - 1.7.3 Message format for API requests and responses
  - 1.8 [Step-by-Step API Operation Workflow](#18-step-by-step-api-operation-workflow)
    - 1.8.1 Receiving and parsing operation request
    - 1.8.2 Running all quality gates in sequence
    - 1.8.3 Preparing and executing API call with retry logic
    - 1.8.4 Processing and validating API response
    - 1.8.5 Logging operation to audit file
    - 1.8.6 Reporting result to orchestrator or callback agent
  - 1.9 [Using GitHub CLI and GraphQL Tools](#19-using-github-cli-and-graphql-tools)
    - 1.9.1 Common gh CLI commands for issues and PRs
    - 1.9.2 Using gh api for raw REST API calls
    - 1.9.3 Executing GraphQL mutations for Projects V2
    - 1.9.4 Parsing JSON responses with jq

- [multi-user-workflow](references/multi-user-workflow.md) — Managing multiple GitHub identities on one machine
  - [Use-Case TOC](#use-case-toc)
    - [Part 1: Setup and Configuration](#part-1-setup-and-configuration)
    - [Part 2: Operations and Troubleshooting](#part-2-operations-and-troubleshooting)
  - [Overview](#overview)
    - [Why Multiple Identities?](#why-multiple-identities)
    - [Identity Components](#identity-components)
  - [Quick Start](#quick-start)
    - [1. Generate SSH Key for Secondary Account](#1-generate-ssh-key-for-secondary-account)
    - [2. Add Key to GitHub](#2-add-key-to-github)
    - [3. Configure SSH Host Alias](#3-configure-ssh-host-alias)
    - [4. Authenticate Secondary Account with gh CLI](#4-authenticate-secondary-account-with-gh-cli)
    - [5. Configure Repository for Secondary Identity](#5-configure-repository-for-secondary-identity)
  - [Key Files and Locations](#key-files-and-locations)
  - [Common Commands Quick Reference](#common-commands-quick-reference)
  - [See Also](#see-also)

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
