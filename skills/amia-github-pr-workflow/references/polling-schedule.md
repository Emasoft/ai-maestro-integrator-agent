# Polling Schedule

## Table of Contents

- 7.1 Base polling frequency
- 7.2 What to check on each poll
- 7.3 Adaptive polling rules
- 7.4 Notification triggers

---

## 7.1 Base polling frequency

**Default**: Poll regularly based on activity level. No fixed intervals - poll as needed.

### Recommended frequency by context

| Context | Frequency | Rationale |
|---------|-----------|-----------|
| Normal operations | Regular | Balance between responsiveness and overhead |
| Active PR work | More frequent | Faster feedback during implementation |
| Waiting for CI | Frequent | CI completion can unblock work |
| Low activity periods | Less frequent | Reduced activity expected |
| Urgent PR | Very frequent | Needs attention |

### Polling implementation

**Option 1: Manual polling**
The orchestrator explicitly runs the poll script:
```bash
python scripts/amia_orchestrator_pr_poll.py --repo owner/repo
```

**Option 2: Background task**
Delegate polling to a monitoring subagent:
```
You are a PR monitoring subagent. Your task is:
Poll PR status regularly and report significant changes.

Actions:
1. Run poll script at regular intervals (use judgment based on activity)
2. Compare results to previous poll
3. Report via AI Maestro message if significant change detected
```

**Option 3: Event-driven (preferred)**
Use GitHub webhooks or CLI notifications when available.

### Polling considerations

**Why poll frequency matters**:
- API rate limits (respect GitHub limits)
- Context consumption
- Orchestrator availability for other tasks

**Principle**: Poll frequently enough to stay responsive, but not so often that you waste resources. Use judgment.

---

## 7.2 What to check on each poll

### Mandatory checks (every poll)

| Check | Command | Purpose |
|-------|---------|---------|
| PR state | `gh pr view --json state` | Detect close/merge |
| CI status | `gh pr checks` | Detect pass/fail |
| New comments | `gh api` comments endpoint | Detect activity |
| Merge eligibility | `gh pr view --json mergeable` | Detect blockers |

### Periodic checks (every 3rd poll)

| Check | Command | Purpose |
|-------|---------|---------|
| Full verification | `amia_verify_pr_completion.py` | Comprehensive status |
| Unresolved threads | GraphQL query | Detect missed items |
| Unpushed commits | `git log origin..HEAD` | Detect local work |

### On-demand checks (triggered by condition)

| Trigger | Check | Purpose |
|---------|-------|---------|
| CI was pending | CI status | Confirm completion |
| Commits were pushed | CI status | Verify new run |
| Review requested | Review status | Detect response |
| Conflict detected | Merge status | Confirm resolution |

### Poll result data structure

```json
{
  "poll_time": "2024-01-15T10:30:00Z",
  "prs_checked": 3,
  "results": [
    {
      "pr_number": 123,
      "state": "open",
      "mergeable": true,
      "ci_status": "passing",
      "new_comments": 0,
      "unresolved_threads": 0,
      "action_needed": "none",
      "changed_since_last_poll": false
    },
    {
      "pr_number": 456,
      "state": "open",
      "mergeable": false,
      "ci_status": "failing",
      "new_comments": 2,
      "unresolved_threads": 1,
      "action_needed": "fix_ci",
      "changed_since_last_poll": true
    }
  ]
}
```

---

## 7.3 Adaptive polling rules

Polling frequency should adapt based on PR state and recent activity.

### Poll more frequently when

| Condition | Rationale |
|-----------|-----------|
| CI just started | Know completion ASAP |
| Commits just pushed | Await CI start |
| Active conversation | Respond quickly |
| User is online | More responsive |
| Needs attention | Work is time-sensitive |

### Poll less frequently when

| Condition | Rationale |
|-----------|-----------|
| CI has been pending a while | Long-running, don't spam |
| No recent activity | Likely stalled |
| Low activity periods | Reduced activity expected |
| Waiting for human | Can't control timing |
| All PRs stable | Nothing to action |

### State-based polling priority

