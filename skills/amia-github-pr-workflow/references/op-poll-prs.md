# Operation: Poll for PRs Requiring Attention

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
- [Output](#output)
- [Status Values](#status-values)
- [Action Values](#action-values)
- [Error Handling](#error-handling)
- [Example](#example)

---

```yaml
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-poll-prs
```

---

## Purpose

Survey all open PRs in a repository and identify which ones require action.

## When to Use

- At start of PR review workflow
- On each polling interval
- When returning from hibernation
- After completing a batch of PR tasks

## Prerequisites

- GitHub CLI (`gh`) authenticated
- Python 3.8+ available
- Repository access (owner/repo)

## Steps

1. **Run the polling script**:

   ```bash
   python scripts/amia_orchestrator_pr_poll.py --repo owner/repo
   ```

2. **Parse the output** - JSON with prioritized PR list:

   ```json
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

3. **Process by priority** - Handle priority 1 PRs first

4. **For each PR**, determine next action based on `action_needed` field

## Output

| Field | Type | Description |
|-------|------|-------------|
| prs | array | List of PRs requiring attention |
| prs[].number | int | PR number |
| prs[].status | string | Current PR status |
| prs[].priority | int | Priority ranking (1 = highest) |
| prs[].action_needed | string | Recommended action |

## Status Values

| Status | Meaning |
|--------|---------|
| needs_review | No review submitted yet |
| needs_changes | Review requested changes |
| ready | All checks passing, ready for merge |
| blocked | Cannot proceed (conflicts, failing CI) |

## Action Values

| Action | Next Step |
|--------|-----------|
| delegate_review | Spawn review subagent |
| delegate_fix | Spawn implementation subagent |
| verify_completion | Run completion verification |
| wait | No action needed now |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Script not found | Wrong path | Verify script location |
| Auth error | gh not authenticated | Run `gh auth login` |
| Rate limited | Too many API calls | Wait and retry |

## Example

```bash
# Poll for PRs
python scripts/amia_orchestrator_pr_poll.py --repo Emasoft/my-project

# Sample output
{
  "prs": [
    {"number": 45, "title": "Add feature X", "status": "needs_review", "priority": 1, "action_needed": "delegate_review"},
    {"number": 42, "title": "Fix bug Y", "status": "ready", "priority": 2, "action_needed": "verify_completion"}
  ]
}
```
