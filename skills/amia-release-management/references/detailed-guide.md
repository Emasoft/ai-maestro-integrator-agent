# Release Management Skill — Detailed Guide

## Table of Contents

- [Decision Tree](#decision-tree)
- [Semantic Versioning Quick Reference](#semantic-versioning-quick-reference)
- [State-Based Verification Model](#state-based-verification-model)
- [Escalation Order](#escalation-order)
- [Scripts Reference](#scripts-reference)
- [Critical Rules](#critical-rules)
- [Release Pipeline Design by Project Type](#release-pipeline-design-by-project-type)
- [Error Handling](#error-handling)
- [AI Maestro Communication](#ai-maestro-communication)
- [Examples](#examples)
- [Reference Documentation Details](#reference-documentation-details)

## Decision Tree

The success path runs THROUGH the MANAGER-approval gate — never around it.
Entering the release pipeline (`complete -> publish` / `complete -> deploy`)
is a NON-EXEMPT **Tier-2** action.

```
Release Request Received
|
+--> What type of release?
|    +--> PATCH: X.Y.Z+1 (bug fixes only, no breaking changes)
|    +--> MINOR: X.Y+1.0 (new features, backward compatible)
|    +--> MAJOR: X+1.0.0 (breaking changes, migration guide required)
|
+--> Pre-release verification passes?
|    +--> NO  --> Critical: STOP, escalate | Non-critical: document, then seek approval
|    +--> YES --> continue
|
+--> TIER-2 GATE: is a MANAGER approval RECORDED in the TRDD's "## Approval log"?
|    +--> NO  --> Send the Tier-2 approval request (AMP template, see persona);
|    |            WAIT. Do NOT release. (Solo/autonomous project: the project
|    |            owner-as-MANAGER records the approval, or use --solo-user-approval.)
|    +--> YES --> Pass --approval-trdd <TRDD> to amia_create_release.py
|                 (the script hard-refuses with exit 7 if the evidence is absent)
|
+--> Release deployed successfully?
     +--> YES --> Create release notes; notify stakeholders; INTEGRATOR validates the
     |            artifact satisfies the TRDD, then flips the column -> published/live
     +--> NO --> Initiate rollback (also Tier-2 gated on --execute; see references/rollback-procedures.md)
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
| `amia_create_release.py` | Create GitHub release (Tier-2 gated) | `python scripts/amia_create_release.py --repo owner/repo --version 1.2.3 --notes release_notes.md --approval-trdd design/tasks/TRDD-<id>-...md` |
| `amia_rollback.py` | Rollback release (`--execute` is Tier-2 gated) | `python scripts/amia_rollback.py --repo owner/repo --from v1.2.3 --to v1.2.2 --reason "reason" --execute --approval-trdd <trdd>` |

`amia_create_release.py` and `amia_rollback.py --execute` REFUSE to run (exit 7,
`GOVERNANCE_BLOCK`) unless a recorded MANAGER approval is supplied via
`--approval-trdd <TRDD>` (whose `## Approval log` carries an `APPROVED` release
entry) or, on a solo/autonomous project, `--solo-user-approval "<rationale>"`.
| `amia_cleanup_version_branches.py` | Detect tag/branch collisions | `uv run scripts/amia_cleanup_version_branches.py` |

## Critical Rules

1. **Never Release Without a RECORDED MANAGER Approval (Tier-2 gate)** — entering
   the release pipeline is NON-EXEMPT. A recorded approval lives in the approving
   TRDD's `## Approval log` (an `APPROVED` release entry) and is passed to the
   release script via `--approval-trdd`. Team membership is NOT approval. The
   release scripts enforce this in code (exit 7 without it); the human must not
   route around the gate. On a solo/autonomous project the owner IS the MANAGER
   and records the approval (or uses `--solo-user-approval "<rationale>"`).
2. **Verify Before and After** - Run pre-release and post-release verification for every release.
3. **Document Everything** - Every release needs updated changelog, release notes, version bump, and annotated git tag.
4. **Be Ready to Rollback** - Always have a rollback plan before releasing; `--execute` is itself Tier-2 gated.
5. **Follow Semantic Versioning** - Version numbers communicate meaning; never use incorrect increments.
6. **INTEGRATOR owns the column -> completed/published/live flip** — validate that
   the shipped artifact actually satisfies the TRDD before flipping; nobody self-marks done.

## Release Pipeline Design by Project Type

The release pipeline is **INTEGRATOR-designed per project** — there is no single
universal pipeline. INTEGRATOR selects (and the USER may override) the pipeline
that matches the project type, then records the chosen pipeline in the project's
PRRD / TRDD. Every pipeline, regardless of type, passes the Tier-2 approval gate
before its publish/deploy step executes.

| Project type | Pipeline shape (INT designs the concrete steps) |
|---|---|
| **Library / package** (PyPI, npm, crate, gem, …) | verify -> changelog -> version bump -> build artifact -> **publish to the package registry** -> tag + GitHub release |
| **Application** (desktop / mobile / CLI binary) | verify -> build -> **sign / notarize** (codesign, notarytool, APK/AAB signing) -> package installers -> attach binaries to a **GitHub release** -> optional store / marketplace submission |
| **Service** (web API, worker, site) | verify -> build -> **containerize** (image build) -> push to image registry -> **deploy** staging -> smoke test -> deploy production -> soak / monitor |
| **Claude Code plugin** | the CPV canonical `publish.py` (validate -> test -> lint -> bump -> commit -> push -> marketplace) |

**CPV `publish.py` is Claude-Code-plugins-only.** It is a *recommendation* for the
plugin project type — NOT a universal release tool. Do not invoke it for libraries,
applications, or services; design the matching pipeline above instead.

**USER override.** The USER may mandate ANY custom pipeline (a private registry, a
specific signing identity, a bespoke deploy target, an extra manual gate, a
different sequence). A USER-specified pipeline overrides the type defaults above;
INTEGRATOR implements it as specified and records it in the PRRD / TRDD.

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
# Tier-2 gate: --approval-trdd points at the TRDD whose ## Approval log records the MANAGER APPROVED entry.
python scripts/amia_create_release.py --repo owner/repo --version 1.2.4 --notes release_notes.md \
    --approval-trdd design/tasks/TRDD-<id>-...md
```

### Rollback After Failed Release

```bash
# --execute is Tier-2 gated; without --approval-trdd / --solo-user-approval it exits 7.
python scripts/amia_rollback.py --repo owner/repo --from v1.2.4 --to v1.2.3 --reason "Critical regression" \
    --execute --approval-trdd design/tasks/TRDD-<id>-...md
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

## Full Reference Document Index

Content moved from SKILL.md for brevity. All files are in the `references/` directory:

**Process & Definitions:**

- `release-types.md` — Patch/minor/major/pre-release definitions
- `semantic-versioning.md` — Version format and rules
- `release-process.md` — Bumping, changelog, notes, tagging
- `release-workflow-chain.md` — Two-workflow automation

**Verification:**

- `pre-release-verification.md` — Quality gates checklist
- `post-release-verification.md` — Deployment smoke testing

**Operations:**

- `rollback-procedures.md` — Rollback procedures
- `cicd-integration.md` — Pipeline automation
- `release-responsibilities.md` — Roles and RACI matrix
- `troubleshooting-tag-branch-collision.md` — Tag-branch collisions

**Operational Procedures:**

- `op-determine-version.md` — Version determination
- `op-bump-version.md` — Version bump
- `op-generate-changelog.md` — Changelog generation
- `op-create-release-tag.md` — Release tag creation
- `op-verify-release-readiness.md` — Readiness verification
- `op-validate-changelog-gate.md` — Changelog gate
- `op-validate-release-tags.md` — Tag validation
- `op-execute-rollback.md` — Rollback execution
- `op-escalate-release-blocker.md` — Blocker escalation
- `op-update-readme-badges.md` — Badge updates
- `git-cliff-integration.md` — Git-cliff integration
