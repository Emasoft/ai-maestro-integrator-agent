# Implementation Guide Part 2: Agent Orchestrator Integration

## Table of Contents

- [Integration Architecture](#integration-architecture)
- [Integration Patterns](#integration-patterns)
  - [Pattern 1: Automatic Issue Creation](#pattern-1-automatic-issue-creation)
  - [Pattern 2: Status Synchronization](#pattern-2-status-synchronization)
  - [Pattern 3: Automated PR Creation](#pattern-3-automated-pr-creation)
- [Agent Configuration](#agent-configuration)
- [Monitoring Agent-GitHub Health](#monitoring-agent-github-health)
- [Next Steps After Implementation](#next-steps-after-implementation)
  - [1. Start Using the Workflow](#1-start-using-the-workflow)
  - [2. Monitor Synchronization](#2-monitor-synchronization)
  - [3. Collect Team Feedback](#3-collect-team-feedback)
  - [4. Optimize Workflow](#4-optimize-workflow)
  - [5. Scale Implementation](#5-scale-implementation)
- [Team Onboarding](#team-onboarding)
  - [Onboarding New Team Members](#onboarding-new-team-members)
  - [Training Materials](#training-materials)

This skill is designed to integrate with agent orchestrators to automate GitHub operations.

## Integration Architecture

```
┌─────────────────────┐
│  Agent Orchestrator │
│                     │
│  ┌───────────────┐  │      ┌──────────────┐
│  │  Task Manager │  │◄────►│ GitHub API   │
│  └───────────────┘  │      └──────────────┘
│          ▲          │              │
│          │          │              ▼
│  ┌───────┴───────┐  │      ┌──────────────┐
│  │   Sync Agent  │  │◄────►│ Projects V2  │
│  └───────────────┘  │      └──────────────┘
└─────────────────────┘
```

## Integration Patterns

### Pattern 1: Automatic Issue Creation

```python
# Agent creates task
task = orchestrator.create_task(
    title="Add OAuth authentication",
    description="Implement OAuth 2.0 for Google login",
    type="feature"
)

# Sync agent creates GitHub issue
github_issue = sync_agent.create_issue(
    title=task.title,
    body=task.description,
    label=task.type,  # Maps to 9-label system
    project_id=config.project_id
)

# Link task to issue
task.github_issue_id = github_issue.number
orchestrator.save_task(task)
```

### Pattern 2: Status Synchronization

```python
# GitHub webhook receives issue update
@webhook.route('/github/issues', methods=['POST'])
def handle_issue_update():
    payload = request.json
    issue_number = payload['issue']['number']
    new_status = get_project_status(issue_number)

    # Update agent task
    task = orchestrator.find_task_by_issue(issue_number)
    task.status = map_status(new_status)
    orchestrator.save_task(task)

    return {'status': 'ok'}
```

### Pattern 3: Automated PR Creation

```python
# Agent completes task
orchestrator.on_task_complete(task_id, callback=lambda task: {
    # Create branch
    repo.create_branch(f"feature/issue-{task.github_issue_id}"),

    # Commit changes
    repo.commit_changes(task.changes),

    # Create PR
    github.create_pr(
        title=task.title,
        body=f"Closes #{task.github_issue_id}",
        head=f"feature/issue-{task.github_issue_id}",
        base="main"
    )
})
```

## Agent Configuration

Enable GitHub integration in agent config:

```yaml
# agent-config.yml
github:
  enabled: true
  owner: "username"
  repo: "repository"
  project_id: 1
  sync_interval: 3600  # 1 hour
  auto_create_issues: true
  auto_create_prs: true
  label_mapping:
    feature: "feature"
    bug: "bug"
    refactor: "refactor"
    test: "test"
```

## Monitoring Agent-GitHub Health

Track sync metrics:

```python
# Monitor sync health
sync_metrics = {
    'last_sync_time': sync_agent.last_sync,
    'issues_synced': sync_agent.issues_synced_count,
    'errors': sync_agent.error_count,
    'pending_syncs': sync_agent.pending_count
}

# Alert if sync is stale
if (now - sync_metrics['last_sync_time']) > timedelta(hours=2):
    alert_ops("GitHub sync is stale")
```

---

# Next Steps After Implementation

After completing the implementation checklist:

## 1. Start Using the Workflow

- Create your first real issue following documented process
- Create corresponding PR with proper linking
- Merge PR and verify issue closes automatically

## 2. Monitor Synchronization

- Check sync logs daily for first week
- Verify bidirectional sync is working correctly
- Address any sync failures immediately

## 3. Collect Team Feedback

- Ask team members about workflow effectiveness
- Identify pain points or confusion
- Document FAQs based on questions

## 4. Optimize Workflow

- Adjust label system if needed (add project-specific labels)
- Refine project board structure
- Tune automation rules based on usage patterns

## 5. Scale Implementation

- As project grows, consider multiple projects for different areas
- Create team-specific boards if needed
- Implement advanced automation with GitHub Actions

---

# Team Onboarding

## Onboarding New Team Members

### Day 1: Setup

- [ ] Provide GitHub account access
- [ ] Grant repository write permissions
- [ ] Add to Projects V2 board
- [ ] Install and authenticate GitHub CLI
- [ ] Clone repository

### Day 2: Training

- [ ] Review 9-label system
- [ ] Demonstrate issue creation
- [ ] Show Projects V2 board usage
- [ ] Explain PR workflow
- [ ] Practice creating test issue and PR

### Week 1: Supervised Practice

- [ ] Create first real issue under supervision
- [ ] Create first PR with code review
- [ ] Participate in sprint planning
- [ ] Use Projects V2 board to track work

### Ongoing

- [ ] Answer questions as they arise
- [ ] Review issue/PR quality regularly
- [ ] Provide feedback and coaching
- [ ] Share best practices

## Training Materials

Create these materials for team reference:

### 1. Quick Start Guide (1-2 pages)

- Most common commands
- Issue template
- PR template
- When to use each label

### 2. Detailed Workflow Guide (5-10 pages)

- Complete issue lifecycle
- PR creation and review process
- Projects V2 usage
- Troubleshooting common issues

### 3. Video Tutorials (optional)

- Screen recording of issue creation
- Screen recording of PR workflow
- Demo of Projects V2 board
