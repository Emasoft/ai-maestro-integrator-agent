# Core Concepts

## Use-Case TOC
- When you need to understand GitHub Projects V2 → [What is GitHub Projects V2](#what-is-github-projects-v2)
- When you need to understand the label system → [The 9-Label System](#the-9-label-system)
- When you need to understand synchronization → [Bidirectional Synchronization](#bidirectional-synchronization)
- When choosing which label to use → [Label Selection Guide](#label-selection-guide)

## Table of Contents

- [What is GitHub Projects V2](#what-is-github-projects-v2)
  - [Projects V2 vs Legacy Projects](#projects-v2-vs-legacy-projects)
  - [Why Use Projects V2](#why-use-projects-v2)
- [The 9-Label System](#the-9-label-system)
  - [Why Nine Labels?](#why-nine-labels)
  - [Label Selection Guide](#label-selection-guide)
  - [Important Rules](#important-rules)
- [Label Selection Guide](#label-selection-guide)
- [Bidirectional Synchronization](#bidirectional-synchronization)
  - [How Bidirectional Sync Works](#how-bidirectional-sync-works)
  - [Sync Triggers](#sync-triggers)
  - [Conflict Resolution](#conflict-resolution)
  - [Sync Health Monitoring](#sync-health-monitoring)
  - [When Sync Fails](#when-sync-fails)
- [Best Practices](#best-practices)
  - [For Projects V2](#for-projects-v2)
  - [For Labels](#for-labels)
  - [For Synchronization](#for-synchronization)

---

## What is GitHub Projects V2

GitHub Projects V2 is a table-based project management system built directly into GitHub repositories. Unlike the legacy Projects system, Projects V2 provides:

- **Customizable Tables**: Fields beyond built-in properties like title and assignees
- **Bidirectional Sync**: Automatic synchronization between pull requests, issues, and custom fields
- **Automation Rules**: Conditional workflows that trigger on status changes
- **Status Tracking**: Visual representation of work progress through custom status fields

### Projects V2 vs Legacy Projects

| Feature | Legacy Projects | Projects V2 |
|---------|----------------|-------------|
| Custom fields | No | Yes |
| Bidirectional sync | No | Yes |
| Automation | Limited | Extensive |
| Multi-repository | No | Yes |
| API access | GraphQL only | GraphQL + REST |

### Why Use Projects V2

Projects V2 provides:
1. **Centralized View**: See all work items across multiple repositories
2. **Custom Workflows**: Define status transitions specific to your team
3. **Real-time Updates**: Changes in GitHub automatically reflect in the project
4. **Advanced Filtering**: Filter and group by any field
5. **Integration Ready**: API access for automation and synchronization

## The 9-Label System

The 9-label system is a standardized classification approach that categorizes all GitHub issues and pull requests into exactly nine mutually-exclusive or clearly-separated categories:

1. **feature** - New functionality or enhancement
2. **bug** - Defect requiring correction
3. **refactor** - Code quality improvements
4. **test** - Testing infrastructure and coverage
5. **docs** - Documentation and examples
6. **performance** - Speed and efficiency improvements
7. **security** - Security vulnerability or hardening
8. **dependencies** - Dependency management and updates
9. **workflow** - Development process and automation improvements

### Why Nine Labels?

The 9-label system provides:

- **Standardization**: Consistent categorization across all projects
- **Simplicity**: Small enough to remember, large enough to cover all cases
- **Filtering**: Easy to filter by category in GitHub and Projects V2
- **Automation**: Simple rules for automated routing and priority assignment
- **Metrics**: Clear tracking of effort distribution across categories

### Label Selection Guide

| If your work involves... | Use label... | Example |
|--------------------------|-------------|---------|
| Adding new capability | `feature` | "Add user authentication" |
| Fixing incorrect behavior | `bug` | "Fix null pointer crash" |
| Improving code structure | `refactor` | "Extract service layer" |
| Adding tests | `test` | "Add integration tests" |
| Writing docs/guides | `docs` | "Write API documentation" |
| Optimizing performance | `performance` | "Reduce load time" |
| Security hardening | `security` | "Add CSRF protection" |
| Updating dependencies | `dependencies` | "Upgrade React to v18" |
| CI/CD or tooling | `workflow` | "Add GitHub Actions" |

### Important Rules

- **Each issue MUST have exactly one label** from the 9-label system
- **Labels are case-sensitive** - "Feature" ≠ "feature"
- **No mixing categories** - If work spans multiple categories, create separate issues
- **Project-specific labels** can supplement but not replace the 9-label system

## Label Selection Guide

Use this decision guide when choosing which label to apply:

**Start here:** What is the primary purpose of this issue?

- **Adding new capability users can access?** → `feature`
- **Fixing something that doesn't work correctly?** → `bug`
- **Improving code without changing behavior?** → `refactor`
- **Adding or improving tests?** → `test`
- **Writing or updating documentation?** → `docs`
- **Making something faster or more efficient?** → `performance`
- **Addressing security vulnerability or hardening?** → `security`
- **Updating library or framework versions?** → `dependencies`
- **Improving CI/CD, build, or development tools?** → `workflow`

**When uncertain:**
1. Read the issue description carefully
2. Identify the primary goal (not side effects)
3. Choose the label that best matches the primary goal
4. If truly split between two categories, create two separate issues

**Examples of correct labeling:**
- "Add OAuth login" → `feature` (primary: new capability)
- "Fix crash on login" → `bug` (primary: defect)
- "Extract auth service layer" → `refactor` (primary: code structure)
- "Add login integration tests" → `test` (primary: testing)
- "Optimize login query" → `performance` (primary: speed)

## Bidirectional Synchronization

Bidirectional synchronization means that changes in one direction (agent creates issue → GitHub updates) automatically trigger updates in the other direction (GitHub status changes → agent is notified). This prevents manual duplication of work and keeps all systems in perfect alignment.

### How Bidirectional Sync Works

**Direction 1: Agent → GitHub**
```
Agent creates task
    ↓
Sync script creates GitHub issue
    ↓
Issue appears in Projects V2
    ↓
Issue gets status "Backlog"
```

**Direction 2: GitHub → Agent**
```
User updates issue status in Projects V2
    ↓
Webhook or polling detects change
    ↓
Sync script updates agent task
    ↓
Agent reflects new status
```

### Sync Triggers

**Actions that trigger sync from Agent to GitHub:**
- Agent creates new task
- Agent updates task status
- Agent assigns task to user
- Agent sets due date or priority

**Actions that trigger sync from GitHub to Agent:**
- Issue status changes in Projects V2
- Issue is assigned or reassigned
- Issue is closed
- Pull request is linked to issue
- Pull request is merged

### Conflict Resolution

When conflicts occur (e.g., both systems update status simultaneously):

1. **GitHub wins**: GitHub is the source of truth for issue metadata
2. **Agent reconciles**: Agent updates its state to match GitHub
3. **Audit trail**: All conflicts are logged for review
4. **Manual override**: Agents can force-update with explicit flag

### Sync Health Monitoring

To ensure sync is working correctly:

```bash
# Check last sync time
gh api graphql -f query='{ viewer { login } }'

# Verify issue count matches
gh issue list --limit 1000 --json number | jq 'length'

# Check for sync errors in logs
tail -f sync-projects-v2.log
```

### When Sync Fails

If synchronization fails:
1. Check GitHub CLI authentication: `gh auth status`
2. Verify project ID exists: `gh project list`
3. Review sync logs for error messages
4. Re-run sync script manually: `python3 scripts/sync-projects-v2.py`
5. Check webhook configuration (if using webhooks)

## Best Practices

### For Projects V2

- Create one project per major feature area
- Use consistent status values across all projects
- Link all pull requests to their corresponding issues
- Automate status transitions when possible

### For Labels

- Apply label immediately when creating issue
- Never create issues without a label from the 9-label system
- Document label usage in your CONTRIBUTING.md
- Review label distribution monthly to ensure balance

### For Synchronization

- Run sync script at least daily (hourly for active projects)
- Monitor sync logs for failures
- Set up alerts for sync failures
- Test sync with a small number of issues first
