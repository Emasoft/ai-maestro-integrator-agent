# Orchestrator PR Workflow -- Detailed Guide

## Contents

- [Decision Tree](#decision-tree)
- [Scripts Reference](#scripts-reference)
- [Section Index](#section-index)
- [Error Handling](#error-handling)
- [Extended Examples](#extended-examples)

## Decision Tree

```
PR Review Request Received
|
+---> Is PR from human or AI agent?
|   +---> Human PR -> Escalate to user for guidance
|   +---> AI/Bot PR -> Direct delegation allowed
|
+---> What type of work is needed?
|   +---> Code review -> Delegate to review subagent
|   +---> Code changes -> Delegate to implementation subagent
|   +---> CI verification -> Delegate to CI monitor subagent
|   +---> Status check -> Use polling script directly
|
+---> Should I block waiting?
|   +---> NEVER block. Always use background tasks or polling.
|
+---> Is PR ready to merge?
    +---> Run completion verification script
    +---> All criteria pass -> Report to user, await merge decision
    +---> Criteria fail -> Identify gaps, delegate fixes
```

## Scripts Reference

### amia_orchestrator_pr_poll.py

**Location**: `scripts/amia_orchestrator_pr_poll.py`
**Purpose**: Get all open PRs, check status, identify actions needed
**When to use**: On each polling interval to survey PR landscape

```bash
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

```bash
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123

# Output format
{
  "pr_number": 123,
  "complete": true,
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

## Section Index

Detailed content for each workflow section is in its own reference file:

### 1. Orchestrator Responsibilities

See `orchestrator-responsibilities.md` for:
- What the orchestrator MUST do (monitor, delegate, track, report)
- What the orchestrator MUST NOT do (write code, block, merge unilaterally)

### 2. Delegation Rules

See `delegation-rules.md` for:
- When to spawn subagents (complexity thresholds, time triggers, resource checks)
- How to structure subagent prompts (required elements, context passing, output format)
- Maximum concurrent agents and task isolation requirements
- Result aggregation patterns

### 3. Verification Workflow

See `verification-workflow.md` for:
- Pre-review and post-review verification checklists
- CI check verification
- Thread resolution verification
- Merge readiness verification
- The 4-verification-loop protocol (structure, timing, exit conditions, escalation)

### 4. Worktree Coordination

See `worktree-coordination.md` for:
- When to use worktrees
- Worktree assignment to subagents
- Isolation enforcement rules
- Cleanup coordination and conflict handling

### 5. Human vs AI PR Assignment

See `human-vs-ai-assignment.md` for:
- Identifying PR author type (human, AI agent, bot categories)
- Communication style differences
- Escalation rules for human PRs
- Direct action rules for AI PRs

### 6. Completion Criteria

See `completion-criteria.md` for:
- All 8 criteria that must be true before merge
- Failure handling by type

### 7. Polling Schedule

See `polling-schedule.md` for:
- Base polling frequency
- What to check on each poll
- Adaptive polling rules
- Notification triggers

### 8. Merge Failure Recovery

See `merge-failure-recovery.md` for:
- Types of merge failures
- Merge conflict resolution steps
- CI failure during merge handling
- Partial merge recovery and rollback procedures
- Prevention strategies

## Error Handling

### Subagent not returning results

**Cause**: Subagent may have crashed or become unresponsive
**Solution**: Check subagent logs, re-delegate with simpler scope

### PR status appears stale

**Cause**: GitHub API rate limiting or cache
**Solution**: Wait briefly, then re-poll. If persistent, check API rate limits.

### Completion verification fails intermittently

**Cause**: Race condition with GitHub webhook processing
**Solution**: Implement quiet period check before final verification

### Multiple subagents conflicting

**Cause**: Insufficient task isolation
**Solution**: Use worktrees for parallel work, enforce file-level isolation

### User not receiving status updates

**Cause**: Notification not triggered
**Solution**: Check notification triggers in polling schedule, ensure report step executes

## Extended Examples

### Example 1: Standard PR Review Coordination

```bash
# 1. Poll for open PRs requiring action
python scripts/amia_orchestrator_pr_poll.py --repo owner/repo

# 2. For each PR needing review, delegate to review subagent
#    (orchestrator spawns subagent with appropriate prompt)

# 3. Verify completion before reporting
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123
```

### Example 2: Verify PR is Ready to Merge

```bash
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123
# If complete: true, report to user for merge decision
# If complete: false, identify failing_criteria and delegate fixes
```
