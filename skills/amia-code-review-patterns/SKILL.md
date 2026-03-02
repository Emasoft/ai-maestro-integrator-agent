---
name: amia-code-review-patterns
description: "Use when reviewing pull requests. Trigger with PR review or code quality requests."
license: Apache-2.0
compatibility: Requires intermediate software development experience and familiarity with code review basics. Designed for reviewers analyzing pull requests with 1-30+ file changes using an 8-dimensional evaluation framework. Requires AI Maestro installed.
triggers:
  - Review a pull request for quality and issues
  - Assess code changes before merge
  - Perform quick scan followed by deep dive analysis
  - Evaluate code across 8 dimensions (functional, architecture, quality, performance, security, testing, compatibility, documentation)
  - Review this PR
  - Check this code for issues
metadata:
  author: Emasoft
  version: 1.0.0
agent: amia-main
context: fork
workflow-instruction: "Step 21"
procedure: "proc-evaluate-pr"
user-invocable: false
---

# Code Review Patterns Skill

## Overview

This skill teaches the **two-stage code review methodology** for comprehensive PR analysis.

## Prerequisites

Intermediate software development experience, familiarity with code review basics and PR workflows, access to the target repository, and Python 3.8+ for helper scripts.

## Output

| Output Type | Format | Contents |
|-------------|--------|----------|
| Quick Scan Report | Markdown table | File structure, diff magnitude, obvious issues, initial confidence score (0-100%), Go/No-Go decision |
| Deep Dive Report | Markdown table | 8-dimension analysis with individual scores, final confidence score (0-100%), approval/rejection decision, actionable feedback |
| Final Review Document | Markdown | Complete review with both stages, confidence calculations, decision rationale, merge/rejection status |

## Instructions

1. **Receive PR review request** from AMOA or user via AI Maestro
2. **Perform Gate 0 compliance check** - Verify requirements using [references/requirement-compliance.md](references/requirement-compliance.md)
3. **Execute Stage 1: Quick Scan** - Surface-level assessment using [references/stage-one-quick-scan.md](references/stage-one-quick-scan.md)
   - Assess file structure and diff magnitude
   - Identify obvious issues and red flags
   - Calculate initial confidence score
   - Make Go/No-Go decision (proceed if ≥70% confidence)
4. **Execute Stage 2: Deep Dive** - Full 8-dimension analysis using [references/stage-two-deep-dive.md](references/stage-two-deep-dive.md)
   - Evaluate all 8 dimensions (Functional, Architecture, Quality, Performance, Security, Testing, Compatibility, Documentation)
   - Calculate final confidence score
   - Make approval/rejection decision (approve if ≥80% confidence)
5. **Run quality gates** - Execute tests, verify linting, check documentation
6. **Create final review report** using scripts/review_report_generator.py
7. **Merge or reject PR** based on final decision
8. **Close related issues** if PR is merged
9. **Report completion** to requesting agent via AI Maestro

### Checklist

Copy this checklist and track your progress:

- [ ] Receive PR review request from AMOA or user via AI Maestro
- [ ] Perform Gate 0 compliance check using requirement-compliance.md
- [ ] Execute Stage 1: Quick Scan
  - [ ] Assess file structure and diff magnitude
  - [ ] Identify obvious issues and red flags
  - [ ] Calculate initial confidence score
  - [ ] Make Go/No-Go decision (proceed if ≥70% confidence)
- [ ] Execute Stage 2: Deep Dive (8 dimensions)
  - [ ] Evaluate Functional Correctness
  - [ ] Evaluate Architecture & Design
  - [ ] Evaluate Code Quality
  - [ ] Evaluate Performance
  - [ ] Evaluate Security
  - [ ] Evaluate Testing
  - [ ] Evaluate Backward Compatibility
  - [ ] Evaluate Documentation
  - [ ] Calculate final confidence score
- [ ] Run quality gates (tests, linting, documentation)
- [ ] Create final review report using `scripts/review_report_generator.py`
- [ ] Merge or reject PR based on final decision (≥80% to approve)
- [ ] Close related issues if PR is merged
- [ ] Report completion to requesting agent via AI Maestro

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

## Reference Documents

### Gate 0: Requirement Compliance ([references/requirement-compliance.md](references/requirement-compliance.md))
- 5.1 Gate 0: Requirement Compliance Overview
- 5.2 Gate 0 Checklist Template
- 5.3 Review Checklist Additions
  - 5.3.1 Requirement Traceability
  - 5.3.2 Technology Compliance
  - 5.3.3 Scope Compliance
- 5.4 Forbidden Review Approvals
- 5.5 Correct Review Approach

### Stage One: Quick Scan ([references/stage-one-quick-scan.md](references/stage-one-quick-scan.md))
- 1.1 Objective and Purpose
- 1.2 Scope Targets by PR Size
  - 1.2.1 Small PRs (1-10 files)
  - 1.2.2 Medium PRs (11-30 files)
  - 1.2.3 Large PRs (30+ files)
