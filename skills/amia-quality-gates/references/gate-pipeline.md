# Gate Pipeline Flow

## Overview

The quality gate pipeline consists of four sequential gates that code must pass through before reaching production. This document describes the complete flow and gate transitions.

## Pipeline Diagram

```
PR Created
    ↓
┌─────────────────────┐
│ Pre-Review Gate     │ ← Automated checks
│ - Tests             │
│ - Linting           │
│ - Build             │
│ - Description       │
└──────────┬──────────┘
           │ PASS
           ↓
┌─────────────────────┐
│ Review Gate         │ ← Human review
│ - 8 Dimensions      │
│ - Confidence >= 80% │
└──────────┬──────────┘
           │ PASS
           ↓
┌─────────────────────┐
│ Pre-Merge Gate      │ ← Final checks
│ - CI Pipeline       │
│ - No Conflicts      │
│ - Valid Approval    │
└──────────┬──────────┘
           │ PASS
           ↓
       MERGE
           ↓
┌─────────────────────┐
│ Post-Merge Gate     │ ← Verification
│ - Main Build        │
│ - No Regressions    │
│ - Deployment OK     │
└──────────┬──────────┘
           │ PASS
           ↓
    Issue Closed
    Integration Complete
```

## Gate Transitions

### Transition: Pre-Review → Review

**Condition**: All automated checks pass
**Labels**: Remove `gate:pre-review-pending`, add `gate:pre-review-passed`
**Action**: Notify reviewers that PR is ready for review

### Transition: Review → Pre-Merge

**Condition**: Review confidence >= 80%, no blocking issues
**Labels**: Remove `gate:review-pending`, add `gate:review-passed`
**Action**: Await final CI checks and approval

### Transition: Pre-Merge → Merge

**Condition**: CI green, no conflicts, approval valid
**Labels**: Remove `gate:pre-merge-pending`, add `gate:pre-merge-passed`
**Action**: Execute merge operation

### Transition: Merge → Post-Merge

**Condition**: Merge completed successfully
**Labels**: Add `gate:post-merge-pending`
**Action**: Monitor main branch health

### Transition: Post-Merge → Complete

**Condition**: Main branch healthy after merge
**Labels**: Add `gate:post-merge-passed`
**Action**: Close linked issue, mark integration complete

## Failure Handling

At any gate failure:
1. Stop progression
2. Apply appropriate `gate:*-failed` label
3. Follow escalation path for that gate
4. Do not advance until failure resolved

## Parallel Gates

Gates are **strictly sequential** - no parallel execution. A PR cannot be in multiple gates simultaneously.

## Gate Bypass

Gates cannot be bypassed. Overrides require explicit authorization and documentation. See **Override Policies** in SKILL.md.
