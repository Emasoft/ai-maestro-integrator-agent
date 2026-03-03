---
name: amia-quality-gates
description: "Quality gate enforcement for PR integration. Use when verifying code through pre-review, review, pre-merge, or post-merge checkpoints. Trigger with /amia-enforce-gates."
version: 1.0.0
license: Apache-2.0
compatibility: Requires familiarity with CI/CD pipelines, code review processes, and GitHub workflows. Designed for the Integrator Agent role enforcing quality standards. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: amia-main
context: fork
user-invocable: false
---

# AMIA Quality Gates

## Overview

Quality gates are **mandatory checkpoints** that code must pass before advancing through the integration pipeline. Each gate defines specific criteria, blocking conditions, and escalation paths.

## Prerequisites

Before using this skill, ensure:
- Repository has CI/CD pipeline configured
- GitHub labels from **amia-label-taxonomy** are applied
- Review checklist from **amia-code-review-patterns** is available
- GitHub CLI (`gh`) is installed and authenticated
- Access to repository permissions for label management
- Understanding of the four-gate pipeline model

## Instructions

1. Identify the current gate by checking PR labels (no gate label = Pre-Review Gate)
2. Execute gate-specific checks (Pre-Review: tests/lints, Review: 8-dimension review, Pre-Merge: CI/conflicts, Post-Merge: main branch health)
3. Apply gate decision label (passed/failed/warning) based on check results
4. If checks pass, advance PR to next gate
5. If checks fail, apply "failed" label and follow escalation path (A, B, C, or D)
6. Document failure reasons in PR comments
7. Notify responsible parties per escalation order

**Step 5: Process Overrides (if applicable)**
- Verify override authority per Override Authority Matrix
- Document override justification in PR
- Apply `gate:override-applied` label
- Proceed with next gate

### Workflow Checklist

Copy this checklist and track your progress:

- [ ] Identify current gate by checking PR labels
- [ ] Execute gate-specific checks for current gate
- [ ] Evaluate check results against gate criteria
- [ ] Apply appropriate gate decision label (passed/failed/warning)
- [ ] If PASSED: advance PR to next gate
- [ ] If FAILED: apply failure label and identify escalation path
- [ ] Document failure reasons in PR comments
- [ ] Notify responsible parties per escalation order
- [ ] If override requested: verify authority per Override Authority Matrix
- [ ] If override approved: document justification and apply override label
- [ ] Update gate status in PR labels
- [ ] Verify next steps are clear to all parties

## Output

When executing quality gates, provide:
- **Gate Status**: Current gate name and pass/fail decision
- **Check Results**: List of all checks performed with outcomes
- **Labels Applied**: All labels added or removed
- **Escalation Actions**: Any notifications sent or escalations triggered
- **Next Steps**: What should happen next in the pipeline

**Example Output Format**:
```
Gate: Pre-Review Gate
Status: FAILED
Checks:
  - Tests: FAILED (3 failing tests in auth module)
  - Linting: PASSED
  - Build: PASSED
  - Description: PASSED

Labels Applied:
  - gate:pre-review-failed
  - gate:flaky-test

Escalation:
  - Commented on PR with test failure details
  - Notified @author

Next Steps:
  - Author must fix failing tests
  - Re-run pre-review gate after fixes
```

## Error Handling

**Common Errors and Solutions**:

1. **CI Pipeline Not Running**
   - Check GitHub Actions are enabled
   - Verify workflow files exist in `.github/workflows/`
   - Ensure branch protection rules allow CI execution

2. **Labels Not Applying**
   - Verify GitHub token has label permissions
   - Check label exists in repository (create from taxonomy if missing)
   - Use `gh pr edit $PR_NUMBER --add-label "label-name"` manually if automation fails

3. **Escalation Notification Failure**
   - Verify notification channels (email, Slack, etc.) are configured
   - Check user handles are correct (@mentions)
   - Fallback to manual notification if automation fails

4. **Gate Stuck in Pending State**
   - Check all required status checks are reporting
   - Verify no infrastructure outages
   - Manually re-trigger CI if needed
   - Document stuck state and escalate to AMOA

5. **Override Authority Unavailable**
   - Follow alternate escalation path
   - Document urgency in PR
   - NEVER bypass security gates
   - Escalate to project maintainer if critical

