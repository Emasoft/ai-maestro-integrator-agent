---
name: amia-release-management
description: "Software release management and coordination. Use when creating releases, bumping versions, or rolling back deployments. Trigger with release tasks or /amia-create-release."
license: Apache-2.0
compatibility: Requires understanding of semantic versioning, git tagging, and CI/CD pipelines. Designed for release coordinators managing patch, minor, and major releases. Requires AI Maestro installed.
triggers:
  - Create a new release
  - Bump version number
  - Generate changelog
  - Create release notes
  - Tag a release
  - Verify release readiness
  - Rollback a release
  - Prepare release candidate
metadata:
  author: Emasoft
  version: 1.0.0
  category: release-management
  tags: "release, versioning, changelog, tagging, rollback, ci-cd"
agent: amia-main
context: fork
workflow-instruction: "support"
procedure: "support-skill"
user-invocable: false
---

# Release Management Skill

## Overview

This skill defines the **release management procedures** for coordinating software releases across patch, minor, and major version changes.

Release management is the final gate before code reaches production. It requires systematic verification, proper versioning, comprehensive documentation, and reliable rollback procedures.

## Prerequisites

Before using this skill, ensure:
1. GitHub CLI (`gh`) installed and authenticated
2. Repository has proper access permissions for releases
3. Python 3.8+ for running helper scripts
4. Semantic versioning is followed in the project
5. CI/CD pipeline is configured and operational

## Output

| Output Type | Format | Contents |
|-------------|--------|----------|
| Release Verification Report | Markdown | Pre-release checklist results, pass/fail status, blocking issues |
| Changelog | Markdown | Categorized list of changes since last release |
| Release Notes | Markdown | User-facing summary of changes, highlights, migration notes |
| Version Bump Confirmation | JSON | Old version, new version, files modified |
| Release Tag | Git tag | Annotated tag with version and release notes summary |
| Rollback Report | Markdown | Rollback steps taken, verification of rollback success |

## Instructions

1. **Receive release request** - From AMOA or user, including target release type
2. **Determine version number** - Based on change scope (see Section 2: Release Types)
3. **Verify release readiness** - Run pre-release verification checklist (see Section 5)
4. **Generate changelog** - Compile changes since last release (see Section 4.2)
5. **Create release notes** - Write user-facing summary (see Section 4.3)
6. **Bump version** - Update version in all required files (see Section 4.1)
7. **Create release tag** - Tag commit with version and annotation (see Section 4.4)
8. **Trigger CI/CD** - Run release pipeline (see Section 8)
9. **Verify post-release** - Confirm release deployed correctly (see Section 6)
10. **Report completion** - Notify requesting agent of release status

### Checklist

Copy this checklist and track your progress:

- [ ] Receive release request with target type (patch/minor/major)
- [ ] Determine version number based on semantic versioning rules
- [ ] Verify release readiness (pre-release checklist)
  - [ ] All tests pass
  - [ ] No critical bugs open
  - [ ] Documentation updated
  - [ ] Breaking changes documented (if major)
- [ ] Generate changelog from commit history
- [ ] Create release notes with highlights and migration notes
- [ ] Bump version in all required files
- [ ] Create annotated git tag
- [ ] Trigger CI/CD release pipeline
- [ ] Verify post-release deployment
- [ ] Report completion to requesting agent

---

## Quick Reference: Decision Tree

```
Release Request Received
|
+--> What type of release?
|    +--> PATCH (bug fixes only)
|    |    +--> Version: X.Y.Z+1
|    |    +--> No breaking changes allowed
|    |    +--> Minimal changelog required
|    |
|    +--> MINOR (new features, backward compatible)
|    |    +--> Version: X.Y+1.0
|    |    +--> New features documented
|    |    +--> Deprecation notices if applicable
|    |
|    +--> MAJOR (breaking changes)
|         +--> Version: X+1.0.0
|         +--> Migration guide required
|         +--> Breaking changes documented
|         +--> User notification required
|
+--> Pre-release verification passes?
|    +--> YES --> Proceed to release
|    +--> NO --> Identify blocking issues
|              +--> Critical issues --> STOP, escalate to user
|              +--> Non-critical --> Document and proceed (with approval)
|
+--> Release deployed successfully?
     +--> YES --> Create release notes, notify stakeholders
     +--> NO --> Initiate rollback (see Section 7)
```

---

## Reference Documentation

Complete detailed procedures are in reference files:

### 1. Release Management Responsibilities
[references/release-responsibilities.md](references/release-responsibilities.md) - What coordinators must/must not do

