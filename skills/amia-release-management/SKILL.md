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

This skill defines the **release management procedures** for coordinating software releases across patch, minor, and major version changes. Release management is the final gate before code reaches production, requiring systematic verification, proper versioning, comprehensive documentation, and reliable rollback procedures.

## Prerequisites

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
2. **Determine version number** - Based on change scope (see Release Types reference)
3. **Verify release readiness** - Run pre-release verification checklist
4. **Generate changelog** - Compile changes since last release
5. **Create release notes** - Write user-facing summary
6. **Bump version** - Update version in all required files
7. **Create release tag** - Tag commit with version and annotation
8. **Trigger CI/CD** - Run release pipeline
9. **Verify post-release** - Confirm release deployed correctly
10. **Report completion** - Notify requesting agent of release status

### Checklist

Copy this checklist and track your progress:

- [ ] Receive release request with target type (patch/minor/major)
- [ ] Determine version number based on semantic versioning rules
- [ ] Verify release readiness (all tests pass, no critical bugs, docs updated)
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
|    +--> PATCH: X.Y.Z+1 (bug fixes only, no breaking changes)
|    +--> MINOR: X.Y+1.0 (new features, backward compatible)
|    +--> MAJOR: X+1.0.0 (breaking changes, migration guide required)
|
+--> Pre-release verification passes?
|    +--> YES --> Proceed to release
|    +--> NO --> Critical: STOP, escalate | Non-critical: Document and proceed (with approval)
|
+--> Release deployed successfully?
     +--> YES --> Create release notes, notify stakeholders
     +--> NO --> Initiate rollback (see Rollback Procedures reference)
