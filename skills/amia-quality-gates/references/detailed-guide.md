# AMIA Quality Gates -- Detailed Guide

> **MULTI-REPO RULE:** All `gh` commands MUST include `--repo "$OWNER/$REPO"` since the integrator works across multiple repos.

## Contents

- [Purpose and Principles](#purpose-and-principles)
- [Gate Types and Pipeline Position](#gate-types-and-pipeline-position)
- [Error Handling](#error-handling)
- [Output Discipline](#output-discipline)
- [Design Document Scripts](#design-document-scripts)
- [Encoding Compliance Scripts](#encoding-compliance-scripts)
- [Unicode Enforcement Scripts](#unicode-enforcement-scripts)
- [PR Gate Scripts](#pr-gate-scripts)
- [Script Locations](#script-locations)
- [Integration with Other Skills](#integration-with-other-skills)

---

## Purpose and Principles

Quality gates serve to:

- Prevent defective code from reaching production
- Ensure consistent quality standards across all contributions
- Provide clear, objective criteria for advancement
- Enable systematic escalation when gates fail

**Key Principle:** Quality gates use **state-based triggers**, not time-based values. Gates advance or block based on conditions being met, not elapsed time.

---

## Gate Types and Pipeline Position

The integration pipeline has four sequential gates:

1. **Pre-Review Gate** -- Automated checks (tests, linting, build, PR description, issue linked). See `pre-review-gate.md`.
2. **Review Gate** -- 8-dimension code review with 80% confidence threshold. See `review-gate.md`.
3. **Pre-Merge Gate** -- CI pipeline success, no merge conflicts, valid approval, branch up-to-date. See `pre-merge-gate.md`.
4. **Post-Merge Gate** -- Main branch health verification and issue closure. See `post-merge-gate.md`.

See `gate-pipeline.md` for the complete flow diagram, gate transitions, failure handling, parallel gates, and gate bypass rules.

---

## Error Handling

### CI Pipeline Not Running

- Check GitHub Actions are enabled
- Verify workflow files exist in `.github/workflows/`
- Ensure branch protection rules allow CI execution

### Labels Not Applying

- Verify GitHub token has label permissions
- Check label exists in repository (create from taxonomy if missing)
- Use `gh pr edit $PR_NUMBER --add-label "label-name"` manually if automation fails

### Escalation Notification Failure

- Verify notification channels (email, Slack, etc.) are configured
- Check user handles are correct (@mentions)
- Fallback to manual notification if automation fails

### Gate Stuck in Pending State

- Check all required status checks are reporting
- Verify no infrastructure outages
- Manually re-trigger CI if needed
- Document stuck state and escalate to AMOA

### Override Authority Unavailable

- Follow alternate escalation path
- Document urgency in PR
- NEVER bypass security gates
- Escalate to project maintainer if critical

---

## Output Discipline

All scripts support the `--output-file <path>` flag:

- **With flag**: Full JSON written to file; concise summary printed to stderr
- **Without flag**: Full JSON printed to stdout (backward compatible)

When invoking from agents or automated workflows, always pass `--output-file` to minimize token consumption.

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

---

## Design Document Scripts

These scripts manage design documents for quality gate integration:

| Script | Purpose | Usage |
|--------|---------|-------|
| `amia_design_create.py` | Create new design documents with proper GUUID | `python scripts/amia_design_create.py --type <TYPE> --title "<TITLE>"` |
| `amia_design_search.py` | Search design documents by UUID, type, or status | `python scripts/amia_design_search.py --type <TYPE> --status <STATUS>` |
| `amia_design_validate.py` | Validate design document frontmatter compliance | `python scripts/amia_design_validate.py --all` |

---

## Encoding Compliance Scripts

**Script**: `scripts/amia_check_encoding.py` -- Checks Python files for missing UTF-8 encoding parameters.

When to run:

- Before pushing code changes
- As part of pre-push hooks
- When reviewing PRs that modify Python files

What the checker verifies (5 checks):

1. UTF-8 encoding declaration present
2. File is valid UTF-8
3. No BOM markers
4. Consistent line endings
5. Encoding parameter in file I/O calls

See `encoding-compliance-checker.md` for full details on running and fixing violations.

---

## Unicode Enforcement Scripts

**Script**: `../../scripts/amia_unicode_compliance.py` -- Full Unicode compliance checker (BOM, line endings, encoding, non-ASCII identifiers).

What the hook checks (4 checks):

1. BOM markers
2. Line ending consistency
3. Encoding declarations
4. Non-ASCII identifiers

See `unicode-enforcement-hook.md` for configuration and violation fixes.

---

## PR Gate Scripts

These scripts enforce quality gates on pull requests:

| Script | Purpose | Usage |
|--------|---------|-------|
| `amia_github_pr_gate.py` | Run pre-merge quality checks on PRs | `python scripts/amia_github_pr_gate.py --pr <NUMBER>` |
| `amia_github_pr_gate_checks.py` | Individual check implementations for PR gates | (Internal, called by amia_github_pr_gate.py) |
| `amia_github_report.py` | Generate comprehensive GitHub project reports | `python scripts/amia_github_report.py --owner <OWNER> --repo <REPO> --project <NUM>` |
| `amia_github_report_formatters.py` | Format reports in markdown/JSON | (Internal, used by amia_github_report.py) |

---

## Script Locations

All scripts are located in the **root `scripts/` directory** of the ai-maestro-integrator-agent project (path: `../../scripts/` relative to this skill file, i.e., `ai-maestro-integrator-agent/scripts/`). Do **not** look for scripts inside `skills/amia-quality-gates/scripts/` -- that directory does not exist.

---

## Integration with Other Skills

### Dependency on Label Taxonomy

This skill uses labels defined in **amia-label-taxonomy**. Ensure the label taxonomy is applied to the repository before using quality gates.

### Related Skills

| Skill | Relationship |
|-------|-------------|
| **amia-label-taxonomy** | Complete label definitions used by gates |
| **amia-code-review-patterns** | Review methodology for Review Gate |
| **amia-github-pr-workflow** | PR workflow including gates |
| **amia-tdd-enforcement** | TDD requirements for Pre-Review Gate |
| **amia-ci-failure-patterns** | CI failure analysis |

---

## Content Moved from SKILL.md (Trim)

### Full Reference Documents List

**Gate Details:**

- `references/gate-pipeline.md` -- Pipeline flow diagram and transitions
- `references/pre-review-gate.md` -- Gate 1: tests, lints, build, description
- `references/review-gate.md` -- Gate 2: 8-dimension review, 80% confidence
- `references/pre-merge-gate.md` -- Gate 3: CI, conflicts, approval, merge strategies
- `references/post-merge-gate.md` -- Gate 4: main branch health, issue closure

**Escalation and Overrides:**

- `references/escalation-paths.md` -- Escalation paths A, B, C, D
- `references/escalation-procedures.md` -- Detailed procedures per level
- `references/override-policies.md` -- Override authority matrix
- `references/override-examples.md` -- Override examples

**Code Quality Checks:**

- `references/encoding-compliance-checker.md` -- UTF-8 encoding
- `references/unicode-enforcement-hook.md` -- BOM, line endings, non-ASCII

**Procedures and Examples:**

- `references/gate-examples.md` -- Examples for all gates
- `references/gate-checklist.md` -- Enforcement checklist
- `references/gate-decision-flowchart.md` -- Decision flowchart
- `references/label-reference.md` -- Gate and warning label list
- `references/troubleshooting.md` -- Common issues and solutions

**Verification and Evaluation:**

- `references/rule-14-enforcement.md` -- RULE 14 enforcement
- `references/pr-evaluation.md` -- PR evaluation
- `references/integration-verification.md` -- Integration verification

### Full Prerequisites

- Repository has CI/CD pipeline configured
- GitHub labels from **amia-label-taxonomy** applied
- Review checklist from **amia-code-review-patterns** available
- GitHub CLI (`gh`) installed and authenticated
- Understanding of the four-gate pipeline model

### Full Instructions

1. Identify the current gate by checking PR labels (no gate label = Pre-Review)
2. Execute gate-specific checks (Pre-Review: tests/lints, Review: 8-dimension review, Pre-Merge: CI/conflicts, Post-Merge: main branch health)
3. Apply gate decision label (passed/failed/warning) based on results
4. If checks pass, advance PR to next gate
5. If checks fail, apply "failed" label and follow escalation path (A, B, C, or D)
6. Document failure reasons in PR comments and notify responsible parties
7. For overrides: verify authority per Override Matrix, document justification, apply `gate:override-applied` label

### Full Checklist

- [ ] Identify current gate by checking PR labels
- [ ] Execute gate-specific checks for current gate
- [ ] Evaluate results against gate criteria
- [ ] Apply appropriate decision label (passed/failed/warning)
- [ ] If PASSED: advance to next gate
- [ ] If FAILED: apply failure label, identify escalation path
- [ ] Document failure reasons in PR comments
- [ ] Notify responsible parties per escalation order
- [ ] If override requested: verify authority and document justification
- [ ] Verify next steps are clear to all parties