### 2. Release Types
[references/release-types.md](references/release-types.md) - Patch, minor, major, pre-release definitions

### 3. Semantic Versioning Rules
[references/semantic-versioning.md](references/semantic-versioning.md) - Version format and incrementing rules

### 4. Release Process
[references/release-process.md](references/release-process.md) - Version bumping, changelog, release notes, tagging

### 5. Pre-Release Verification
[references/pre-release-verification.md](references/pre-release-verification.md) - Quality gates and verification checklist

### 6. Post-Release Verification
[references/post-release-verification.md](references/post-release-verification.md) - Deployment verification and smoke testing

### 7. Rollback Procedures
[references/rollback-procedures.md](references/rollback-procedures.md) - When and how to rollback releases

### 8. CI/CD Integration
[references/cicd-integration.md](references/cicd-integration.md) - Pipeline configuration and automation

### 9. Tag-Branch Collision Troubleshooting

For tag-branch collision troubleshooting, see [troubleshooting-tag-branch-collision.md](references/troubleshooting-tag-branch-collision.md):
- What is a tag-branch name collision
- How collisions cause HTTP 300 errors
- How to detect collisions using amia_cleanup_version_branches.sh
- How to resolve collisions safely
- Best practices to prevent future collisions

**Script**: `scripts/amia_cleanup_version_branches.sh` — Detects and reports version tag/branch name collisions (safe, print-only)

---

## Semantic Versioning Quick Reference

| Change Type | Version Increment | Example |
|-------------|-------------------|---------|
| Bug fix (no API change) | PATCH | 1.2.3 -> 1.2.4 |
| New feature (backward compatible) | MINOR | 1.2.3 -> 1.3.0 |
| Breaking change | MAJOR | 1.2.3 -> 2.0.0 |
| Pre-release alpha | PATCH + suffix | 1.2.3 -> 1.2.4-alpha.1 |
| Pre-release beta | PATCH + suffix | 1.2.4-alpha.1 -> 1.2.4-beta.1 |
| Release candidate | PATCH + suffix | 1.2.4-beta.1 -> 1.2.4-rc.1 |

---

## State-Based Verification Model

### Release Readiness States

Instead of time-based checks, use state-based transitions:

```
UNVERIFIED
    |
    v
VERIFICATION_IN_PROGRESS
    |
    +--> All gates pass --> READY_FOR_RELEASE
    |
    +--> Any gate fails --> BLOCKED
                             |
                             v
                        Identify blocker type
                             |
                             +--> Critical --> ESCALATE_TO_USER
                             +--> Non-critical --> DOCUMENT_AND_AWAIT_APPROVAL
```

### Escalation Order

When verification fails, follow this escalation order:

| Order | Condition | Action |
|-------|-----------|--------|
| 1 | Test failure | Delegate fix to implementation agent, await resolution |
| 2 | Critical bug open | Escalate to user for release decision |
| 3 | Missing documentation | Delegate documentation task, await completion |
| 4 | Dependency vulnerability | Escalate to user with severity assessment |
| 5 | CI/CD failure | Investigate cause, escalate if infrastructure issue |

---

## Scripts Reference

> **Note:** The following scripts are planned but not yet implemented: `amia_release_verify.py`, `amia_changelog_generate.py`, `amia_version_bump.py`, `amia_create_release.py`, `amia_rollback.py`. Only `amia_cleanup_version_branches.sh` is currently available.

### amia_release_verify.py
**Location**: `scripts/amia_release_verify.py`
**Purpose**: Run pre-release verification checklist
**When to use**: Before any release to verify readiness
**Output**: JSON with pass/fail status for each gate

```bash
# Usage
python scripts/amia_release_verify.py --repo owner/repo --version 1.2.3

# Output format
{
  "version": "1.2.3",
  "ready": true|false,
  "gates": {
    "tests_pass": {"status": "pass", "details": "142 tests passed"},
    "no_critical_bugs": {"status": "pass", "details": "0 critical issues"},
    "docs_updated": {"status": "pass", "details": "CHANGELOG.md updated"},
    "dependencies_clean": {"status": "pass", "details": "No vulnerabilities"}
  },
  "blockers": []
}
```
<!-- TODO: Script not yet implemented -->

### amia_changelog_generate.py
**Location**: `scripts/amia_changelog_generate.py`
**Purpose**: Generate changelog from commit history
**When to use**: Before creating release notes
**Output**: Markdown changelog content

