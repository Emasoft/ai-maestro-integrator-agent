---
name: amia-github-pr-workflow
description: Use when coordinating PR review work as orchestrator. Defines delegation rules, verification, and completion criteria. Trigger with /start-pr-review [PR_NUMBER].
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: 1.0.0
  author: Emasoft
  category: workflow
  tags: "pr-review, orchestration, delegation, verification, github"
agent: api-coordinator
context: fork
user-invocable: false
---

# Orchestrator PR Workflow Skill

## Overview

Coordination workflow for PR reviews. The coordinator delegates review tasks to subagents, monitors completion, and reports results. It never writes code or merges without user approval.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+ for automation scripts
- AI Maestro configured for inter-agent communication
- Access to spawn subagents for delegation

## Instructions

1. **Poll for PRs** -- Run `amia_orchestrator_pr_poll.py` to get open PRs and status
2. **Identify author type** -- Human PR = escalate to user; AI/bot PR = direct delegation
3. **Classify work needed** -- Review, changes, verification, or wait
4. **Delegate to subagent** -- Spawn specialized subagent (never do work yourself)
5. **Monitor progress** -- Use polling/background tasks (never block)
6. **Verify completion** -- Run `amia_verify_pr_completion.py` before reporting ready
7. **Report to user** -- Provide status, await merge decision (never merge without approval)

### Checklist

- [ ] Poll for PRs using `amia_orchestrator_pr_poll.py`
- [ ] Identify if PR author is human or AI/bot
- [ ] Classify work needed (review/changes/verification/wait)
- [ ] Delegate to appropriate subagent
- [ ] Monitor subagent progress via polling
- [ ] Verify all criteria using `amia_verify_pr_completion.py`
- [ ] Report status to user and await merge decision
- [ ] Handle failures by delegating fixes

### Critical Rules

1. **Never Block** -- All long-running tasks delegated or run as background tasks
2. **Never Write Code** -- Code writing always delegated to implementation subagents
3. **Never Merge Without User** -- Merge requires explicit user approval
4. **Always Verify** -- Run verification script before reporting any status
5. **Human PRs Require Escalation** -- Always escalate human PRs to user for guidance

## Output

| Output Type | Format | Description |
|---|---|---|
| Subagent Delegation | Task spawn | Spawned subagent with PR review/fix instructions |
| Status Report | Text/JSON | Current PR status and action recommendations |
| Verification Result | JSON | Pass/fail status for all completion criteria |
| User Notification | Text | Human-readable summary of PR readiness |

> **Output discipline:** All scripts support `--output-file <path>`. Use it to minimize token consumption.

## Reference Documents

**Orchestrator Role:**

- `references/orchestrator-responsibilities.md` -- Orchestrator role definition and boundaries
- `references/delegation-rules.md` -- Subagent delegation patterns and prompt structure
- `references/human-vs-ai-assignment.md` -- Author type identification and escalation rules

**Verification and Completion:**

- `references/verification-workflow.md` -- Pre/post-review verification procedures
- `references/completion-criteria.md` -- All 8 criteria that must pass before merge
- `references/polling-schedule.md` -- Polling frequency and adaptive rules

**Recovery and Coordination:**

- `references/merge-failure-recovery.md` -- Merge failure types and recovery steps
- `references/worktree-coordination.md` -- Worktree assignment and isolation rules

**Step-by-Step Operations:**

- `references/op-poll-prs.md` -- Polling for PRs requiring attention
- `references/op-identify-author-type.md` -- Identifying PR author type
- `references/op-classify-work.md` -- Classifying work needed
- `references/op-delegate-subagent.md` -- Delegating to subagents
- `references/op-monitor-progress.md` -- Monitoring subagent progress
- `references/op-verify-completion.md` -- Verifying completion criteria
- `references/op-report-status.md` -- Reporting status to user
- `references/op-handle-failure.md` -- Handling verification failures

**Detailed Guide:**

- `references/detailed-guide.md` -- Decision tree, script usage, error handling, and examples

## Examples

### Example 1: Standard PR Review Coordination

```bash
# Poll for open PRs requiring action
python scripts/amia_orchestrator_pr_poll.py --repo owner/repo
# Delegate each PR needing review to a subagent
# Verify completion before reporting
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123
```
