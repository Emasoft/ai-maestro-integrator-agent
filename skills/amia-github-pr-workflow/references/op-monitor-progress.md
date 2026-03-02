# Operation: Monitor Subagent Progress

---
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-monitor-progress
---

## Purpose

Track progress of delegated subagents without blocking. Use polling to check status.

## When to Use

- After spawning a subagent
- On each polling interval
- When user requests status update

## Prerequisites

- Subagent previously spawned
- Subagent ID or task identifier known
- Polling schedule established

## Steps

1. **Check subagent output location**:
   - Review the output file path specified in delegation
   - Check `docs_dev/` for task reports

2. **Check AI Maestro for messages**: Check your inbox using the `agent-messaging` skill. Filter for messages where `content.data.task_id` matches the task being monitored. **Verify**: Confirm message delivery via the `agent-messaging` skill's sent messages feature.

3. **Evaluate progress state**:

   | State | Indicators | Action |
   |-------|------------|--------|
   | Completed | Output file exists, [DONE] in message | Process result |
   | In Progress | No output yet, no failure message | Continue polling |
   | Failed | [FAILED] in message, error in output | Handle failure |
   | Stale | No progress after N polls | Escalate or reassign |

4. **Update orchestration log** with current state

5. **Trigger next action** based on state

## Polling Frequency

| Situation | Frequency |
|-----------|-----------|
| Active work | Every 2-5 minutes |
| Waiting on CI | Every 5-10 minutes |
| Long-running task | Every 15-30 minutes |
| Overnight/weekend | Every 1-2 hours |

## Output

| Field | Type | Description |
|-------|------|-------------|
| task_id | string | Task being monitored |
| state | string | Current state |
| last_update | timestamp | When last progress seen |
| output_summary | string | Brief result if complete |

## Stale Detection

A task is considered stale if:
- No progress after 3 consecutive polls
- No messages received in expected timeframe
- Output file not updated

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| No output file | Subagent still working | Continue polling |
| Partial output | Subagent crashed | Re-delegate with smaller scope |
| Conflicting results | Multiple subagents on same task | Check task isolation |

## Example

Check for completion messages by checking your inbox using the `agent-messaging` skill. Filter for messages where the subject contains "PR #123".

Also check the output file:
```bash
cat docs_dev/pr-reviews/pr-123-review.md 2>/dev/null || echo "Not yet available"
```

## Critical Rule

**Never block waiting** for subagent completion. Always use polling. The coordinator must remain responsive to other tasks and messages.
