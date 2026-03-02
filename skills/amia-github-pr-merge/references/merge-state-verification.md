# Merge State Verification

This document explains why GraphQL must be used as the authoritative source for PR merge state, and how to properly verify merge status before and after merge operations.

## Table of Contents

- 1.1 Why `gh pr view --json state` can be stale
  - 1.1.1 REST API caching behavior
  - 1.1.2 Race conditions in merge state
- 1.2 GraphQL as the source of truth
  - 1.2.1 GraphQL query for merge state
  - 1.2.2 Interpreting MergeStateStatus values
- 1.3 MergeStateStatus values explained
  - 1.3.1 MERGEABLE - safe to merge
  - 1.3.2 CONFLICTING - conflicts exist
  - 1.3.3 UNKNOWN - state being computed
  - 1.3.4 BLOCKED - branch protection rules blocking
  - 1.3.5 BEHIND - branch needs update
  - 1.3.6 DIRTY - merge commit cannot be cleanly created
  - 1.3.7 UNSTABLE - failing required status checks
- 1.4 Pre-merge verification checklist
  - 1.4.1 Required checks before merge
  - 1.4.2 Verification script usage

---

## 1.1 Why `gh pr view --json state` Can Be Stale

### 1.1.1 REST API Caching Behavior

The GitHub REST API (which `gh pr view` uses) employs aggressive caching for performance reasons. This means:

1. **Response caching**: GitHub caches REST API responses for varying durations
2. **ETags and conditional requests**: Even with fresh requests, the underlying data may be cached at GitHub's infrastructure layer
3. **Eventual consistency**: After a merge operation, the REST API may continue returning `OPEN` state for several seconds

**Example of stale data:**

```bash
# This can return state="OPEN" even after PR is merged
gh pr view 123 --repo owner/repo --json state
# Output: {"state":"OPEN"}  # STALE!

# Meanwhile, the PR is actually merged in GitHub's database
```

### 1.1.2 Race Conditions in Merge State

Race conditions occur when:

1. **Concurrent operations**: Multiple actors (humans, bots) operating on the same PR
2. **CI completion timing**: Status checks completing at the moment of merge attempt
3. **Review submission**: Approvals being added while merge is in progress
4. **Branch updates**: Base branch receiving commits during merge

The REST API cannot guarantee atomicity in these scenarios. Only GraphQL with the right queries provides the real-time state.

---

## 1.2 GraphQL as the Source of Truth

### 1.2.1 GraphQL Query for Merge State

The authoritative query for PR merge state:

```graphql
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      id
      number
      title
      state
      merged
      mergedAt
      mergeCommit {
        oid
        messageHeadline
      }
      mergeable
      mergeStateStatus
      autoMergeRequest {
        enabledAt
        mergeMethod
      }
      reviewDecision
      commits(last: 1) {
        nodes {
          commit {
            statusCheckRollup {
              state
            }
          }
        }
      }
    }
  }
}
```

**Execute with gh CLI:**

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        state
        merged
        mergedAt
        mergeCommit { oid }
        mergeable
        mergeStateStatus
      }
    }
  }
' -f owner="owner" -f repo="repo" -F number=123
```

### 1.2.2 Interpreting MergeStateStatus Values

The `mergeStateStatus` field is the definitive indicator of whether a PR can be merged. The `state` field alone is insufficient - it only tells you OPEN/CLOSED/MERGED at a high level.

**Key fields to check:**

| Field | Type | Description |
|-------|------|-------------|
| `state` | Enum | OPEN, CLOSED, or MERGED |
| `merged` | Boolean | True if PR has been merged |
| `mergedAt` | DateTime | Timestamp of merge (null if not merged) |
| `mergeCommit.oid` | String | SHA of merge commit (null if not merged) |
| `mergeable` | Enum | MERGEABLE, CONFLICTING, or UNKNOWN |
| `mergeStateStatus` | Enum | Detailed merge eligibility status |

**Decision logic:**

```python
# Check if PR is merged
if data["merged"] == True and data["mergeCommit"]["oid"]:
    # PR is definitely merged, mergeCommit.oid is the merge SHA
    pass

# Check if PR can be merged now
if data["mergeStateStatus"] == "MERGEABLE":
    # Safe to merge
    pass
elif data["mergeStateStatus"] == "UNKNOWN":
    # Retry after short delay
    pass
else:
    # Cannot merge - check specific status for reason
    pass