- 1.3 Step-by-Step Quick Scan Process
  - 1.3.1 File Structure Assessment
  - 1.3.2 Diff Magnitude Review
  - 1.3.3 Obvious Issue Scan
  - 1.3.4 Immediate Red Flags Detection
  - 1.3.5 Quick Confidence Assessment
- 1.4 Quick Scan Output Format Template
- 1.5 Go/No-Go Decision Criteria

### Stage Two: Deep Dive ([references/stage-two-deep-dive.md](references/stage-two-deep-dive.md))
- 2.1 Objective and Purpose
- 2.2 Scope Coverage by PR Size
- 2.3 Eight Dimension Analysis Overview
  - 2.3.1 Dimension 1: Functional Correctness
  - 2.3.2 Dimension 2: Architecture & Design
  - 2.3.3 Dimension 3: Code Quality
  - 2.3.4 Dimension 4: Performance
  - 2.3.5 Dimension 5: Security
  - 2.3.6 Dimension 6: Testing
  - 2.3.7 Dimension 7: Backward Compatibility
  - 2.3.8 Dimension 8: Documentation
- 2.4 Confidence Score Calculation Method
- 2.5 Final Decision Making Thresholds
- 2.6 Deep Dive Output Format Template

### Workflow and Decision Tree ([references/workflow-and-decision-tree.md](references/workflow-and-decision-tree.md))
- 3.1 Four-Phase Workflow Overview
  - 3.1.1 Phase 1: Initial Assessment
  - 3.1.2 Phase 2: Quick Scan (Stage One)
  - 3.1.3 Phase 3: Deep Dive (Stage Two)
  - 3.1.4 Phase 4: Feedback & Resolution
- 3.2 Confidence Scoring Decision Tree
- 3.3 Decision Flow Diagram
- 3.4 Handling Edge Cases

### Implementation Checklist ([references/implementation-checklist.md](references/implementation-checklist.md))
- 4.1 Complete Implementation Checklist
  - 4.1.1 Setup Phase Checklist
  - 4.1.2 Stage One: Quick Scan Checklist
  - 4.1.3 Stage Two: Deep Dive Checklist
  - 4.1.4 Scoring & Decision Checklist
  - 4.1.5 Follow-up Checklist
- 4.2 Quick Reference Tables
  - 4.2.1 Confidence Score Ranges
  - 4.2.2 Scope Complexity Guide
  - 4.2.3 Dimension Weight Summary

### Pre-PR Quality Gate ([references/pre-pr-quality-gate.md](references/pre-pr-quality-gate.md))
- 6.1 Overview - Purpose of the Pre-PR quality gate
- 6.2 The 4 Validation Steps
  - 6.2.1 Step 1: All Tests Pass Locally
  - 6.2.2 Step 2: No Linting Errors
  - 6.2.3 Step 3: Documentation Updated
  - 6.2.4 Step 4: Changelog Entry Added
- 6.3 Checklist Template
- 6.4 Automation - Scripts to run before every PR

### Commit Conventions ([references/commit-conventions.md](references/commit-conventions.md))
- **Contents:**
  - Writing descriptive commit messages with WHAT and WHY sections
    - Commit message structure and required sections
    - Documenting file changes (ADDED, MODIFIED, REMOVED, RENAMED)
    - Documenting symbol changes (functions, classes, variables)
    - Documenting configuration changes
  - Choosing the correct commit category prefix
    - Category prefix reference table
    - When to use each category
  - Making commits searchable for future decision archaeology
    - Search scenarios and requirements
    - Indexing best practices
  - Managing dual-git repositories (project vs design)
    - When to commit to project git
    - When to commit to design git
    - Setting up dual-git configuration
  - Documenting removals and renames with supersedes information
    - Supersedes section format
    - Migration instructions
    - Breaking change indicators

### Review Workflow ([references/review-workflow.md](references/review-workflow.md))
- **Contents:**
  - When starting a code review task
    - Receiving and parsing review requests
    - Extracting PR metadata and specifications
  - When gathering context before review
    - Loading specification documents
    - Reading changed files and test files
    - Collecting previous review comments
  - When executing Gate 1: Specification Compliance
    - Verifying user requirements compliance
    - Checking functional requirements match
    - Validating architectural compliance
    - Assessing interface contracts
    - Determining Gate 1 outcome (PASS/FAIL/BLOCKED)
  - When executing Gate 2: Code Quality Evaluation
    - Evaluating correctness and security
    - Assessing performance and maintainability
    - Checking reliability and style compliance
    - Running automated analysis tools
    - Determining Gate 2 outcome (PASS/FAIL/CONDITIONAL)
  - When generating review reports
    - Creating structured review reports
    - Documenting findings with 80%+ confidence
    - Saving reports to correct locations
  - When creating fix instructions for developers
    - Writing WHAT/WHY/WHERE descriptions
    - Specifying verification criteria
    - Avoiding code examples and implementations
  - When communicating findings via AI Maestro
    - Formatting AI Maestro messages
    - Including report file references
  - When updating GitHub Projects tracking
    - Adding PR labels
    - Updating project board status
    - Posting PR summary comments
  - When archiving review artifacts
    - Saving review reports and fix instructions
    - Creating JSON log entries
    - Preparing minimal orchestrator output

