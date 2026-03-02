# Completion Criteria

## Table of Contents

- 6.1 ALL criteria that must be true
  - 6.1.1 Review comments addressed
  - 6.1.2 PR comments acknowledged
  - 6.1.3 No new comments (45s wait)
  - 6.1.4 CI checks pass
  - 6.1.5 No unresolved threads
  - 6.1.6 Merge eligible
  - 6.1.7 PR not already merged
  - 6.1.8 Commits pushed
- 6.2 Failure handling by type

---

## 6.1 ALL criteria that must be true

**Critical rule**: A PR is ONLY complete when ALL criteria pass. A single failure means the PR is not ready.

### Summary checklist

```
[ ] 6.1.1 All review comments addressed
[ ] 6.1.2 All PR comments acknowledged
[ ] 6.1.3 No new comments after quiet period
[ ] 6.1.4 All required CI checks pass
[ ] 6.1.5 No unresolved conversation threads
[ ] 6.1.6 GitHub shows merge eligible
[ ] 6.1.7 PR is not already merged
[ ] 6.1.8 All local commits pushed to remote
```

---

### 6.1.1 Review comments addressed

**Definition**: Every comment left by reviewers during code review has been addressed.

**What "addressed" means**:
1. Code was changed according to the suggestion, OR
2. A reply explains why the suggestion was not followed, OR
3. The reviewer marked the thread as resolved, OR
4. The reviewer explicitly said "no action needed"

**Verification method**:
```bash
gh api repos/{owner}/{repo}/pulls/{pr}/reviews --jq '.[].state'
gh api repos/{owner}/{repo}/pulls/{pr}/comments
```

**Check for**:
- No `CHANGES_REQUESTED` review state without subsequent approval
- All comment threads have responses or resolution

**Failure indicators**:
- Review comment without response
- "Changes requested" review without new commits addressing it
- Comment explicitly says "please fix" without subsequent fix

### 6.1.2 PR comments acknowledged

**Definition**: Comments on the PR itself (not on code lines) have been acknowledged.

**What "acknowledged" means**:
- Question comments have answers
- Feedback comments have responses (agreement or explanation)
- Action item comments have been acted upon
- Informational comments may not need response

**Verification method**:
```bash
gh api repos/{owner}/{repo}/issues/{pr}/comments
```

**Determine if acknowledgment needed**:
| Comment Type | Needs Acknowledgment |
|--------------|---------------------|
| Question | Yes - answer required |
| Suggestion | Yes - agreement or explanation |
| Request for action | Yes - confirmation of action |
| Information sharing | No - unless question implied |
| Praise/thanks | No |

### 6.1.3 No new comments (quiet period)

**Definition**: No new activity on the PR after a brief quiet period.

**Why a quiet period**:
- GitHub webhooks can be delayed
- UI updates are not instant
- Comments might appear after we checked
- Prevents race conditions

**Implementation**:
```python
def check_quiet_period(pr_number, owner, repo):
    """Check if PR has been quiet - no recent activity."""
    import subprocess
    from datetime import datetime, timezone

    # Get latest activity timestamps
    cmd = f"gh api repos/{owner}/{repo}/issues/{pr_number}/comments --jq '.[].created_at' | tail -1"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if not result.stdout.strip():
        return True  # No comments at all

    last_comment = datetime.fromisoformat(result.stdout.strip().replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)

    # Use judgment - is this recent enough to indicate ongoing activity?
    time_since_comment = now - last_comment
    return time_since_comment.total_seconds() > 30  # brief quiet period
```

**If quiet period fails**:
- Wait for quiet period to pass
- Re-check other criteria after waiting
- If new activity detected, address it first

### 6.1.4 CI checks pass

**Definition**: All required status checks defined in branch protection rules pass.

**Verification method**:
```bash
gh pr checks {pr_number} --required
```

**Check states**:
| State | Meaning | PR Ready? |
|-------|---------|-----------|
| pass | Check succeeded | Yes |
| fail | Check failed | No |
| pending | Check running | No |
| skipped | Check skipped | Maybe (depends on rules) |

**Required vs optional**:
- **Required checks**: Must pass. Defined in branch protection.
- **Optional checks**: Nice to have. Failures noted but don't block.

**Handling pending checks**:
1. Do not report ready while checks pending
2. Set up polling to re-check
3. Wait until CI completes or fails
4. If CI appears stuck, escalate to user

### 6.1.5 No unresolved threads

**Definition**: All conversation threads on the PR are resolved.

**Thread types**:
1. **Review comment threads**: Started during code review
2. **PR comment threads**: On the PR itself
3. **Suggested change threads**: Created by "suggestion" feature

**Verification method**:
```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $pr: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $pr) {
        reviewThreads(first: 100) {
          nodes {
            isResolved
            comments(first: 1) {
              nodes {
                body
              }
            }
          }
        }
      }
    }
  }
' -f owner={owner} -f repo={repo} -F pr={pr_number}
```

