# Issue Management

## Table of Contents

- [Use-Case TOC](#use-case-toc)
- [Creating Issues](#creating-issues)
  - [Basic Issue Creation Syntax](#basic-issue-creation-syntax)
  - [Parameters](#parameters)
  - [Examples](#examples)
- [Assigning Labels](#assigning-labels)
  - [Multiple Labels](#multiple-labels)
  - [Creating Labels](#creating-labels)
  - [Adding Labels to Existing Issues](#adding-labels-to-existing-issues)
  - [Removing Labels from Issues](#removing-labels-from-issues)
  - [Listing All Labels](#listing-all-labels)
- [Issue Lifecycle](#issue-lifecycle)
  - [Typical Issue Lifecycle](#typical-issue-lifecycle)
  - [Phase 1: Issue Creation](#phase-1-issue-creation)
  - [Phase 2: Issue Transition (Backlog → In Progress)](#phase-2-issue-transition-backlog--in-progress)
  - [Phase 3: Work Completion (In Progress → AI Review)](#phase-3-work-completion-in-progress--ai-review)
  - [Phase 4: Issue Closure (AI Review → Done)](#phase-4-issue-closure-ai-review--done)
- [Linking Issues to PRs](#linking-issues-to-prs)
  - [Linking Keywords](#linking-keywords)
  - [Multiple Issue Linking](#multiple-issue-linking)
  - [Example PR Body with Issue Linking](#example-pr-body-with-issue-linking)
- [Closing Issues](#closing-issues)
  - [Automatic Closure](#automatic-closure)
  - [Manual Closure](#manual-closure)
  - [Reopening Issues](#reopening-issues)
- [Batch Issue Creation](#batch-issue-creation)
- [Best Practices](#best-practices)

## Use-Case TOC
- When you need to create a new issue → [Creating Issues](#creating-issues)
- When you need to assign labels → [Assigning Labels](#assigning-labels)
- When you need to update issue status → [Issue Lifecycle](#issue-lifecycle)
- When you need to link issues to pull requests → [Linking Issues to PRs](#linking-issues-to-prs)
- When you need to close an issue → [Closing Issues](#closing-issues)
- If you need to create multiple issues → [Batch Issue Creation](#batch-issue-creation)

## Creating Issues

Create issues programmatically with proper label assignment from the 9-label system.

### Basic Issue Creation Syntax

```bash
gh issue create \
  --title "Title of the issue" \
  --body "Detailed description of the issue" \
  --label "feature" \
  --assignee "@username" \
  --project "1"
```

### Parameters

- `--title`: Short, descriptive title (required)
  - Format: "Action + Object" (e.g., "Add user login", "Fix navigation bug")
  - Keep under 80 characters
  - Use imperative mood

- `--body`: Detailed description supporting context and acceptance criteria (required)
  - Include background/context
  - Define acceptance criteria
  - List related issues or dependencies
  - Provide examples if applicable

- `--label`: One label from the 9-label system (required)
  - Must be: feature, bug, refactor, test, docs, performance, security, dependencies, or workflow
  - Case-sensitive
  - Label must already exist in repository

- `--assignee`: GitHub username of the person responsible (optional)
  - Format: `@username` or `username`
  - Can assign multiple people: `--assignee user1 --assignee user2`

- `--project`: Project ID or name (optional but recommended)
  - Use project ID for accuracy: `--project 1`
  - Or use project name: `--project "Backend Development"`

### Examples

**Example 1: Feature Issue**
```bash
gh issue create \
  --title "Add OAuth authentication for Google login" \
  --body "Implement OAuth 2.0 flow for Google authentication.

**Acceptance Criteria:**
- Users can log in with Google account
- Profile information is retrieved from Google
- Session is maintained across browser restarts

**Related:** #42 (user authentication epic)" \
  --label "feature" \
  --assignee "@auth-team-lead" \
  --project "1"
```

**Example 2: Bug Issue**
```bash
gh issue create \
  --title "Fix null pointer exception in user profile page" \
  --body "When users with no avatar access their profile page, the app crashes.

**Steps to Reproduce:**
1. Create user without avatar
2. Navigate to /profile
3. Observe crash

**Expected:** Default avatar is shown
**Actual:** Null pointer exception

**Stack trace:** See attached logs" \
  --label "bug" \
  --assignee "@backend-dev" \
  --project "1"
```

**Example 3: Documentation Issue**
```bash
gh issue create \
  --title "Write deployment guide for Docker setup" \
  --body "Create comprehensive deployment documentation for Docker-based setup.

**Contents:**
- Prerequisites (Docker version, system requirements)
- Step-by-step deployment instructions
- Environment variable configuration
- Troubleshooting common issues

**Format:** Markdown in docs/deployment/" \
  --label "docs" \
  --assignee "@tech-writer" \
  --project "2"
```

## Assigning Labels

### Multiple Labels

While each issue must have exactly one label from the 9-label system, you can add additional project-specific labels:

```bash
gh issue create \
  --title "Security audit required for authentication" \
  --body "Conduct full security audit of login flow" \
  --label "security" \
  --label "high-priority" \
  --label "Q1-2024" \
  --assignee "@security-team-lead"
```

The first label (`security`) is from the 9-label system. Additional labels (`high-priority`, `Q1-2024`) are project-specific.

### Creating Labels

If a label doesn't exist in your repository, create it first:

```bash
gh label create "feature" \
  --description "New feature or functionality" \
  --color "0e8a16"
```

**Recommended Colors for 9-Label System:**
- `feature`: `0e8a16` (green)
- `bug`: `d73a4a` (red)
- `refactor`: `fbca04` (yellow)
- `test`: `1d76db` (blue)
- `docs`: `0075ca` (light blue)
- `performance`: `5319e7` (purple)
- `security`: `b60205` (dark red)
- `dependencies`: `0366d6` (dark blue)
- `workflow`: `c2e0c6` (light green)

### Adding Labels to Existing Issues

```bash
gh issue edit <issue_number> --add-label "feature"
```

### Removing Labels from Issues

```bash
gh issue edit <issue_number> --remove-label "old-label"
```

### Listing All Labels

```bash
gh label list --limit 100
```

## Issue Lifecycle

Issues progress through several states from creation to closure.

### Typical Issue Lifecycle

```
Created → Backlog → Todo → In Progress → AI Review → Done → Closed
```

### Phase 1: Issue Creation

When an issue is first created:
- Assign appropriate label from 9-label system
- Link to GitHub Projects V2 board
- Set initial status (e.g., "Backlog" or "Todo")
- Assign owner if known

**Commands:**
```bash
# Create issue (shown in previous sections)
gh issue create --title "..." --body "..." --label "feature" --project "1"

# Verify issue was added to project
gh project item-list 1 --owner "@username" --format json
```

### Phase 2: Issue Transition (Backlog → In Progress)

When work begins on an issue:
- Update status in Projects V2 to "In Progress"
- Assign if not already assigned
- Set due date if applicable

**Commands:**
```bash
# Update issue status in Projects V2
gh project item-edit <project_id> \
  --id "<item_id>" \
  --field-id "<status_field_id>" \
  --field-value "In Progress"

# Update assignee
gh issue edit <issue_number> --assignee "@username"
```

### Phase 3: Work Completion (In Progress → AI Review)

When work is complete and a pull request is created:
- Link pull request to issue (see [Linking Issues to PRs](#linking-issues-to-prs))
- Update status to "AI Review"
- Request code review

**Commands:**
```bash
# Create PR and link to issue
gh pr create \
  --title "Implement feature from issue #123" \
  --body "Closes #123" \
  --head "feature/issue-123"

# Status updates to "AI Review" automatically when PR is created (if automation is configured)
```

### Phase 4: Issue Closure (AI Review → Done)

When pull request is merged:
- GitHub automatically closes issue (if linked with "Closes #123")
- Status updates to "Done" in Projects V2
- Add closing comment summarizing resolution

**Commands:**
```bash
# Merge PR (automatically closes linked issue)
gh pr merge <pr_number> --squash --delete-branch

# Manually close issue with comment
gh issue close <issue_number> --comment "Resolved by PR #456"
```

## Linking Issues to PRs

GitHub automatically closes issues when pull requests containing specific keywords are merged.

### Linking Keywords

Use these keywords in the pull request body:
- `Closes #123`
- `Fixes #123`
- `Resolves #123`

**Important:** These are case-insensitive but must use the exact keyword. "Close", "Fix", "Resolve" (without the 's') will NOT work.

### Multiple Issue Linking

Link multiple issues in one PR:
```
Closes #123
Fixes #124
Resolves #125
```

### Example PR Body with Issue Linking

```bash
gh pr create \
  --title "Add OAuth authentication" \
  --body "This PR implements OAuth 2.0 authentication for Google login.

**Changes:**
- Added OAuth controller
- Implemented callback handler
- Added session management

**Closes #42**
**Related to #38**

**Testing:**
- Manual testing completed
- Unit tests added
- Integration tests passing"
```

## Closing Issues

### Automatic Closure

Issues close automatically when:
- Linked pull request is merged (using "Closes #123" syntax)
- Commit message contains "Closes #123" and is pushed to default branch

### Manual Closure

Close issues manually when:
- Issue is duplicate
- Issue is no longer relevant
- Issue is fixed without a pull request

**Commands:**
```bash
# Close with reason
gh issue close <issue_number> --comment "Duplicate of #456"

# Close and mark as "not planned"
gh issue close <issue_number> --reason "not planned"

# Close and mark as "completed"
gh issue close <issue_number> --reason "completed"
```

### Reopening Issues

If an issue needs to be reopened:
```bash
gh issue reopen <issue_number> --comment "Regression detected, reopening"
```

## Batch Issue Creation

When creating multiple related issues, use a script:

```bash
#!/bin/bash
# create-issues.sh

LABELS=("feature" "test" "docs")
TITLES=(
  "Implement OAuth authentication"
  "Add OAuth integration tests"
  "Document OAuth setup process"
)
BODIES=(
  "Implement OAuth 2.0 for Google login"
  "Add comprehensive integration tests for OAuth flow"
  "Write documentation for OAuth configuration and deployment"
)

for i in "${!TITLES[@]}"; do
  gh issue create \
    --title "${TITLES[$i]}" \
    --body "${BODIES[$i]}" \
    --label "${LABELS[$i]}" \
    --project "1"

  echo "Created issue: ${TITLES[$i]}"
  sleep 1  # Rate limiting
done
```

Run the script:
```bash
chmod +x create-issues.sh
./create-issues.sh
```

## Best Practices

1. **Always assign a label** from the 9-label system when creating issues
2. **Link to Projects V2** immediately upon creation
3. **Write clear descriptions** with acceptance criteria
4. **Update status regularly** as work progresses
5. **Link pull requests** using "Closes #123" syntax
6. **Close with comments** explaining resolution
7. **Use templates** for consistent issue format
