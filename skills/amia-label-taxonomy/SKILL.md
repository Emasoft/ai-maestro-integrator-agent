---
name: amia-label-taxonomy
description: GitHub label taxonomy reference for the Integrator Agent. Use when managing PR reviews, updating PR status, or applying review labels. Trigger with review label requests.
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: amia-main
context: fork
user-invocable: false
license: Apache-2.0
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
- [op-request-changes](references/op-request-changes.md) — Procedure for requesting changes
- [op-approve-and-merge](references/op-approve-and-merge.md) — Procedure for approving and merging
- [op-mark-blocked-pr](references/op-mark-blocked-pr.md) — Procedure for marking a PR blocked

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