## Examples

See [references/gate-examples.md](references/gate-examples.md) for complete examples including:
- **Contents:** Example 1: Pre-Review Gate Success, Example 2: Review Gate Failure (Low Confidence), Example 3: Pre-Merge Gate Failure (Merge Conflict), Example 4: Post-Merge Gate Failure (Main Branch Broken), Example 5: Gate Override Application

**Purpose of Quality Gates:**
- Prevent defective code from reaching production
- Ensure consistent quality standards across all contributions
- Provide clear, objective criteria for advancement
- Enable systematic escalation when gates fail

**Key Principle:** Quality gates use **state-based triggers**, not time-based values. Gates advance or block based on conditions being met, not elapsed time.

---

## Gate Types and Pipeline Position

The integration pipeline has four sequential gates. See [references/gate-pipeline.md](references/gate-pipeline.md) for the complete flow diagram.
- **Contents:** Overview, Pipeline Diagram, Gate Transitions, Failure Handling, Parallel Gates, Gate Bypass

## Gate 1: Pre-Review Gate

See [references/pre-review-gate.md](references/pre-review-gate.md) for:
- **Contents:** Purpose, Required Checks, Tests Pass, Linting Pass, Build Success, PR Description Present, Issue Linked, Warning Conditions (Non-Blocking), Gate Pass Procedure, Gate Fail Procedure, Re-Evaluation Triggers, Troubleshooting, Flaky Test Failures, Infrastructure Issues

## Gate 2: Review Gate

See [references/review-gate.md](references/review-gate.md) for:
- Required checks (8 dimensions, 80% confidence)
- Blocking conditions
- Warning conditions
- Gate pass/fail procedures

## Gate 3: Pre-Merge Gate

See [references/pre-merge-gate.md](references/pre-merge-gate.md) for:
- **Contents:** Purpose, Required Checks, CI Pipeline Success, No Merge Conflicts, Valid Approval, Branch Up-to-Date, Warning Conditions (Non-Blocking), Gate Pass Procedure, Gate Fail Procedure, Merge Strategies, Squash Merge (Default), Merge Commit, Rebase Merge, Re-Evaluation Triggers, Troubleshooting, CI Stuck in Pending, Approval Disappeared, Intermittent Merge Conflicts, Fast-Moving Main Branch

## Gate 4: Post-Merge Gate

See [references/post-merge-gate.md](references/post-merge-gate.md) for:
- Required checks (main branch health)
- Blocking conditions
- Issue closure procedures

---

## Escalation Paths

See [references/escalation-paths.md](references/escalation-paths.md) for complete escalation procedures including:
- Escalation Path A: Pre-Review Gate Failure
- Escalation Path B: Review Gate Failure (with Override Authority matrix)
- Escalation Path C: Pre-Merge Gate Failure
- Escalation Path D: Post-Merge Gate Failure (with Revert Authority matrix)
- Actions by failure type for each path

---

## Gate Override Policies

See [references/override-policies.md](references/override-policies.md) for:
- Override Authority Matrix (who can override which gates)
- Override procedure and documentation requirements
- When overrides are allowed vs forbidden (e.g., security gates cannot be overridden)

---

## Complete Label Reference

See [references/label-reference.md](references/label-reference.md) for complete list of:
- Gate status labels (passed/failed/pending for each gate)
- Warning labels (coverage, changelog, large PR, style issues, performance, flaky tests, etc.)
- When each label should be applied

---

## Gate Enforcement Checklist

See [references/gate-checklist.md](references/gate-checklist.md) for a copy-paste checklist covering:
- Pre-Review Gate verification steps
- Review Gate verification steps
- Pre-Merge Gate verification steps
- Post-Merge Gate verification steps

---

## Integration with Other Skills

### Related Skills

- **amia-label-taxonomy** - Complete label definitions
- **amia-code-review-patterns** - Review methodology for Review Gate
- **amia-github-pr-workflow** - PR workflow including gates
- **amia-tdd-enforcement** - TDD requirements for Pre-Review Gate
- **amia-ci-failure-patterns** - CI failure analysis

### Dependency on Label Taxonomy

This skill uses labels defined in **amia-label-taxonomy**. Ensure the label taxonomy is applied to the repository before using quality gates.

