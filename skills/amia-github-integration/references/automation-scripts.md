# Automation Scripts

## Table of Contents

- [Use-Case TOC](#use-case-toc)
- [Sync Projects V2 Script](#sync-projects-v2-script)
  - [When to Use](#when-to-use)
  - [Usage](#usage)
  - [Parameters](#parameters)
  - [Example Output](#example-output)
  - [What This Script Does](#what-this-script-does)
  - [Error Handling](#error-handling)
  - [Scheduling Sync](#scheduling-sync)
- [Bulk Label Assignment Script](#bulk-label-assignment-script)
  - [When to Use](#when-to-use-1)
  - [Usage](#usage-1)
  - [Parameters](#parameters-1)
  - [Filter Syntax](#filter-syntax)
  - [Examples](#examples)
  - [Expected Output](#expected-output)
- [Pull Request Monitor Script](#pull-request-monitor-script)
  - [When to Use](#when-to-use-2)
  - [Usage](#usage-2)
  - [Parameters](#parameters-2)
  - [Example Output](#example-output-1)
  - [Notification Options](#notification-options)
- [Bulk Issue Creation Script](#bulk-issue-creation-script)
  - [When to Use](#when-to-use-3)
  - [Usage](#usage-3)
  - [CSV Format](#csv-format)
  - [JSON Format](#json-format)
  - [Example Output](#example-output-2)
- [Project Reporting Script](#project-reporting-script)
  - [When to Use](#when-to-use-4)
  - [Usage](#usage-4)
  - [Parameters](#parameters-3)
  - [Example Output (Markdown)](#example-output-markdown)
- [Script Installation and Setup](#script-installation-and-setup)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
- [Best Practices](#best-practices)

## Use-Case TOC
- When you need to sync GitHub Projects V2 with agent tasks → [Sync Projects V2 Script](#sync-projects-v2-script)
- When you need to bulk assign labels → [Bulk Label Assignment Script](#bulk-label-assignment-script)
- When you need to monitor PR status → [Pull Request Monitor Script](#pull-request-monitor-script)
- When you need to create issues from CSV → [Bulk Issue Creation Script](#bulk-issue-creation-script)
- When you need to generate project reports → [Project Reporting Script](#project-reporting-script)

## Sync Projects V2 Script

**Location:** `scripts/sync-projects-v2.py`

**Purpose:** Bidirectionally synchronizes issues between your agent task system and GitHub Projects V2

### When to Use

- After agent tasks are created, to sync them to GitHub
- After GitHub issues are updated, to reflect changes in your agent system
- Periodically (hourly/daily) to ensure sync integrity
- After manual changes in either system

### Usage

```bash
python3 scripts/sync-projects-v2.py \
  --owner "username" \
  --repo "repository-name" \
  --project "project-id-or-name" \
  --agent-db "path/to/agent-tasks.db"
```

### Parameters

- `--owner`: GitHub username or organization (required)
- `--repo`: Repository name (required)
- `--project`: Project ID or name (required)
- `--agent-db`: Path to agent task database (required)
- `--dry-run`: Preview changes without applying (optional)
- `--direction`: Sync direction - "both", "to-github", "from-github" (optional, default: "both")
- `--verbose`: Enable detailed logging (optional)

### Example Output

```
[INFO] Sync Projects V2 started at 2024-01-15 14:30:00
[INFO] Fetching issues from GitHub...
[INFO] Fetched 42 issues from github.com/username/repository
[INFO] Fetching tasks from agent database...
[INFO] Fetched 38 tasks from agent-tasks.db
[INFO] Analyzing differences...
[INFO] Found 4 new agent tasks to create in GitHub
[INFO] Found 2 status updates in GitHub to sync to agent
[INFO] Syncing new issues to GitHub...
[INFO]   Created issue #127: Add OAuth authentication
[INFO]   Created issue #128: Fix null pointer in profile
[INFO]   Created issue #129: Update React to v18
[INFO]   Created issue #130: Write deployment docs
[INFO] Syncing status changes to agent...
[INFO]   Updated task T-42 status: In Progress → Done
[INFO]   Updated task T-38 status: Backlog → In Progress
[INFO] Sync complete: 42 issues synchronized
[INFO] Success: 6, Failed: 0, Skipped: 36
```

### What This Script Does

1. **Fetch from GitHub**: Retrieves all issues from specified repository and project
2. **Fetch from Agent**: Retrieves all tasks from agent database
3. **Identify Differences**: Compares both systems to find:
   - New agent tasks not in GitHub → Create GitHub issues
   - New GitHub issues not in agent → Create agent tasks
   - Status changes in either system → Sync to the other
4. **Execute Sync**: Applies changes bidirectionally
5. **Report Results**: Summarizes what was synchronized

### Error Handling

The script handles common errors:
- **Authentication failure** → Prompts to run `gh auth login`
- **Project not found** → Lists available projects
- **Database connection error** → Verifies database path exists
- **API rate limiting** → Automatically backs off and retries

### Scheduling Sync

Run sync automatically using cron:

```bash
# Edit crontab
crontab -e

# Add entry to sync every hour
0 * * * * cd /path/to/project && python3 scripts/sync-projects-v2.py --owner "username" --repo "repository" --project "1" --agent-db "agent-tasks.db" >> sync.log 2>&1
```

## Bulk Label Assignment Script

**Location:** `scripts/bulk-label-assignment.py`

**Purpose:** Assigns labels to multiple issues that match filter criteria

### When to Use

- When initializing a project with consistent labeling
- When adding a new label category to all related issues
- When correcting labeling across multiple issues
- When migrating from old label system to 9-label system

### Usage

```bash
python3 scripts/bulk-label-assignment.py \
  --owner "username" \
  --repo "repository-name" \
  --filter "is:issue is:open" \
  --add-label "feature" \
  --remove-label "enhancement"
```

### Parameters

- `--owner`: GitHub username or organization (required)
- `--repo`: Repository name (required)
- `--filter`: GitHub search filter using standard GitHub search syntax (required)
- `--add-label`: Label to add (optional, but --add-label or --remove-label required)
- `--remove-label`: Label to remove (optional)
- `--dry-run`: Preview changes without applying (optional)
- `--confirm`: Require confirmation before executing (optional, default: true)

### Filter Syntax

Use GitHub's standard search syntax:
- `is:issue` - Only issues (not PRs)
- `is:pr` - Only pull requests
- `is:open` - Only open items
- `is:closed` - Only closed items
- `label:bug` - Items with specific label
- `no:label` - Items without any labels
- `created:>2024-01-01` - Created after date
- `author:username` - Created by user

### Examples

**Example 1: Add "feature" to all unlabeled issues**
```bash
python3 scripts/bulk-label-assignment.py \
  --owner "myorg" \
  --repo "backend-api" \
  --filter "is:issue is:open no:label" \
  --add-label "feature"
```

**Example 2: Replace "enhancement" with "feature"**
```bash
python3 scripts/bulk-label-assignment.py \
  --owner "myorg" \
  --repo "backend-api" \
  --filter "is:issue label:enhancement" \
  --remove-label "enhancement" \
  --add-label "feature"
```

**Example 3: Add "backlog" to recent bugs**
```bash
python3 scripts/bulk-label-assignment.py \
  --owner "myorg" \
  --repo "backend-api" \
  --filter "is:issue is:open label:bug created:>2024-01-01" \
  --add-label "backlog"
```

### Expected Output

```
[INFO] Bulk Label Assignment started
[INFO] Filter: is:issue is:open no:label
[INFO] Searching for matching issues...
[INFO] Found 15 matching issues:
[INFO]   #123: Add user authentication
[INFO]   #124: Fix navigation bug
[INFO]   #125: Update dependencies
[INFO]   ... (12 more)
[INFO]
[INFO] Planned changes:
[INFO]   Add label: feature
[INFO]   Remove label: (none)
[INFO]
[PROMPT] Apply these changes to 15 issues? (y/n):
```

After confirmation:
```
[INFO] Applying changes...
[INFO]   ✓ Updated issue #123
[INFO]   ✓ Updated issue #124
[INFO]   ✓ Updated issue #125
[INFO]   ... (12 more)
[INFO] Successfully updated 15 issues
[INFO] Failed: 0
```

## Pull Request Monitor Script

**Location:** `scripts/monitor-pull-requests.py`

**Purpose:** Monitors pull request status and alerts when action is needed

### When to Use

- During active development to track CI/CD failures
- When waiting for code reviews
- When troubleshooting merge conflicts or test failures
- To generate daily PR status reports

### Usage

```bash
python3 scripts/monitor-pull-requests.py \
  --owner "username" \
  --repo "repository-name" \
  --check-interval 60 \
  --watch-states "pending,failed"
```

### Parameters

- `--owner`: GitHub username or organization (required)
- `--repo`: Repository name (required)
- `--check-interval`: Check interval in seconds (optional, default: 60)
- `--watch-states`: Comma-separated states to watch - "pending,failed,success" (optional, default: "pending,failed")
- `--notify`: Notification method - "stdout,email,slack" (optional, default: "stdout")
- `--continuous`: Run continuously (optional, default: false for single check)

### Example Output

```
[INFO] PR Monitor started at 2024-01-15 14:30:00
[INFO] Monitoring 5 open pull requests in username/repository

[WATCH] PR #42: Add OAuth authentication
  Status: Review pending
  Checks: 3/3 passing ✓
  Reviews: 0/2 approvals
  Waiting: 2h 15m

[ALERT] PR #38: Fix null pointer exception
  Status: CI/CD pipeline failed ✗
  Checks: 2/3 failed
    ✓ build (1m 30s)
    ✗ test (2m 45s) - 3 tests failed
    ✗ lint (0m 45s) - 12 issues found
  Reviews: 1/2 approvals
  Action needed: Fix failing tests and linting issues

[WATCH] PR #39: Update React dependencies
  Status: Ready to merge ✓
  Checks: 3/3 passing ✓
  Reviews: 2/2 approvals ✓
  Action needed: Merge when ready

[INFO] Summary:
  Total PRs: 5
  Ready to merge: 1
  Awaiting review: 2
  Failed checks: 1
  Awaiting author: 1

[INFO] Next check in 60 seconds...
```

### Notification Options

**Email Notifications:**
```bash
python3 scripts/monitor-pull-requests.py \
  --owner "username" \
  --repo "repository" \
  --notify "email" \
  --email-to "dev-team@company.com" \
  --email-smtp "smtp.gmail.com:587" \
  --email-from "ci@company.com"
```

**Slack Notifications:**
```bash
python3 scripts/monitor-pull-requests.py \
  --owner "username" \
  --repo "repository" \
  --notify "slack" \
  --slack-webhook "https://hooks.slack.com/services/..."
```

## Bulk Issue Creation Script

**Location:** `scripts/bulk-create-issues.py`

**Purpose:** Create multiple issues from CSV file or JSON data

### When to Use

- When importing issues from another system
- When creating a large number of related issues
- When templating common issue patterns

### Usage

```bash
python3 scripts/bulk-create-issues.py \
  --owner "username" \
  --repo "repository-name" \
  --input "issues.csv" \
  --project "1"
```

### CSV Format

```csv
title,body,label,assignee
"Add OAuth authentication","Implement OAuth 2.0 for Google login",feature,@auth-dev
"Fix null pointer in profile","Fix crash when user has no avatar",bug,@backend-dev
"Update React to v18","Upgrade React dependency",dependencies,@frontend-dev
```

### JSON Format

```json
[
  {
    "title": "Add OAuth authentication",
    "body": "Implement OAuth 2.0 for Google login",
    "label": "feature",
    "assignee": "@auth-dev"
  },
  {
    "title": "Fix null pointer in profile",
    "body": "Fix crash when user has no avatar",
    "label": "bug",
    "assignee": "@backend-dev"
  }
]
```

### Example Output

```
[INFO] Bulk Issue Creation started
[INFO] Reading input file: issues.csv
[INFO] Found 25 issues to create
[INFO] Creating issues in username/repository...
[INFO]   Created issue #127: Add OAuth authentication
[INFO]   Created issue #128: Fix null pointer in profile
[INFO]   Created issue #129: Update React to v18
[INFO]   ... (22 more)
[INFO] Successfully created 25 issues
[INFO] Failed: 0
```

## Project Reporting Script

**Location:** `scripts/generate-project-report.py`

**Purpose:** Generate comprehensive reports on project status and metrics

### When to Use

- Weekly/monthly project status updates
- Sprint reviews and retrospectives
- Stakeholder reporting
- Tracking progress over time

### Usage

```bash
python3 scripts/generate-project-report.py \
  --owner "username" \
  --repo "repository-name" \
  --project "1" \
  --output "report.md" \
  --format "markdown"
```

### Parameters

- `--owner`: GitHub username or organization (required)
- `--repo`: Repository name (required)
- `--project`: Project ID (required)
- `--output`: Output file path (optional, default: stdout)
- `--format`: Output format - "markdown", "html", "json" (optional, default: "markdown")
- `--period`: Reporting period - "week", "month", "quarter" (optional, default: "week")

### Example Output (Markdown)

```markdown
# Project Report: Backend Development Q1 2024
Generated: 2024-01-15 14:30:00

## Summary

- **Total Issues**: 42
- **Open**: 28 (67%)
- **Closed**: 14 (33%)
- **In Progress**: 8
- **AI Review**: 5

## By Label (9-Label System)

| Label | Open | Closed | Total | % of Total |
|-------|------|--------|-------|------------|
| feature | 12 | 5 | 17 | 40% |
| bug | 8 | 6 | 14 | 33% |
| refactor | 3 | 2 | 5 | 12% |
| test | 2 | 1 | 3 | 7% |
| docs | 3 | 0 | 3 | 7% |

## Recent Activity

### Last 7 Days
- **Created**: 8 issues
- **Closed**: 5 issues
- **PRs Merged**: 6

### Top Contributors
1. @backend-dev: 12 issues closed
2. @frontend-dev: 8 issues closed
3. @qa-lead: 4 issues closed

## Velocity

- **Average Time to Close**: 5.2 days
- **Average Time in Review**: 1.8 days
- **Issues Closed per Week**: 4.2

## Blockers

- PR #38: Failing tests (2 days blocked)
- Issue #89: Waiting for external API access

## Next Sprint Planning

### Ready to Start (5 issues)
- #101: Add pagination to user list
- #102: Implement rate limiting
- #103: Add caching layer
- #104: Write API documentation
- #105: Update error handling
```

## Script Installation and Setup

### Prerequisites

All scripts require:
- Python 3.8 or higher
- GitHub CLI (`gh`) installed and authenticated
- Required Python packages (see `requirements.txt`)

### Installation Steps

**1. Install Python dependencies:**
```bash
pip install -r scripts/requirements.txt
```

**2. Make scripts executable:**
```bash
chmod +x scripts/*.py
chmod +x scripts/*.sh
```

**3. Configure environment variables:**
```bash
# Create .env file
cat > .env << EOF
GITHUB_OWNER=your-username
GITHUB_REPO=your-repository
PROJECT_ID=1
AGENT_DB_PATH=agent-tasks.db
EOF
```

**4. Test installation:**
```bash
python3 scripts/sync-projects-v2.py --help
```

## Best Practices

1. **Run with --dry-run first** - Always preview changes before applying
2. **Use version control** - Keep scripts in Git for tracking changes
3. **Log all operations** - Enable verbose logging for troubleshooting
4. **Schedule regular syncs** - Use cron for hourly/daily synchronization
5. **Monitor script output** - Review logs regularly for errors
6. **Handle API rate limits** - Add sleep between operations
7. **Back up before bulk operations** - Create backups before major changes
8. **Test on small datasets** - Verify scripts work before full execution
