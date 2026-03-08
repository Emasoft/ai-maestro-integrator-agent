# Release Management Skill — Detailed Guide

## Contents

- [Decision Tree](#decision-tree)
- [Semantic Versioning Quick Reference](#semantic-versioning-quick-reference)
- [State-Based Verification Model](#state-based-verification-model)
- [Escalation Order](#escalation-order)
- [Scripts Reference](#scripts-reference)
- [Critical Rules](#critical-rules)
- [Error Handling](#error-handling)
- [AI Maestro Communication](#ai-maestro-communication)
- [Examples](#examples)
- [Reference Documentation Details](#reference-documentation-details)

## Decision Tree

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
     +--> NO --> Initiate rollback (see references/rollback-procedures.md)
```

## Semantic Versioning Quick Reference

| Change Type | Version Increment | Example |
|-------------|-------------------|---------|
| Bug fix (no API change) | PATCH | 1.2.3 -> 1.2.4 |
| New feature (backward compatible) | MINOR | 1.2.3 -> 1.3.0 |
| Breaking change | MAJOR | 1.2.3 -> 2.0.0 |
| Pre-release | PATCH + suffix | 1.2.3 -> 1.2.4-alpha.1 |

## State-Based Verification Model

Use state-based transitions instead of time-based checks:

```
UNVERIFIED --> VERIFICATION_IN_PROGRESS
  +--> All gates pass --> READY_FOR_RELEASE
  +--> Any gate fails --> BLOCKED
        +--> Critical --> ESCALATE_TO_USER
        +--> Non-critical --> DOCUMENT_AND_AWAIT_APPROVAL
```

## Escalation Order

| Order | Condition | Action |
|-------|-----------|--------|
| 1 | Test failure | Delegate fix to implementation agent, await resolution |
| 2 | Critical bug open | Escalate to user for release decision |
| 3 | Missing documentation | Delegate documentation task, await completion |
| 4 | Dependency vulnerability | Escalate to user with severity assessment |
| 5 | CI/CD failure | Investigate cause, escalate if infrastructure issue |

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `amia_release_verify.py` | Pre-release verification | `python scripts/amia_release_verify.py --repo owner/repo --version 1.2.3` |
| `amia_changelog_generate.py` | Generate changelog | `python scripts/amia_changelog_generate.py --repo owner/repo --from v1.2.2 --to HEAD` |
| `amia_version_bump.py` | Bump version | `python scripts/amia_version_bump.py --repo owner/repo --type patch\|minor\|major` |
| `amia_create_release.py` | Create GitHub release | `python scripts/amia_create_release.py --repo owner/repo --version 1.2.3 --notes release_notes.md` |
| `amia_rollback.py` | Rollback release | `python scripts/amia_rollback.py --repo owner/repo --from v1.2.3 --to v1.2.2 --reason "reason"` |
| `amia_cleanup_version_branches.py` | Detect tag/branch collisions | `uv run scripts/amia_cleanup_version_branches.py` |

## Critical Rules

1. **Never Release Without Approval** - Always present verification results and await explicit user decision.
2. **Verify Before and After** - Run pre-release and post-release verification for every release.
3. **Document Everything** - Every release needs updated changelog, release notes, version bump, and annotated git tag.
4. **Be Ready to Rollback** - Always have a rollback plan before releasing.
5. **Follow Semantic Versioning** - Version numbers communicate meaning; never use incorrect increments.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Pre-release verification fails | Quality gates not passing | Identify failing gates, delegate fixes, await resolution |
| Version bump conflicts | Version already bumped elsewhere | Check all files, resolve conflicts, ensure consistency |
| Tag already exists | Previous failed release | Verify tag commit; delete and recreate if incorrect |
| CI/CD pipeline fails | Infrastructure/test/config issue | Check logs, identify failure stage, address root cause |
| Post-release not detected | Delay, misconfiguration, or failure | Check deployment logs, verify registry, run smoke tests |
| Rollback cannot complete | Registry restrictions, deployment issues | Document manual steps, escalate, consider hotfix |

## AI Maestro Communication

Use the `agent-messaging` skill for all inter-agent communication. Key message types:

| Scenario | Recipient | Priority | Content Type |
|----------|-----------|----------|--------------|
| Release readiness report | `orchestrator-amoa` | high | `release-ready` |
| Release completion | `orchestrator-amoa` | normal | `release-complete` |
| Release blocker escalation | `orchestrator-amoa` | urgent | `release-blocked` |
| Rollback notification | `orchestrator-amoa` | urgent | `rollback-initiated` |

Always verify message delivery via the skill's send confirmation.

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

## Reference Documentation Details

### Release Management Responsibilities
`references/release-responsibilities.md` - Contents: Overview, Core Roles, Release Manager, Technical Lead, Quality Assurance Lead, DevOps Engineer, Product Owner, Responsibility Matrix (RACI), Escalation Path, Communication Responsibilities, Decision Authority, Handoff Procedures, Accountability Measures, Continuous Improvement.

### Pre-Release Verification
`references/pre-release-verification.md` - Contents: Overview, Verification Principles, Core Principles, Verification Levels, Verification Checklist by Category (Code Quality, Testing, Data, Infrastructure, Monitoring, Documentation, Compliance, Business, Communication, Contingency), Final Go/No-Go Decision, Go Decision Criteria, No-Go Criteria, Verification Automation, Continuous Improvement.

### Post-Release Verification
`references/post-release-verification.md` - Contents: Overview, Verification Timeline (Immediate 0-4h, Short-term 4-24h, Medium-term 24-72h, Long-term 1-2 weeks), Deployment Completion Verification, Smoke Test Execution, Error Monitoring, Performance Baseline, User Experience Validation, Security Validation, Trend Analysis, Feature Adoption, Support and Feedback, Business Value Validation, Stability Assessment, Release Retrospective, Verification Success Criteria.

### Rollback Procedures
`references/rollback-procedures.md` - Contents: Overview, Rollback Fundamentals, When to Rollback vs Fix Forward, Rollback Decision Criteria, Rollback Planning (Pre-Release), Rollback Readiness Assessment, Rollback Execution Steps, Communication During Rollback, Post-Rollback Activities, Root Cause Analysis, Prevention Measures, Re-Release Planning, Best Practices, Anti-Patterns.

### CI/CD Integration
`references/cicd-integration.md` - Contents: Overview, CI/CD Fundamentals, Pipeline Architecture, Standard Pipeline Stages, CI Pipeline Configuration (Build, Test, Analysis, Artifact Publishing), CD Pipeline Configuration (Deployment Stages, Database Migration, Release Gates), Rollback Automation, Deployment Strategies, Multi-Environment Pipeline, Monitoring and Observability, Best Practices.
