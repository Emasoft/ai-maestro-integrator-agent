# Progress Report Template

## Table of Contents

- [Template](#template)
- [Executive Summary](#executive-summary)
- [Metrics Overview](#metrics-overview)
- [Task Status](#task-status)
  - [Completed (X)](#completed-x)
  - [In Progress (Y)](#in-progress-y)
  - [Pending (Z)](#pending-z)
  - [Blocked (W)](#blocked-w)
- [Milestones](#milestones)
- [Recommendations](#recommendations)
- [Next Actions](#next-actions)
- [Field Definitions](#field-definitions)
- [Status Icons](#status-icons)

Template for tracking task and milestone progress over a reporting period.

---

## Template

```markdown
# Progress Report
**Generated**: YYYY-MM-DD HH:MM:SS
**Scope**: [Project/Milestone/Sprint Name]
**Period**: [Date Range]

## Executive Summary
[2-3 sentences summarizing overall status]

## Metrics Overview
- **Total Tasks**: X (Y% complete)
- **Active Tasks**: X in-progress, Y pending, Z blocked
- **Milestones**: X/Y complete
- **Velocity**: X tasks/week (vs Y target)
- **Health**: 🟢 Green / 🟡 Yellow / 🔴 Red

## Task Status

### Completed (X)
- ✅ [Task #1] - Brief description
- ✅ [Task #2] - Brief description

### In Progress (Y)
- 🔄 [Task #3] - Brief description (XX% complete)
  - ✅ Subtask 3.1
  - 🔄 Subtask 3.2
  - ⏸️ Subtask 3.3

### Pending (Z)
- ⏸️ [Task #4] - Brief description (blocked by Task #3)

### Blocked (W)
- 🚫 [Task #5] - Brief description
  - **Blocker**: Dependency on external API
  - **Impact**: High
  - **Mitigation**: Investigating alternative approach

## Milestones

╔════════════════════════════╦══════════╦══════════════╦═══════════╗
║ Milestone                  ║ Progress ║ Target Date  ║ Status    ║
╠════════════════════════════╬══════════╬══════════════╬═══════════╣
║ MVP Feature Set            ║ 85%      ║ 2025-01-15   ║ On Track  ║
║ Beta Release               ║ 40%      ║ 2025-02-01   ║ At Risk   ║
║ Documentation Complete     ║ 60%      ║ 2025-01-20   ║ On Track  ║
╚════════════════════════════╩══════════╩══════════════╩═══════════╝

## Recommendations
1. [Action item 1]
2. [Action item 2]

## Next Actions
- [ ] [Immediate action 1]
- [ ] [Immediate action 2]

---
**Sources**: GitHub Projects, GitHub Issues, AI Maestro Messages
**Report ID**: progress_YYYYMMDD_HHMMSS
```

---

## Field Definitions

| Field | Description |
|-------|-------------|
| **Scope** | Project, milestone, or sprint being reported on |
| **Period** | Date range covered by the report |
| **Velocity** | Tasks completed per week vs target |
| **Health** | Overall project health indicator |

## Status Icons

| Icon | Meaning |
|------|---------|
| ✅ | Completed |
| 🔄 | In Progress |
| ⏸️ | Pending/Paused |
| 🚫 | Blocked |
| 🟢 | Green/Healthy |
| 🟡 | Yellow/At Risk |
| 🔴 | Red/Critical |

---

**Back to [Report Templates Index](report-templates.md)**