```bash
# Usage
python scripts/amia_changelog_generate.py --repo owner/repo --from v1.2.2 --to HEAD

# Output: Markdown formatted changelog
```
<!-- TODO: Script not yet implemented -->

### amia_version_bump.py
**Location**: `scripts/amia_version_bump.py`
**Purpose**: Bump version in all required files
**When to use**: After determining new version number
**Output**: JSON with files modified

```bash
# Usage
python scripts/amia_version_bump.py --repo owner/repo --type patch|minor|major

# Output format
{
  "old_version": "1.2.2",
  "new_version": "1.2.3",
  "files_modified": ["package.json", "pyproject.toml", "VERSION"]
}
```
<!-- TODO: Script not yet implemented -->

### amia_create_release.py
**Location**: `scripts/amia_create_release.py`
**Purpose**: Create GitHub release with tag and notes
**When to use**: After all verification passes
**Output**: Release URL

```bash
# Usage
python scripts/amia_create_release.py --repo owner/repo --version 1.2.3 --notes release_notes.md

# Output format
{
  "release_url": "https://github.com/owner/repo/releases/tag/v1.2.3",
  "tag": "v1.2.3",
  "status": "published"
}
```
<!-- TODO: Script not yet implemented -->

### amia_rollback.py
**Location**: `scripts/amia_rollback.py`
**Purpose**: Execute rollback to previous version
**When to use**: When post-release verification fails
**Output**: Rollback status report

```bash
# Usage
python scripts/amia_rollback.py --repo owner/repo --from v1.2.3 --to v1.2.2 --reason "Critical bug"

# Output format
{
  "rolled_back_from": "v1.2.3",
  "rolled_back_to": "v1.2.2",
  "status": "success",
  "actions_taken": [
    "Deprecated npm package 1.2.3",
    "Deleted git tag v1.2.3",
    "Created rollback issue #456"
  ]
}
```
<!-- TODO: Script not yet implemented -->

### amia_cleanup_version_branches.sh
**Location**: `scripts/amia_cleanup_version_branches.sh`
**Purpose**: Detect and report version tag/branch name collisions
**When to use**: When HTTP 300 errors occur on release downloads, or as a periodic maintenance check
**Output**: Colored terminal output listing collisions and safe deletion commands (print-only, does not auto-delete)

```bash
# Usage
bash scripts/amia_cleanup_version_branches.sh
```

---

## Critical Rules Summary

### Rule 1: Never Release Without Approval
The release coordinator must NEVER publish a release without explicit user approval. Always present verification results and await decision.

### Rule 2: Verify Before and After
Always run pre-release verification before starting release process. Always run post-release verification after deployment completes.

### Rule 3: Document Everything
Every release must have:
- Updated changelog
- Release notes
- Version bump in all files
- Annotated git tag

### Rule 4: Be Ready to Rollback
Always have a rollback plan before releasing. Know exactly how to revert if issues arise.

### Rule 5: Follow Semantic Versioning
Version numbers communicate meaning. Never use incorrect version increments.

---

## Examples

### Example 1: Standard Patch Release

```bash
# 1. Verify release readiness
python scripts/amia_release_verify.py --repo owner/repo --version 1.2.4

# 2. Generate changelog
python scripts/amia_changelog_generate.py --repo owner/repo --from v1.2.3 --to HEAD

# 3. Bump version
python scripts/amia_version_bump.py --repo owner/repo --type patch

# 4. Create release (after user approval)
python scripts/amia_create_release.py --repo owner/repo --version 1.2.4 --notes release_notes.md
```

### Example 2: Major Release with Breaking Changes

```bash
# 1. Verify release readiness (includes migration guide check)
python scripts/amia_release_verify.py --repo owner/repo --version 2.0.0 --type major

# 2. Generate comprehensive changelog
python scripts/amia_changelog_generate.py --repo owner/repo --from v1.9.0 --to HEAD --include-breaking

# 3. Bump version
python scripts/amia_version_bump.py --repo owner/repo --type major

# 4. Create release with migration notes
python scripts/amia_create_release.py --repo owner/repo --version 2.0.0 --notes release_notes.md --prerelease false
```

### Example 3: Rollback After Failed Release

```bash
# 1. Execute rollback
python scripts/amia_rollback.py --repo owner/repo --from v1.2.4 --to v1.2.3 --reason "Critical regression in API"

# 2. Verify rollback success
python scripts/amia_release_verify.py --repo owner/repo --version 1.2.3 --mode verify-deployed
```

---

## Error Handling

### Issue: Pre-release verification fails
**Cause**: One or more quality gates not passing
**Solution**: Identify failing gates from verification report, delegate fixes to appropriate agent, await resolution before proceeding

