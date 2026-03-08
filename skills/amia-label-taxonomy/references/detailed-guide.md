# AMIA Label Taxonomy — Detailed Guide

## Contents

- [Error Handling](#error-handling)
- [Review Labels Detail](#review-labels-detail)
- [Kanban Columns](#kanban-columns)
- [Status Labels AMIA Updates](#status-labels-amia-updates)
- [Labels AMIA Reads](#labels-amia-reads)
- [AMIA Label Commands](#amia-label-commands)
- [Extended Examples](#extended-examples)
- [Quick Reference Tables](#quick-reference-tables)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `label not found` | Label doesn't exist in repo | Create label first via `gh label create` |
| `permission denied` | No write access to PR | Verify GitHub token scopes |
| `PR not found` | Invalid PR number | Verify PR number with `gh pr list` |
| `conflict` | Multiple agents editing labels | Retry after short delay |

## Review Labels Detail

AMIA is the PRIMARY manager of review labels (`review:*`) on PRs.

| Label | Description | When AMIA Sets It |
|-------|-------------|------------------|
| `review:needed` | PR needs review | Assigned by AMOA or PR creator |
| `review:in-progress` | AMIA reviewing | When starting review |
| `review:changes-requested` | Issues found | After review with issues |
| `review:approved` | Review passed | After successful review |
| `review:blocked` | Cannot review | When conflicts or missing info |

**AMIA Review Workflow:**

```
PR created → review:needed → review:in-progress → review:approved OR review:changes-requested
                                                          ↓
                                             changes made → review:in-progress (repeat)
```

## Kanban Columns

The full workflow uses these 8 status columns:

| # | Column Code | Display Name | Label | Description |
|---|-------------|-------------|-------|-------------|
| 1 | `backlog` | Backlog | `status:backlog` | Entry point for new tasks |
| 2 | `todo` | Todo | `status:todo` | Ready to start |
| 3 | `in-progress` | In Progress | `status:in-progress` | Active work |
| 4 | `ai-review` | AI Review | `status:ai-review` | Integrator agent reviews ALL tasks |
| 5 | `human-review` | Human Review | `status:human-review` | User reviews BIG tasks only (via AMAMA) |
| 6 | `merge-release` | Merge/Release | `status:merge-release` | Ready to merge |
| 7 | `done` | Done | `status:done` | Completed |
| 8 | `blocked` | Blocked | `status:blocked` | Blocked at any stage |

**Task Routing Rules:**

- **Small tasks**: In Progress -> AI Review -> Merge/Release -> Done
- **Big tasks**: In Progress -> AI Review -> Human Review -> Merge/Release -> Done
- **Human Review** is requested via AMAMA (Assistant Manager asks user to test/review)
- Not all tasks go through Human Review -- only significant changes requiring human judgment

## Status Labels AMIA Updates

| Label | When AMIA Sets It |
|-------|------------------|
| `status:ai-review` | When task/PR is ready for AI review |
| `status:human-review` | When significant task needs user review (escalates via AMAMA) |
| `status:merge-release` | When AI review passes and task is ready to merge |
| `status:blocked` | When PR has conflicts or CI failures |
| `status:done` | After PR merged and verified |

## Labels AMIA Reads

### Assignment Labels (`assign:*`)

AMIA checks assignment to know who created the PR:

- `assign:implementer-1`, `assign:implementer-2` - Implementation agents
- `assign:orchestrator` - AMOA-created PRs

### Priority Labels (`priority:*`)

AMIA uses priority to order review queue:

- `priority:critical` - Review immediately
- `priority:high` - Review soon
- `priority:normal` - Standard queue
- `priority:low` - Review when available

### Type Labels (`type:*`)

AMIA adjusts review depth based on type:

- `type:security` - Deep security review
- `type:refactor` - Focus on behavior preservation
- `type:docs` - Light review
- `type:feature` - Full functionality review

## AMIA Label Commands

### When Starting Review

```bash
gh pr edit $PR_NUMBER --remove-label "review:needed" --add-label "review:in-progress"
```

### When Review Complete (Approved)

```bash
gh pr edit $PR_NUMBER --remove-label "review:in-progress" --add-label "review:approved"
```

### When Changes Requested

```bash
gh pr edit $PR_NUMBER --remove-label "review:in-progress" --add-label "review:changes-requested"
```

### When PR Merged

```bash
gh issue edit $ISSUE_NUMBER --remove-label "status:ai-review" --add-label "status:done"
gh issue edit $ISSUE_NUMBER --remove-label "assign:$AGENT_NAME"
```

## Extended Examples

### Example 1: Starting a PR Review

```bash
# Scenario: PR #45 is labeled review:needed, priority:high
gh pr edit 45 --remove-label "review:needed" --add-label "review:in-progress"
```

### Example 2: Requesting Changes

```bash
# Scenario: Review found issues in PR #45
gh pr edit 45 --remove-label "review:in-progress" --add-label "review:changes-requested"
gh pr review 45 --request-changes --body "Please address the following issues: ..."
```

### Example 3: Approving and Merging

```bash
# Scenario: PR #45 passes all checks
gh pr edit 45 --remove-label "review:in-progress" --add-label "review:approved"
gh pr review 45 --approve
# After merge: Update parent issue
gh issue edit 78 --remove-label "status:ai-review" --add-label "status:done"
```

### Example 4: Blocked PR

```bash
# Scenario: PR #45 has merge conflicts
gh pr edit 45 --add-label "review:blocked"
gh pr comment 45 --body "Cannot review: merge conflicts detected. Please resolve conflicts."
```

## Quick Reference Tables

### AMIA Label Responsibilities

| Action | Labels Involved |
|--------|-----------------|
| Start review | Remove `review:needed`, add `review:in-progress` |
| Approve PR | Remove `review:in-progress`, add `review:approved` |
| Request changes | Remove `review:in-progress`, add `review:changes-requested` |
| After merge | Issue: remove `status:*`, add `status:done` |
| Mark blocked | Add `status:blocked` or `review:blocked` |

### Labels AMIA Never Sets

- `assign:*` - Set by AMOA only
- `type:*` - Set at issue creation
- `effort:*` - Set during triage
- `component:*` - Set at issue creation
