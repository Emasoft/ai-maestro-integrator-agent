---
name: amia-release-management
description: "Software release management and coordination. Use when creating releases, bumping versions, or rolling back deployments. Trigger with release tasks or /amia-create-release. Loaded by ai-maestro-integrator-agent-main-agent."
license: MIT
compatibility: Requires understanding of semantic versioning, git tagging, and CI/CD pipelines. Designed for release coordinators managing patch, minor, and major releases. Requires AI Maestro installed.
tags: "release, versioning, changelog, tagging, rollback, ci-cd"
metadata:
  author: Emasoft
  version: 1.0.0
  category: release-management
agent: ai-maestro-integrator-agent-main-agent
context: fork
background: false
user-invocable: false
---

# Release Management Skill

## Overview

Coordinates software releases: version bumping, changelog, tagging, CI/CD, and rollback.

## Prerequisites

- GitHub CLI (`gh`) authenticated with release permissions
- Python 3.8+ and CI/CD pipeline configured
- Semantic versioning followed in the project

## Instructions

1. **Receive request** with target type (patch/minor/major)
2. **Determine version** using semver rules and **verify readiness** (tests pass, no critical bugs)
3. **Generate changelog** from commits and **bump version** in all required files
4. **Obtain the Tier-2 MANAGER approval** — entering the release pipeline is NON-EXEMPT;
   confirm it is recorded in the approving TRDD's `## Approval log`
5. **Run the project-type pipeline** (library / app / service / Claude-Code-plugin —
   see detailed-guide), passing `--approval-trdd <TRDD>` to the release script
6. **Verify deployment**; INTEGRATOR flips the column to published/live only after
   validating the artifact satisfies the TRDD; rollback if failed; report completion

### Checklist

Copy this checklist and track your progress:

- [ ] Obtain + record the **Tier-2 MANAGER approval** (the `## Approval log` entry) — team membership is NOT approval
- [ ] Receive release request with target type
- [ ] Determine version and verify readiness
- [ ] Generate changelog from commit history
- [ ] Bump version and create annotated git tag
- [ ] Select the **project-type pipeline** (CPV `publish.py` is plugins-only) and run it, passing `--approval-trdd`
- [ ] Verify deployment; INTEGRATOR validates the artifact, then flips the column
- [ ] Rollback if needed (`--execute` is also Tier-2 gated); report completion

## The async approval model (R41) — `min-approval-requirement:` and `mandate:`

The release column transitions this skill drives (`publish → published`,
`deploy → live`) are governed moves on the TRDD that carries them. Every TRDD
declares its approval floor as `min-approval-requirement:`
(`none | orchestrator | chief-of-staff | manager | user`; an ABSENT field means
`none`). Authorization arrives in exactly one of two shapes:

- **Mandate** — the card sits in `design/tasks/` with `mandate: true`: it was
  born approved by the authority at or above its floor. Execute it; you may
  flag a genuine problem and pause, but you may not refuse it. R41: never
  approve a card you authored.
- **Proposal** — the card sits in `design/proposals/` with
  `column: proposal`: it is WAITING. Do not act on it and do not transition it;
  the approving authority sets `column: planned` and records the decision in
  the `## Approval log` (asynchronous — keep working meanwhile).

Before any governed transition, self-classify: if the card's floor is higher
than the authorization your dispatch carries, stop and route the request
upward (INTEGRATOR → CHIEF-OF-STAFF). Authoring an approval that never happened
is the failure this model exists to prevent — an approval is CHECKABLE, not
merely readable (verify the `## Approval log` entry matches the dispatch).

## Output

| Output Type | Format | Contents |
|-------------|--------|----------|
| Verification Report | Markdown | Pre-release checklist results, blocking issues |
| Changelog | Markdown | Categorized changes since last release |
| Release Notes | Markdown | User-facing summary, migration notes |
| Version Bump | JSON | Old/new version, files modified |
| Release Tag | Git tag | Annotated tag with version and notes |
| Rollback Report | Markdown | Steps taken, verification of success |

> **Output discipline:** All scripts support `--output-file <path>`.

## Error Handling

Script failures return non-zero exit codes with details on stderr.

## Examples

### Patch Release

```bash
python scripts/amia_release_verify.py --repo owner/repo --version 1.2.4
python scripts/amia_changelog_generate.py --repo owner/repo --from v1.2.3 --to HEAD
python scripts/amia_version_bump.py --repo owner/repo --type patch
# Tier-2 gate: amia_create_release.py exits 7 without a recorded MANAGER approval.
python scripts/amia_create_release.py --repo owner/repo --version 1.2.4 --notes release_notes.md \
    --approval-trdd design/tasks/TRDD-<id>-...md
```

## Resources

Full reference: [detailed-guide](references/detailed-guide.md):
  - Decision Tree
  - Semantic Versioning Quick Reference
  - State-Based Verification Model
  - Escalation Order
  - Scripts Reference
  - Critical Rules
  - Release Pipeline Design by Project Type
  - Error Handling
  - AI Maestro Communication
  - Examples
    - Standard Patch Release
    - Rollback After Failed Release
  - Reference Documentation Details
    - Release Management Responsibilities
    - Pre-Release Verification
    - Post-Release Verification
    - Rollback Procedures
    - CI/CD Integration
  - Full Reference Document Index