```

---

## Reference Documentation

### 1. Release Management Responsibilities
[references/release-responsibilities.md](references/release-responsibilities.md) - What coordinators must/must not do
- **Contents:** Overview, Core Roles, Release Manager, Technical Lead, Quality Assurance Lead, DevOps Engineer, Product Owner, Responsibility Matrix (RACI), Escalation Path, Level 1: Team Level, Level 2: Management Level, Level 3: Executive Level, Communication Responsibilities, Daily During Release Window, Weekly (Pre-Release), Post-Release, Decision Authority, Release Manager Has Final Authority On, Technical Lead Has Final Authority On, QA Lead Has Final Authority On, DevOps Engineer Has Final Authority On, Product Owner Has Final Authority On, Handoff Procedures, Development to QA, QA to DevOps, DevOps to Operations, Accountability Measures, Success Metrics by Role, Cross-Functional Collaboration, Required Collaboration Points, Collaboration Best Practices, Conflict Resolution, Continuous Improvement, Training and Development

### 2. Release Types
[references/release-types.md](references/release-types.md) - Patch, minor, major, pre-release definitions
  <!-- TOC: release-types.md -->
  - Overview
  - Major Release
  - Definition
  <!-- /TOC -->

### 3. Semantic Versioning Rules
[references/semantic-versioning.md](references/semantic-versioning.md) - Version format and incrementing rules

### 4. Release Process
[references/release-process.md](references/release-process.md) - Version bumping, changelog, release notes, tagging

### 5. Pre-Release Verification
[references/pre-release-verification.md](references/pre-release-verification.md) - Quality gates and verification checklist
- **Contents:** Overview, Verification Principles, Core Principles, Verification Levels, Verification Checklist by Category, Code Quality Verification, Testing Verification, Data Verification, Infrastructure Verification, Monitoring and Observability, Documentation Verification, Compliance and Legal Verification, Business Verification, Communication and Training, Contingency Planning, Final Go/No-Go Decision, Decision Meeting, Go Decision Criteria, No-Go Criteria (any one triggers delay), Conditional Go, Decision Documentation, Post-Verification Activities, Final Preparation, Pre-Deployment Brief, Verification Sign-Off, Verification Automation, Automated Verification Gates, Verification Dashboard, Continuous Improvement, Verification Metrics, Process Improvements

### 6. Post-Release Verification
[references/post-release-verification.md](references/post-release-verification.md) - Deployment verification and smoke testing
- **Contents:** Overview, Verification Timeline, Immediate (0-4 hours), Short-term (4-24 hours), Medium-term (24-72 hours), Long-term (1-2 weeks), Immediate Post-Release Verification (0-4 Hours), Deployment Completion Verification, Smoke Test Execution, Error Monitoring, Performance Baseline, User Experience Validation, Security Validation, Short-Term Verification (4-24 Hours), Comprehensive Monitoring, Issue Identification and Triage, Performance Analysis, Medium-Term Verification (24-72 Hours), Trend Analysis, Feature Adoption Tracking, Support and Feedback Analysis, Long-Term Verification (1-2 Weeks), Business Value Validation, Stability Assessment, Cost Analysis, Release Retrospective, Continuous Verification, Ongoing Monitoring, Continuous Improvement, Post-Release Verification Checklist Summary, Verification Success Criteria

### 7. Rollback Procedures
[references/rollback-procedures.md](references/rollback-procedures.md) - When and how to rollback releases
- **Contents:** Overview, Rollback Fundamentals, What is a Rollback?, When to Rollback vs. Fix Forward, Rollback Decision Criteria, Rollback Planning (Pre-Release), Rollback Readiness Assessment, Rollback Documentation, Rollback Execution, Rollback Decision Process, Rollback Execution Steps, Communication During Rollback, Post-Rollback Activities, Incident Documentation, Root Cause Analysis, Prevention Measures, Re-Release Planning, Rollback Best Practices, Rollback Anti-Patterns, Conclusion

### 8. CI/CD Integration
[references/cicd-integration.md](references/cicd-integration.md) - Pipeline configuration and automation
- **Contents:** Overview, CI/CD Fundamentals, Continuous Integration (CI), Continuous Deployment (CD), Release Management Integration, CI/CD Pipeline Architecture, Standard Pipeline Stages, CI Pipeline Configuration, Build Stage, Test Stage, Analysis Stage, Artifact Publishing, CD Pipeline Configuration, Deployment Stages, Database Migration Integration, Release Gates and Approvals, Rollback Automation, Advanced CI/CD Patterns, Deployment Strategies, Multi-Environment Pipeline, Monitoring and Observability, Pipeline Monitoring, Notification Integration, Best Practices, CI/CD Pipeline Design, Release Automation, Quality and Security, Documentation and Communication, Conclusion

### 9. Tag-Branch Collision Troubleshooting
[references/troubleshooting-tag-branch-collision.md](references/troubleshooting-tag-branch-collision.md) - Tag-branch collision detection and resolution
- **Contents:** What is a tag-branch name collision, How collisions cause HTTP 300 errors, How to detect collisions using amia_cleanup_version_branches.py, How to resolve collisions safely, Best practices to prevent future collisions

**Script**: `scripts/amia_cleanup_version_branches.py` -- Detects and reports version tag/branch name collisions (safe, print-only)

---

## Semantic Versioning Quick Reference

| Change Type | Version Increment | Example |
|-------------|-------------------|---------|
| Bug fix (no API change) | PATCH | 1.2.3 -> 1.2.4 |
| New feature (backward compatible) | MINOR | 1.2.3 -> 1.3.0 |
| Breaking change | MAJOR | 1.2.3 -> 2.0.0 |
| Pre-release | PATCH + suffix | 1.2.3 -> 1.2.4-alpha.1 |

---

## State-Based Verification Model

Use state-based transitions instead of time-based checks:

```
UNVERIFIED --> VERIFICATION_IN_PROGRESS
  +--> All gates pass --> READY_FOR_RELEASE
  +--> Any gate fails --> BLOCKED
        +--> Critical --> ESCALATE_TO_USER
        +--> Non-critical --> DOCUMENT_AND_AWAIT_APPROVAL
