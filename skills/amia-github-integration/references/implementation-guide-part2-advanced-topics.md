# Implementation Guide Part 2: Advanced Topics

## Use-Case TOC
- When you need to onboard your team → [Team Onboarding](#team-onboarding)
- When you need multi-repo projects → [Multi-Repository Projects](#multi-repository-projects)
- When you need custom GitHub Actions → [Custom GitHub Actions Workflows](#custom-github-actions-workflows)
- When you need advanced GraphQL queries → [Advanced GraphQL Queries](#advanced-graphql-queries)
- When you need real-time webhooks → [Real-time Webhooks](#real-time-webhooks)
- When you need CI/CD integration → [CI/CD Integration](#cicd-integration)
- When you need to measure success → [Success Metrics](#success-metrics)
- For basic workflow setup → See [implementation-guide-part1-basic-workflow.md](implementation-guide-part1-basic-workflow.md)

## Table of Contents

- [Team Onboarding](#team-onboarding)
  - [Onboarding New Team Members](#onboarding-new-team-members)
  - [Training Materials](#training-materials)
- [Advanced Implementation Topics](#advanced-implementation-topics)
  - [Multi-Repository Projects](#multi-repository-projects)
  - [Custom GitHub Actions Workflows](#custom-github-actions-workflows)
  - [Advanced GraphQL Queries](#advanced-graphql-queries)
  - [Real-time Webhooks](#real-time-webhooks)
  - [CI/CD Integration](#cicd-integration)
- [Success Metrics](#success-metrics)
  - [Adoption Metrics](#adoption-metrics)
  - [Quality Metrics](#quality-metrics)
  - [Efficiency Metrics](#efficiency-metrics)
  - [Team Satisfaction](#team-satisfaction)

---

## Team Onboarding

### Onboarding New Team Members

**Day 1: Setup**
- [ ] Provide GitHub account access
- [ ] Grant repository write permissions
- [ ] Add to Projects V2 board
- [ ] Install and authenticate GitHub CLI
- [ ] Clone repository

**Day 2: Training**
- [ ] Review 9-label system
- [ ] Demonstrate issue creation
- [ ] Show Projects V2 board usage
- [ ] Explain PR workflow
- [ ] Practice creating test issue and PR

**Week 1: Supervised Practice**
- [ ] Create first real issue under supervision
- [ ] Create first PR with code review
- [ ] Participate in sprint planning
- [ ] Use Projects V2 board to track work

**Ongoing:**
- [ ] Answer questions as they arise
- [ ] Review issue/PR quality regularly
- [ ] Provide feedback and coaching
- [ ] Share best practices

### Training Materials

Create these materials for team reference:

1. **Quick Start Guide** (1-2 pages)
   - Most common commands
   - Issue template
   - PR template
   - When to use each label

2. **Detailed Workflow Guide** (5-10 pages)
   - Complete issue lifecycle
   - PR creation and review process
   - Projects V2 usage
   - Troubleshooting common issues

3. **Video Tutorials** (optional)
   - Screen recording of issue creation
   - Screen recording of PR workflow
   - Demo of Projects V2 board

---

## Advanced Implementation Topics

For teams ready to go beyond basic implementation, these advanced topics extend the GitHub integration capabilities. These features are optional and should only be implemented after mastering the basic workflow.

### Multi-Repository Projects

**Purpose:** Manage work across multiple related repositories in a single project board.

**Use cases:**
- Microservices architecture with separate repositories
- Frontend/backend split repositories
- Mono-repository with multiple subprojects

**Implementation steps:**
1. Create organization-level Projects V2 board
2. Enable auto-add workflow for multiple repositories
3. Add custom field "Repository" to track source
4. Filter and group by repository in project views

**Commands:**
```bash
# Create organization project
gh project create --title "Multi-Repo Project" --owner "@org-name"

# Add issues from multiple repos
gh project item-add <project_id> --url "https://github.com/org/repo1/issues/1"
gh project item-add <project_id> --url "https://github.com/org/repo2/issues/5"
```

**Sync considerations:**
- Maintain separate sync agents for each repository
- Use repository prefix in task IDs to avoid collisions
- Implement cross-repository dependency tracking

### Custom GitHub Actions Workflows

**Purpose:** Automate complex status transitions and notifications beyond built-in automation.

**Common workflows:**

**1. Auto-label based on file changes:**
```yaml
name: Auto-label PR
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@v4
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          configuration-path: .github/labeler.yml
```

**2. Slack notification for high-priority issues:**
```yaml
name: Notify High Priority
on:
  issues:
    types: [labeled]

jobs:
  notify:
    if: github.event.label.name == 'high-priority'
    runs-on: ubuntu-latest
    steps:
      - name: Send Slack notification
        uses: slackapi/slack-github-action@v1
        with:
          webhook: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {"text": "High priority issue: ${{ github.event.issue.html_url }}"}
```

**3. Auto-update project status:**
```yaml
name: Update Project Status
on:
  pull_request:
    types: [opened, closed, ready_for_review]

jobs:
  update-status:
    runs-on: ubuntu-latest
    steps:
      - name: Update Projects V2
        uses: actions/github-script@v7
        with:
          script: |
            // GraphQL mutation to update project status
            const mutation = `mutation { updateProjectV2ItemFieldValue(...) }`
            await github.graphql(mutation)
```

### Advanced GraphQL Queries

**Purpose:** Perform complex filtering and bulk operations efficiently.

**Example 1: Fetch all issues with specific label and status:**
```bash
gh api graphql -f query='
query {
  repository(owner: "owner", name: "repo") {
    issues(first: 100, filterBy: {labels: ["feature"], states: OPEN}) {
      nodes {
        number
        title
        projectItems(first: 5) {
          nodes {
            fieldValueByName(name: "Status") {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
              }
            }
          }
        }
      }
    }
  }
}'
```

**Example 2: Bulk update issue statuses:**
```bash
gh api graphql -f query='
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PROJECT_ID"
    itemId: "ITEM_ID"
    fieldId: "FIELD_ID"
    value: {singleSelectOptionId: "OPTION_ID"}
  }) {
    projectV2Item {
      id
    }
  }
}'
```

**Example 3: Generate custom metrics:**
```bash
gh api graphql -f query='
query {
  repository(owner: "owner", name: "repo") {
    issues(first: 100) {
      totalCount
      nodes {
        labels(first: 10) {
          nodes {
            name
          }
        }
        createdAt
        closedAt
      }
    }
  }
}' | jq '[.data.repository.issues.nodes[] | {
  label: .labels.nodes[0].name,
  duration: (.closedAt | if . then (fromdateiso8601 - (.createdAt | fromdateiso8601)) else null end)
}] | group_by(.label) | map({label: .[0].label, avg_duration: (map(.duration // 0) | add / length)})'
```

### Real-time Webhooks

**Purpose:** Enable instant synchronization instead of polling-based sync.

**Setup webhook receiver:**
```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "your-webhook-secret"

@app.route('/webhook', methods=['POST'])
def webhook():
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    body = request.data
    expected = 'sha256=' + hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, expected):
        return {'error': 'Invalid signature'}, 401

    # Process webhook event
    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    if event == 'issues':
        handle_issue_event(payload)
    elif event == 'pull_request':
        handle_pr_event(payload)

    return {'status': 'ok'}

def handle_issue_event(payload):
    action = payload['action']
    issue = payload['issue']

    if action == 'opened':
        # Sync new issue to agent
        sync_agent.create_task(issue)
    elif action == 'edited':
        # Update existing task
        sync_agent.update_task(issue)
    elif action == 'closed':
        # Mark task complete
        sync_agent.complete_task(issue)
```

**Configure webhook in GitHub:**
1. Repository Settings → Webhooks → Add webhook
2. Payload URL: `https://your-server.com/webhook`
3. Content type: `application/json`
4. Secret: Set matching secret
5. Events: Select "Issues", "Pull requests", "Projects v2 items"
6. Active: Checked

**Security best practices:**
- Always verify webhook signature
- Use HTTPS for webhook endpoint
- Rotate webhook secret regularly
- Implement rate limiting on webhook endpoint
- Log all webhook deliveries for audit

### CI/CD Integration

**Purpose:** Link issue tracking to deployment lifecycle.

**Example: Tag issues with deployment environment:**
```yaml
name: Tag Deployed Issues
on:
  deployment_status:
    types: [success]

jobs:
  tag-issues:
    runs-on: ubuntu-latest
    steps:
      - name: Extract issue numbers from commits
        id: issues
        run: |
          # Get commits in deployment
          COMMITS=$(gh api repos/${{ github.repository }}/deployments/${{ github.event.deployment.id }}/statuses)
          # Extract issue numbers
          ISSUES=$(echo "$COMMITS" | grep -oP '#\K\d+' | sort -u)
          echo "issues=$ISSUES" >> $GITHUB_OUTPUT

      - name: Add deployment label
        run: |
          for ISSUE in ${{ steps.issues.outputs.issues }}; do
            gh issue edit $ISSUE --add-label "deployed-${{ github.event.deployment.environment }}"
          done
```

**Example: Generate release notes from issues:**
```bash
#!/bin/bash
# generate-release-notes.sh

PREVIOUS_TAG=$(git describe --tags --abbrev=0 HEAD^)
CURRENT_TAG=$(git describe --tags --abbrev=0 HEAD)

# Get all issues closed between tags
ISSUES=$(git log $PREVIOUS_TAG..$CURRENT_TAG --oneline | grep -oP 'Closes #\K\d+' | sort -u)

echo "# Release Notes: $CURRENT_TAG"
echo ""
echo "## Features"
for ISSUE in $ISSUES; do
  LABEL=$(gh issue view $ISSUE --json labels --jq '.labels[0].name')
  if [ "$LABEL" == "feature" ]; then
    TITLE=$(gh issue view $ISSUE --json title --jq '.title')
    echo "- #$ISSUE: $TITLE"
  fi
done

echo ""
echo "## Bug Fixes"
for ISSUE in $ISSUES; do
  LABEL=$(gh issue view $ISSUE --json labels --jq '.labels[0].name')
  if [ "$LABEL" == "bug" ]; then
    TITLE=$(gh issue view $ISSUE --json title --jq '.title')
    echo "- #$ISSUE: $TITLE"
  fi
done
```

**Best practices:**
- Tag issues with deployment environment (staging, production)
- Track deployment timestamp in custom field
- Link deployments to specific issue resolution
- Generate release notes automatically from closed issues
- Archive issues only after successful production deployment

---

## Success Metrics

Track these metrics to measure implementation success:

### Adoption Metrics
- % of team using issue workflow
- % of PRs properly linked to issues
- % of issues with correct labels
- Projects V2 board usage frequency

### Quality Metrics
- Average time to close issues
- Average time in review
- % of issues closed on first PR
- Number of reopened issues

### Efficiency Metrics
- Issues closed per week/sprint
- PRs merged per week/sprint
- Sync success rate
- CI/CD pass rate

### Team Satisfaction
- Workflow satisfaction score (survey)
- Number of process improvement suggestions
- Reduction in manual coordination overhead

---

**See also:** [implementation-guide-part1-basic-workflow.md](implementation-guide-part1-basic-workflow.md) for basic workflow setup and implementation checklist.