---

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for solutions to common issues:
- Gate appears stuck
- False positive gate failure
- Escalation not triggering
- Override needed but no authority available

---

## Design Document Scripts

These scripts manage design documents for quality gate integration:

> **Note:** `amia_design_validate.py` is planned but not yet implemented.

| Script | Purpose | Usage |
|--------|---------|-------|
| `amia_design_create.py` | Create new design documents with proper GUUID | `python scripts/amia_design_create.py --type <TYPE> --title "<TITLE>"` |
| `amia_design_search.py` | Search design documents by UUID, type, or status | `python scripts/amia_design_search.py --type <TYPE> --status <STATUS>` |
| `amia_design_validate.py` | Validate design document frontmatter compliance | `python scripts/amia_design_validate.py --all` | <!-- TODO: Script not yet implemented -->

### Encoding Compliance Scripts

**Script**: `scripts/amia_check_encoding.py` — Checks Python files for missing UTF-8 encoding parameters

For encoding compliance checking, see [encoding-compliance-checker.md](references/encoding-compliance-checker.md):
- When to run the encoding compliance checker
- How to run amia_check_encoding.py on specific files
- How to run amia_check_encoding.py on an entire directory
- What the checker verifies (5 checks)
- How to fix each type of encoding violation
- Integrating with pre-push hooks

### Unicode Enforcement Scripts

**Script**: `../../scripts/amia_unicode_compliance.py` — Full Unicode compliance checker (BOM, line endings, encoding, non-ASCII identifiers)

For Unicode enforcement hook details, see [unicode-enforcement-hook.md](references/unicode-enforcement-hook.md):
- When the Unicode enforcement hook runs
- What the hook checks (4 checks)
- How to fix each type of Unicode violation
- Running the standalone Unicode compliance checker
- Configuring the hook in pre-push scripts

### PR Gate Scripts

These scripts enforce quality gates on pull requests:

| Script | Purpose | Usage |
|--------|---------|-------|
| `amia_github_pr_gate.py` | Run pre-merge quality checks on PRs | `python scripts/amia_github_pr_gate.py --pr <NUMBER>` |
| `amia_github_pr_gate_checks.py` | Individual check implementations for PR gates | (Internal, called by amia_github_pr_gate.py) |
| `amia_github_report.py` | Generate comprehensive GitHub project reports | `python scripts/amia_github_report.py --owner <OWNER> --repo <REPO> --project <NUM>` |
| `amia_github_report_formatters.py` | Format reports in markdown/JSON | (Internal, used by amia_github_report.py) |

### Script Locations

All scripts are located in the **root `scripts/` directory** of the ai-maestro-integrator-agent project (path: `../../scripts/` relative to this skill file, i.e., `ai-maestro-integrator-agent/scripts/`). Do **not** look for scripts inside `skills/amia-quality-gates/scripts/` -- that directory does not exist.

---

## Resources

### Gate Details
- [references/gate-pipeline.md](references/gate-pipeline.md) - Complete pipeline flow diagram
  <!-- TOC: gate-pipeline.md -->
  - Overview
  - Pipeline Diagram
  - Gate Transitions
  <!-- /TOC -->
- [references/pre-review-gate.md](references/pre-review-gate.md) - Pre-Review Gate details
  <!-- TOC: pre-review-gate.md -->
  - Purpose
  - Required Checks
  - Tests Pass
  <!-- /TOC -->
- [references/review-gate.md](references/review-gate.md) - Review Gate details
- [references/pre-merge-gate.md](references/pre-merge-gate.md) - Pre-Merge Gate details
  <!-- TOC: pre-merge-gate.md -->
  - Purpose
  - Required Checks
  - CI Pipeline Success
  <!-- /TOC -->
- [references/post-merge-gate.md](references/post-merge-gate.md) - Post-Merge Gate details
  <!-- TOC: post-merge-gate.md -->
  - Purpose
  - Required Checks
  - Main Branch Build Success
  <!-- /TOC -->

### Code Quality Checks
- [references/encoding-compliance-checker.md](references/encoding-compliance-checker.md) - UTF-8 encoding compliance checker
  <!-- TOC: encoding-compliance-checker.md -->
  - When to run the encoding compliance checker
  - How to run amia_check_encoding.py on specific files
  - How to run amia_check_encoding.py on an entire directory
  <!-- /TOC -->
