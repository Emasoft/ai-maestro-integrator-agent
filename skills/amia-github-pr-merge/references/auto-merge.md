# Auto-Merge Configuration

This document explains how to configure and manage GitHub's auto-merge feature, which automatically merges a pull request when all requirements are satisfied.

## Table of Contents

- 3.1 Setting up auto-merge via GraphQL API
  - 3.1.1 EnablePullRequestAutoMerge mutation
  - 3.1.2 Required permissions
- 3.2 Requirements for auto-merge
  - 3.2.1 Repository settings
  - 3.2.2 Branch protection rules
  - 3.2.3 Required status checks
- 3.3 Canceling auto-merge
  - 3.3.1 DisablePullRequestAutoMerge mutation
  - 3.3.2 When auto-merge is automatically canceled
- 3.4 Auto-merge with required reviewers
  - 3.4.1 Approval requirements
  - 3.4.2 Review dismissal handling

---

## 3.1 Setting Up Auto-Merge via GraphQL API

### 3.1.1 EnablePullRequestAutoMerge Mutation

Auto-merge is enabled using the GraphQL API. The REST API does not support this operation.

**GraphQL mutation:**

```graphql
mutation EnableAutoMerge($pullRequestId: ID!, $mergeMethod: PullRequestMergeMethod!) {
  enablePullRequestAutoMerge(input: {
    pullRequestId: $pullRequestId
    mergeMethod: $mergeMethod
  }) {
    pullRequest {
      id
      autoMergeRequest {
        enabledAt
        mergeMethod
        enabledBy {
          login
        }
      }
    }
  }
}
```

**Execute with gh CLI:**

```bash
# First, get the PR's node ID
PR_ID=$(gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        id
      }
    }
  }
' -f owner="owner" -f repo="repo" -F number=123 --jq '.data.repository.pullRequest.id')

# Then enable auto-merge
gh api graphql -f query='
  mutation($prId: ID!, $method: PullRequestMergeMethod!) {
    enablePullRequestAutoMerge(input: {
      pullRequestId: $prId
      mergeMethod: $method
    }) {
      pullRequest {
        autoMergeRequest {
          enabledAt
          mergeMethod
        }
      }
    }
  }
' -f prId="$PR_ID" -f method="SQUASH"
```

**Available merge methods:**
- `MERGE` - Create a merge commit
- `SQUASH` - Squash all commits into one
- `REBASE` - Rebase commits onto base branch

**Optional parameters:**

```graphql
mutation {
  enablePullRequestAutoMerge(input: {
    pullRequestId: "PR_kwDOxxxxxx"
    mergeMethod: SQUASH
    commitHeadline: "feat: add user authentication (#123)"
    commitBody: "Detailed description of the changes"
    authorEmail: "author@example.com"
  }) {
    pullRequest {
      autoMergeRequest {
        enabledAt
      }
    }
  }
}
```

### 3.1.2 Required Permissions

**User permissions required:**
- Write access to the repository
- Ability to merge PRs (not blocked by branch protection)

**Repository requirements:**
- Auto-merge must be enabled in repository settings
- Branch protection rules must be configured (auto-merge only works with protected branches)

**Check if user can enable auto-merge:**

```graphql
query {
  repository(owner: "owner", name: "repo") {
    pullRequest(number: 123) {
      viewerCanEnableAutoMerge
      viewerCanDisableAutoMerge
    }
  }
}
```

**Possible reasons for `viewerCanEnableAutoMerge: false`:**
1. Repository doesn't allow auto-merge
2. Branch is not protected
3. User doesn't have write access
4. Auto-merge already enabled
5. PR is already merged
6. PR is closed

---

## 3.2 Requirements for Auto-Merge

### 3.2.1 Repository Settings

Auto-merge must be explicitly enabled in repository settings.

**Enable via UI:**
Settings > General > Pull Requests > "Allow auto-merge"

**Check via API:**

```bash
gh api repos/{owner}/{repo} --jq '.allow_auto_merge'
```

**Enable via API:**

```bash
gh api repos/{owner}/{repo} -X PATCH -f allow_auto_merge=true
```

**Note**: Enabling this setting does not automatically enable auto-merge on PRs. Each PR must have auto-merge enabled individually.

### 3.2.2 Branch Protection Rules

**Auto-merge only works with protected branches.**

If the base branch (e.g., `main`) has no branch protection rules, auto-merge cannot be enabled. This is a GitHub design decision to ensure there are actual requirements to wait for.