**Resolution requirements**:
- GitHub's "Resolve conversation" button clicked, OR
- Thread has response AND reviewer approved, OR
- Thread marked as outdated (code changed)

### 6.1.6 Merge eligible

**Definition**: GitHub indicates the PR can be merged (merge button enabled).

**Verification method**:
```bash
gh pr view {pr_number} --json mergeable,mergeStateStatus
```

**Merge states**:
| State | Meaning | Action |
|-------|---------|--------|
| MERGEABLE | Can merge | Ready |
| CONFLICTING | Has conflicts | Resolve conflicts |
| UNKNOWN | Still calculating | Wait and re-check |
| BLOCKED | Rules prevent merge | Check what's blocking |

**Common blockers**:
- Required reviews not obtained
- Required checks not passing
- Branch protection rules not met
- User lacks merge permission

### 6.1.7 PR not already merged

**Definition**: The PR is still open and has not been merged.

**Verification method**:
```bash
gh pr view {pr_number} --json state,merged
```

**States**:
| State | Merged | Meaning |
|-------|--------|---------|
| OPEN | false | PR is active |
| CLOSED | false | PR was closed without merge |
| CLOSED | true | PR was merged |

**If already merged**:
- Stop all work on this PR
- Report to user: "PR #X was already merged"
- Clean up: remove worktrees, close tracking issues

### 6.1.8 Commits pushed

**Definition**: All local commits have been pushed to the remote branch.

**Verification method**:
```bash
git fetch origin
git log origin/{branch}..HEAD
```

**If output is empty**: All commits pushed (good)
**If output has commits**: Local commits not pushed (must push)

**Why this matters**:
- Reviews are based on pushed code
- CI runs on pushed code
- Unpushed commits are not visible to others

**Before reporting ready**:
1. Verify no unpushed commits
2. If unpushed commits exist, push them
3. Wait for CI to run on new commits
4. Re-verify all criteria

---

## 6.2 Failure handling by type

When a criterion fails, the response depends on the failure type.

### Failure type: Review comments not addressed

**Symptoms**:
- Review state is CHANGES_REQUESTED
- Comments without responses

**Resolution steps**:
1. Identify unaddressed comments
2. Delegate implementation work for code changes
3. Delegate response writing for non-code feedback
4. After changes, request re-review

### Failure type: PR comments not acknowledged

**Symptoms**:
- Questions without answers
- Suggestions without responses

**Resolution steps**:
1. Identify unanswered comments
2. If question can be answered by AI, delegate response
3. If question requires human input, escalate to user

### Failure type: New comments detected

**Symptoms**:
- Quiet period check fails
- New comment detected recently

**Resolution steps**:
1. Wait for quiet period to pass
2. If new comment needs response, address it
3. Restart verification loop

### Failure type: CI checks failing

**Symptoms**:
- `gh pr checks` shows failures
- Required check in failed state

**Resolution steps**:
1. Identify which check failed
2. Get failure details from check output
3. Delegate fix to implementation subagent
4. After fix pushed, wait for CI re-run

### Failure type: Unresolved threads

**Symptoms**:
- GraphQL query shows `isResolved: false`
- GitHub UI shows unresolved conversations

**Resolution steps**:
1. List all unresolved threads
2. For each: determine if code change or response needed
3. Delegate appropriate action
4. After addressing, threads should auto-resolve or can be manually resolved

### Failure type: Not merge eligible

**Symptoms**:
- mergeable state is CONFLICTING or BLOCKED

**For CONFLICTING**:
1. Delegate conflict resolution
2. Push resolved changes
3. Re-verify

**For BLOCKED**:
1. Identify blocker via `mergeStateStatus`
2. Address blocker (get review, fix check, etc.)
3. Re-verify

### Failure type: Already merged

**Symptoms**:
- state is CLOSED
- merged is true

**Resolution**:
1. Stop all work
2. Report: "PR #X already merged"
3. Clean up resources
4. No further action needed

### Failure type: Commits not pushed

**Symptoms**:
- `git log origin/branch..HEAD` shows commits

**Resolution steps**:
1. Push commits: `git push origin {branch}`
2. Wait for CI to start
3. Re-verify all criteria

---

## Quick Failure Response Matrix

| Criterion | Failure | Immediate Action |
|-----------|---------|------------------|
| 6.1.1 Reviews | Not addressed | Delegate changes |
| 6.1.2 Comments | Not acknowledged | Delegate responses |
| 6.1.3 Quiet period | New activity | Wait 45s, re-check |
| 6.1.4 CI | Failing | Delegate fix |
| 6.1.5 Threads | Unresolved | Delegate resolution |
| 6.1.6 Merge eligible | Blocked | Address blocker |
| 6.1.7 Not merged | Already merged | Stop, report, cleanup |
| 6.1.8 Pushed | Unpushed commits | Push, then re-verify |