```

### Escalation Order

| Order | Condition | Action |
|-------|-----------|--------|
| 1 | Test failure | Delegate fix to implementation agent, await resolution |
| 2 | Critical bug open | Escalate to user for release decision |
| 3 | Missing documentation | Delegate documentation task, await completion |
| 4 | Dependency vulnerability | Escalate to user with severity assessment |
| 5 | CI/CD failure | Investigate cause, escalate if infrastructure issue |

---

## Scripts Reference

> **Note:** Only `amia_cleanup_version_branches.py` is currently available. The following are planned: `amia_release_verify.py`, `amia_changelog_generate.py`, `amia_version_bump.py`, `amia_create_release.py`, `amia_rollback.py`.

| Script | Purpose | Usage |
|--------|---------|-------|
| `amia_release_verify.py` | Pre-release verification | `python scripts/amia_release_verify.py --repo owner/repo --version 1.2.3` |
| `amia_changelog_generate.py` | Generate changelog | `python scripts/amia_changelog_generate.py --repo owner/repo --from v1.2.2 --to HEAD` |
| `amia_version_bump.py` | Bump version | `python scripts/amia_version_bump.py --repo owner/repo --type patch\|minor\|major` |
| `amia_create_release.py` | Create GitHub release | `python scripts/amia_create_release.py --repo owner/repo --version 1.2.3 --notes release_notes.md` |
| `amia_rollback.py` | Rollback release | `python scripts/amia_rollback.py --repo owner/repo --from v1.2.3 --to v1.2.2 --reason "reason"` |
| `amia_cleanup_version_branches.py` | Detect tag/branch collisions | `uv run scripts/amia_cleanup_version_branches.py` |

---

## Critical Rules Summary

1. **Never Release Without Approval** - Always present verification results and await explicit user decision.
2. **Verify Before and After** - Run pre-release and post-release verification for every release.
3. **Document Everything** - Every release needs updated changelog, release notes, version bump, and annotated git tag.
4. **Be Ready to Rollback** - Always have a rollback plan before releasing.
5. **Follow Semantic Versioning** - Version numbers communicate meaning; never use incorrect increments.

---

## Examples

### Standard Patch Release

```bash
python scripts/amia_release_verify.py --repo owner/repo --version 1.2.4
python scripts/amia_changelog_generate.py --repo owner/repo --from v1.2.3 --to HEAD
python scripts/amia_version_bump.py --repo owner/repo --type patch
python scripts/amia_create_release.py --repo owner/repo --version 1.2.4 --notes release_notes.md
```

### Rollback After Failed Release

```bash
python scripts/amia_rollback.py --repo owner/repo --from v1.2.4 --to v1.2.3 --reason "Critical regression"
python scripts/amia_release_verify.py --repo owner/repo --version 1.2.3 --mode verify-deployed
```

---

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Pre-release verification fails | Quality gates not passing | Identify failing gates, delegate fixes, await resolution |
| Version bump conflicts | Version already bumped elsewhere | Check all files, resolve conflicts, ensure consistency |
| Tag already exists | Previous failed release | Verify tag commit; delete and recreate if incorrect |
| CI/CD pipeline fails | Infrastructure/test/config issue | Check logs, identify failure stage, address root cause |
| Post-release not detected | Delay, misconfiguration, or failure | Check deployment logs, verify registry, run smoke tests |
| Rollback cannot complete | Registry restrictions, deployment issues | Document manual steps, escalate, consider hotfix |

---

## AI Maestro Communication

Use the `agent-messaging` skill for all inter-agent communication. Key message types:

| Scenario | Recipient | Priority | Content Type |
|----------|-----------|----------|--------------|
| Release readiness report | `orchestrator-amoa` | high | `release-ready` |
| Release completion | `orchestrator-amoa` | normal | `release-complete` |
| Release blocker escalation | `orchestrator-amoa` | urgent | `release-blocked` |
| Rollback notification | `orchestrator-amoa` | urgent | `rollback-initiated` |

Always verify message delivery via the skill's send confirmation.

---

## Resources

- [references/semantic-versioning.md](references/semantic-versioning.md) - Semantic versioning rules
- [references/release-types.md](references/release-types.md) - Release categories (patch/minor/major)
  <!-- TOC: release-types.md -->
  - Overview
  - Major Release
  - Definition
  <!-- /TOC -->
- [references/release-process.md](references/release-process.md) - Full release process
- [references/release-workflow-chain.md](references/release-workflow-chain.md) - Workflow chain
  <!-- TOC: release-workflow-chain.md -->
  - Why release automation uses two separate workflows instead of one
  - How the prepare-release workflow works
  - Version detection from project metadata
  <!-- /TOC -->
- [references/pre-release-verification.md](references/pre-release-verification.md) - Pre-release checklist
  <!-- TOC: pre-release-verification.md -->
  - Overview
  - Verification Principles
  - Core Principles
  <!-- /TOC -->
- [references/post-release-verification.md](references/post-release-verification.md) - Post-release checklist
  <!-- TOC: post-release-verification.md -->
  - Overview
  - Verification Timeline
  - Immediate (0-4 hours)
  <!-- /TOC -->
- [references/rollback-procedures.md](references/rollback-procedures.md) - Rollback procedures
  <!-- TOC: rollback-procedures.md -->
  - Overview
  - Rollback Fundamentals
  - What is a Rollback?
  <!-- /TOC -->
- [references/cicd-integration.md](references/cicd-integration.md) - CI/CD integration
  <!-- TOC: cicd-integration.md -->
  - Overview
  - CI/CD Fundamentals
  - Continuous Integration (CI)
  <!-- /TOC -->
- [references/release-responsibilities.md](references/release-responsibilities.md) - Agent responsibilities
  <!-- TOC: release-responsibilities.md -->
  - Overview
  - Core Roles
  - Release Manager
  <!-- /TOC -->

**Version**: 1.0.0 | **Updated**: 2025-02-04