---

## Dimension-Specific References

### Functional Correctness ([references/functional-correctness.md](references/functional-correctness.md))
- When you need to verify core functionality → Verification Checklist: Core Functionality
- If you need to check logic correctness → Verification Checklist: Logic Correctness
- When reviewing data flow → Verification Checklist: Data Flow
- If you're concerned about input validation → Verification Checklist: Input Validation
- When verifying output → Verification Checklist: Output Verification
- If you suspect logic errors → Common Issues to Look For

### Architecture and Design ([references/architecture-design.md](references/architecture-design.md))
- When evaluating SOLID principles adherence → Verification Checklist: Architectural Principles
- If you're concerned about code organization → Verification Checklist: Code Organization
- When verifying design patterns are appropriate → Verification Checklist: Design Patterns
- If you need to review API design → Verification Checklist: API Design
- When assessing data structure choices → Verification Checklist: Data Structures
- If you're checking dependencies → Verification Checklist: Dependencies
- If you suspect architecture issues → Common Issues to Look For

### Code Quality ([references/code-quality.md](references/code-quality.md))
- When checking if code is readable → Verification Checklist: Readability
- If you need to verify naming conventions → Verification Checklist: Naming Conventions
- When assessing code complexity → Verification Checklist: Code Complexity
- If you're reviewing comments and documentation → Verification Checklist: Comments and Documentation
- When evaluating code organization → Verification Checklist: Code Organization
- If you need to assess error handling → Verification Checklist: Error Handling
- When detecting code quality issues → Verification Checklist: Code Smells

### Performance ([references/performance-analysis.md](references/performance-analysis.md))
- When reviewing algorithm efficiency → Verification Checklist: Algorithm Efficiency
- If you need to evaluate data structure choices → Verification Checklist: Data Structure Selection
- When assessing database performance → Verification Checklist: Database Performance
- If you're concerned about I/O operations → Verification Checklist: I/O Operations
- When checking memory management → Verification Checklist: Memory Management
- If you need to verify concurrency handling → Verification Checklist: Concurrency
- When evaluating caching strategy → Verification Checklist: Caching

### Security ([references/security-analysis.md](references/security-analysis.md))
- When validating input handling → Verification Checklist: Input Validation
- If you're reviewing authentication and authorization → Verification Checklist: Authentication & Authorization
- When checking sensitive data protection → Verification Checklist: Data Protection
- If you're concerned about SQL injection → Verification Checklist: SQL Injection Prevention
- When verifying XSS protection → Verification Checklist: XSS Prevention
- If you need to check CSRF protection → Verification Checklist: CSRF Protection
- When reviewing cryptography usage → Verification Checklist: Cryptography
- If you're assessing dependency security → Verification Checklist: Dependency Security

### Testing ([references/testing-analysis.md](references/testing-analysis.md))
- When reviewing test coverage → Verification Checklist: Test Coverage
- If you need to evaluate test quality → Verification Checklist: Test Quality
- When assessing test types used → Verification Checklist: Test Types
- If you're reviewing test data setup → Verification Checklist: Test Data
- When evaluating mocking strategies → Verification Checklist: Mocking and Stubbing
- If you need to check assertions → Verification Checklist: Assertions
- When assessing test maintenance → Verification Checklist: Test Maintenance
- If you're reviewing CI/CD integration → Verification Checklist: Continuous Integration

### Backward Compatibility ([references/backward-compatibility.md](references/backward-compatibility.md))
- When reviewing API compatibility → Verification Checklist: API Compatibility
- If you need to verify data compatibility → Verification Checklist: Data Compatibility
- When checking behavioral compatibility → Verification Checklist: Behavioral Compatibility
- If you're concerned about deprecation → Verification Checklist: Deprecation Strategy
- When verifying versioning practices → Verification Checklist: Versioning
- If you need to assess client impact → Verification Checklist: Client Impact
- If you suspect breaking changes → Common Issues to Look For

### Documentation ([references/documentation-analysis.md](references/documentation-analysis.md))
- When reviewing code documentation → See Verification Checklists
- If you need to evaluate docstring quality → See Part 1: Checklists
- When identifying documentation issues → See Part 2: Common Issues
- When scoring documentation quality → See Part 3: Scoring and Practices

