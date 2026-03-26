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

Orchestrator workflow for delegating PR reviews to subagents, verifying completion, and reporting to user.

## Prerequisites

- GitHub CLI (`gh`) authenticated
- Python 3.8+ and AI Maestro configured
- Subagent spawning capability

## Instructions

1. **Poll** -- Run `amia_orchestrator_pr_poll.py` to get open PRs
2. **Classify** -- Human PR = escalate; AI/bot PR = delegate directly
3. **Delegate** -- Spawn subagent for review/changes (never do work yourself)
4. **Monitor** -- Poll progress via background tasks (never block)
5. **Verify** -- Run `amia_verify_pr_completion.py` before reporting

### Checklist

Copy this checklist and track your progress:

- [ ] Poll PRs using `amia_orchestrator_pr_poll.py`
- [ ] Classify author type and work needed
- [ ] Delegate to subagent
- [ ] Monitor and verify using `amia_verify_pr_completion.py`
- [ ] Report to user, await merge decision
- [ ] Handle failures by delegating fixes

### Critical Rules

- Never block, write code, or merge without user approval
- Always verify before reporting status
- Escalate human PRs to user

## Output

| Output Type | Format | Description |
|---|---|---|
| Subagent Delegation | Task spawn | Spawned subagent with PR review/fix instructions |
| Status Report | Text/JSON | Current PR status and action recommendations |
| Verification Result | JSON | Pass/fail status for all completion criteria |
| User Notification | Text | Human-readable summary of PR readiness |

> **Output discipline:** All scripts support `--output-file <path>`. Use it to minimize token consumption.

## Reference Documents

See `references/` directory for all reference documents. Full index in [detailed-guide](references/detailed-guide.md).

## Error Handling

Script failures return non-zero exit codes. See [detailed-guide](references/detailed-guide.md) for details.

## Examples

```bash
python scripts/amia_orchestrator_pr_poll.py --repo owner/repo
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123
# Output: {"complete": true, "recommendation": "ready_to_merge"}
```

## Resources

See [detailed-guide](references/detailed-guide.md) for decision tree, scripts, and extended examples.
