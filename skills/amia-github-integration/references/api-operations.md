# GitHub API Operations Reference

## Table of Contents

- 1.1 [Executing GitHub Issue Operations](#11-executing-github-issue-operations)
  - 1.1.1 Creating issues with labels, milestones, and assignees
  - 1.1.2 Updating issue metadata (title, body, labels)
  - 1.1.3 Managing issue lifecycle (close, reopen, transfer)
- 1.2 [Executing GitHub Pull Request Operations](#12-executing-github-pull-request-operations)
  - 1.2.1 Creating PRs from branches
  - 1.2.2 Managing PR reviewers and assignees
  - 1.2.3 Submitting PR reviews (approve, request changes, comment)
  - 1.2.4 Merging PRs with different strategies
- 1.3 [Executing GitHub Projects V2 Operations](#13-executing-github-projects-v2-operations)
  - 1.3.1 Adding items to project boards
  - 1.3.2 Moving items between columns
  - 1.3.3 Updating custom field values via GraphQL
  - 1.3.4 Batch updating project items
- 1.4 [Managing Conversation Threads on Issues and PRs](#14-managing-conversation-threads-on-issues-and-prs)
  - 1.4.1 Posting comments and replies
  - 1.4.2 Marking threads as resolved
  - 1.4.3 Locking and unlocking conversations
- 1.5 [Handling GitHub API Rate Limits](#15-handling-github-api-rate-limits)
  - 1.5.1 Checking rate limit status before operations
  - 1.5.2 Implementing exponential backoff on rate limit errors
  - 1.5.3 Queuing non-urgent operations during limit pressure
  - 1.5.4 Handling GraphQL-specific point-based rate limits
- 1.6 [Running Quality Gates Before API Operations](#16-running-quality-gates-before-api-operations)
  - 1.6.1 Gate 1: Verifying authentication status
  - 1.6.2 Gate 2: Verifying repository and project permissions
  - 1.6.3 Gate 3: Verifying resource existence (issue, PR, label, milestone)
  - 1.6.4 Gate 4: Validating state before state-changing operations
  - 1.6.5 Gate 5: Pre-flight rate limit check
- 1.7 [Coordinating API Operations via AI Maestro](#17-coordinating-api-operations-via-ai-maestro)
  - 1.7.1 Receiving API operation requests
  - 1.7.2 Sending operation results back to requesting agent
  - 1.7.3 Message format for API requests and responses
- 1.8 [Step-by-Step API Operation Workflow](#18-step-by-step-api-operation-workflow)
  - 1.8.1 Receiving and parsing operation request
  - 1.8.2 Running all quality gates in sequence
  - 1.8.3 Preparing and executing API call with retry logic
  - 1.8.4 Processing and validating API response
  - 1.8.5 Logging operation to audit file
  - 1.8.6 Reporting result to orchestrator or callback agent
- 1.9 [Using GitHub CLI and GraphQL Tools](#19-using-github-cli-and-graphql-tools)
  - 1.9.1 Common gh CLI commands for issues and PRs
  - 1.9.2 Using gh api for raw REST API calls
  - 1.9.3 Executing GraphQL mutations for Projects V2
  - 1.9.4 Parsing JSON responses with jq

---

## 1.1 Executing GitHub Issue Operations

### 1.1.1 Creating issues with labels, milestones, and assignees

**When to use**: When you need to create a new issue in a GitHub repository with specific metadata.

**Procedure**:

1. **Verify authentication and permissions** (run Gates 1 and 2 first)
2. **Check rate limit** (run Gate 5)
3. **Build the gh CLI command**:

```bash
gh issue create \
  --repo owner/repo \
  --title "Issue title" \
  --body "Issue description" \
  --label "bug,priority-high" \
  --milestone "v1.0" \
  --assignee "username"
```

1. **Execute the command** and capture the issue number:

```bash
ISSUE_URL=$(gh issue create --repo owner/repo --title "..." --body "..." --label "bug" --json url -q .url)
ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')
```

1. **Log the operation** to `logs/api-operations-YYYYMMDD.log`:

```bash
echo "$(date -Iseconds) | CREATE_ISSUE | owner/repo | #$ISSUE_NUMBER | SUCCESS" >> logs/api-operations-$(date +%Y%m%d).log
```

1. **Return the issue number and URL** to the caller.

**Error handling**: If the issue creation fails, capture the error message and log it. If rate limited (HTTP 429), apply exponential backoff (see section 1.5.2).

---

### 1.1.2 Updating issue metadata (title, body, labels)

**When to use**: When you need to modify an existing issue's title, description, or labels.

**Procedure**:

1. **Verify the issue exists** (run Gate 3):

```bash
gh issue view ISSUE_NUMBER --repo owner/repo --json number
```

1. **Check the issue is in a valid state** (run Gate 4):

```bash
gh issue view ISSUE_NUMBER --repo owner/repo --json state
```

1. **Update the issue**:

```bash
# Update title and body
gh issue edit ISSUE_NUMBER --repo owner/repo --title "New title" --body "New body"

# Add labels
gh issue edit ISSUE_NUMBER --repo owner/repo --add-label "enhancement,ai-review"

# Remove labels
gh issue edit ISSUE_NUMBER --repo owner/repo --remove-label "wontfix"

# Update milestone
gh issue edit ISSUE_NUMBER --repo owner/repo --milestone "v2.0"
```

1. **Log the operation**.

**Note**: Multiple updates can be combined in a single command for efficiency.

---

### 1.1.3 Managing issue lifecycle (close, reopen, transfer)

**When to use**: When you need to close, reopen, or transfer an issue between repositories.

**Procedure for closing an issue**:

```bash
gh issue close ISSUE_NUMBER --repo owner/repo --reason "completed"
# Reasons: completed, not_planned
```

**Procedure for reopening an issue**:

```bash
gh issue reopen ISSUE_NUMBER --repo owner/repo
```

**Procedure for transferring an issue**:

```bash
gh issue transfer ISSUE_NUMBER --repo source-owner/source-repo target-owner/target-repo
```

**Important**: Transferring requires admin permissions on both repositories. Run Gate 2 for both repos before attempting.

---

## 1.2 Executing GitHub Pull Request Operations

### 1.2.1 Creating PRs from branches

**When to use**: When you need to create a new pull request from an existing branch.

**Procedure**:

1. **Verify the branch exists** and has commits ahead of base branch.
2. **Check rate limit** (Gate 5).
3. **Create the PR**:

```bash
gh pr create \
  --repo owner/repo \
  --base main \
  --head feature-branch \
  --title "PR title" \
  --body "PR description" \
  --label "enhancement" \
  --milestone "v1.0" \
  --assignee "@me"
```

1. **Capture PR number**:

```bash
PR_URL=$(gh pr create --repo owner/repo ... --json url -q .url)
PR_NUMBER=$(echo "$PR_URL" | grep -oE '[0-9]+$')
```

1. **Log the operation**.

**Using a PR body from file**:

```bash
gh pr create --repo owner/repo --base main --head feature --title "..." --body-file pr-body.md
```

---

### 1.2.2 Managing PR reviewers and assignees

**When to use**: When you need to request reviews from team members or assign the PR to someone.

**Procedure**:

1. **Verify the PR exists** (Gate 3):

```bash
gh pr view PR_NUMBER --repo owner/repo --json number
```

1. **Request reviewers**:

```bash
# Request individual reviewers
gh pr edit PR_NUMBER --repo owner/repo --add-reviewer "username1,username2"

# Request team review
gh pr edit PR_NUMBER --repo owner/repo --add-reviewer "org/team-name"
```

1. **Add assignees**:

```bash
gh pr edit PR_NUMBER --repo owner/repo --add-assignee "username"
```

1. **Remove reviewers or assignees**:

```bash
gh pr edit PR_NUMBER --repo owner/repo --remove-reviewer "username"
gh pr edit PR_NUMBER --repo owner/repo --remove-assignee "username"
```

**Note**: Requesting team reviews requires the requester to be a member of the organization.

---

### 1.2.3 Submitting PR reviews (approve, request changes, comment)

**When to use**: When you need to submit a review on a pull request.

**Procedure**:

1. **Verify PR exists and is open** (Gates 3 and 4).

2. **Submit an approval**:

```bash
gh pr review PR_NUMBER --repo owner/repo --approve --body "LGTM! Changes look good."
```

1. **Request changes**:

```bash
gh pr review PR_NUMBER --repo owner/repo --request-changes --body "Please address the following issues..."
```

1. **Submit a comment review** (no approval/rejection):

```bash
gh pr review PR_NUMBER --repo owner/repo --comment --body "General feedback on the PR."
```

1. **Submit inline comments** (on specific lines):

```bash
gh pr review PR_NUMBER --repo owner/repo --comment --body "Comment text" --comment-file review-comments.json
```

**Format for review-comments.json**:

```json
[
  {
    "path": "src/file.py",
    "position": 42,
    "body": "This line needs attention"
  }
]
```

1. **Log the review submission**.

---

### 1.2.4 Merging PRs with different strategies

**When to use**: When you need to merge a pull request into the base branch.

**Procedure**:

1. **Run all merge quality gates**:
   - Gate 3: PR exists
   - Gate 4: PR is mergeable (all checks passed, no conflicts)
   - Gate 2: User has write permissions

```bash
# Check mergeable status
MERGEABLE=$(gh pr view PR_NUMBER --repo owner/repo --json mergeable,mergeStateStatus -q .mergeable)
if [ "$MERGEABLE" != "MERGEABLE" ]; then
    echo "BLOCKED: PR is not mergeable"
    exit 1
fi
```

1. **Execute merge with chosen strategy**:

```bash
# Merge commit (default)
gh pr merge PR_NUMBER --repo owner/repo --merge --body "Merge message"

# Squash merge (recommended for feature branches)
gh pr merge PR_NUMBER --repo owner/repo --squash --body "Squashed commit message"

# Rebase merge (maintains linear history)
gh pr merge PR_NUMBER --repo owner/repo --rebase
```

1. **Delete the source branch** (optional):

```bash
gh pr merge PR_NUMBER --repo owner/repo --squash --delete-branch
```

1. **Log the merge operation** with strategy used.

**Important**: Always verify `mergeStateStatus` is `CLEAN` before merging to avoid conflicts.

---

## 1.3 Executing GitHub Projects V2 Operations

### 1.3.1 Adding items to project boards

**When to use**: When you need to add an issue or PR to a GitHub Projects V2 board.

**Procedure**:

1. **Get the project ID** (this is a one-time lookup):

```bash
gh api graphql -f query='
  query {
    user(login: "username") {
      projectV2(number: PROJECT_NUMBER) {
        id
      }
    }
  }
' -q .data.user.projectV2.id
```

Or for organization projects:

```bash
gh api graphql -f query='
  query {
    organization(login: "org-name") {
      projectV2(number: PROJECT_NUMBER) {
        id
      }
    }
  }
' -q .data.organization.projectV2.id
```

1. **Get the content ID** (issue or PR global node ID):

```bash
# For issue
CONTENT_ID=$(gh issue view ISSUE_NUMBER --repo owner/repo --json id -q .id)

# For PR
CONTENT_ID=$(gh pr view PR_NUMBER --repo owner/repo --json id -q .id)
```

1. **Add the item to the project**:

```bash
gh api graphql -f query='
  mutation {
    addProjectV2ItemById(input: {
      projectId: "PROJECT_ID"
      contentId: "CONTENT_ID"
    }) {
      item { id }
    }
  }
' -q .data.addProjectV2ItemById.item.id
```

1. **Capture the project item ID** for future operations.

2. **Log the operation**.

---

### 1.3.2 Moving items between columns

**When to use**: When you need to change the status/column of an item on a project board.

**Procedure**:

1. **Get the field ID for the Status column**:

```bash
gh api graphql -f query='
  query {
    node(id: "PROJECT_ID") {
      ... on ProjectV2 {
        fields(first: 20) {
          nodes {
            ... on ProjectV2SingleSelectField {
              id
              name
              options { id name }
            }
          }
        }
      }
    }
  }
'
```

Find the field with `name: "Status"` and note its `id` and the option IDs for each column (e.g., "Todo", "In Progress", "Done").

1. **Update the item's status field**:

```bash
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(input: {
      projectId: "PROJECT_ID"
      itemId: "ITEM_ID"
      fieldId: "STATUS_FIELD_ID"
      value: { singleSelectOptionId: "COLUMN_OPTION_ID" }
    }) {
      projectV2Item { id }
    }
  }
'
```

1. **Verify the update** by querying the item's current field value.

2. **Log the operation**.

**Note**: This same pattern works for any single-select custom field (Priority, Sprint, etc.).

---

### 1.3.3 Updating custom field values via GraphQL

**When to use**: When you need to update text, number, date, or iteration fields on project items.

**Procedure for text fields**:

```bash
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(input: {
      projectId: "PROJECT_ID"
      itemId: "ITEM_ID"
      fieldId: "TEXT_FIELD_ID"
      value: { text: "Custom text value" }
    }) {
      projectV2Item { id }
    }
  }
'
```

**Procedure for number fields**:

```bash
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(input: {
      projectId: "PROJECT_ID"
      itemId: "ITEM_ID"
      fieldId: "NUMBER_FIELD_ID"
      value: { number: 42 }
    }) {
      projectV2Item { id }
    }
  }
'
```

**Procedure for date fields**:

```bash
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(input: {
      projectId: "PROJECT_ID"
      itemId: "ITEM_ID"
      fieldId: "DATE_FIELD_ID"
      value: { date: "2025-02-05" }
    }) {
      projectV2Item { id }
    }
  }
'
```

**Procedure for iteration fields**:

```bash
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(input: {
      projectId: "PROJECT_ID"
      itemId: "ITEM_ID"
      fieldId: "ITERATION_FIELD_ID"
      value: { iterationId: "ITERATION_ID" }
    }) {
      projectV2Item { id }
    }
  }
'
```

**Log each operation**.

---

### 1.3.4 Batch updating project items

**When to use**: When you need to update multiple items with the same field value (e.g., moving all items from "Todo" to "In Progress").

**Procedure**:

1. **Query all items with the target filter**:

```bash
gh api graphql -f query='
  query {
    node(id: "PROJECT_ID") {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            id
            fieldValues(first: 20) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  field { ... on ProjectV2SingleSelectField { name } }
                  optionId
                }
              }
            }
          }
        }
      }
    }
  }
'
```

1. **Filter items in JSON** to find those matching criteria (e.g., Status = "Todo"):

```bash
ITEMS=$(... | jq '.data.node.items.nodes[] | select(.fieldValues.nodes[] | select(.field.name == "Status" and .optionId == "TODO_OPTION_ID")) | .id')
```

1. **Loop through items** and update each:

```bash
for ITEM_ID in $ITEMS; do
    gh api graphql -f query='
      mutation {
        updateProjectV2ItemFieldValue(input: {
          projectId: "PROJECT_ID"
          itemId: "'$ITEM_ID'"
          fieldId: "STATUS_FIELD_ID"
          value: { singleSelectOptionId: "IN_PROGRESS_OPTION_ID" }
        }) {
          projectV2Item { id }
        }
      }
    '

    # Rate limit protection: wait 1 second between updates
    sleep 1
done
```

1. **Log the batch operation** with count of updated items.

**Important**: For large batches (>50 items), check rate limits before each update (see section 1.5.1).

---

## 1.4 Managing Conversation Threads on Issues and PRs

### 1.4.1 Posting comments and replies

**When to use**: When you need to add a comment to an issue or PR, or reply to an existing thread.

**Procedure for posting a new comment**:

```bash
# On an issue
gh issue comment ISSUE_NUMBER --repo owner/repo --body "Comment text"

# On a PR
gh pr comment PR_NUMBER --repo owner/repo --body "Comment text"
```

**Procedure for replying to a specific comment** (threaded reply):

1. **Get the comment ID**:

```bash
# List comments on issue
gh api repos/owner/repo/issues/ISSUE_NUMBER/comments | jq '.[] | {id, body}'

# List comments on PR
gh api repos/owner/repo/pulls/PR_NUMBER/comments | jq '.[] | {id, body}'
```

1. **Post a reply** (using REST API):

```bash
gh api repos/owner/repo/issues/comments/COMMENT_ID/replies \
  --method POST \
  --field body="Reply text"
```

**Note**: Threaded replies are only supported on PRs with the new comment system. For issues, replies are top-level comments that quote the original.

---

### 1.4.2 Marking threads as resolved

**When to use**: When a review comment thread on a PR has been addressed and should be marked resolved.

**Procedure**:

1. **Get the thread ID** from the PR review comments:

```bash
gh api repos/owner/repo/pulls/PR_NUMBER/comments | jq '.[] | select(.body | contains("specific comment")) | .id'
```

1. **Resolve the thread**:

```bash
gh api graphql -f query='
  mutation {
    resolveReviewThread(input: {
      threadId: "THREAD_ID"
    }) {
      thread { isResolved }
    }
  }
'
```

1. **Verify resolution**:

```bash
gh api graphql -f query='
  query {
    node(id: "THREAD_ID") {
      ... on PullRequestReviewThread {
        isResolved
      }
    }
  }
'
```

**Note**: Only the PR author or reviewers can resolve threads.

---

### 1.4.3 Locking and unlocking conversations

**When to use**: When you need to prevent further comments on an issue or PR (e.g., after resolution, to prevent spam).

**Procedure for locking a conversation**:

```bash
# Lock an issue
gh api repos/owner/repo/issues/ISSUE_NUMBER/lock --method PUT \
  --field lock_reason="resolved"

# Lock a PR
gh api repos/owner/repo/pulls/PR_NUMBER/lock --method PUT \
  --field lock_reason="resolved"
```

**Valid lock reasons**:

- `resolved` - Issue/PR is resolved
- `off-topic` - Conversation went off-topic
- `too heated` - Discussion became unconstructive
- `spam` - Spammy comments

**Procedure for unlocking a conversation**:

```bash
# Unlock an issue
gh api repos/owner/repo/issues/ISSUE_NUMBER/lock --method DELETE

# Unlock a PR
gh api repos/owner/repo/pulls/PR_NUMBER/lock --method DELETE
```

**Important**: Only users with write access or higher can lock/unlock conversations.

---

## 1.5 Handling GitHub API Rate Limits

### 1.5.1 Checking rate limit status before operations

**When to use**: Before executing any GitHub API operation, especially batch operations.

**Procedure**:

1. **Check current rate limit status**:

```bash
gh api rate_limit | jq '.resources.core'
```

**Response format**:

```json
{
  "limit": 5000,
  "used": 4800,
  "remaining": 200,
  "reset": 1706745600
}
```

1. **Interpret the status**:

| Remaining | Status | Action |
|-----------|--------|--------|
| > 500 | Green | Normal operation - proceed |
| 100-500 | Yellow | Delay non-urgent, warn orchestrator |
| 10-100 | Orange | Only critical operations |
| < 10 | Red | STOP all operations, wait for reset |

1. **If in Yellow or Orange zone**, send warning to orchestrator using the `agent-messaging` skill with:
   - **Recipient**: `orchestrator-master`
   - **Subject**: `GitHub Rate Limit Warning`
   - **Priority**: `high`
   - **Content**: `{"type": "warning", "message": "GitHub API rate limit in YELLOW zone: <REMAINING> remaining"}`
   - **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

2. **If in Red zone**, calculate wait time:

```bash
RESET_TIME=$(gh api rate_limit | jq '.resources.core.reset')
CURRENT_TIME=$(date +%s)
WAIT_SECONDS=$((RESET_TIME - CURRENT_TIME))

echo "BLOCKED: Rate limit critical. Reset in $WAIT_SECONDS seconds."
```

1. **Log the rate limit check**.

---

### 1.5.2 Implementing exponential backoff on rate limit errors

**When to use**: When a GitHub API call fails with HTTP 429 (rate limited) or 403 (secondary rate limit).

**Procedure**:

1. **Detect rate limit error** (exit code or HTTP status):

```bash
# gh CLI returns exit code 4 for rate limit errors
if [ $? -eq 4 ]; then
    # Rate limited
fi
```

1. **Implement exponential backoff**:

```bash
DELAY=1
MAX_RETRIES=5

for attempt in $(seq 1 $MAX_RETRIES); do
    gh api "$ENDPOINT" --method POST --input params.json
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo "Operation succeeded on attempt $attempt"
        break
    elif [ $EXIT_CODE -eq 4 ]; then
        # Rate limit error - backoff and retry
        echo "Rate limited. Waiting $DELAY seconds before retry $attempt/$MAX_RETRIES"
        sleep $DELAY
        DELAY=$((DELAY * 2))  # Double the delay for next retry
    else
        # Other error - don't retry
        echo "Failed with non-rate-limit error: $EXIT_CODE"
        break
    fi
done

if [ $EXIT_CODE -ne 0 ]; then
    echo "FAILED after $MAX_RETRIES retries"
    exit 1
fi
```

**Backoff schedule**:

- Attempt 1: Immediate
- Attempt 2: Wait 1 second
- Attempt 3: Wait 2 seconds
- Attempt 4: Wait 4 seconds
- Attempt 5: Wait 8 seconds
- Attempt 6: Wait 16 seconds (final)

1. **If all retries exhausted**, queue the operation for later retry and report failure.

2. **Log each retry attempt** with the delay used.

---

### 1.5.3 Queuing non-urgent operations during limit pressure

**When to use**: When rate limit is in Yellow/Orange zone and you have non-urgent operations to perform.

**Procedure**:

1. **Classify operation priority** (should be provided in request):
   - `critical`: Security fixes, blocking issues, production hotfixes
   - `high`: User-reported bugs, PR merges
   - `normal`: Feature development, documentation updates
   - `low`: Cleanup tasks, label updates, archival

2. **Check rate limit status**:

```bash
REMAINING=$(gh api rate_limit | jq '.resources.core.remaining')
```

1. **Apply priority-based throttling**:

```bash
if [ "$REMAINING" -lt 500 ] && [ "$REMAINING" -ge 100 ]; then
    # Yellow zone - only high and critical
    if [ "$PRIORITY" = "low" ] || [ "$PRIORITY" = "normal" ]; then
        echo "QUEUED: Rate limit pressure. Queueing $PRIORITY operation for later."
        echo "$OPERATION_JSON" >> queue/pending-operations.json
        exit 0
    fi
elif [ "$REMAINING" -lt 100 ]; then
    # Orange/Red zone - only critical
    if [ "$PRIORITY" != "critical" ]; then
        echo "QUEUED: Rate limit critical. Queueing $PRIORITY operation for later."
        echo "$OPERATION_JSON" >> queue/pending-operations.json
        exit 0
    fi
fi
```

1. **Process queued operations** when rate limit recovers:

```bash
# Run this periodically (e.g., every 5 minutes)
REMAINING=$(gh api rate_limit | jq '.resources.core.remaining')

if [ "$REMAINING" -gt 500 ]; then
    # Process queued operations
    while IFS= read -r operation; do
        echo "Processing queued operation: $operation"
        # Execute operation
        sleep 1  # Rate limit safety
    done < queue/pending-operations.json

    # Clear queue
    > queue/pending-operations.json
fi
```

1. **Notify orchestrator** when operations are queued.

---

### 1.5.4 Handling GraphQL-specific point-based rate limits

**When to use**: Before executing GraphQL queries for Projects V2 operations.

**Key difference**: GraphQL uses a **point-based system** (5,000 points/hour) instead of request counting.

**Procedure**:

1. **Check GraphQL rate limit**:

```bash
gh api graphql -f query='
  query {
    rateLimit {
      limit
      cost
      remaining
      resetAt
    }
  }
' | jq '.data.rateLimit'
```

**Response format**:

```json
{
  "limit": 5000,
  "cost": 1,
  "remaining": 4800,
  "resetAt": "2025-02-05T12:00:00Z"
}
```

1. **Estimate query cost** before execution:
   - Simple queries (fetch single item): 1 point
   - Medium queries (fetch list with filters): 10-50 points
   - Complex queries (nested data, large lists): 100+ points

2. **Verify sufficient points remain**:

```bash
REMAINING=$(gh api graphql -f query='{ rateLimit { remaining } }' | jq '.data.rateLimit.remaining')

if [ "$REMAINING" -lt 100 ]; then
    echo "BLOCKED: GraphQL rate limit critical ($REMAINING points remaining)"
    exit 1
fi
```

1. **After query execution**, check the actual cost:

```bash
COST=$(gh api graphql -f query='...' | jq '.extensions.cost.actualCost // .data.rateLimit.cost')
echo "Query consumed $COST points"
```

1. **Apply the same backoff and queueing strategies** as REST API rate limits.

**Important**: GraphQL and REST API have **separate rate limits**. Monitor both independently.

---

## 1.6 Running Quality Gates Before API Operations

### 1.6.1 Gate 1: Verifying authentication status

**When to use**: Before ANY GitHub API operation.

**Purpose**: Ensure gh CLI is authenticated and the token is valid.

**Procedure**:

1. **Check authentication status**:

```bash
gh auth status
```

**Expected output** (success):

```
github.com
  ✓ Logged in to github.com account username (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_****
```

1. **Verify the output**:

```bash
if ! gh auth status 2>&1 | grep -q "Logged in to github.com"; then
    echo "BLOCKED: Gate 1 FAILED - Not authenticated to GitHub"
    exit 1
fi
```

1. **If authentication failed**, block the operation and report:

```bash
echo "FAILED: Authentication verification failed. Run 'gh auth login' to authenticate."
exit 1
```

**Pass condition**: Output contains "Logged in to github.com account"

**Block condition**: Output contains "not logged in" or command fails

---

### 1.6.2 Gate 2: Verifying repository and project permissions

**When to use**: Before any write operation (create, update, delete).

**Purpose**: Ensure the authenticated user has sufficient permissions for the requested operation.

**Procedure for repository permissions**:

1. **Check user's permission level**:

```bash
PERMISSION=$(gh repo view owner/repo --json viewerPermission -q .viewerPermission)
```

**Possible values**:

- `ADMIN` - Full access
- `WRITE` - Can push and merge
- `READ` - Read-only access
- `NONE` - No access

1. **Verify sufficient permission for operation**:

```bash
case "$OPERATION" in
    create-issue|update-issue|create-pr|comment)
        # Requires WRITE or ADMIN
        if [[ "$PERMISSION" != "WRITE" && "$PERMISSION" != "ADMIN" ]]; then
            echo "BLOCKED: Gate 2 FAILED - Requires WRITE permission (have: $PERMISSION)"
            exit 1
        fi
        ;;
    delete-branch|update-settings)
        # Requires ADMIN
        if [ "$PERMISSION" != "ADMIN" ]; then
            echo "BLOCKED: Gate 2 FAILED - Requires ADMIN permission (have: $PERMISSION)"
            exit 1
        fi
        ;;
esac
```

**Procedure for project permissions**:

1. **Check project access** (GraphQL):

```bash
gh api graphql -f query='
  query {
    node(id: "PROJECT_ID") {
      ... on ProjectV2 {
        viewerCanUpdate
      }
    }
  }
' | jq '.data.node.viewerCanUpdate'
```

1. **Verify `viewerCanUpdate` is true**:

```bash
CAN_UPDATE=$(gh api graphql -f query='...' | jq '.data.node.viewerCanUpdate')

if [ "$CAN_UPDATE" != "true" ]; then
    echo "BLOCKED: Gate 2 FAILED - No update permission for project"
    exit 1
fi
```

**Pass condition**: User has required permission level

**Block condition**: Insufficient permissions for operation type

---

### 1.6.3 Gate 3: Verifying resource existence (issue, PR, label, milestone)

**When to use**: Before any update or delete operation on a resource.

**Purpose**: Ensure the target resource exists before attempting to modify it.

**Procedure for verifying issue exists**:

```bash
if ! gh issue view ISSUE_NUMBER --repo owner/repo --json number >/dev/null 2>&1; then
    echo "BLOCKED: Gate 3 FAILED - Issue #$ISSUE_NUMBER does not exist"
    exit 1
fi
```

**Procedure for verifying PR exists**:

```bash
if ! gh pr view PR_NUMBER --repo owner/repo --json number >/dev/null 2>&1; then
    echo "BLOCKED: Gate 3 FAILED - PR #$PR_NUMBER does not exist"
    exit 1
fi
```

**Procedure for verifying label exists**:

```bash
if ! gh label list --repo owner/repo | grep -q "^$LABEL_NAME"; then
    echo "BLOCKED: Gate 3 FAILED - Label '$LABEL_NAME' does not exist"
    exit 1
fi
```

**Procedure for verifying milestone exists**:

```bash
MILESTONE_EXISTS=$(gh api repos/owner/repo/milestones | jq '.[] | select(.title == "'"$MILESTONE_NAME"'") | .number')

if [ -z "$MILESTONE_EXISTS" ]; then
    echo "BLOCKED: Gate 3 FAILED - Milestone '$MILESTONE_NAME' does not exist"
    exit 1
fi
```

**Pass condition**: Resource exists and is accessible

**Block condition**: Resource not found (404) or not accessible

---

### 1.6.4 Gate 4: Validating state before state-changing operations

**When to use**: Before operations that require a specific resource state (e.g., merging PR requires mergeable state).

**Purpose**: Prevent invalid state transitions that would fail or cause data issues.

**Procedure for PR merge validation**:

```bash
# Get PR mergeable state
MERGE_STATE=$(gh pr view PR_NUMBER --repo owner/repo --json mergeable,mergeStateStatus -q '"\(.mergeable)|\(.mergeStateStatus)"')

IFS='|' read -r MERGEABLE STATUS <<< "$MERGE_STATE"

if [ "$MERGEABLE" != "MERGEABLE" ]; then
    echo "BLOCKED: Gate 4 FAILED - PR is not mergeable (status: $STATUS)"
    echo "Reasons:"
    gh pr view PR_NUMBER --repo owner/repo --json statusCheckRollup -q '.statusCheckRollup[] | select(.conclusion != "SUCCESS") | "  - \(.name): \(.conclusion)"'
    exit 1
fi
```

**Possible merge states**:

- `CLEAN` - Ready to merge
- `UNSTABLE` - Checks failed but merge allowed
- `BLOCKED` - Merge blocked by rules
- `BEHIND` - Branch needs update
- `DIRTY` - Merge conflicts exist

**Procedure for issue close validation**:

```bash
# Check issue is open
STATE=$(gh issue view ISSUE_NUMBER --repo owner/repo --json state -q .state)

if [ "$STATE" = "CLOSED" ]; then
    echo "BLOCKED: Gate 4 FAILED - Issue is already closed"
    exit 1
fi
```

**Procedure for issue reopen validation**:

```bash
# Check issue is closed
STATE=$(gh issue view ISSUE_NUMBER --repo owner/repo --json state -q .state)

if [ "$STATE" = "OPEN" ]; then
    echo "BLOCKED: Gate 4 FAILED - Issue is already open"
    exit 1
fi
```

**Pass condition**: Resource is in valid state for operation

**Block condition**: State transition is invalid or not allowed

---

### 1.6.5 Gate 5: Pre-flight rate limit check

**When to use**: Before EVERY GitHub API operation, especially at the start of batch operations.

**Purpose**: Prevent operations from starting when rate limits are exhausted or critical.

**Procedure**:

1. **Check current rate limit**:

```bash
REMAINING=$(gh api rate_limit | jq '.resources.core.remaining')
```

1. **Apply threshold policy**:

```bash
if [ "$REMAINING" -lt 10 ]; then
    # Red zone - block all operations
    RESET_TIME=$(gh api rate_limit | jq '.resources.core.reset')
    CURRENT_TIME=$(date +%s)
    WAIT_SECONDS=$((RESET_TIME - CURRENT_TIME))

    echo "BLOCKED: Gate 5 FAILED - Rate limit critical ($REMAINING remaining)"
    echo "Rate limit resets in $WAIT_SECONDS seconds"
    exit 1
elif [ "$REMAINING" -lt 100 ]; then
    # Orange zone - only critical operations
    if [ "$PRIORITY" != "critical" ]; then
        echo "BLOCKED: Gate 5 FAILED - Rate limit low ($REMAINING remaining), non-critical operation queued"
        exit 1
    fi
fi
```

1. **Log the rate limit check**:

```bash
echo "Gate 5: Rate limit check PASS ($REMAINING remaining)"
```

**Pass condition**: Remaining > 10 for critical, > 100 for non-critical

**Block condition**: Rate limit in Red zone, or Orange zone for non-critical operations

---

## 1.7 Coordinating API Operations via AI Maestro

### 1.7.1 Receiving API operation requests

**When to use**: At the start of every API Coordinator session, to check for pending requests.

**Purpose**: Retrieve queued API operation requests from other agents via AI Maestro.

**Procedure**:

1. **Check for unread messages**: Check your inbox using the `agent-messaging` skill.

2. **Filter for API requests**: Filter inbox messages for `content.type == "api-request"` using the `agent-messaging` skill.

3. **Parse request message**:

```json
{
  "id": "msg-123",
  "from": "orchestrator-master",
  "to": "amia-api-coordinator",
  "subject": "Create GitHub Issue",
  "priority": "high",
  "content": {
    "type": "api-request",
    "operation": "create-issue",
    "params": {
      "repo": "owner/repo",
      "title": "Issue title",
      "body": "Issue body",
      "labels": ["bug", "priority-high"]
    },
    "callback_agent": "orchestrator-master"
  },
  "timestamp": "2025-02-05T10:30:00Z"
}
```

1. **Extract operation parameters**:

```bash
OPERATION=$(echo "$MESSAGE" | jq -r '.content.operation')
PARAMS=$(echo "$MESSAGE" | jq -r '.content.params')
CALLBACK=$(echo "$MESSAGE" | jq -r '.content.callback_agent')
PRIORITY=$(echo "$MESSAGE" | jq -r '.priority')
```

1. **Mark message as read**: Mark the message as read using the `agent-messaging` skill.

2. **Execute the operation** (proceed to section 1.8).

---

### 1.7.2 Sending operation results back to requesting agent

**When to use**: After completing an API operation, to report the result to the agent that requested it.

**Purpose**: Close the request-response loop via AI Maestro messaging.

**Procedure for successful operations**: Send a message using the `agent-messaging` skill with:

- **Recipient**: The callback agent
- **Subject**: `API Operation Complete: <OPERATION>`
- **Priority**: `normal`
- **Content**: `{"type": "api-response", "operation": "<OPERATION>", "status": "success", "result": {"issue_number": 456, "issue_url": "https://github.com/owner/repo/issues/456"}}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

**Procedure for failed operations**: Send a message using the `agent-messaging` skill with:

- **Recipient**: The callback agent
- **Subject**: `API Operation Failed: <OPERATION>`
- **Priority**: `high`
- **Content**: `{"type": "api-response", "operation": "<OPERATION>", "status": "failed", "error": "Gate 2 failed: insufficient permissions", "details_file": "logs/api-operations-20250205.log"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

**Procedure for rate-limited operations**: Send a message using the `agent-messaging` skill with:

- **Recipient**: The callback agent
- **Subject**: `API Operation Queued: <OPERATION>`
- **Priority**: `normal`
- **Content**: `{"type": "api-response", "operation": "<OPERATION>", "status": "rate-limited", "message": "Operation queued due to rate limit pressure. Will retry when limit resets.", "retry_after": "2025-02-05T12:00:00Z"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

---

### 1.7.3 Message format for API requests and responses

**When to use**: When crafting AI Maestro messages for API coordination.

**Request message structure**:

```json
{
  "to": "amia-api-coordinator",
  "subject": "Brief operation description",
  "priority": "critical|high|normal|low",
  "content": {
    "type": "api-request",
    "operation": "create-issue|update-issue|create-pr|merge-pr|update-project|...",
    "params": {
      "repo": "owner/repo",
      "...": "operation-specific parameters"
    },
    "callback_agent": "requesting-agent-session-name"
  }
}
```

**Valid operation types**:

- Issue operations: `create-issue`, `update-issue`, `close-issue`, `reopen-issue`, `transfer-issue`
- PR operations: `create-pr`, `update-pr`, `merge-pr`, `close-pr`, `review-pr`
- Project operations: `add-to-project`, `update-project-item`, `move-project-item`
- Comment operations: `add-comment`, `reply-to-thread`, `resolve-thread`
- Label operations: `add-label`, `remove-label`

**Response message structure**:

```json
{
  "to": "callback-agent",
  "subject": "API Operation Result: operation-type",
  "priority": "normal|high",
  "content": {
    "type": "api-response",
    "operation": "operation-type",
    "status": "success|failed|rate-limited|queued",
    "result": {
      "...": "operation-specific results (on success)"
    },
    "error": "error message (on failure)",
    "details_file": "logs/api-operations-YYYYMMDD.log"
  }
}
```

**Important**: Always include `callback_agent` in requests so the coordinator knows where to send the response.

---

## 1.8 Step-by-Step API Operation Workflow

### 1.8.1 Receiving and parsing operation request

**When to use**: At the start of every API operation workflow.

**Purpose**: Extract and validate the operation parameters from the request source (AI Maestro message or orchestrator delegation).

**Procedure**:

1. **Determine request source**:
   - AI Maestro message (see section 1.7.1)
   - Direct orchestrator delegation (via Task tool invocation)

2. **Extract operation details**: Read the incoming message from your inbox using the `agent-messaging` skill. Filter for messages with `content.type == "api-request"`. Extract the following fields from the message:
   - `OPERATION` = `content.operation`
   - `PARAMS` = `content.params`
   - `CALLBACK` = `content.callback_agent`
   - `PRIORITY` = `priority`

3. **Validate request format**:

```bash
# Check required fields exist
if [ -z "$OPERATION" ] || [ -z "$PARAMS" ] || [ -z "$CALLBACK" ]; then
    echo "FAILED: Invalid request format - missing required fields"
    exit 1
fi

# Check operation type is valid
VALID_OPS="create-issue|update-issue|close-issue|create-pr|merge-pr|update-project|..."
if ! echo "$OPERATION" | grep -qE "^($VALID_OPS)$"; then
    echo "FAILED: Invalid operation type: $OPERATION"
    exit 1
fi
```

1. **Log the request**:

```bash
echo "$(date -Iseconds) | REQUEST | $OPERATION | from: $CALLBACK | priority: $PRIORITY" >> logs/api-operations-$(date +%Y%m%d).log
```

1. **Proceed to Gate 1** (section 1.6.1).

---

### 1.8.2 Running all quality gates in sequence

**When to use**: After parsing the request, before executing the API call.

**Purpose**: Validate all prerequisites are met before attempting the operation.

**Procedure**:

1. **Run Gate 1 (Authentication)**:

```bash
if ! gh auth status 2>&1 | grep -q "Logged in to github.com"; then
    echo "FAILED: Gate 1 - Authentication verification failed"
    # Send failure response to callback agent
    exit 1
fi
echo "Gate 1: PASS - Authentication verified"
```

1. **Run Gate 2 (Permissions)**:

```bash
PERMISSION=$(gh repo view owner/repo --json viewerPermission -q .viewerPermission)

if [[ "$PERMISSION" != "WRITE" && "$PERMISSION" != "ADMIN" ]]; then
    echo "FAILED: Gate 2 - Insufficient permissions (have: $PERMISSION)"
    # Send failure response
    exit 1
fi
echo "Gate 2: PASS - Permissions verified ($PERMISSION)"
```

1. **Run Gate 3 (Resource Existence)** - if operation is update/delete:

```bash
if [[ "$OPERATION" =~ ^(update-issue|close-issue|merge-pr)$ ]]; then
    if ! gh issue view $ISSUE_NUMBER --repo owner/repo --json number >/dev/null 2>&1; then
        echo "FAILED: Gate 3 - Resource does not exist"
        # Send failure response
        exit 1
    fi
    echo "Gate 3: PASS - Resource exists"
fi
```

1. **Run Gate 4 (State Validation)** - if operation is state-changing:

```bash
if [ "$OPERATION" = "merge-pr" ]; then
    MERGEABLE=$(gh pr view $PR_NUMBER --repo owner/repo --json mergeable -q .mergeable)
    if [ "$MERGEABLE" != "MERGEABLE" ]; then
        echo "FAILED: Gate 4 - PR is not mergeable"
        # Send failure response
        exit 1
    fi
    echo "Gate 4: PASS - State valid for operation"
fi
```

1. **Run Gate 5 (Rate Limit Check)**:

```bash
REMAINING=$(gh api rate_limit | jq '.resources.core.remaining')

if [ "$REMAINING" -lt 10 ]; then
    echo "FAILED: Gate 5 - Rate limit critical ($REMAINING remaining)"
    # Send queued response
    exit 1
fi
echo "Gate 5: PASS - Rate limit OK ($REMAINING remaining)"
```

1. **Log gate results**:

```bash
echo "$(date -Iseconds) | GATES_PASS | $OPERATION | All quality gates passed" >> logs/api-operations-$(date +%Y%m%d).log
```

1. **Proceed to execute API call** (section 1.8.3).

**If ANY gate fails**, skip to section 1.8.6 to report failure.

---

### 1.8.3 Preparing and executing API call with retry logic

**When to use**: After all quality gates pass.

**Purpose**: Execute the GitHub API operation with proper error handling and retry logic.

**Procedure**:

1. **Build the gh CLI command** based on operation type:

```bash
case "$OPERATION" in
    create-issue)
        REPO=$(echo "$PARAMS" | jq -r '.repo')
        TITLE=$(echo "$PARAMS" | jq -r '.title')
        BODY=$(echo "$PARAMS" | jq -r '.body')
        LABELS=$(echo "$PARAMS" | jq -r '.labels | join(",")')

        CMD="gh issue create --repo $REPO --title \"$TITLE\" --body \"$BODY\" --label \"$LABELS\" --json url,number"
        ;;

    merge-pr)
        REPO=$(echo "$PARAMS" | jq -r '.repo')
        PR_NUMBER=$(echo "$PARAMS" | jq -r '.pr_number')
        STRATEGY=$(echo "$PARAMS" | jq -r '.strategy // "squash"')

        CMD="gh pr merge $PR_NUMBER --repo $REPO --$STRATEGY --json url"
        ;;

    # ... other operations
esac
```

1. **Execute with retry logic**:

```bash
DELAY=1
MAX_RETRIES=5
ATTEMPT=0
SUCCESS=false

for ATTEMPT in $(seq 1 $MAX_RETRIES); do
    echo "Executing: $CMD (attempt $ATTEMPT/$MAX_RETRIES)"

    RESULT=$(eval "$CMD" 2>&1)
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo "Operation succeeded on attempt $ATTEMPT"
        SUCCESS=true
        break
    elif [ $EXIT_CODE -eq 4 ]; then
        # Rate limit error - backoff and retry
        echo "Rate limited. Waiting $DELAY seconds before retry"
        sleep $DELAY
        DELAY=$((DELAY * 2))
    else
        # Other error - don't retry
        echo "Operation failed with non-rate-limit error: $EXIT_CODE"
        echo "Error: $RESULT"
        break
    fi
done

if [ "$SUCCESS" != "true" ]; then
    echo "FAILED: Operation did not succeed after $ATTEMPT attempts"
    # Proceed to report failure (section 1.8.6)
    exit 1
fi
```

1. **Capture the result**:

```bash
# Parse JSON response
ISSUE_NUMBER=$(echo "$RESULT" | jq -r '.number')
ISSUE_URL=$(echo "$RESULT" | jq -r '.url')
```

1. **Log the execution**:

```bash
echo "$(date -Iseconds) | EXECUTE_SUCCESS | $OPERATION | attempts: $ATTEMPT | result: $RESULT" >> logs/api-operations-$(date +%Y%m%d).log
```

1. **Proceed to process response** (section 1.8.4).

---

### 1.8.4 Processing and validating API response

**When to use**: After successful API call execution.

**Purpose**: Extract relevant data from the response and validate it contains expected fields.

**Procedure**:

1. **Parse the response** based on operation type:

```bash
case "$OPERATION" in
    create-issue)
        ISSUE_NUMBER=$(echo "$RESULT" | jq -r '.number')
        ISSUE_URL=$(echo "$RESULT" | jq -r '.url')

        # Validate response contains expected fields
        if [ -z "$ISSUE_NUMBER" ] || [ "$ISSUE_NUMBER" = "null" ]; then
            echo "FAILED: Invalid response - missing issue number"
            exit 1
        fi
        ;;

    merge-pr)
        PR_URL=$(echo "$RESULT" | jq -r '.url')
        MERGE_COMMIT=$(echo "$RESULT" | jq -r '.mergeCommit.oid // .sha')

        if [ -z "$MERGE_COMMIT" ] || [ "$MERGE_COMMIT" = "null" ]; then
            echo "FAILED: Invalid response - missing merge commit"
            exit 1
        fi
        ;;

    # ... other operations
esac
```

1. **Build result object** for response message:

```bash
RESULT_JSON=$(jq -n \
  --arg issue_number "$ISSUE_NUMBER" \
  --arg issue_url "$ISSUE_URL" \
  '{issue_number: $issue_number, issue_url: $issue_url}')
```

1. **Validate critical fields**:

```bash
# Ensure all expected fields are present and non-null
if echo "$RESULT_JSON" | jq -e 'to_entries | map(select(.value == null or .value == "")) | length == 0' >/dev/null; then
    echo "Response validation: PASS"
else
    echo "FAILED: Response contains null or empty fields"
    exit 1
fi
```

1. **Log the processed response**:

```bash
echo "$(date -Iseconds) | PROCESS_SUCCESS | $OPERATION | result: $RESULT_JSON" >> logs/api-operations-$(date +%Y%m%d).log
```

1. **Proceed to logging** (section 1.8.5).

---

### 1.8.5 Logging operation to audit file

**When to use**: After processing the API response, before reporting back.

**Purpose**: Create a complete audit trail of all API operations for debugging and compliance.

**Procedure**:

1. **Determine log file path**:

```bash
LOG_FILE="logs/api-operations-$(date +%Y%m%d).log"

# Create logs directory if it doesn't exist
mkdir -p logs
```

1. **Write detailed log entry**:

```bash
cat >> "$LOG_FILE" <<EOF
---
Timestamp: $(date -Iseconds)
Operation: $OPERATION
Priority: $PRIORITY
Request From: $CALLBACK_AGENT
Repository: $(echo "$PARAMS" | jq -r '.repo // "N/A"')
Gates: ALL PASS
Execution Attempts: $ATTEMPT
Status: SUCCESS
Result: $RESULT_JSON
Rate Limit After: $(gh api rate_limit | jq '.resources.core.remaining') remaining
---
EOF
```

1. **For failures, log the failure reason**:

```bash
cat >> "$LOG_FILE" <<EOF
---
Timestamp: $(date -Iseconds)
Operation: $OPERATION
Request From: $CALLBACK_AGENT
Gates: FAILED at Gate $FAILED_GATE
Failure Reason: $FAILURE_REASON
Status: FAILED
---
EOF
```

1. **Verify log entry was written**:

```bash
if ! tail -1 "$LOG_FILE" | grep -q "---"; then
    echo "WARNING: Log entry may not have been written correctly"
fi
```

1. **Proceed to report result** (section 1.8.6).

---

### 1.8.6 Reporting result to orchestrator or callback agent

**When to use**: After logging the operation (final step of workflow).

**Purpose**: Close the request-response loop by notifying the requesting agent of the outcome.

**Procedure for success**: Send a message using the `agent-messaging` skill with:

- **Recipient**: The callback agent
- **Subject**: `API Operation Complete: <OPERATION>`
- **Priority**: `normal`
- **Content**: `{"type": "api-response", "operation": "<OPERATION>", "status": "success", "result": <RESULT_JSON>, "details_file": "<LOG_FILE>"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

Then output: `[DONE] api-coordinator - <OPERATION> completed successfully`

**Procedure for failure**: Send a message using the `agent-messaging` skill with:

- **Recipient**: The callback agent
- **Subject**: `API Operation Failed: <OPERATION>`
- **Priority**: `high`
- **Content**: `{"type": "api-response", "operation": "<OPERATION>", "status": "failed", "error": "<FAILURE_REASON>", "failed_gate": "<FAILED_GATE>", "details_file": "<LOG_FILE>"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

Then output: `[FAILED] api-coordinator - <OPERATION> failed: <FAILURE_REASON>`

**Procedure for rate-limited/queued**: Send a message using the `agent-messaging` skill with:

- **Recipient**: The callback agent
- **Subject**: `API Operation Queued: <OPERATION>`
- **Priority**: `normal`
- **Content**: `{"type": "api-response", "operation": "<OPERATION>", "status": "rate-limited", "message": "Operation queued due to rate limit. Will retry after limit resets.", "retry_after": "<RESET_ISO>", "details_file": "<LOG_FILE>"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

Then output: `[QUEUED] api-coordinator - <OPERATION> queued due to rate limit`

**Verification**: Check that the message was sent successfully:

```bash
if [ $? -eq 0 ]; then
    echo "Response sent successfully to $CALLBACK_AGENT"
else
    echo "WARNING: Failed to send response to $CALLBACK_AGENT"
fi
```

**Final checklist** (all must be complete):

- [ ] Operation executed (or failed with clear reason)
- [ ] Response validated (if successful)
- [ ] Operation logged to audit file
- [ ] AI Maestro message sent to callback agent
- [ ] Rate limit checked post-operation
- [ ] Minimal output returned (under 3 lines)

---

## 1.9 Using GitHub CLI and GraphQL Tools

### 1.9.1 Common gh CLI commands for issues and PRs

**When to use**: For most GitHub REST API operations.

**Purpose**: Quick reference for the most common gh CLI commands.

**Issue commands**:

```bash
# Create issue
gh issue create --repo owner/repo --title "Title" --body "Body" --label "bug" --assignee "user"

# View issue
gh issue view ISSUE_NUMBER --repo owner/repo --json state,title,body,labels

# Edit issue
gh issue edit ISSUE_NUMBER --repo owner/repo --title "New title" --add-label "enhancement"

# Close issue
gh issue close ISSUE_NUMBER --repo owner/repo --reason "completed"

# Reopen issue
gh issue reopen ISSUE_NUMBER --repo owner/repo

# List issues
gh issue list --repo owner/repo --state open --label "bug" --assignee "@me"

# Comment on issue
gh issue comment ISSUE_NUMBER --repo owner/repo --body "Comment text"
```

**PR commands**:

```bash
# Create PR
gh pr create --repo owner/repo --base main --head feature --title "Title" --body "Body"

# View PR
gh pr view PR_NUMBER --repo owner/repo --json state,title,mergeable,mergeStateStatus

# Edit PR
gh pr edit PR_NUMBER --repo owner/repo --title "New title" --add-reviewer "user"

# Review PR
gh pr review PR_NUMBER --repo owner/repo --approve --body "LGTM"
gh pr review PR_NUMBER --repo owner/repo --request-changes --body "Issues found"

# Merge PR
gh pr merge PR_NUMBER --repo owner/repo --squash --delete-branch

# Close PR
gh pr close PR_NUMBER --repo owner/repo

# Checkout PR locally
gh pr checkout PR_NUMBER --repo owner/repo

# List PRs
gh pr list --repo owner/repo --state open --label "ready-to-merge"

# Comment on PR
gh pr comment PR_NUMBER --repo owner/repo --body "Comment text"
```

**JSON output**: Always use `--json` flag with specific fields to get structured output:

```bash
gh issue view 123 --repo owner/repo --json number,title,state,labels,assignees | jq .
```

---

### 1.9.2 Using gh api for raw REST API calls

**When to use**: For GitHub API endpoints not covered by gh CLI subcommands.

**Purpose**: Direct access to GitHub REST API v3.

**Basic syntax**:

```bash
gh api [METHOD] ENDPOINT [--input FILE] [--field key=value] [--raw-field key=value]
```

**Examples**:

```bash
# GET request
gh api repos/owner/repo/issues

# POST request with JSON input
gh api repos/owner/repo/issues --method POST --input issue.json

# POST request with inline fields
gh api repos/owner/repo/issues --method POST \
  --field title="Issue title" \
  --field body="Issue body" \
  --field labels='["bug","urgent"]'

# PATCH request
gh api repos/owner/repo/issues/123 --method PATCH \
  --field state="closed"

# DELETE request
gh api repos/owner/repo/issues/comments/456 --method DELETE

# Using raw fields (no JSON encoding)
gh api repos/owner/repo/git/refs --method POST \
  --raw-field ref="refs/heads/new-branch" \
  --field sha="abc123"
```

**Pagination**:

```bash
# Get all pages
gh api --paginate repos/owner/repo/issues

# Limit pages
gh api --paginate --page-count 3 repos/owner/repo/issues
```

**Headers**:

```bash
# Custom headers
gh api repos/owner/repo/issues --header "Accept: application/vnd.github.v3+json"

# Check rate limit headers
gh api rate_limit --include
```

**Output processing**:

```bash
# Use jq for filtering
gh api repos/owner/repo/issues | jq '.[] | select(.state == "open") | .title'

# Use -q for extracting single value
gh api repos/owner/repo | jq -r '.full_name'
```

---

### 1.9.3 Executing GraphQL mutations for Projects V2

**When to use**: For GitHub Projects V2 operations (Projects V2 only supports GraphQL).

**Purpose**: Add, update, and query project board items.

**Basic syntax**:

```bash
gh api graphql -f query='GRAPHQL_QUERY_STRING'
```

**Query project structure**:

```bash
gh api graphql -f query='
  query {
    organization(login: "org-name") {
      projectV2(number: 1) {
        id
        title
        fields(first: 20) {
          nodes {
            ... on ProjectV2Field {
              id
              name
            }
            ... on ProjectV2SingleSelectField {
              id
              name
              options { id name }
            }
          }
        }
      }
    }
  }
'
```

**Add item to project**:

```bash
gh api graphql -f query='
  mutation {
    addProjectV2ItemById(input: {
      projectId: "PVT_kwDOABCDEF"
      contentId: "I_kwDOXYZ123"
    }) {
      item {
        id
      }
    }
  }
'
```

**Update item field (single-select)**:

```bash
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(input: {
      projectId: "PVT_kwDOABCDEF"
      itemId: "PVTI_lADOABCDEFzgABCDE"
      fieldId: "PVTF_lADOABCDEFzgABCDE"
      value: { singleSelectOptionId: "abc123" }
    }) {
      projectV2Item { id }
    }
  }
'
```

**Update item field (text)**:

```bash
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(input: {
      projectId: "PVT_kwDOABCDEF"
      itemId: "PVTI_lADOABCDEFzgABCDE"
      fieldId: "PVTF_lADOABCDEFzgABCDE"
      value: { text: "Custom value" }
    }) {
      projectV2Item { id }
    }
  }
'
```

**Query items with filters**:

```bash
gh api graphql -f query='
  query {
    node(id: "PVT_kwDOABCDEF") {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            id
            content {
              ... on Issue { number title state }
              ... on PullRequest { number title state }
            }
            fieldValues(first: 20) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  optionId
                  field { ... on ProjectV2SingleSelectField { name } }
                }
              }
            }
          }
        }
      }
    }
  }
'
```

**Important**: Always use variable binding for dynamic values in production:

```bash
gh api graphql \
  -f query='mutation($projectId: ID!, $itemId: ID!) { ... }' \
  -f projectId="$PROJECT_ID" \
  -f itemId="$ITEM_ID"
```

---

### 1.9.4 Parsing JSON responses with jq

**When to use**: For extracting specific fields from gh CLI JSON output.

**Purpose**: Process and filter JSON responses efficiently.

**Basic field extraction**:

```bash
# Extract single field
gh issue view 123 --repo owner/repo --json title | jq -r '.title'

# Extract nested field
gh pr view 456 --repo owner/repo --json mergeStateStatus | jq -r '.mergeStateStatus'

# Extract multiple fields
gh issue view 123 --repo owner/repo --json number,title,state | jq '{number, title, state}'
```

**Array operations**:

```bash
# Extract array of labels
gh issue view 123 --repo owner/repo --json labels | jq -r '.labels[].name'

# Join array into comma-separated string
gh issue view 123 --repo owner/repo --json labels | jq -r '.labels | map(.name) | join(",")'

# Filter array
gh issue list --repo owner/repo --json number,title,state | \
  jq '.[] | select(.state == "OPEN") | .title'

# Count array elements
gh issue list --repo owner/repo --json number | jq '. | length'
```

**Conditional logic**:

```bash
# If-then-else
gh pr view 456 --repo owner/repo --json mergeable | \
  jq 'if .mergeable == "MERGEABLE" then "ready" else "blocked" end'

# Check field exists
gh issue view 123 --repo owner/repo --json assignees | \
  jq 'if .assignees | length > 0 then "assigned" else "unassigned" end'
```

**Building JSON objects**:

```bash
# Create new object from fields
gh issue view 123 --repo owner/repo --json number,title | \
  jq '{issue_id: .number, issue_title: .title, processed_at: now}'

# Pass values as jq variables
PRIORITY="high"
gh issue view 123 --repo owner/repo --json number,title | \
  jq --arg pri "$PRIORITY" '{number, title, priority: $pri}'
```

**Error handling**:

```bash
# Provide default value if field is null
gh issue view 123 --repo owner/repo --json milestone | \
  jq -r '.milestone.title // "No milestone"'

# Exit with error if field is missing
gh pr view 456 --repo owner/repo --json mergeable | \
  jq -e '.mergeable == "MERGEABLE"' || echo "PR is not mergeable"
```

**Common patterns**:

```bash
# Extract ID from URL
ISSUE_URL="https://github.com/owner/repo/issues/123"
ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')

# Check if response is empty
RESULT=$(gh issue list --repo owner/repo --json number)
if [ "$(echo "$RESULT" | jq '. | length')" -eq 0 ]; then
    echo "No issues found"
fi

# Pretty print JSON
gh api repos/owner/repo | jq '.'

# Compact JSON (remove whitespace)
gh api repos/owner/repo | jq -c '.'

# Raw output (no quotes for strings)
gh api repos/owner/repo | jq -r '.full_name'
```

---

## Summary

This reference document covers all procedural aspects of GitHub API operations:

1. **Issue Operations** - Creating, updating, and managing issues
2. **PR Operations** - Creating, reviewing, and merging pull requests
3. **Projects V2** - Adding items, moving between columns, updating custom fields
4. **Thread Management** - Comments, replies, resolution, locking
5. **Rate Limit Handling** - Checking status, exponential backoff, queueing
6. **Quality Gates** - Authentication, permissions, existence, state, rate limits
7. **AI Maestro Coordination** - Receiving requests, sending responses, message formats
8. **Operation Workflow** - Step-by-step process from request to completion
9. **Tools Usage** - gh CLI commands, GraphQL mutations, jq parsing

Use the table of contents to quickly jump to the specific procedure you need for the current operation.
