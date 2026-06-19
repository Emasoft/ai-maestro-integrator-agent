---
name: amia-label-taxonomy
description: GitHub label taxonomy reference for the Integrator Agent. Use when managing PR reviews, updating PR status, or applying review labels. Trigger with review label requests. Loaded by ai-maestro-integrator-agent-main-agent.
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: ai-maestro-integrator-agent-main-agent
context: fork
user-invocable: false
license: MIT
---

# AMIA Label Taxonomy

## Overview

Label taxonomy for the Integrator Agent (AMIA) role. Defines the review and status labels AMIA manages on PRs and issues, plus labels it reads from other roles.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Active PR or issue number to label
- Understanding of AMIA role (see AGENT_OPERATIONS.md)
- Knowledge of current PR review state

## Instructions

1. Identify current PR state and existing labels
2. Check `priority:*` labels to determine review urgency
3. Check `type:*` labels to adjust review depth
4. Update `review:*` labels via `gh pr edit` as review progresses
5. After merge, set issue `status:done` and remove `assign:*` labels

### Checklist

Copy this checklist and track your progress:

- [ ] Identify current PR state and existing labels
- [ ] Check priority labels (critical/high/normal/low)
- [ ] Check type labels to determine review depth
- [ ] Set `review:in-progress` when starting
- [ ] Perform review according to type requirements
- [ ] Set `review:approved` or `review:changes-requested`
- [ ] After merge: set issue `status:done`
- [ ] After merge: remove assignment labels
- [ ] Verify label changes in GitHub PR timeline

## Output

| Output Type | Format | Example |
|-------------|--------|---------|
| Label update | CLI stdout | `gh pr edit $PR --remove-label X --add-label Y` |
| Current labels | JSON | `gh pr view $PR --json labels` |
| Label history | GitHub timeline | View in PR web interface |

> **Output discipline:** Use `gh pr edit` and `gh issue edit` for all label operations.

## Reference Documents

**Operations:**

- [op-start-pr-review](references/op-start-pr-review.md) — Procedure for starting a PR review
  - [Purpose](#purpose)
  - [When to Use](#when-to-use)
  - [Prerequisites](#prerequisites)
  - [Procedure](#procedure)
    - [Step 1: Verify PR Exists and Status](#step-1-verify-pr-exists-and-status)
    - [Step 2: Check Priority and Type](#step-2-check-priority-and-type)
    - [Step 3: Update Review Label](#step-3-update-review-label)
    - [Step 4: Comment on PR (Optional)](#step-4-comment-on-pr-optional)
    - [Step 5: Verify Label Update](#step-5-verify-label-update)
  - [Example](#example)
  - [Review Depth by Type](#review-depth-by-type)
  - [Error Handling](#error-handling)
  - [Notes](#notes)
- [op-request-changes](references/op-request-changes.md) — Procedure for requesting changes
  - [Purpose](#purpose)
  - [When to Use](#when-to-use)
  - [Prerequisites](#prerequisites)
  - [Procedure](#procedure)
    - [Step 1: Update Review Label](#step-1-update-review-label)
    - [Step 2: Submit Review with Changes Requested](#step-2-submit-review-with-changes-requested)
    - [Issues Found](#issues-found)
    - [Before Re-review](#before-re-review)
    - [Step 3: Notify Author (via AI Maestro if agent)](#step-3-notify-author-via-ai-maestro-if-agent)
    - [Step 4: Verify Label Update](#step-4-verify-label-update)
  - [Example](#example)
    - [Issues Found](#issues-found)
    - [Before Re-review](#before-re-review)
  - [Review Comment Templates](#review-comment-templates)
    - [Missing Tests](#missing-tests)
  - [Changes Requested: Missing Test Coverage](#changes-requested-missing-test-coverage)
    - [Code Quality Issues](#code-quality-issues)
  - [Changes Requested: Code Quality](#changes-requested-code-quality)
  - [Error Handling](#error-handling)
  - [Notes](#notes)
- [op-approve-and-merge](references/op-approve-and-merge.md) — Procedure for approving and merging
  - [Purpose](#purpose)
  - [When to Use](#when-to-use)
  - [Prerequisites](#prerequisites)
  - [Procedure](#procedure)
    - [Step 1: Verify All Checks Pass](#step-1-verify-all-checks-pass)
    - [Step 2: Update Review Label to Approved](#step-2-update-review-label-to-approved)
    - [Step 3: Submit Approval Review](#step-3-submit-approval-review)
    - [Step 4: Get Linked Issue Number](#step-4-get-linked-issue-number)
    - [Step 5: Merge PR (if authorized)](#step-5-merge-pr-if-authorized)
    - [Step 6: Update Linked Issue Status](#step-6-update-linked-issue-status)
    - [Step 7: Verify Merge](#step-7-verify-merge)
  - [Example](#example)
  - [Merge Strategies](#merge-strategies)
  - [Post-Merge Checklist](#post-merge-checklist)
  - [Error Handling](#error-handling)
  - [Notes](#notes)
- [op-mark-blocked-pr](references/op-mark-blocked-pr.md) — Procedure for marking a PR blocked
  - [Purpose](#purpose)
  - [When to Use](#when-to-use)
  - [Prerequisites](#prerequisites)
  - [Procedure](#procedure)
    - [Step 1: Identify Blocker Type](#step-1-identify-blocker-type)
    - [Step 2: Add Blocked Label](#step-2-add-blocked-label)
    - [Step 3: Comment with Blocker Details](#step-3-comment-with-blocker-details)
    - [Step 4: Notify Author (if agent)](#step-4-notify-author-if-agent)
    - [Step 5: Verify Label Update](#step-5-verify-label-update)
  - [Example](#example)
  - [Blocker Templates](#blocker-templates)
    - [Merge Conflicts](#merge-conflicts)
  - [Review Blocked: Merge Conflicts](#review-blocked-merge-conflicts)
    - [CI Failing](#ci-failing)
  - [Review Blocked: CI Failures](#review-blocked-ci-failures)
    - [Dependent PR](#dependent-pr)
  - [Review Blocked: Dependency](#review-blocked-dependency)
  - [Unblocking a PR](#unblocking-a-pr)
  - [Error Handling](#error-handling)
  - [Notes](#notes)

**Guides:**

See [detailed-guide](references/detailed-guide.md) for full reference:
  - Error Handling
  - Review Labels Detail
  - Kanban Columns
  - Status Labels AMIA Updates
  - Labels AMIA Reads
  - AMIA Label Commands
  - Extended Examples
  - Quick Reference Tables

## Error Handling

Exit 1: invalid params. Exit 2-4: GitHub API errors. See the detailed guide in Resources.

## Resources

Full reference: [detailed-guide](references/detailed-guide.md):
  - Error Handling
  - Review Labels Detail
  - Kanban Columns
  - Status Labels AMIA Updates
  - Labels AMIA Reads
    - Assignment Labels
    - Priority Labels
    - Type Labels
  - AMIA Label Commands
    - When Starting Review
    - When Review Complete (Approved)
    - When Changes Requested
    - When PR Merged
  - Extended Examples
  - Quick Reference Tables

## Examples

### Example 1: Full Review Cycle

```bash
# Start review
gh pr edit 45 --remove-label "review:needed" --add-label "review:in-progress"
# Approve after review
gh pr edit 45 --remove-label "review:in-progress" --add-label "review:approved"
gh pr review 45 --approve
# After merge: update parent issue
gh issue edit 78 --remove-label "status:ai-review" --add-label "status:done"
```