```
PR State Machine:
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  DRAFT → READY_FOR_REVIEW → IN_REVIEW → CHANGES_REQUESTED   │
│    │           │                │              │             │
│  Low       Regular          Frequent       Frequent          │
│                                │                             │
│                          APPROVED → CI_PENDING → READY       │
│                             │          │           │         │
│                          Regular   Frequent    Frequent      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Adaptive polling logic

```python
def should_poll_frequently(pr_status, recent_activity):
    """Determine if PR needs frequent polling based on state."""

    # High priority - poll more frequently
    if pr_status.ci_status == "pending" and pr_status.ci_recently_started:
        return True  # CI completion is imminent
    if pr_status.recently_pushed_commits:
        return True  # Waiting for CI to start
    if pr_status.has_recent_comments:
        return True  # Active conversation

    # Low priority - poll less frequently
    if not recent_activity:
        return False  # Stalled
    if pr_status.state == "draft":
        return False  # Not ready for review
    if pr_status.waiting_for_human:
        return False  # Can't control timing

    # Default - regular polling
    return None  # Use standard frequency
```

---

## 7.4 Notification triggers

The orchestrator should notify the user when significant events occur.

### Immediate notification triggers

| Event | Notification | Priority |
|-------|--------------|----------|
| CI failed | "CI failed on PR #X: [reason]" | High |
| PR merged externally | "PR #X was merged" | Medium |
| PR closed externally | "PR #X was closed without merge" | Medium |
| Merge conflict detected | "PR #X has merge conflicts" | High |
| Human commented | "Human @Y commented on PR #X" | High |
| All criteria pass | "PR #X ready for merge" | Medium |

### Periodic summary triggers

| Condition | Summary | Frequency |
|-----------|---------|-----------|
| Start of work day | "PR status summary: [count] open, [count] need action" | Daily |
| Multiple PRs ready | "Batch: [count] PRs ready for merge" | As occurs |
| Stalled PRs | "[count] PRs have no activity for 24h" | Daily |

### Escalation triggers

| Condition | Escalation | When |
|-----------|------------|------|
| CI stuck | "CI for PR #X stuck. Check status." | When CI appears stuck |
| Repeated failure | "Repeated failure on PR #X: [criterion]" | After multiple attempts |
| Human waiting | "Human awaiting response on PR #X" | When response is overdue |
| Conflict persists | "Merge conflict on PR #X needs attention" | When conflict lingers |

### Notification suppression

**Do not notify for**:
- Routine polling with no changes
- Expected CI runs
- Automated bot updates (unless failure)
- Intermediate states during active work

### Notification format

```
## [Priority] PR #[number] Notification

**Event**: [description]
**Time**: [timestamp]
**Action needed**: [what user should do]
**Details**: [link to PR or status file]
```

---

## Polling Script Usage

### Full poll

```bash
python scripts/amia_orchestrator_pr_poll.py --repo owner/repo
```

### Filtered poll

```bash
# Only PRs needing action
python scripts/amia_orchestrator_pr_poll.py --repo owner/repo --filter needs_action

# Only specific PR
python scripts/amia_orchestrator_pr_poll.py --repo owner/repo --pr 123
```

### Output example

```json
{
  "poll_time": "2024-01-15T10:30:00Z",
  "repo": "owner/repo",
  "prs": [
    {
      "number": 123,
      "title": "Add new feature",
      "state": "open",
      "author": "johndoe",
      "author_type": "human",
      "created_at": "2024-01-14T09:00:00Z",
      "updated_at": "2024-01-15T10:25:00Z",
      "status": "needs_review",
      "ci_status": "passing",
      "mergeable": true,
      "priority": 1,
      "action_needed": "delegate_review",
      "next_poll_interval": 10
    }
  ],
  "summary": {
    "total_open": 3,
    "needs_action": 1,
    "blocked": 0,
    "ready_to_merge": 2
  }
}
```

---

## Polling Best Practices

1. **Always check CI first**: CI status often determines next steps
2. **Compare to previous poll**: Only act on changes
3. **Respect rate limits**: Don't poll more than necessary
4. **Use adaptive intervals**: Adjust based on state
5. **Batch notifications**: Don't spam user with minor updates
6. **Log poll results**: Keep history for debugging
7. **Handle API failures gracefully**: Retry with backoff
