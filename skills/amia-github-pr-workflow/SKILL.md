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

This skill defines the coordination workflow for Pull Request reviews. The approach is **coordination-only**: monitor PR status, delegate review tasks to specialized subagents, track completion, and report results.

**Core Principle**: This workflow separates coordination from work. The coordinator delegates, monitors, and reports — it does not perform direct review work.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+ for running automation scripts
- AI Maestro configured for inter-agent communication
- Access to spawn subagents for delegation

## Output

| Output Type | Format | Description |
|-------------|--------|-------------|
| Subagent Delegation | Task spawn | Spawned subagent with PR review/fix instructions |
| Status Report | Text/JSON | Current PR status and action recommendations |
| Verification Result | JSON | Pass/fail status for all completion criteria |
| User Notification | Text | Human-readable summary of PR readiness |
| Polling Schedule | Background task | Recurring PR status checks |

## Instructions

1. **Poll for PRs requiring attention** - Run `amia_orchestrator_pr_poll.py` to get list of open PRs and their status
2. **Identify PR author type** - Determine if PR is from human contributor or AI/bot (see section 5)
3. **Classify work needed** - Review PR status and determine action type (review/changes/verification/wait)
4. **Delegate to appropriate subagent** - Spawn specialized subagent based on work type (never do the work yourself)
5. **Monitor subagent progress** - Use polling to track completion (never block waiting)
6. **Verify completion criteria** - Run `amia_verify_pr_completion.py` before reporting ready
7. **Report to user** - Provide status update and await merge decision (never merge without approval)
8. **Handle failures** - If verification fails, identify gaps and delegate fixes (see section 6.2)

### Checklist

Copy this checklist and track your progress:

- [ ] Poll for PRs requiring attention using `amia_orchestrator_pr_poll.py`
- [ ] Identify if PR is from human or AI/bot author
- [ ] Classify the work needed (review/changes/verification/wait)
- [ ] Delegate to appropriate subagent (never do work yourself)
- [ ] Monitor subagent progress via polling (never block)
- [ ] Verify all completion criteria using `amia_verify_pr_completion.py`
- [ ] Report status to user and await merge decision
- [ ] Handle any failures by delegating fixes

Follow the decision tree below to determine the appropriate action for any PR review request.

---

## Quick Reference: Decision Tree

```
PR Review Request Received
│
├─► Is PR from human or AI agent?
│   ├─► Human PR → Escalate to user for guidance
│   └─► AI/Bot PR → Direct delegation allowed
│
├─► What type of work is needed?
│   ├─► Code review → Delegate to review subagent
│   ├─► Code changes → Delegate to implementation subagent
│   ├─► CI verification → Delegate to CI monitor subagent
│   └─► Status check → Use polling script directly
│
├─► Should I block waiting?
│   └─► NEVER block. Always use background tasks or polling.
│
└─► Is PR ready to merge?
    ├─► Run completion verification script
    ├─► All criteria pass → Report to user, await merge decision
    └─► Criteria fail → Identify gaps, delegate fixes
```

---

## Table of Contents with Reference Maps

### 1. Orchestrator Responsibilities
**Reference**: [orchestrator-responsibilities.md](references/orchestrator-responsibilities.md)
- 1.1 What the orchestrator MUST do
  - 1.1.1 Monitor PR status periodically
  - 1.1.2 Delegate review work to subagents
  - 1.1.3 Track completion status
  - 1.1.4 Report to user
- 1.2 What the orchestrator MUST NOT do
  - 1.2.1 Write code directly
  - 1.2.2 Block on long operations
  - 1.2.3 Make unilateral merge decisions

### 2. Delegation Rules
**Reference**: [delegation-rules.md](references/delegation-rules.md)
- 2.1 When to spawn subagents
  - 2.1.1 Task complexity thresholds
  - 2.1.2 Time-based triggers
  - 2.1.3 Resource availability checks
- 2.2 How to structure subagent prompts
  - 2.2.1 Required prompt elements
  - 2.2.2 Context passing rules
  - 2.2.3 Output format requirements
- 2.3 Maximum concurrent agents
- 2.4 Task isolation requirements
- 2.5 Result aggregation patterns

### 3. Verification Workflow
**Reference**: [verification-workflow.md](references/verification-workflow.md)
- 3.1 Pre-review verification checklist
- 3.2 Post-review verification checklist
- 3.3 CI check verification
- 3.4 Thread resolution verification
- 3.5 Merge readiness verification
- 3.6 The 4-verification-loop protocol
  - 3.6.1 Loop structure and timing
  - 3.6.2 Exit conditions
  - 3.6.3 Escalation triggers

### 4. Worktree Coordination
**Reference**: [worktree-coordination.md](references/worktree-coordination.md)
- 4.1 When to use worktrees
- 4.2 Worktree assignment to subagents
- 4.3 Isolation enforcement rules
- 4.4 Cleanup coordination
- 4.5 Conflict handling procedures

### 5. Human vs AI PR Assignment
**Reference**: [human-vs-ai-assignment.md](references/human-vs-ai-assignment.md)
- 5.1 Identifying PR author type
  - 5.1.1 Human contributors
  - 5.1.2 AI agent PRs
  - 5.1.3 Bot categories
