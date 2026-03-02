# Planning Phase to GitHub Status Mapping

## Table of Contents

1. [When mapping planning phases to GitHub statuses](#overview)
2. [When you need the phase-to-status mapping table](#phase-to-status-mapping)
3. [When status should automatically transition](#automatic-transitions)
4. [When manually overriding automatic transitions](#manual-override-rules)
5. [When integrating with other automation](#integration-points)
6. [When you need workflow examples](#examples)

## Overview
Maps planning-patterns phases to GitHub Projects board columns for status tracking.

## Phase-to-Status Mapping

| Planning Phase | GitHub Status | Description |
|----------------|---------------|-------------|
| Not Started | Backlog | Issue created but not planned |
| Planning (Architecture) | Todo | Architecture design in progress |
| Planning (Risk) | Todo | Risk identification in progress |
| Planning (Roadmap) | Todo | Roadmap creation in progress |
| Implementation | In Progress | Code/work being done |
| Quality Review | AI Review | PR created, awaiting AI review |
| Complete | Done | Work merged and verified |
| Blocked | Blocked | External dependency blocking |

## Automatic Transitions

### Planning → Todo
Triggered when:
- Plan file created (`plans/GH-{N}-*.md`)
- Issue linked to plan file
- Architecture phase started

### Todo → In Progress
Triggered when:
- Worktree created for issue
- First commit on feature branch
- Agent claims task

### In Progress → AI Review
Triggered when:
- PR opened linking issue
- All implementation tasks marked complete in plan

### AI Review → Human Review (for large/risky tasks)
Triggered when:
- AI review passes all automated checks
- Issue is labeled `size:L`, `size:XL`, or `risk:high`

### AI Review → Done (for small/routine tasks)
Triggered when:
- AI review passes all automated checks
- Issue is NOT labeled for human review

### Human Review → Done
Triggered when:
- PR merged
- Verification patterns confirm success
- No blocking issues remain

## Manual Override Rules
- Status can always be set manually via `gh issue edit`
- Manual changes should include comment explaining reason
- Blocked status requires blocker issue link

## Integration Points
- generate-task-tracker.py reads GitHub status
- generate-status-report.py aggregates status data
- Orchestrator monitors status for task assignment

## Examples
1. New feature workflow
2. Bug fix workflow
3. Documentation workflow
