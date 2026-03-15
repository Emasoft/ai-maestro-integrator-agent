# Escalation Procedures

## Table of Contents

- [Overview](#overview)
- [Escalation Path A: Pre-Review Gate Failure](#escalation-path-a-pre-review-gate-failure)
  - [Level 1: Author Notification](#level-1-author-notification)
  - [Level 2: Follow-Up Notification](#level-2-follow-up-notification)
  - [Level 3: Orchestrator Escalation](#level-3-orchestrator-escalation)
  - [Level 4: Maintainer Escalation (Final)](#level-4-maintainer-escalation-final)
- [Escalation Path B: Review Gate Failure](#escalation-path-b-review-gate-failure)
  - [Level 1: Request Changes](#level-1-request-changes)
  - [Level 2: Re-Request Changes](#level-2-re-request-changes)
  - [Level 3: Orchestrator Escalation](#level-3-orchestrator-escalation-1)
  - [Level 4: Consider Closure](#level-4-consider-closure)
- [Escalation Path C: Pre-Merge Gate Failure](#escalation-path-c-pre-merge-gate-failure)
  - [Level 1: Automatic Block + Comment](#level-1-automatic-block--comment)
  - [Level 2: Author Notification](#level-2-author-notification)
  - [Level 3: Orchestrator Escalation](#level-3-orchestrator-escalation-2)
- [Escalation Path D: Post-Merge Gate Failure](#escalation-path-d-post-merge-gate-failure)
  - [Level 1: Immediate Notification (All Parties)](#level-1-immediate-notification-all-parties)
  - [Level 2: Revert vs Hotfix Decision](#level-2-revert-vs-hotfix-decision)
  - [Level 3: Execute Response](#level-3-execute-response)
  - [Level 4: Post-Incident Review](#level-4-post-incident-review)
- [Escalation Timeline Summary](#escalation-timeline-summary)
- [Override Authority During Escalation](#override-authority-during-escalation)
- [Notification Channels](#notification-channels)

## Overview

When quality gates fail and issues are not resolved through normal channels, systematic escalation ensures problems are addressed by the appropriate authority.

---

## Escalation Path A: Pre-Review Gate Failure

**Trigger**: Automated checks (tests, linting, build) fail

### Level 1: Author Notification

**Action**: Comment on PR with failure details
**Timeline**: Immediate upon gate failure
**Responsible**: AMIA Integrator Agent

**Template**:

```
❌ Pre-review gate failed:

**Failures**:
- [Specific check failed]
- [Details of failure]

**Required Actions**:
- [What author must do]

**Re-evaluation**: Gate will re-run on next push.

cc @author
```

**Success Criteria**: Author acknowledges and begins fixes

### Level 2: Follow-Up Notification

**Action**: Second comment requesting status
**Timeline**: 24 hours after Level 1 (configurable)
**Responsible**: AMIA Integrator Agent

**Trigger**: No commits or response after Level 1

**Template**:

```
⏰ Pre-review gate failure follow-up

PR has been blocked for 24 hours due to failing checks.

**Status**: Awaiting fixes from @author

**Impact**: Review process cannot begin until checks pass.

Please provide status update or address failures.
```

**Success Criteria**: Author responds or pushes fixes

### Level 3: Orchestrator Escalation

**Action**: Notify AMOA (AI Maestro Orchestration Agent)
**Timeline**: 48 hours after Level 2 (configurable)
**Responsible**: AMIA Integrator Agent

**Trigger**: Author unresponsive after 2 follow-ups

**Notification**:

```
@amoa - Pre-review gate escalation

PR #${PR_NUMBER} blocked for 72+ hours due to failing automated checks.

**Author**: @author (unresponsive)
**Issue**: [Summary of failures]
**History**: 2 notifications sent, no response

**Request**: Author engagement or PR disposition decision
```

**Success Criteria**: AMOA contacts author or makes disposition decision

### Level 4: Maintainer Escalation (Final)

**Action**: Notify project maintainer
**Timeline**: 1 week after Level 3 (configurable)
**Responsible**: AMOA

**Trigger**: No resolution after AMOA engagement

**Outcome Options**:

- Maintainer contacts author directly
- PR marked as stale and closed
- Maintainer assigns another developer to complete work

---

## Escalation Path B: Review Gate Failure

**Trigger**: Code review identifies issues (low confidence or blocking issues)

### Level 1: Request Changes

**Action**: Submit PR review requesting changes
**Timeline**: Immediate after review completion
**Responsible**: AMIA Integrator Agent (reviewer role)

**Template**:

```
❌ Review gate failed

**Confidence Score**: X% (threshold: 80%)

**Blocking Issues**:
- [Issue 1 with details]
- [Issue 2 with details]

**Improvement Areas**:
[Dimension-by-dimension feedback]

Please address these issues and request re-review when ready.

cc @author
```

**Success Criteria**: Author addresses issues and requests re-review

### Level 2: Re-Request Changes

**Action**: Follow-up review comment
**Timeline**: 48 hours after Level 1 (configurable)
**Responsible**: AMIA Integrator Agent

**Trigger**: Changes not addressed or re-review shows same issues

**Template**:

```
⏰ Review gate failure follow-up

Original review issues remain unresolved.

**Outstanding Issues**:
- [Issues not yet addressed]

**Status**: Awaiting changes from @author

Please address feedback or discuss if clarification needed.
```

**Success Criteria**: Author makes meaningful progress on issues

### Level 3: Orchestrator Escalation

**Action**: Notify AMOA
**Timeline**: 1 week after Level 2 (configurable)
**Responsible**: AMIA Integrator Agent

**Trigger**: No meaningful progress on review feedback

**Notification**:

```
@amoa - Review gate escalation

PR #${PR_NUMBER} blocked for 1+ week due to unresolved review issues.

**Author**: @author
**Issues**: [Summary of blocking issues]
**History**: Request changes submitted, one follow-up, minimal progress

**Request**: Mediation or PR disposition decision
```

**Outcome Options**:

- AMOA mediates between reviewer and author
- AMOA provides guidance on resolving issues
- PR marked for closure if abandoned

### Level 4: Consider Closure

**Action**: Close PR with explanation
**Timeline**: 2 weeks after Level 3 (configurable)
**Responsible**: AMOA or Maintainer

**Trigger**: No path forward after AMOA engagement

**Closure Template**:

```
Closing due to unresolved review issues.

**Reason**: Review feedback not addressed after multiple attempts to engage.

**History**:
- Review requested changes: [date]
- Follow-up: [date]
- AMOA escalation: [date]
- No resolution achieved

Author is welcome to reopen or submit fresh PR if issues are addressed.
```

---

## Escalation Path C: Pre-Merge Gate Failure

**Trigger**: Final checks fail (CI, conflicts, stale approval)

### Level 1: Automatic Block + Comment

**Action**: Block merge, comment with failure
**Timeline**: Immediate upon gate failure
**Responsible**: AMIA Integrator Agent

**Template**:

```
❌ Pre-merge gate failed - merge blocked

**Failures**:
- [CI status]
- [Merge conflict status]
- [Approval validity status]

**Required Actions**:
- [What must be fixed]

Merge will be unblocked when all checks pass.

cc @author
```

**Success Criteria**: Author resolves issues

### Level 2: Author Notification

**Action**: Direct notification to resolve
**Timeline**: 24 hours after Level 1 (configurable)
**Responsible**: AMIA Integrator Agent

**Trigger**: No action after initial block

**Template**:

```
⏰ Pre-merge gate failure - action required

PR remains blocked for 24 hours.

**Issue**: [Specific blocker]
**Impact**: Cannot merge until resolved

Please [specific action - rebase, fix CI, etc.].
```

**Success Criteria**: Author takes action

### Level 3: Orchestrator Escalation

**Action**: Notify AMOA for investigation
**Timeline**: If CI infrastructure issue suspected
**Responsible**: AMIA Integrator Agent

**Trigger**: Persistent CI failure unrelated to PR code

**Notification**:

```
@amoa - Pre-merge gate CI infrastructure issue

PR #${PR_NUMBER} blocked by CI failures that appear infrastructure-related.

**Evidence**:
- [Describe why infrastructure is suspected]
- [CI logs showing infra errors]

**Request**: Infrastructure investigation
```

**Outcome**: AMOA investigates CI infrastructure, resolves issue or confirms code problem

---

## Escalation Path D: Post-Merge Gate Failure

**Trigger**: Main branch issues after merge (CI fails, regressions, deployment failures)

### Level 1: Immediate Notification (All Parties)

**Action**: Notify author, reviewer, and AMOA simultaneously
**Timeline**: Immediate upon detection
**Responsible**: AMIA Integrator Agent

**Template**:

```
🚨 **POST-MERGE GATE FAILED** 🚨

Main branch health check failed after merging PR #${PR_NUMBER}.

**Issue**: [Specific failure - CI, regression, deployment]
**Impact**: [Production impact if any]

@author @reviewer @amoa - Immediate attention required.

**Next Steps**: Evaluating revert vs hotfix (decision within 30 minutes)
```

**Success Criteria**: All parties acknowledge and engage

### Level 2: Revert vs Hotfix Decision

**Action**: Evaluate options and make decision
**Timeline**: 30 minutes after Level 1
**Responsible**: AMOA with input from author/reviewer

**Decision Matrix**:

| Condition | Decision |
|-----------|----------|
| Main broken, fix unclear | REVERT |
| Main broken, trivial fix | HOTFIX |
| Regression, user-impacting | REVERT |
| Regression, minor | HOTFIX |
| Deployment failed | ROLLBACK + evaluate revert |

**Decision Documentation**:

```
**Decision**: [REVERT / HOTFIX / ROLLBACK]

**Reasoning**: [Why this option chosen]
**Action Plan**: [Specific steps]
**Timeline**: [Expected resolution time]
**Responsible**: [Who will execute]
```

### Level 3: Execute Response

**Action**: Execute revert or hotfix
**Timeline**: Immediate after decision
**Responsible**: Designated person from Level 2

**Revert Execution**:

```bash
# Create revert PR
gh pr create --title "Revert: [Original PR]" --body "[Reason]"

# Fast-track through gates (reverts bypass some checks)
# Merge immediately
gh pr merge --admin --squash
```

**Hotfix Execution**:

```bash
# Create hotfix PR
gh pr create --title "Hotfix: [Issue]" --body "[Fix details]"

# Fast-track review
# Merge when approved
```

### Level 4: Post-Incident Review

**Action**: Analyze root cause and prevent recurrence
**Timeline**: 24-48 hours after resolution
**Responsible**: AMOA

**Review Template**:

```
## Post-Merge Failure Post-Mortem

**Incident**: PR #${PR_NUMBER} post-merge failure
**Date**: [Date]
**Resolution**: [REVERT / HOTFIX]

**Root Cause**: [Why did this pass gates but fail post-merge?]

**Contributing Factors**:
- [Factor 1]
- [Factor 2]

**Lessons Learned**:
- [Lesson 1]
- [Lesson 2]

**Action Items**:
- [ ] [Prevention measure 1]
- [ ] [Prevention measure 2]
- [ ] [Gate improvement 1]
```

---

## Escalation Timeline Summary

| Path | Level 1 | Level 2 | Level 3 | Level 4 |
|------|---------|---------|---------|---------|
| **A: Pre-Review** | Immediate | +24h | +48h | +1 week |
| **B: Review** | Immediate | +48h | +1 week | +2 weeks |
| **C: Pre-Merge** | Immediate | +24h | As needed | N/A |
| **D: Post-Merge** | Immediate | +30 min | Immediate | +24-48h |

**Note**: All timelines are configurable per repository policy.

---

## Override Authority During Escalation

At any escalation level, authorized parties can override the gate:

| Escalation Level | Who Can Override |
|------------------|------------------|
| Level 1-2 | Senior Reviewer (non-security only) |
| Level 3 | AMOA or Maintainer |
| Level 4 | Maintainer only |

**Security issues**: No override at any level.

See [override-examples.md](./override-examples.md) for override documentation examples.

---

## Notification Channels

Escalations use multiple channels for reliability:

1. **PR Comments** - Primary (always)
2. **GitHub @mentions** - Secondary (always)
3. **Email** - Tertiary (for urgent escalations)
4. **Slack/Discord** - Optional (if configured)
5. **AI Maestro Messages** - Optional (for agent-to-agent coordination)

Configure channels in repository settings.