**Minimum branch protection for auto-merge:**

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci/build", "ci/test"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
```

**Check branch protection:**

```graphql
query {
  repository(owner: "owner", name: "repo") {
    branchProtectionRules(first: 10) {
      nodes {
        pattern
        requiresStatusChecks
        requiredStatusCheckContexts
        requiresApprovingReviews
        requiredApprovingReviewCount
      }
    }
  }
}
```

### 3.2.3 Required Status Checks

Auto-merge waits for all required status checks to pass.

**How it works:**

1. Auto-merge is enabled on PR
2. GitHub monitors required status check contexts
3. When ALL required checks show `success`, merge proceeds
4. If any required check fails, auto-merge remains queued (does not cancel)

**Status check states:**

| State | Auto-merge behavior |
|-------|-------------------|
| `pending` | Waits |
| `success` | Proceeds (if all checks pass) |
| `failure` | Waits (check may be re-run) |
| `error` | Waits (check may be re-run) |

**Query status checks:**

```graphql
query {
  repository(owner: "owner", name: "repo") {
    pullRequest(number: 123) {
      commits(last: 1) {
        nodes {
          commit {
            statusCheckRollup {
              state
              contexts(first: 50) {
                nodes {
                  ... on CheckRun {
                    name
                    status
                    conclusion
                  }
                  ... on StatusContext {
                    context
                    state
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 3.3 Canceling Auto-Merge

### 3.3.1 DisablePullRequestAutoMerge Mutation

**GraphQL mutation:**

```graphql
mutation DisableAutoMerge($pullRequestId: ID!) {
  disablePullRequestAutoMerge(input: {
    pullRequestId: $pullRequestId
  }) {
    pullRequest {
      id
      autoMergeRequest {
        enabledAt
      }
    }
  }
}
```

**Execute with gh CLI:**

```bash
# Get PR ID first
PR_ID=$(gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        id
      }
    }
  }
' -f owner="owner" -f repo="repo" -F number=123 --jq '.data.repository.pullRequest.id')

# Disable auto-merge
gh api graphql -f query='
  mutation($prId: ID!) {
    disablePullRequestAutoMerge(input: {
      pullRequestId: $prId
    }) {
      pullRequest {
        autoMergeRequest {
          enabledAt
        }
      }
    }
  }
' -f prId="$PR_ID"
```

**After disabling:**
- `autoMergeRequest` will be `null`
- PR remains open
- Manual merge is required

### 3.3.2 When Auto-Merge Is Automatically Canceled

GitHub automatically cancels auto-merge in these situations:

1. **Base branch changed**: If the base branch reference changes (e.g., someone changes the target from `main` to `develop`)

2. **New commits pushed**: Pushing new commits to the PR branch cancels auto-merge. You must re-enable it.

3. **PR closed**: Closing the PR cancels auto-merge

4. **Merge conflicts introduced**: If the base branch receives commits that conflict with the PR

5. **Required reviewers change their review**: If a required reviewer dismisses their approval or requests changes

**Auto-merge is NOT canceled by:**
- Failing status checks (just waits for re-run)
- Comments or discussions
- Label changes
- Milestone changes

**Monitor auto-merge status:**

```graphql
query {
  repository(owner: "owner", name: "repo") {
    pullRequest(number: 123) {
      autoMergeRequest {
        enabledAt
        enabledBy { login }
        mergeMethod
      }
    }
  }
}
```

If `autoMergeRequest` is `null`, auto-merge is not enabled (or was canceled).

---

## 3.4 Auto-Merge with Required Reviewers

### 3.4.1 Approval Requirements

When branch protection requires reviews, auto-merge waits for approvals.

**Configuration example:**

```json
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 2,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  }
}
```

**Auto-merge behavior:**
1. Waits for required number of approvals
2. Waits for CODEOWNERS approval if required
3. Re-waits if reviews are dismissed
4. Proceeds only when `reviewDecision` is `APPROVED`

**Check review requirements:**

```graphql
query {
  repository(owner: "owner", name: "repo") {
    pullRequest(number: 123) {
      reviewDecision
      autoMergeRequest {
        enabledAt
      }
      latestReviews(first: 10) {
        nodes {
          state
          author { login }
          submittedAt
        }
      }
    }
  }
}
```

**Review decision values:**

| Value | Meaning | Auto-merge behavior |
|-------|---------|-------------------|
| `APPROVED` | Has required approvals | Proceeds (if checks pass) |
| `CHANGES_REQUESTED` | Has change requests | Waits |
| `REVIEW_REQUIRED` | Waiting for reviews | Waits |
| `null` | No review policy | Proceeds (if checks pass) |

### 3.4.2 Review Dismissal Handling

When "dismiss stale reviews" is enabled:

1. **New commits pushed** → Existing approvals are dismissed → Auto-merge canceled (new commits)
2. **Re-approval needed** → Auto-merge must be re-enabled after re-approval

**Workflow for stale review handling:**

```bash
# 1. Check if reviews are stale
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        reviewDecision
        autoMergeRequest { enabledAt }
      }
    }
  }
' -f owner="owner" -f repo="repo" -F number=123

# 2. If auto-merge was canceled and reviews re-approved,
#    re-enable auto-merge
```

**Best practice for CI/CD:**

When automating auto-merge:
1. Enable auto-merge after PR is created
2. If commits are pushed (e.g., by automation), re-enable auto-merge
3. Monitor for auto-merge cancellation
4. Log when auto-merge completes or fails

**Timeline example:**

```
t0: PR created
t1: Auto-merge enabled (SQUASH)
t2: CI starts
t3: Review requested
t4: Review approved
t5: CI passes
t6: Auto-merge executes → PR merged
```

**With stale review dismissal:**

```
t0: PR created
t1: Auto-merge enabled (SQUASH)
t2: Review approved
t3: New commit pushed → Auto-merge CANCELED, review dismissed
t4: Re-approval obtained
t5: Auto-merge re-enabled
t6: CI passes
t7: Auto-merge executes → PR merged
```