- [references/unicode-enforcement-hook.md](references/unicode-enforcement-hook.md) - Unicode enforcement hook (BOM, line endings, encoding, non-ASCII identifiers)
  <!-- TOC: unicode-enforcement-hook.md -->
  - When the Unicode enforcement hook runs
  - What the hook checks (4 checks)
  - How to fix each type of Unicode violation
  <!-- /TOC -->

### Procedures and Examples
- [references/gate-examples.md](references/gate-examples.md) - Practical examples for all gates
  <!-- TOC: gate-examples.md -->
  - Example 1: Pre-Review Gate Success
  - Example 2: Review Gate Failure (Low Confidence)
  - Example 3: Pre-Merge Gate Failure (Merge Conflict)
  <!-- /TOC -->
- [references/gate-checklist.md](references/gate-checklist.md) - Copy-paste enforcement checklist
  <!-- TOC: gate-checklist.md -->
  - Pre-Review Gate
  - Review Gate
  - Pre-Merge Gate
  <!-- /TOC -->
- [references/escalation-paths.md](references/escalation-paths.md) - Escalation paths A, B, C, D
  <!-- TOC: escalation-paths.md -->
  - Escalation Path A: Pre-Review Gate Failure
  - Escalation Path B: Review Gate Failure
  - Escalation Path C: Pre-Merge Gate Failure
  <!-- /TOC -->
- [references/escalation-procedures.md](references/escalation-procedures.md) - Detailed escalation procedures
  <!-- TOC: escalation-procedures.md -->
  - Overview
  - Escalation Path A: Pre-Review Gate Failure
  - Level 1: Author Notification
  <!-- /TOC -->
- [references/override-policies.md](references/override-policies.md) - Override authority and procedures
  <!-- TOC: override-policies.md -->
  - Overrides Are Exceptions
  - Override Authority Matrix
  - Override Procedure
  <!-- /TOC -->
- [references/override-examples.md](references/override-examples.md) - Override documentation examples
  <!-- TOC: override-examples.md -->
  - Overview
  - Example 1: Pre-Review Gate Override (Urgent Hotfix)
  - Example 2: Review Gate Override (Style Issues)
  <!-- /TOC -->

### Reference Materials
- [references/gate-decision-flowchart.md](references/gate-decision-flowchart.md) - Visual decision flowchart
  <!-- TOC: gate-decision-flowchart.md -->
  - Visual Decision Tree
  - Pre-Review Gate Decision
  - Review Gate Decision
  <!-- /TOC -->
- [references/label-reference.md](references/label-reference.md) - Complete label list
  <!-- TOC: label-reference.md -->
  - Gate Status Labels
  - Warning Labels
  <!-- /TOC -->
- [references/troubleshooting.md](references/troubleshooting.md) - Common issues and solutions
  <!-- TOC: troubleshooting.md -->
  - Gate Appears Stuck
  - False Positive Gate Failure
  - Escalation Not Triggering
  <!-- /TOC -->
- [references/rule-14-enforcement.md](references/rule-14-enforcement.md) - RULE 14 canonical text and enforcement procedures
  <!-- TOC: rule-14-enforcement.md -->
  - 1 When handling user requirements in any workflow
  - 2 When detecting potential requirement deviations
  - 3 When a technical constraint conflicts with a requirement
  <!-- /TOC -->
- [references/pr-evaluation.md](references/pr-evaluation.md) - PR evaluation procedures from amia-pr-evaluator
  <!-- TOC: pr-evaluation.md -->
  - 0 When to evaluate a PR for merge readiness
  - 0 Evaluation gates that must pass before approval
  - 1 Gate 0: Requirement Compliance (verifying PR implements what user requested)
  <!-- /TOC -->
- [references/integration-verification.md](references/integration-verification.md) - Integration verification from amia-integration-verifier
  <!-- TOC: integration-verification.md -->
  - Verifying Component Integration Readiness
  - 1 Environment baseline verification
  - 2 Service connectivity testing
  <!-- /TOC -->

---

**Version**: 1.0.0
**Last Updated**: 2025-02-04
**Skill Type**: Integration Process
**Required Knowledge**: CI/CD, code review, GitHub workflows
