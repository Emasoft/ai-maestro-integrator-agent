# Automation Scripts

## Table of Contents

1. [When using skill automation scripts](#overview)
2. [When bulk creating issues from task lists](#sync_taskspy)
3. [When receiving GitHub webhook events](#ci_webhook_handlerpy)
4. [When synchronizing project with CI status](#kanban_syncpy)
5. [When configuring shared thresholds](#thresholds-configuration)

## Overview

The github-projects-sync skill includes automation scripts for common operations. All scripts are located in the `scripts/` directory.

**Script Locations:**
```
github-projects-sync/
├── scripts/
│   ├── sync_tasks.py           # Bulk issue creation
│   ├── ci_webhook_handler.py   # Webhook receiver
│   └── amia_kanban_sync.py          # CI status sync
└── ../shared/
    ├── thresholds.py           # Shared thresholds
    └── aimaestro_notify.py     # AI Maestro CLI wrapper
```

## sync_tasks.py

Bulk create GitHub issues from markdown or JSON task lists and add them to Projects V2.

### Purpose

- Parse markdown or JSON task lists
- Create GitHub issues via GraphQL API
- Link issues to Projects V2 boards
- Support labels, assignees, and milestones
- Dry-run mode for preview

### Usage

```bash
python scripts/sync_tasks.py --repo OWNER/REPO --project PROJECT_NUMBER --tasks tasks.md
```

### Options

| Option | Description |
|--------|-------------|
| `--repo` | Repository (OWNER/REPO format) |
| `--project` | Project number |
| `--tasks` | Path to task file (markdown or JSON) |
| `--dry-run` | Preview without creating |
| `--skip-existing` | Skip issues with matching titles |

### Examples

**Dry-run to preview:**
```bash
python scripts/sync_tasks.py \
  --repo myorg/myrepo \
  --project 5 \
  --tasks backlog.md \
  --dry-run
```

**Create issues:**
```bash
python scripts/sync_tasks.py \
  --repo myorg/myrepo \
  --project 5 \
  --tasks backlog.md
```

### Input Format (Markdown)

```markdown
# Sprint 5 Tasks

- [ ] Implement login endpoint #labels:type:feature,priority:high @dev-agent-1
- [ ] Fix password validation bug #labels:type:bug,priority:critical
- [ ] Add user documentation #labels:type:docs
- [ ] Refactor auth module #labels:type:refactor
```

**Syntax:**
- `- [ ]` - Task marker
- `#labels:label1,label2` - Labels (comma-separated)
- `@assignee` - Assignee username

### Input Format (JSON)

```json
[
  {
    "title": "Implement login endpoint",
    "body": "Detailed description here",
    "labels": ["type:feature", "priority:high"],
    "assignee": "dev-agent-1"
  },
  {
    "title": "Fix password validation bug",
    "labels": ["type:bug", "priority:critical"]
  }
]
```

### Output

```
Dry Run Mode - No issues will be created

Processing 4 tasks from backlog.md

[1/4] Implement login endpoint
      Labels: type:feature, priority:high
      Assignee: dev-agent-1
      Would create issue and add to project #5

[2/4] Fix password validation bug
      Labels: type:bug, priority:critical
      Would create issue and add to project #5

...

Summary:
  Total: 4
  Would create: 4
  Would skip: 0
```

## ci_webhook_handler.py

GitHub webhook receiver that syncs CI events with project status and sends AI Maestro notifications.

### Purpose

- Receive GitHub webhook events
- Update project item status based on CI results
- Send notifications to orchestrator
- Log all webhook events

### Usage

```bash
python scripts/ci_webhook_handler.py --port 9000
```

### Options

| Option | Description |
|--------|-------------|
| `--port` | Port to listen on (default: 9000) |
| `--log-dir` | Directory for webhook logs |
| `--test` | Test with sample payload file |

### Handled Events

| Event | Action | Trigger |
|-------|--------|---------|
| `workflow_run` (success) | Update → AI Review | CI passes |
| `workflow_run` (failure) | Update → Blocked | CI fails |
| `check_run` (failure) | Notify orchestrator | Check fails |
| `pull_request` (opened) | Update → AI Review | PR created |
| `pull_request` (merged) | Update → Done | PR merged |
| `issues` (labeled) | Update status | Status label added |

### Environment Variables

```bash
export GITHUB_WEBHOOK_SECRET="your_secret"
export WEBHOOK_PORT=9000
export LOG_DIR="$HOME/design/webhook_logs"
```

### Testing

```bash
# Test with sample payload
cat > /tmp/test_payload.json << 'EOF'
{
  "action": "completed",
  "workflow_run": {
    "conclusion": "failure",
    "head_branch": "feature/test"
  },
  "repository": {"full_name": "owner/repo"}
}
EOF

python scripts/ci_webhook_handler.py --test /tmp/test_payload.json
```

### Webhook Configuration

See [ci-notification-setup.md](./ci-notification-setup.md) for complete setup instructions.

## amia_kanban_sync.py

Synchronize all project issues with current CI/PR state.

### Purpose

- Query all project items
- Check CI status for linked PRs
- Update status based on CI results
- Handle automatic transitions
- Send AI Maestro notifications for changes

### Usage

```bash
python scripts/amia_kanban_sync.py --owner OWNER --repo REPO --project NUMBER
```

### Options

| Option | Description |
|--------|-------------|
| `--owner` | Repository owner |
| `--repo` | Repository name |
| `--project` | Project number |
| `--dry-run` | Show changes without applying |
| `--notify` | Send AI Maestro notifications |

### Automatic Status Transitions

| Condition | Current Status | New Status |
|-----------|----------------|------------|
| CI passes | In Progress | AI Review |
| CI fails | Any | Blocked |
| PR merged | Merge/Release | Done |
| Changes requested | AI Review | In Progress |
| Review approved (small task) | AI Review | Merge/Release |
| Review approved (big task) | AI Review | Human Review |
| Human review approved | Human Review | Merge/Release |

### Example Run

```bash
python scripts/amia_kanban_sync.py \
  --owner myorg \
  --repo myrepo \
  --project 5 \
  --notify
```

### Output

```
Kanban Sync - myorg/myrepo Project #5

Checking 12 items...

[#42] Implement login
  Current: In Progress
  PR: #52 (CI: passing)
  Action: Update → AI Review

[#43] Fix auth bug
  Current: AI Review
  PR: #53 (CI: failing)
  Action: Update → Blocked
  Notification: Sent to orchestrator

...

Summary:
  Checked: 12
  Updated: 3
  Blocked: 1
  Notifications: 2
```

## Thresholds Configuration

The `../shared/thresholds.py` module defines automation thresholds used by scripts.

### GitHubThresholds Class

```python
class GitHubThresholds:
    """Critical automation thresholds for GitHub Projects sync."""

    # Consecutive CI failures before escalation
    MAX_CONSECUTIVE_FAILURES = 3

    # Hours before inactive "In Progress" items are flagged
    INACTIVE_HOURS = 24

    # Hours before "AI Review" items are escalated
    LONG_REVIEW_HOURS = 48

    # Hours before blocked items are escalated to user
    BLOCKED_ESCALATION_HOURS = 72
```

### Usage in Scripts

```python
from shared.thresholds import GitHubThresholds

# Check consecutive failures
if failure_count >= GitHubThresholds.MAX_CONSECUTIVE_FAILURES:
    escalate_to_orchestrator(issue_id)

# Check inactive items
if hours_since_activity >= GitHubThresholds.INACTIVE_HOURS:
    query_agent_status(issue_id)
```

### Blocked Conditions

An issue is automatically marked "Blocked" when ANY of:

1. **Explicit block**: Agent sends blocked status report
2. **CI failures**: CI fails MAX_CONSECUTIVE_FAILURES (3) times consecutively
3. **Unmet dependencies**: Depends on issues that are not yet Done

### Modifying Thresholds

Edit `../shared/thresholds.py` to customize thresholds:

```python
# Example: Stricter CI failure threshold
MAX_CONSECUTIVE_FAILURES = 2

# Example: Longer review tolerance
LONG_REVIEW_HOURS = 72
```

**Note:** Restart webhook handler and sync scripts after modifying thresholds.