```

---

## 1.3 MergeStateStatus Values Explained

### 1.3.1 MERGEABLE - Safe to Merge

**Meaning**: The PR can be merged right now. All requirements are satisfied.

**What this guarantees:**
- No merge conflicts exist
- All required status checks have passed
- All required reviews are approved
- Branch protection rules are satisfied

**Action**: Proceed with merge operation.

### 1.3.2 CONFLICTING - Conflicts Exist

**Meaning**: The PR has merge conflicts that must be resolved before merging.

**Causes:**
- Files modified in both the PR branch and base branch
- File deletions in one branch, modifications in another
- Rename conflicts

**Action**:
1. Update PR branch with base branch changes
2. Resolve conflicts locally
3. Push resolved changes
4. Wait for new status check

### 1.3.3 UNKNOWN - State Being Computed

**Meaning**: GitHub is calculating the merge state. This is temporary.

**When this occurs:**
- Immediately after PR creation
- After pushing new commits
- After base branch changes
- During high API load periods

**Action**: Wait 5-10 seconds and retry the query. Implement exponential backoff:

```python
import time

def wait_for_merge_state(max_retries=5):
    for attempt in range(max_retries):
        state = get_merge_state_status()
        if state != "UNKNOWN":
            return state
        time.sleep(2 ** attempt)  # 1, 2, 4, 8, 16 seconds
    raise TimeoutError("Merge state still UNKNOWN after retries")
```

### 1.3.4 BLOCKED - Branch Protection Rules Blocking

**Meaning**: Branch protection rules prevent the merge.

**Common causes:**
- Required status checks not passing
- Required number of approvals not met
- CODEOWNERS review not approved
- Required conversation resolution not met
- Administrator override required

**Action**: Check specific blocking requirements:

```graphql
query {
  repository(owner: "owner", name: "repo") {
    pullRequest(number: 123) {
      mergeStateStatus
      reviewDecision
      commits(last: 1) {
        nodes {
          commit {
            statusCheckRollup {
              state
              contexts(first: 50) {
                nodes {
                  ... on CheckRun {
                    name
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

### 1.3.5 BEHIND - Branch Needs Update

**Meaning**: The PR branch is behind the base branch and must be updated before merge.

**When this occurs:**
- Branch protection requires "up to date before merge"
- Base branch has received new commits

**Action**:
1. Update PR branch: `gh pr update-branch 123`
2. Or merge base into PR branch locally
3. Wait for status checks to complete

### 1.3.6 DIRTY - Merge Commit Cannot Be Cleanly Created

**Meaning**: GitHub cannot create a clean merge commit.

**Causes:**
- Complex merge conflicts
- Submodule issues
- Git history problems

**Action**: Manual intervention required:
1. Checkout PR branch locally
2. Merge base branch manually
3. Resolve all issues
4. Force push updated branch

### 1.3.7 UNSTABLE - Failing Required Status Checks

**Meaning**: One or more required status checks are failing.

**Note**: This is different from BLOCKED - UNSTABLE specifically indicates status check failures, while BLOCKED can be any branch protection rule.

**Action**:
1. Query status checks to identify failures
2. Fix failing checks
3. Push updates or re-run workflows

---

## 1.4 Pre-Merge Verification Checklist

### 1.4.1 Required Checks Before Merge

Always verify these conditions before attempting a merge:

1. **PR is not already merged**
   ```python
   assert data["merged"] == False
   assert data["state"] == "OPEN"
   ```

2. **No merge conflicts**
   ```python
   assert data["mergeable"] != "CONFLICTING"
   ```

3. **Merge state is determined**
   ```python
   assert data["mergeStateStatus"] != "UNKNOWN"
   ```

4. **PR is mergeable**
   ```python
   assert data["mergeStateStatus"] == "MERGEABLE"
   ```

5. **CI status is acceptable** (if not ignoring CI)
   ```python
   ci_state = data["commits"]["nodes"][0]["commit"]["statusCheckRollup"]["state"]
   assert ci_state == "SUCCESS"
   ```

6. **Review decision is acceptable** (if reviews required)
   ```python
   # APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED, or null
   assert data["reviewDecision"] in ["APPROVED", None]
   ```

### 1.4.2 Verification Script Usage

Use the provided `amia_test_pr_merge_ready.py` script:

```bash
# Full verification
python scripts/amia_test_pr_merge_ready.py --pr 123 --repo owner/repo

# JSON output explains any blocking reasons:
# {
#   "ready": false,
#   "blocking_reasons": [
#     {"code": "CI_FAILING", "message": "Required status check 'tests' is failing"},
#     {"code": "REVIEW_REQUIRED", "message": "Waiting for required review approval"}
#   ],
#   "merge_state_status": "BLOCKED",
#   "mergeable": "MERGEABLE"
# }
```

**Exit codes:**
- `0`: Ready to merge
- `1`: CI failing
- `2`: Conflicts exist
- `3`: Unresolved threads
- `4`: Reviews required/changes requested

The script automatically handles UNKNOWN state with retries, so you don't need to implement retry logic in your automation.
