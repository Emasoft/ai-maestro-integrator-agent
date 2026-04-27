---
name: amia-release-management
description: "Software release management and coordination. Use when creating releases, bumping versions, or rolling back deployments. Trigger with release tasks or /amia-create-release. Loaded by ai-maestro-integrator-agent-main-agent."
license: Apache-2.0
compatibility: Requires understanding of semantic versioning, git tagging, and CI/CD pipelines. Designed for release coordinators managing patch, minor, and major releases. Requires AI Maestro installed.
tags: "release, versioning, changelog, tagging, rollback, ci-cd"
metadata:
  author: Emasoft
  version: 1.0.0
  category: release-management
agent: amia-main
context: fork
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
4. **Create tag and trigger CI/CD** release pipeline
5. **Verify deployment**; rollback if failed; report completion

### Checklist

Copy this checklist and track your progress:

- [ ] Verify governance authorization via `team-governance` skill
- [ ] Receive release request with target type
- [ ] Determine version and verify readiness
- [ ] Generate changelog from commit history
- [ ] Bump version and create annotated git tag
- [ ] Trigger CI/CD and verify deployment
- [ ] Rollback if needed; report completion

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
python scripts/amia_create_release.py --repo owner/repo --version 1.2.4 --notes release_notes.md
```

## Resources

Full reference: [detailed-guide](references/detailed-guide.md):
  - Decision Tree
  - Semantic Versioning Quick Reference
  - State-Based Verification Model
  - Escalation Order
  - Scripts Reference
  - Critical Rules
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
