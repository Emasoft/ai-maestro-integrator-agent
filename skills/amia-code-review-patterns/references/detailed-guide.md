# Code Review Patterns — Detailed Guide

## Contents

- [Core Methodology: Two-Stage Review Process](#core-methodology-two-stage-review-process)
- [Key Concepts](#key-concepts)
  - [Confidence Scoring System](#confidence-scoring-system)
  - [Multi-Dimensional Analysis](#multi-dimensional-analysis)
- [Quick Reference Tables](#quick-reference-tables)
  - [Confidence Score Ranges](#confidence-score-ranges)
  - [Dimension Weight Summary](#dimension-weight-summary)
- [Scripts Available](#scripts-available)
- [AI Maestro Communication Templates](#ai-maestro-communication-templates)
  - [Template 1: Receiving PR Review Request](#template-1-receiving-pr-review-request)
  - [Template 2: Reporting Review Completion](#template-2-reporting-review-completion)
  - [Template 3: Requesting Clarification from Author](#template-3-requesting-clarification-from-author)
  - [Template 4: Escalating Quality Gate Failure](#template-4-escalating-quality-gate-failure)
- [Error Handling](#error-handling)
- [Reference Document TOCs](#reference-document-tocs)

---

## Core Methodology: Two-Stage Review Process

The skill is built on a structured two-stage approach:

**Stage One: Quick Scan (Small Scope)**

- Initial surface-level assessment
- Identification of obvious issues
- Scope: File structure + diff magnitude review
- Confidence scoring threshold: 70%+
- Go/No-Go decision point

**Stage Two: Deep Dive (Full Scope)**

- Comprehensive multi-dimensional analysis
- Root cause investigation
- Scope: All 8 dimensions across all changed components
- Confidence scoring threshold: 80%+
- Final approval/rejection decision

---

## Key Concepts

### Confidence Scoring System

Confidence scoring represents the reviewer's certainty about the quality assessment. Scores range from 0-100%:

- **80-100%**: High confidence - Ready for approval
- **60-79%**: Medium confidence - Requires additional review or clarification
- **Below 60%**: Low confidence - Defer decision, escalate for expert review

The 80% threshold ensures that code reviews maintain quality standards before approval.

### Multi-Dimensional Analysis

Code review examines code across 8 dimensions simultaneously:

1. **Functional Correctness** - Does the code do what it should?
2. **Architecture & Design** - Is the structure sound and maintainable?
3. **Code Quality** - Is the code clean, readable, and well-documented?
4. **Performance** - Does the code perform adequately?
5. **Security** - Are there vulnerabilities or compliance issues?
6. **Testing** - Is there adequate test coverage?
7. **Backward Compatibility** - Does it break existing interfaces?
8. **Documentation** - Is it adequately documented for future maintainers?

---

## Quick Reference Tables

### Confidence Score Ranges

| Score Range | Decision | Action |
|-------------|----------|--------|
| 80-100% | Approved | Merge immediately |
| 70-79% | Quick Scan only | Proceed to Deep Dive |
| 60-79% | Conditional | Request specific changes |
| Below 60% | Rejected | Major rework needed |

### Dimension Weight Summary

| Dimension | Weight | Primary Question |
|-----------|--------|------------------|
| Functional Correctness | 20% | Does it work? |
| Security | 20% | Is it safe? |
| Testing | 15% | Is it verified? |
| Architecture | 15% | Is it sustainable? |
| Backward Compatibility | 15% | Does it break things? |
| Code Quality | 10% | Is it maintainable? |
| Performance | 5% | Is it efficient? |
| Documentation | 5% | Is it explained? |

---

## Scripts Available

- `scripts/quick_scan_template.py` - Generate quick scan report
- `scripts/deep_dive_calculator.py` - Calculate confidence scores
- `scripts/review_report_generator.py` - Create final review document

All scripts support `--output-file <path>`:

- **With flag**: Full output written to file; concise summary printed to stderr
- **Without flag**: Full output printed to stdout (backward compatible)

---

## AI Maestro Communication Templates

### Template 1: Receiving PR Review Request

When receiving a PR review request from AMOA or another agent, check your inbox using the `agent-messaging` skill. Filter for messages with `content.type == "pr-review-request"`.

### Template 2: Reporting Review Completion

After completing a code review, notify the requesting agent. Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `Code Review Complete: PR #123`
- **Priority**: `normal`
- **Content**: `{"type": "review-complete", "message": "PR #123 review completed. Confidence: 85%. Decision: APPROVED. Details: docs_dev/integration/reports/pr-123-review.md"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Template 3: Requesting Clarification from Author

When review requires author input, send a message using the `agent-messaging` skill with:

- **Recipient**: The PR author agent name
- **Subject**: `Review Question: PR #123`
- **Priority**: `normal`
- **Content**: `{"type": "clarification-request", "message": "During review of PR #123, need clarification on: [SPECIFIC QUESTION]. Please respond with context."}`

### Template 4: Escalating Quality Gate Failure

When a critical quality gate fails, send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `[QUALITY GATE FAILED] PR #123`
- **Priority**: `urgent`
- **Content**: `{"type": "quality-gate-failure", "message": "PR #123 failed quality gate: SECURITY. Issue: SQL injection in auth.py:42. Action required: reject and request fix."}`

---

## Error Handling

- **Slow reviews** → See `references/troubleshooting-performance.md`
- **Reviewer calibration** → See `references/troubleshooting-calibration.md`
- **Coverage gaps** → See `references/troubleshooting-coverage.md`
- **Reviewer disagreements** → See `references/troubleshooting-agreement.md`

---

## Reference Document TOCs

### Gate 0: Requirement Compliance (`references/requirement-compliance.md`)

- 5.1 Gate 0: Requirement Compliance Overview
- 5.2 Gate 0 Checklist Template
- 5.3 Review Checklist Additions (Requirement Traceability, Technology Compliance, Scope Compliance)
- 5.4 Forbidden Review Approvals
- 5.5 Correct Review Approach

### Stage One: Quick Scan (`references/stage-one-quick-scan.md`)

- 1.1 Objective and Purpose
- 1.2 Scope Targets by PR Size (Small 1-10, Medium 11-30, Large 30+)
- 1.3 Step-by-Step Quick Scan Process (File Structure, Diff Magnitude, Obvious Issues, Red Flags, Confidence)
- 1.4 Quick Scan Output Format Template
- 1.5 Go/No-Go Decision Criteria

### Stage Two: Deep Dive (`references/stage-two-deep-dive.md`)

- 2.1 Objective and Purpose
- 2.2 Scope Coverage by PR Size
- 2.3 Eight Dimension Analysis Overview (all 8 dimensions)
- 2.4 Confidence Score Calculation Method
- 2.5 Final Decision Making Thresholds
- 2.6 Deep Dive Output Format Template

### Workflow and Decision Tree (`references/workflow-and-decision-tree.md`)

- 3.1 Four-Phase Workflow (Initial Assessment, Quick Scan, Deep Dive, Feedback & Resolution)
- 3.2 Confidence Scoring Decision Tree
- 3.3 Decision Flow Diagram
- 3.4 Handling Edge Cases

### Implementation Checklist (`references/implementation-checklist.md`)

- 4.1 Complete Implementation Checklist (Setup, Stage One, Stage Two, Scoring & Decision, Follow-up)
- 4.2 Quick Reference Tables (Confidence Ranges, Scope Complexity, Dimension Weights)

### Review Workflow (`references/review-workflow.md`)

- Starting a code review task (parsing requests, extracting PR metadata)
- Gathering context (specifications, changed files, previous comments)
- Gate 1: Specification Compliance (requirements, architecture, interface contracts)
- Gate 2: Code Quality Evaluation (correctness, security, performance, maintainability)
- Generating review reports
- Creating fix instructions
- Communicating findings via AI Maestro
- Updating GitHub Projects tracking
- Archiving review artifacts

### Commit Conventions (`references/commit-conventions.md`)

- 1.1 Writing Descriptive Commit Messages (WHAT/WHY, File Changes, Symbol Changes, Config Changes)
- 1.2 Choosing the Correct Commit Category Prefix
- 1.3 Making Commits Searchable for Decision Archaeology
- 1.4 Managing Dual-Git Repositories
- 1.5 Documenting Removals and Renames with Supersedes Information
- IRON RULES and Example Commit Messages

**Version**: 1.0 | **Updated**: 2025-01-01 | **Difficulty**: Intermediate

---

## Reference Documents Index (moved from SKILL.md)

**Review Process:**

- `references/requirement-compliance.md` -- Gate 0 compliance checklist
- `references/stage-one-quick-scan.md` -- Stage 1 quick scan process
- `references/stage-two-deep-dive.md` -- Stage 2 eight-dimension analysis
- `references/workflow-and-decision-tree.md` -- Workflow and decision flow
- `references/review-workflow.md` -- Review workflow with gates
- `references/implementation-checklist.md` -- Implementation checklist

**8 Dimensions (Deep Dive):**

- `references/functional-correctness.md` -- Dim 1: Functional Correctness
- `references/architecture-design.md` -- Dim 2: Architecture and Design
- `references/code-quality.md` -- Dim 3: Code Quality
- `references/performance-analysis.md` -- Dim 4: Performance
- `references/security-analysis.md` -- Dim 5: Security
- `references/testing-analysis.md` -- Dim 6: Testing
- `references/backward-compatibility.md` -- Dim 7: Backward Compatibility
- `references/documentation-analysis.md` -- Dim 8: Documentation

**Quality and Standards:**

- `references/pre-pr-quality-gate.md` -- Pre-PR validation steps
- `references/commit-conventions.md` -- Commit message conventions
- `references/examples.md` -- Detailed review examples

**Troubleshooting:**

- `references/troubleshooting-performance.md` -- Slow reviews
- `references/troubleshooting-calibration.md` -- Reviewer calibration
- `references/troubleshooting-coverage.md` -- Coverage gaps
- `references/troubleshooting-agreement.md` -- Reviewer disagreements
