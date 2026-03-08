---
name: amia-release-management
description: "Software release management and coordination. Use when creating releases, bumping versions, or rolling back deployments. Trigger with release tasks or /amia-create-release."
license: Apache-2.0
compatibility: Requires understanding of semantic versioning, git tagging, and CI/CD pipelines. Designed for release coordinators managing patch, minor, and major releases. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
  category: release-management
  tags: "release, versioning, changelog, tagging, rollback, ci-cd"
agent: amia-main
context: fork
user-invocable: false
---

# Release Management Skill

## Overview

Coordinates software releases across patch, minor, and major version changes. Handles version bumping, changelog generation, release tagging, CI/CD triggering, and rollback procedures.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Repository with proper release permissions
- Python 3.8+ for helper scripts
- Semantic versioning followed in the project
- CI/CD pipeline configured and operational

## Instructions

1. **Receive release request** with target type (patch/minor/major)
2. **Determine version** using semver rules (PATCH: bug fixes, MINOR: features, MAJOR: breaking)
3. **Verify readiness** via pre-release checklist (all tests pass, no critical bugs)
4. **Generate changelog** from commit history since last release
5. **Bump version** in all required files and create annotated git tag
6. **Trigger CI/CD** release pipeline and verify deployment
7. **Report completion** to requesting agent; rollback if deployment fails

### Checklist

Copy this checklist and track your progress:

- [ ] Receive release request with target type
- [ ] Determine version number (semver rules)
- [ ] Verify release readiness (tests, bugs, docs)
- [ ] Generate changelog from commit history
- [ ] Create release notes with highlights
- [ ] Bump version in all required files
- [ ] Create annotated git tag
- [ ] Trigger CI/CD release pipeline
- [ ] Verify post-release deployment
- [ ] Report completion to requesting agent

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

## Reference Documents

**Process & Definitions:**

- `references/release-types.md` — Patch/minor/major/pre-release definitions
- `references/semantic-versioning.md` — Version format and rules
- `references/release-process.md` — Bumping, changelog, notes, tagging
- `references/release-workflow-chain.md` — Two-workflow automation

**Verification:**

- `references/pre-release-verification.md` — Quality gates checklist
- `references/post-release-verification.md` — Deployment smoke testing

**Operations:**

- `references/rollback-procedures.md` — Rollback procedures
- `references/cicd-integration.md` — Pipeline automation
- `references/release-responsibilities.md` — Roles and RACI matrix
- `references/troubleshooting-tag-branch-collision.md` — Tag-branch collisions

**Operational Procedures:**

- `references/op-determine-version.md` — Version determination
- `references/op-bump-version.md` — Version bump
- `references/op-generate-changelog.md` — Changelog generation
- `references/op-create-release-tag.md` — Release tag creation
- `references/op-verify-release-readiness.md` — Readiness verification
- `references/op-validate-changelog-gate.md` — Changelog gate
- `references/op-validate-release-tags.md` — Tag validation
- `references/op-execute-rollback.md` — Rollback execution
- `references/op-escalate-release-blocker.md` — Blocker escalation
- `references/op-update-readme-badges.md` — Badge updates
- `references/git-cliff-integration.md` — Git-cliff integration

**Detailed Guide:**

- `references/detailed-guide.md` — Decision trees, scripts, error handling, examples

## Error Handling

Script failures return non-zero exit codes. Check stderr for details. See `references/detailed-guide.md` for common error scenarios.

## Examples

### Patch Release

```bash
python scripts/amia_release_verify.py --repo owner/repo --version 1.2.4
python scripts/amia_changelog_generate.py --repo owner/repo --from v1.2.3 --to HEAD
python scripts/amia_version_bump.py --repo owner/repo --type patch
python scripts/amia_create_release.py --repo owner/repo --version 1.2.4 --notes release_notes.md
```

## Resources

See `references/` directory for all reference documents.
