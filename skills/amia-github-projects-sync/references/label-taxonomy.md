# Label Taxonomy

## Table of Contents

1. [When starting with the label system](#overview)
2. [When you need to know available label categories](#label-categories)
3. [When creating or managing labels via CLI](#label-management)
4. [When applying labels automatically or manually](#label-application-rules)
5. [When searching or filtering issues by labels](#label-based-queries)
6. [When generating label statistics and counts](#label-statistics)
7. [When following label usage best practices](#best-practices)
8. [When choosing label colors](#label-colors-reference)

## Overview

This document defines the complete label system for GitHub issues and pull requests. Labels are organized into categories for consistent filtering and reporting.

## Label Categories

### Type Labels

Identify what kind of work the issue represents.

| Label | Color | Description |
|-------|-------|-------------|
| `type:feature` | `#1D76DB` (blue) | New functionality |
| `type:bug` | `#D73A4A` (red) | Something isn't working |
| `type:refactor` | `#FBCA04` (yellow) | Code improvement without behavior change |
| `type:docs` | `#0075CA` (dark blue) | Documentation only |
| `type:test` | `#7057FF` (purple) | Testing improvements |
| `type:chore` | `#CFD3D7` (gray) | Maintenance tasks |
| `type:security` | `#D93F0B` (orange-red) | Security related |
| `type:performance` | `#5319E7` (violet) | Performance improvement |
| `type:epic` | `#0E8A16` (green) | Large multi-issue feature |

### Priority Labels

Indicate urgency and importance.

| Label | Color | Description | SLA |
|-------|-------|-------------|-----|
| `priority:critical` | `#B60205` (dark red) | Must fix immediately | < 4 hours |
| `priority:high` | `#D93F0B` (orange) | Should complete this sprint | < 3 days |
| `priority:normal` | `#FBCA04` (yellow) | Standard priority | Current sprint |
| `priority:low` | `#0E8A16` (green) | Nice to have | Backlog |

### Status Labels

Track current state (supplements project board status).

| Label | Color | Description |
|-------|-------|-------------|
| `status:backlog` | `#D4C5F9` (light purple) | Not yet scheduled, needs prioritization |
| `status:ready` | `#0E8A16` (green) | Ready to be worked on |
| `status:in-progress` | `#FBCA04` (yellow) | Currently being worked on |
| `status:blocked` | `#D73A4A` (red) | Cannot proceed |
| `status:ai-review` | `#1D76DB` (blue) | Integrator reviews ALL tasks |
| `status:human-review` | `#D876E3` (pink) | User reviews BIG tasks only |
| `status:merge-release` | `#C2E0C6` (light green) | Ready to merge |

### Component Labels

Identify affected areas of the codebase.

| Label | Color | Description |
|-------|-------|-------------|
| `component:api` | `#C2E0C6` (light green) | API endpoints |
| `component:ui` | `#BFD4F2` (light blue) | User interface |
| `component:database` | `#FEF2C0` (light yellow) | Database/storage |
| `component:auth` | `#E99695` (light red) | Authentication |
| `component:infra` | `#D4C5F9` (light purple) | Infrastructure/DevOps |
| `component:core` | `#C5DEF5` (sky blue) | Core functionality |
| `component:tests` | `#BFDADC` (teal) | Test infrastructure |

### Effort Labels

Estimate relative size of work.

| Label | Color | Description | Typical Duration |
|-------|-------|-------------|------------------|
| `effort:xs` | `#0E8A16` (green) | Trivial change | < 1 hour |
| `effort:s` | `#C2E0C6` (light green) | Small task | 1-4 hours |
| `effort:m` | `#FBCA04` (yellow) | Medium task | 4-8 hours |
| `effort:l` | `#D93F0B` (orange) | Large task | 1-3 days |
| `effort:xl` | `#B60205` (dark red) | Epic sized | > 3 days |

### Assignment Labels

Track which agent is working on the issue.

| Label | Color | Description |
|-------|-------|-------------|
| `assign:dev-1` | `#1D76DB` (blue) | Assigned to dev-agent-1 |
| `assign:dev-2` | `#5319E7` (violet) | Assigned to dev-agent-2 |
| `assign:human` | `#0E8A16` (green) | Assigned to human developer |
| `assign:orchestrator` | `#D876E3` (pink) | Orchestrator handling |

### Review Labels

Track review status on PRs.

| Label | Color | Description |
|-------|-------|-------------|
| `review:needed` | `#FBCA04` (yellow) | Needs code review |
| `review:approved` | `#0E8A16` (green) | Review approved |
| `review:changes-requested` | `#D73A4A` (red) | Changes required |
| `review:security-review` | `#D93F0B` (orange) | Needs security review |

### Lifecycle Labels

Track issue lifecycle events.

| Label | Color | Description |
|-------|-------|-------------|
| `lifecycle:duplicate` | `#CFD3D7` (gray) | Duplicate of another issue |
| `lifecycle:wontfix` | `#FFFFFF` (white) | Will not be fixed (documented reason required) |
| `lifecycle:invalid` | `#E4E669` (light olive) | Not valid issue |
| `lifecycle:cannot-reproduce` | `#CFD3D7` (gray) | Bug closed after 3 documented reproduction attempts |
| `lifecycle:completed` | `#0E8A16` (green) | Issue resolved and verified |

**NOTE**: There is NO `lifecycle:stale` label. Issues are NEVER closed due to inactivity.
See Issue Lifecycle Policy in `status-management.md`.

### Attention Labels

Track issues needing attention (instead of closing them).

| Label | Color | Description |
|-------|-------|-------------|
| `needs-attention` | `#D876E3` (pink) | Inactive but still valid, needs follow-up |
| `awaiting-response` | `#FEF2C0` (light yellow) | Waiting for reporter/user input |
| `help-wanted` | `#0E8A16` (green) | Open for community contribution |
| `good-first-issue` | `#7057FF` (purple) | Good for newcomers |

**Usage**: Apply these labels to inactive issues INSTEAD of closing them.
Issues stay open until genuinely resolved.

### Iteration Tracking Labels

Track PR review iterations. Applied automatically during review cycles.

| Label | Color | Description |
|-------|-------|-------------|
| `iteration:1` | `#0E8A16` (green) | First review iteration |
| `iteration:2` | `#FBCA04` (yellow) | Second review iteration |
| `iteration:3+` | `#D93F0B` (orange) | Third or more review iterations |
| `needs-major-rework` | `#D73A4A` (red) | Significant changes required before re-review |

## Label Management

### Creating Labels via CLI

```bash
# Create a label
gh label create "type:feature" \
  --color "1D76DB" \
  --description "New functionality"

# Create all type labels
for label in "feature:1D76DB" "bug:D73A4A" "refactor:FBCA04" "docs:0075CA" "test:7057FF"; do
  name="type:${label%%:*}"
  color="${label##*:}"
  gh label create "$name" --color "$color" --force
done
```

### Bulk Label Creation Script

```bash
#!/bin/bash
# create-all-labels.sh

REPO="owner/repo"

# Type labels
gh label create "type:feature" --color "1D76DB" --description "New functionality" --repo "$REPO" --force
gh label create "type:bug" --color "D73A4A" --description "Something isn't working" --repo "$REPO" --force
gh label create "type:refactor" --color "FBCA04" --description "Code improvement" --repo "$REPO" --force
gh label create "type:docs" --color "0075CA" --description "Documentation only" --repo "$REPO" --force
gh label create "type:test" --color "7057FF" --description "Testing improvements" --repo "$REPO" --force
gh label create "type:chore" --color "CFD3D7" --description "Maintenance tasks" --repo "$REPO" --force
gh label create "type:security" --color "D93F0B" --description "Security related" --repo "$REPO" --force
gh label create "type:epic" --color "0E8A16" --description "Large multi-issue feature" --repo "$REPO" --force

# Priority labels
gh label create "priority:critical" --color "B60205" --description "Must fix immediately" --repo "$REPO" --force
gh label create "priority:high" --color "D93F0B" --description "Should complete this sprint" --repo "$REPO" --force
gh label create "priority:normal" --color "FBCA04" --description "Standard priority" --repo "$REPO" --force
gh label create "priority:low" --color "0E8A16" --description "Nice to have" --repo "$REPO" --force

# Status labels
gh label create "status:backlog" --color "D4C5F9" --description "Not yet scheduled, needs prioritization" --repo "$REPO" --force
gh label create "status:ready" --color "0E8A16" --description "Ready to be worked on" --repo "$REPO" --force
gh label create "status:in-progress" --color "FBCA04" --description "Currently being worked on" --repo "$REPO" --force
gh label create "status:blocked" --color "D73A4A" --description "Cannot proceed" --repo "$REPO" --force
gh label create "status:ai-review" --color "1D76DB" --description "Integrator reviews ALL tasks" --repo "$REPO" --force
gh label create "status:human-review" --color "D876E3" --description "User reviews BIG tasks only" --repo "$REPO" --force
gh label create "status:merge-release" --color "C2E0C6" --description "Ready to merge" --repo "$REPO" --force

# Effort labels
gh label create "effort:xs" --color "0E8A16" --description "< 1 hour" --repo "$REPO" --force
gh label create "effort:s" --color "C2E0C6" --description "1-4 hours" --repo "$REPO" --force
gh label create "effort:m" --color "FBCA04" --description "4-8 hours" --repo "$REPO" --force
gh label create "effort:l" --color "D93F0B" --description "1-3 days" --repo "$REPO" --force
gh label create "effort:xl" --color "B60205" --description "> 3 days" --repo "$REPO" --force

echo "All labels created successfully!"
```

### Listing Labels

```bash
# List all labels
gh label list --repo owner/repo

# List labels in JSON format
gh label list --repo owner/repo --json name,color,description
```

## Label Application Rules

### On Issue Creation

| Issue Type | Automatic Labels |
|------------|------------------|
| Feature request | `type:feature`, `status:backlog` |
| Bug report | `type:bug`, `status:backlog` |
| Documentation | `type:docs`, `status:backlog` |

### On Agent Assignment

```
WHEN issue assigned to agent:
  ADD "agent:{agent-id}" label
  REMOVE "status:backlog" label
  ADD "status:ready" label
```

### On Work Start

```
WHEN agent starts work:
  REMOVE "status:ready" label
  ADD "status:in-progress" label
```

### On PR Creation

```
WHEN PR created for issue:
  REMOVE "status:in-progress" label
  ADD "status:ai-review" label
  ADD "review:needed" label
```

### On PR Review

```
WHEN PR approved:
  REMOVE "review:needed" label
  ADD "review:approved" label

WHEN changes requested:
  REMOVE "review:needed" label
  ADD "review:changes-requested" label
```

### On Completion

```
WHEN PR merged:
  REMOVE all "status:*" labels
  REMOVE all "review:*" labels
  (Issue auto-closed if linked)
```

## Label-Based Queries

### Find All Bugs

```bash
gh issue list --label "type:bug" --state open
```

### Find High Priority Items

```bash
gh issue list --label "priority:critical" --label "priority:high" --state open
```

### Find Blocked Items

```bash
gh issue list --label "status:blocked" --state open
```

### Find Items by Assignment

```bash
gh issue list --label "assign:dev-1" --state open
```

### Find Ready to Work

```bash
gh issue list --label "status:ready" --state open
```

### Complex Query via Search

```bash
# All open bugs with high priority that are not blocked
gh issue list --search "is:open label:type:bug label:priority:high -label:status:blocked"
```

## Label Statistics

### Count by Type

```bash
gh issue list --state all --json labels --jq '
  [.[] | .labels[].name | select(startswith("type:"))]
  | group_by(.)
  | map({label: .[0], count: length})
'
```

### Count by Status

```bash
gh issue list --state open --json labels --jq '
  [.[] | .labels[].name | select(startswith("status:"))]
  | group_by(.)
  | map({label: .[0], count: length})
'
```

## Best Practices

### DO

- Use consistent label naming (category:value)
- Apply type and priority labels to all issues
- Remove outdated status labels when state changes
- Keep agent labels current with actual assignment
- Use effort labels for sprint planning

### DON'T

- Create duplicate labels with different names
- Leave multiple conflicting status labels
- Use labels instead of project board status
- Create one-off labels for single issues
- Forget to update labels when state changes

## Label Colors Reference

| Category | Color Palette |
|----------|---------------|
| Type | Blues, Yellows, Purples |
| Priority | Red spectrum (critical to low) |
| Status | Varies by state |
| Component | Light/pastel colors |
| Effort | Green to Red gradient |
| Review | Status-appropriate colors |