- 5.2 Communication style differences
- 5.3 Escalation rules for human PRs
- 5.4 Direct action rules for AI PRs

### 6. Completion Criteria
**Reference**: [completion-criteria.md](references/completion-criteria.md)
- 6.1 ALL criteria that must be true
  - 6.1.1 Review comments addressed
  - 6.1.2 PR comments acknowledged
  - 6.1.3 No new comments (45s wait)
  - 6.1.4 CI checks pass
  - 6.1.5 No unresolved threads
  - 6.1.6 Merge eligible
  - 6.1.7 PR not already merged
  - 6.1.8 Commits pushed
- 6.2 Failure handling by type

### 7. Polling Schedule
**Reference**: [polling-schedule.md](references/polling-schedule.md)
- 7.1 Base polling frequency
- 7.2 What to check on each poll
- 7.3 Adaptive polling rules
- 7.4 Notification triggers

### 8. Merge Failure Recovery
**Reference**: [merge-failure-recovery.md](references/merge-failure-recovery.md)
- 8.1 Types of merge failures
- 8.2 Merge conflict resolution steps
- 8.3 CI failure during merge handling
- 8.4 Partial merge recovery
- 8.5 Notification procedures for author/reviewer
- 8.6 Rollback if merge corrupts main
- 8.7 Prevention strategies

---

## Scripts Reference

### amia_orchestrator_pr_poll.py
**Location**: `scripts/amia_orchestrator_pr_poll.py`
**Purpose**: Get all open PRs, check status, identify actions needed
**When to use**: On each polling interval to survey PR landscape
**Output**: JSON with prioritized action list

```bash
# Usage
python scripts/amia_orchestrator_pr_poll.py --repo owner/repo

# Output format
{
  "prs": [
    {
      "number": 123,
      "title": "PR Title",
      "status": "needs_review|needs_changes|ready|blocked",
      "priority": 1,
      "action_needed": "delegate_review|delegate_fix|verify_completion|wait"
    }
  ]
}
```

### amia_verify_pr_completion.py
**Location**: `scripts/amia_verify_pr_completion.py`
**Purpose**: Verify all completion criteria for a specific PR
**When to use**: Before reporting PR ready, before merge
**Output**: JSON pass/fail with detailed reasons

```bash
# Usage
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123

# Output format
{
  "pr_number": 123,
  "complete": true|false,
  "criteria": {
    "reviews_addressed": true,
    "comments_acknowledged": true,
    "no_new_comments": true,
    "ci_passing": true,
    "no_unresolved_threads": true,
    "merge_eligible": true,
    "not_merged": true,
    "commits_pushed": true
  },
  "failing_criteria": [],
  "recommendation": "ready_to_merge|needs_work|blocked"
}
```

---

## Critical Rules Summary

### Rule 1: Never Block
This workflow must NEVER execute blocking operations. All long-running tasks must be:
- Delegated to subagents
- Run as background tasks
- Monitored via polling

### Rule 2: Never Write Code
The coordinator role is to coordinate, not to implement. Code writing is ALWAYS delegated to implementation subagents.

### Rule 3: Never Merge Without User
The coordinator may verify merge readiness but NEVER executes merge without explicit user approval.

### Rule 4: Always Verify Before Reporting
Before reporting any status (ready, complete, blocked), always run the verification script to confirm.

### Rule 5: Human PRs Require Escalation
PRs from human contributors require different handling. Always escalate to user for guidance on communication and decisions.

---

## Examples

### Example 1: Standard PR Review Coordination

```bash
# Poll for open PRs requiring action
python scripts/amia_orchestrator_pr_poll.py --repo owner/repo

# For each PR needing review, delegate to review subagent
# (orchestrator spawns subagent with appropriate prompt)

# Verify completion before reporting
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123
```

### Example 2: Verify PR is Ready to Merge

```bash
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123
# If complete: true, report to user for merge decision
# If complete: false, identify failing_criteria and delegate fixes
```

## Error Handling

### Issue: Subagent not returning results
**Cause**: Subagent may have crashed or become unresponsive
**Solution**: Check subagent logs, re-delegate with simpler scope

### Issue: PR status appears stale
**Cause**: GitHub API rate limiting or cache
**Solution**: Wait briefly, then re-poll. If persistent, check API rate limits.

### Issue: Completion verification fails intermittently
**Cause**: Race condition with GitHub webhook processing
**Solution**: Implement quiet period check before final verification

### Issue: Multiple subagents conflicting
**Cause**: Insufficient task isolation
**Solution**: Use worktrees for parallel work, enforce file-level isolation

### Issue: User not receiving status updates
**Cause**: Notification not triggered
**Solution**: Check notification triggers in polling schedule, ensure report step executes

## Resources

- [references/orchestrator-responsibilities.md](references/orchestrator-responsibilities.md) - Orchestrator role definition
- [references/delegation-rules.md](references/delegation-rules.md) - Subagent delegation patterns
- [references/verification-workflow.md](references/verification-workflow.md) - Verification procedures
- [references/completion-criteria.md](references/completion-criteria.md) - PR completion requirements
- [references/polling-schedule.md](references/polling-schedule.md) - Polling frequency configuration
- [references/merge-failure-recovery.md](references/merge-failure-recovery.md) - Merge failure and recovery procedures