### Issue: Version bump conflicts
**Cause**: Version already bumped in another branch or manual edit
**Solution**: Check current version across all files, resolve conflicts, ensure consistency before proceeding

### Issue: Tag already exists
**Cause**: Tag was created previously (possibly from failed release)
**Solution**: Verify tag points to correct commit. If incorrect, delete tag and recreate. If correct, skip tag creation.

### Issue: CI/CD pipeline fails during release
**Cause**: Infrastructure issue, test failure, or configuration problem
**Solution**: Check pipeline logs, identify failure stage, address root cause, re-trigger pipeline

### Issue: Post-release deployment not detected
**Cause**: Deployment delay, monitoring misconfiguration, or actual failure
**Solution**: Check deployment logs, verify package registry, run manual smoke tests, escalate if issue persists

### Issue: Rollback cannot be completed
**Cause**: Package registry restrictions, deployment system issues
**Solution**: Document manual rollback steps, escalate to user, consider publishing hotfix version instead

---

## AI Maestro Communication Templates

### Template 1: Receiving Release Request

Check for incoming release requests by checking your inbox using the `agent-messaging` skill. Filter for messages with `content.type == "release-request"`.

### Template 2: Reporting Release Readiness

Notify requesting agent that release verification is complete. Send a message using the `agent-messaging` skill with:
- **Recipient**: `orchestrator-amoa`
- **Subject**: `Release Verification: v1.2.3`
- **Priority**: `high`
- **Content**: `{"type": "release-ready", "message": "Release v1.2.3 verification complete. All gates passed. Awaiting user approval to publish."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Template 3: Reporting Release Completion

After successful release, send a message using the `agent-messaging` skill with:
- **Recipient**: `orchestrator-amoa`
- **Subject**: `Release Published: v1.2.3`
- **Priority**: `normal`
- **Content**: `{"type": "release-complete", "message": "Release v1.2.3 published successfully. URL: https://github.com/owner/repo/releases/tag/v1.2.3"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Template 4: Escalating Release Blocker

When a critical issue blocks release, send a message using the `agent-messaging` skill with:
- **Recipient**: `orchestrator-amoa`
- **Subject**: `[RELEASE BLOCKED] v1.2.3`
- **Priority**: `urgent`
- **Content**: `{"type": "release-blocked", "message": "Release v1.2.3 blocked. Blocker: CI pipeline failure in security scan. Requires resolution before release."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Template 5: Initiating Rollback Notification

When rollback is initiated, send a message using the `agent-messaging` skill with:
- **Recipient**: `orchestrator-amoa`
- **Subject**: `[ROLLBACK] v1.2.3 -> v1.2.2`
- **Priority**: `urgent`
- **Content**: `{"type": "rollback-initiated", "message": "Rollback initiated from v1.2.3 to v1.2.2. Reason: Critical regression in API. ETA: 15 minutes."
  }'
```

---

## Resources

- [references/release-responsibilities.md](references/release-responsibilities.md) - Release coordinator role definition
- [references/release-types.md](references/release-types.md) - Patch, minor, major release guidelines
- [references/semantic-versioning.md](references/semantic-versioning.md) - Version numbering rules
- [references/release-process.md](references/release-process.md) - Step-by-step release process
- [references/pre-release-verification.md](references/pre-release-verification.md) - Pre-release checklist
- [references/post-release-verification.md](references/post-release-verification.md) - Post-release checklist
- [references/rollback-procedures.md](references/rollback-procedures.md) - Rollback execution guide
- [references/cicd-integration.md](references/cicd-integration.md) - CI/CD pipeline configuration
- [references/troubleshooting-tag-branch-collision.md](references/troubleshooting-tag-branch-collision.md) - Tag-branch collision troubleshooting

## Getting Started

1. Read this SKILL.md file for release management overview
2. Review [references/semantic-versioning.md](references/semantic-versioning.md) for version rules
3. Review [references/release-types.md](references/release-types.md) to understand release categories
4. Review [references/pre-release-verification.md](references/pre-release-verification.md) for verification checklist
5. Use `scripts/amia_release_verify.py` to verify release readiness
6. Use `scripts/amia_changelog_generate.py` to create changelog
7. Use `scripts/amia_create_release.py` to publish release (after user approval)

---

**Version**: 1.0.0
**Last Updated**: 2025-02-04
**Skill Type**: Release Management
**Difficulty**: Intermediate
**Required Knowledge**: Semantic versioning, git tagging, CI/CD pipelines