---

## Troubleshooting References

### Slow Reviews ([references/troubleshooting-performance.md](references/troubleshooting-performance.md))
- **Contents:**
  - If you need to understand the problem → Problem Description
  - When analyzing why reviews are slow → Root Causes
  - If you're looking for immediate fixes → Solutions and Workarounds
  - When preventing slow reviews → Prevention Strategies
  - If you need to measure improvement → Measuring Improvement
  - When to escalate issues → When to Escalate
  - For overarching guidance → Key Principles

### Reviewer Calibration ([references/troubleshooting-calibration.md](references/troubleshooting-calibration.md))
- **Contents:**
  - If you need to understand the problem → Problem Description
  - When analyzing why calibration issues occur → Root Causes
  - If you're looking for fixes → Solutions and Workarounds
  - When preventing calibration issues → Prevention Strategies
  - If you need to measure improvement → Measuring Calibration
  - When resolving specific disagreements → Handling Calibration Conflicts

### Coverage Gaps ([references/troubleshooting-coverage.md](references/troubleshooting-coverage.md))
- **Contents:**
  - If you need to understand the problem → Problem Description
  - When analyzing why coverage is incomplete → Root Causes
  - If you're looking for solutions → Solutions and Workarounds
  - When preventing coverage gaps → Prevention Strategies
  - If you need to identify gaps → Identifying Coverage Gaps

### Reviewer Disagreements ([references/troubleshooting-agreement.md](references/troubleshooting-agreement.md))
- **Contents:**
  - If you need to understand the problem → Problem Description
  - When analyzing why disagreements occur → Root Causes
  - If you're looking for solutions → Solutions and Workarounds
  - When preventing disagreements → Prevention Strategies
  - When dealing with specific disagreement scenarios → Specific Disagreement Scenarios

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

---

## Examples

For detailed examples with code, see [references/examples.md](references/examples.md):
- 1.1 When reviewing a PR from AMOA - Example: Review and Merge PR
- 1.2 When verifying issue closure - Example: Issue Closure Requirements Check
- 1.3 When using scripts for quick scan - Example: Script-Based Quick Scan
- 1.4 When performing full two-stage review - Example: Complete Two-Stage Review with Scripts

## Error Handling

- **Slow reviews** → See [Troubleshooting References](#troubleshooting-references) → Slow Reviews section
- **Reviewer calibration** → See [Troubleshooting References](#troubleshooting-references) → Reviewer Calibration section
- **Coverage gaps** → See [Troubleshooting References](#troubleshooting-references) → Coverage Gaps section
- **Reviewer disagreements** → See [Troubleshooting References](#troubleshooting-references) → Reviewer Disagreements section

## AI Maestro Communication Templates

### Template 1: Receiving PR Review Request

When receiving a PR review request from AMOA or another agent, check your inbox using the `agent-messaging` skill. Filter for messages with `content.type == "pr-review-request"`.

### Template 2: Reporting Review Completion to AMOA

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
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Template 4: Escalating Quality Gate Failure

When a critical quality gate fails, send a message using the `agent-messaging` skill with:
- **Recipient**: `orchestrator-amoa`
- **Subject**: `[QUALITY GATE FAILED] PR #123`
- **Priority**: `urgent`
- **Content**: `{"type": "quality-gate-failure", "message": "PR #123 failed quality gate: SECURITY. Issue: SQL injection in auth.py:42. Action required: reject and request fix."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

---

## Resources

- [references/requirement-compliance.md](references/requirement-compliance.md) - Gate 0 compliance checklist
- [references/stage-one-quick-scan.md](references/stage-one-quick-scan.md) - Stage One process
- [references/stage-two-deep-dive.md](references/stage-two-deep-dive.md) - Stage Two 8-dimension analysis
- [references/workflow-and-decision-tree.md](references/workflow-and-decision-tree.md) - Decision flow
- [references/implementation-checklist.md](references/implementation-checklist.md) - Complete checklist
- [references/pre-pr-quality-gate.md](references/pre-pr-quality-gate.md) - Pre-PR validation
- [references/functional-correctness.md](references/functional-correctness.md) - Dimension 1 details
- [references/architecture-design.md](references/architecture-design.md) - Dimension 2 details
- [references/code-quality.md](references/code-quality.md) - Dimension 3 details
- [references/performance-analysis.md](references/performance-analysis.md) - Dimension 4 details
- [references/security-analysis.md](references/security-analysis.md) - Dimension 5 details
- [references/testing-analysis.md](references/testing-analysis.md) - Dimension 6 details
- [references/backward-compatibility.md](references/backward-compatibility.md) - Dimension 7 details
- [references/documentation-analysis.md](references/documentation-analysis.md) - Dimension 8 details

**Version**: 1.0 | **Updated**: 2025-01-01 | **Difficulty**: Intermediate
