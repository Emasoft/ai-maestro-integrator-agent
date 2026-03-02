# Complete Code Review Workflow and Decision Tree

## Table of Contents

- 3.1 Four-Phase Workflow Overview
  - 3.1.1 Phase 1: Initial Assessment
  - 3.1.2 Phase 2: Quick Scan (Stage One)
  - 3.1.3 Phase 3: Deep Dive (Stage Two)
  - 3.1.4 Phase 4: Feedback & Resolution
- 3.2 Confidence Scoring Decision Tree
- 3.3 Decision Flow Diagram
- 3.4 Handling Edge Cases

---

## 3.1 Four-Phase Workflow Overview

### 3.1.1 Phase 1: Initial Assessment (Before Review)

**Purpose**: Understand context before starting formal review

**Actions:**
- Understand the context and purpose of changes
- Identify the type of change (feature, bug fix, refactor, etc.)
- Check if sufficient information is provided
- Review linked issues or requirements

**Time Target**: 2-5 minutes

### 3.1.2 Phase 2: Quick Scan (Stage One)

**Purpose**: Rapid triage to identify obvious blockers

**Actions:**
- Execute quick scan process
- Assign initial confidence score
- Decide whether to proceed to Stage Two

**Time Target**: 5-15 minutes
**Threshold**: 70%+ to proceed

**Detailed guidance**: See [stage-one-quick-scan.md](./stage-one-quick-scan.md)

### 3.1.3 Phase 3: Deep Dive (Stage Two)

**Purpose**: Comprehensive multi-dimensional analysis

**Actions:**
- Analyze across all 8 dimensions
- Score each dimension
- Calculate final confidence
- Make approval decision

**Time Target**: 30-120 minutes
**Threshold**: 80%+ for approval

**Detailed guidance**: See [stage-two-deep-dive.md](./stage-two-deep-dive.md)

### 3.1.4 Phase 4: Feedback & Resolution

**Purpose**: Clear communication and issue tracking

**Actions:**
- Communicate findings clearly
- List specific required changes
- Assign action items to author
- Re-review after changes if needed
- Archive review for knowledge sharing

**Time Target**: 10-20 minutes

---

## 3.2 Confidence Scoring Decision Tree

```
START REVIEW
    |
    v
RUN QUICK SCAN
    |
    v
Quick Score >= 70%?
    |
    +-- NO --> Request clarification
    |              |
    |              v
    |          Re-submit
    |              |
    |              v
    |          (Return to Quick Scan)
    |
    +-- YES --> Proceed to Deep Dive
                   |
                   v
              ANALYZE ALL 8 DIMENSIONS
                   |
                   v
              Final Score >= 80%?
                   |
                   +-- NO --> Is score 60-79%?
                   |            |
                   |            +-- YES --> Conditional Approval
                   |            |              (Author must address items)
                   |            |              |
                   |            |              v
                   |            |          Re-submit
                   |            |              |
                   |            |              v
                   |            |          (Return to Deep Dive)
                   |            |
                   |            +-- NO --> Rejection
                   |                       (Substantial rework needed)
                   |
                   +-- YES --> APPROVED
                               (Ready to merge)
```

---

## 3.3 Decision Flow Diagram

### Quick Reference Decision Table

| Quick Scan Score | Deep Dive Score | Decision | Action |
|------------------|-----------------|----------|--------|
| < 70% | N/A | HOLD | Request clarification |
| >= 70% | >= 80% | APPROVED | Merge immediately |
| >= 70% | 60-79% | CONDITIONAL | List changes, re-review |
| >= 70% | < 60% | REJECTED | Major rework needed |

### Score Interpretation

| Score Range | Meaning | Reviewer Confidence |
|-------------|---------|---------------------|
| 90-100% | Excellent | Very high |
| 80-89% | Good | High |
| 70-79% | Acceptable for Stage One | Medium |
| 60-69% | Needs work | Low |
| < 60% | Significant issues | Very low |

---

## 3.4 Handling Edge Cases

### When Quick Scan Passes but Deep Dive Reveals Issues

1. Document what was missed in Quick Scan
2. Update Quick Scan checklist for future reviews
3. Proceed with Conditional Approval or Rejection based on severity

### When Author Disagrees with Assessment

1. Document specific points of disagreement
2. Provide concrete evidence for concerns
3. Escalate to senior reviewer if no resolution
4. Record decision rationale for future reference

### When Time Pressure Exists

1. Never skip Stage One (Quick Scan)
2. Focus Deep Dive on Security, Testing, and Functional Correctness
3. Document any dimensions not fully reviewed
4. Request follow-up review for deferred dimensions

### When PR is Too Large

1. Request split into smaller focused PRs
2. If split not possible, plan multiple review sessions
3. Review in logical order (core changes first)
4. Track reviewed vs. unreviewed sections clearly
