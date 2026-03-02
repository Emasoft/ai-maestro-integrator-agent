# Status Management

## Table of Contents

1. [When starting with status management](#overview)
2. [When you need to understand status meanings and metadata](#status-definitions)
3. [When moving issues between statuses](#transition-rules) - See [Part 1: Transitions](./status-management-part1-transitions.md)
4. [When syncing GitHub state with project board](#synchronization-protocol) - See [Part 1: Transitions](./status-management-part1-transitions.md)
5. [When updating status via API or scripts](#status-change-api) - See [Part 2: Operations](./status-management-part2-operations.md)
6. [When generating status reports or summaries](#status-reporting) - See [Part 2: Operations](./status-management-part2-operations.md)
7. [When issues need attention or escalation](#alerting-rules) - See [Part 2: Operations](./status-management-part2-operations.md)
8. [When deciding whether to close inactive issues](#issue-lifecycle-policy-no-stale) - See [Part 2: Operations](./status-management-part2-operations.md)
9. [When following status management best practices](#best-practices) - See [Part 2: Operations](./status-management-part2-operations.md)
10. [When referencing related workflow documentation](#related-references)

---

## Part Files

This document has been split for easier reading:

| Part | Contents | When to Read |
|------|----------|--------------|
| **This file** | Overview, Status Definitions | Understanding what statuses mean |
| **[Part 1: Transitions](./status-management-part1-transitions.md)** | Transition Rules, Sync Protocol | Moving items between statuses |
| **[Part 2: Operations](./status-management-part2-operations.md)** | API, Reporting, Alerts, Lifecycle, Best Practices | Automating status changes |

---

## Overview

This document defines the complete status lifecycle for project items, including transition rules, validation, and synchronization protocols.

## Status Definitions

### Standard Statuses

| Status | Code | Description | Color |
|--------|------|-------------|-------|
| **Backlog** | `backlog` | Not yet scheduled | Gray |
| **Todo** | `todo` | Scheduled for current/next sprint | Blue |
| **In Progress** | `in-progress` | Active development | Yellow |
| **AI Review** | `ai-review` | Integrator reviews ALL tasks | Purple |
| **Human Review** | `human-review` | User reviews BIG tasks only | Pink |
| **Merge/Release** | `merge-release` | Ready to merge | Light Green |
| **Blocked** | `blocked` | Cannot proceed | Red |
| **Done** | `done` | Completed and merged | Green |
| **Cancelled** | `cancelled` | Will not be implemented | Gray |

### Status Metadata

```json
{
  "statuses": {
    "backlog": {
      "name": "Backlog",
      "description": "Items not yet scheduled for work",
      "is_terminal": false,
      "requires_assignment": false,
      "requires_branch": false
    },
    "todo": {
      "name": "Todo",
      "description": "Items scheduled and ready to start",
      "is_terminal": false,
      "requires_assignment": true,
      "requires_branch": false
    },
    "in-progress": {
      "name": "In Progress",
      "description": "Active development underway",
      "is_terminal": false,
      "requires_assignment": true,
      "requires_branch": true
    },
    "ai-review": {
      "name": "AI Review",
      "description": "Integrator reviews ALL tasks",
      "is_terminal": false,
      "requires_assignment": true,
      "requires_branch": true,
      "requires_pr": true
    },
    "human-review": {
      "name": "Human Review",
      "description": "User reviews BIG tasks only",
      "is_terminal": false,
      "requires_assignment": true,
      "requires_branch": true,
      "requires_pr": true
    },
    "merge-release": {
      "name": "Merge/Release",
      "description": "Ready to merge, all reviews completed",
      "is_terminal": false,
      "requires_assignment": true,
      "requires_branch": true,
      "requires_pr": true
    },
    "blocked": {
      "name": "Blocked",
      "description": "Cannot proceed due to external factor",
      "is_terminal": false,
      "requires_assignment": true,
      "requires_blocker_reason": true
    },
    "done": {
      "name": "Done",
      "description": "Completed and merged to main",
      "is_terminal": true,
      "requires_assignment": false
    },
    "cancelled": {
      "name": "Cancelled",
      "description": "Will not be implemented",
      "is_terminal": true,
      "requires_assignment": false,
      "requires_cancel_reason": true
    }
  }
}
```

### Status Properties Summary

| Status | Terminal? | Needs Assignee? | Needs Branch? | Needs PR? |
|--------|-----------|-----------------|---------------|-----------|
| Backlog | No | No | No | No |
| Todo | No | Yes | No | No |
| In Progress | No | Yes | Yes | No |
| AI Review | No | Yes | Yes | Yes |
| Human Review | No | Yes | Yes | Yes |
| Merge/Release | No | Yes | Yes | Yes |
| Blocked | No | Yes | - | - |
| Done | Yes | No | - | - |
| Cancelled | Yes | No | - | - |

---

## Issue Lifecycle Policy (NO STALE)

**IRON RULE**: Issues are NEVER automatically closed due to inactivity.

For complete lifecycle policy including closure conditions, reproduction attempt requirements, and prohibited actions, see **[Part 2: Operations - Issue Lifecycle](./status-management-part2-operations.md#issue-lifecycle-policy-no-stale)**.

Quick reference:
- **Features**: Close only when implemented+merged OR explicitly declined with reason
- **Bugs**: Close only when fixed+verified OR after 3 documented reproduction attempts failed
- **Chores**: Close only when completed and verified
- **NEVER** use stale bots or auto-close automation

---

## Related References

This document is part of the complete GitHub Projects synchronization system. Related documentation:

- **[Part 1: Transitions](./status-management-part1-transitions.md)** - Transition rules and synchronization protocol
- **[Part 2: Operations](./status-management-part2-operations.md)** - API, reporting, alerts, lifecycle, best practices
- **[Iteration Cycle Rules](./iteration-cycle-rules.md)** - Complete iteration workflow, including the 100% approval rule for PR merges
- **[Review Worktree Workflow](./review-worktree-workflow.md)** - Dedicated worktree setup for PR reviews and validation
- **[Plan File Linking](./plan-file-linking.md)** - Plan file creation, linking to issues, and lifecycle management
