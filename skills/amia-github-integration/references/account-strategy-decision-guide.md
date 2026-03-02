# Account Strategy Decision Guide

## Table of Contents

- [Overview](#overview)
- [Decision Tree](#decision-tree)
- [Quick Comparison](#quick-comparison)
- [Detailed Recommendations](#detailed-recommendations)
  - [Use Single-Account When](#use-single-account-when)
  - [Use Multi-Account When](#use-multi-account-when)
- [Migration Paths](#migration-paths)
- [Hybrid Approach](#hybrid-approach)
- [Implementation Checklist](#implementation-checklist)

---

## Overview

This guide helps you choose between single-account (label-based) and multi-account (assignee-based) workflows for tracking AI agent assignments in GitHub.

## Decision Tree

```
Do you have multiple GitHub accounts for AI agents?
│
├── YES → Do you want distinct PR authorship per agent?
│         │
│         ├── YES → Use Multi-Account Workflow
│         │         See: multi-user-workflow.md
│         │
│         └── NO → Either workflow works, prefer Single-Account for simplicity
│
└── NO → Are you willing to create multiple GitHub accounts?
          │
          ├── YES → How many agents will you run simultaneously?
          │         │
          │         ├── 2-3 agents → Multi-Account is manageable
          │         │
          │         └── 4+ agents → Consider Single-Account (labels scale better)
          │
          └── NO → Use Single-Account Workflow
                   See: single-account-workflow.md
```

## Quick Comparison

| Factor | Single-Account (Labels) | Multi-Account (Assignees) |
|--------|-------------------------|---------------------------|
| **Setup time** | 5 minutes | 1-2 hours |
| **Maintenance** | Low | Medium (SSH keys, tokens) |
| **Visual clarity** | Good (colored labels) | Excellent (avatars) |
| **PR attribution** | All under owner | Per-agent |
| **GitHub free tier** | Full support | May need paid org |
| **Team collaboration** | Labels are shared | Native assignee support |
| **Audit trail** | Label changes logged | Assignee changes logged |
| **Scalability** | Excellent (labels cheap) | Limited (accounts costly) |

## Detailed Recommendations

### Use Single-Account When

1. **Solo developer** with one GitHub account
2. **Rapid prototyping** - don't want setup overhead
3. **Many concurrent agents** (4+) - labels scale better
4. **Cost-sensitive** - no need for multiple accounts
5. **Simple audit needs** - label history is sufficient

### Use Multi-Account When

1. **Team environment** - other humans also work on repo
2. **PR attribution matters** - want clear agent authorship
3. **Native GitHub features** - want assignee filters in UI
4. **Compliance requirements** - need distinct identities
5. **External visibility** - stakeholders review contributor list

## Migration Paths

### Single to Multi-Account

1. Create GitHub accounts for each agent
2. Configure SSH keys and tokens
3. Add accounts as repo collaborators
4. For each issue with `assign:X` label:
   - Add corresponding assignee
   - Optionally remove label (or keep for redundancy)
5. Update query scripts to use `--assignee` instead of `--label`

### Multi to Single-Account

1. Create `assign:*` labels for each agent
2. For each issue:
   - Add `assign:X` label matching assignee
   - Keep assignee (or reassign to owner)
3. Update query scripts to use `--label` instead of `--assignee`

## Hybrid Approach

You can use BOTH methods simultaneously:

- **Assignee** = GitHub identity (owner or agent account)
- **Label** = Logical agent assignment

This provides:
- Native GitHub features (assignees)
- Additional filtering (labels)
- Redundancy for clarity

Example hybrid query:
```bash
# Find issues for implementer-1 (either method works)
gh issue list --assignee implementer-1
gh issue list --label "assign:implementer-1"
```

## Implementation Checklist

### Single-Account Setup

- [ ] Create `assign:*` labels (one per agent role)
- [ ] Document label color scheme
- [ ] Update kanban board filters
- [ ] Test query commands with labels

### Multi-Account Setup

- [ ] Create GitHub accounts
- [ ] Configure SSH keys per account
- [ ] Set up gh-multiuser script
- [ ] Add accounts to repository
- [ ] Test identity switching
- [ ] Document account credentials securely
