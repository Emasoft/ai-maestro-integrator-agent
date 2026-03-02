# Verification Workflow

## Table of Contents

- 3.1 Pre-review verification checklist
- 3.2 Post-review verification checklist
- 3.3 CI check verification
- 3.4 Thread resolution verification
- 3.5 Merge readiness verification
- 3.6 The 4-verification-loop protocol
  - 3.6.1 Loop structure and timing
  - 3.6.2 Exit conditions
  - 3.6.3 Escalation triggers

---

## 3.1 Pre-review verification checklist

**Purpose**: Ensure the PR is ready for review before delegating review work.

**Run this checklist before spawning a review subagent**.

### Checklist items

| Item | Verification Method | Pass Condition |
|------|---------------------|----------------|
| PR is open | `gh pr view --json state` | state == "OPEN" |
| PR is not draft | `gh pr view --json isDraft` | isDraft == false |
| PR has description | `gh pr view --json body` | body is not empty |
| Base branch exists | `git branch -r` | base branch listed |
| Head branch exists | `git branch -r` | head branch listed |
| No merge conflicts | `gh pr view --json mergeable` | mergeable != "CONFLICTING" |
| CI not failing | `gh pr checks` | No failed required checks |

### Automated verification

Run the verification script:
```bash
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123 --stage pre-review
```

### If verification fails

| Failure | Action |
|---------|--------|
| PR is draft | Wait or ask user if draft should be converted |
| Missing description | Note in report, may proceed with review |
| Merge conflicts | Delegate conflict resolution before review |
| CI failing | Delegate CI fix before review |

---

## 3.2 Post-review verification checklist

**Purpose**: Ensure all review feedback has been addressed before marking PR ready.

**Run this checklist after implementation subagent reports completion**.

### Checklist items

| Item | Verification Method | Pass Condition |
|------|---------------------|----------------|
| All review comments addressed | `gh api` review comments endpoint | All have responses or resolution |
| No pending review requests | `gh pr view --json reviewRequests` | reviewRequests is empty |
| Latest review is not "changes requested" | `gh pr view --json latestReviews` | No CHANGES_REQUESTED in latest |
| New commits since last review | `gh api` commits endpoint | Commits exist after review |

### Comment addressing criteria

A review comment is considered "addressed" when:
1. Code was changed per the comment's suggestion, OR
2. A reply explains why the suggestion was not followed, OR
3. The comment thread is resolved

### Automated verification

```bash
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123 --stage post-review
```

---

## 3.3 CI check verification

**Purpose**: Ensure all required CI checks pass before considering PR ready.

### Verification method

```bash
gh pr checks <pr_number> --required
```

### Interpretation

| Check State | Meaning | Action |
|-------------|---------|--------|
| pass | Check completed successfully | Continue |
| fail | Check failed | Delegate fix |
| pending | Check still running | Wait and re-check |
| skipped | Check was skipped | Verify if acceptable |

### Required vs optional checks

**Required checks** (must pass):
- Defined in repository branch protection rules
- Listed with `--required` flag

**Optional checks** (nice to have):
- All other checks
- Failures should be noted but don't block

### CI verification timing

1. Check immediately after commit push
2. If pending, poll frequently until CI completes
3. If CI appears stuck, escalate to user
4. No fixed time limits - wait until CI completes or fails

---

## 3.4 Thread resolution verification

**Purpose**: Ensure all conversation threads on the PR are resolved.

### What counts as a thread

1. **Review comments**: Comments left during code review
2. **PR comments**: Comments on the PR itself (not on code)
3. **Resolved threads**: Conversation threads marked as resolved

### Verification method

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments
gh api repos/{owner}/{repo}/issues/{pr}/comments
gh api repos/{owner}/{repo}/pulls/{pr}/reviews
```

### Resolution criteria

| Thread Type | Resolution Criteria |
|-------------|---------------------|
| Review comment on code | Has reply OR is resolved |
| PR-level comment | Has reply (if question) OR acknowledged |
| Review requesting changes | New review approves OR changes made |

### Unresolved thread handling

1. List all unresolved threads
2. Categorize by: needs-code-change, needs-response, needs-clarification
3. Delegate appropriate action for each category

---

## 3.5 Merge readiness verification

**Purpose**: Final verification that all criteria are met before reporting ready to merge.

### Complete criteria checklist

All of these MUST be true:

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | All review comments addressed | See 3.2 |
| 2 | All PR comments acknowledged | See 3.4 |
| 3 | No new comments in 45 seconds | Quiet period check |
| 4 | CI checks passing | See 3.3 |
| 5 | No unresolved threads | See 3.4 |
| 6 | Merge eligible (GitHub shows merge button enabled) | `gh pr view --json mergeable` |
| 7 | PR not already merged | `gh pr view --json state` |
| 8 | Commits have been pushed | Compare commit SHAs |

### The quiet period check

**Why**: GitHub webhooks and UI updates can have delays. A comment might appear after we checked.

**Implementation**:
1. Record timestamp of last comment/activity
2. Wait briefly for any pending updates
3. Re-check for new activity
4. If no new activity, proceed
5. If new activity, repeat the quiet period check

### Merge eligibility states

| State | Meaning | Action |
|-------|---------|--------|
| MERGEABLE | Can be merged | Ready to merge |
| CONFLICTING | Has merge conflicts | Delegate conflict resolution |
| UNKNOWN | GitHub still calculating | Wait and re-check |
| BLOCKED | Protected branch rules not met | Check what's blocking |

---

## 3.6 The 4-verification-loop protocol

**Purpose**: Systematic approach to ensure PR is truly complete.

### 3.6.1 Loop structure and timing

The protocol consists of 4 verification passes with specific timing.

```
┌─────────────────────────────────────────────────────────┐
│                    VERIFICATION LOOP                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Pass 1: Initial Check                                  │
│  ├─ Run full verification script                        │
│  ├─ If all pass → Continue to Pass 2                   │
│  └─ If any fail → Address failures, restart loop       │
│                                                         │
│  [Brief wait]                                           │
│                                                         │
│  Pass 2: Confirmation Check                             │
│  ├─ Run full verification script                        │
│  ├─ If all pass → Continue to Pass 3                   │
│  └─ If any fail → Address failures, restart loop       │
│                                                         │
│  [Brief wait]                                           │
│                                                         │
│  Pass 3: Quiet Period Start                             │
│  ├─ Run full verification script                        │
│  ├─ Record timestamp                                    │
│  ├─ If all pass → Continue to Pass 4                   │
│  └─ If any fail → Address failures, restart loop       │
│                                                         │
│  [Quiet period - wait for any pending updates]          │
│                                                         │
│  Pass 4: Final Verification                             │
│  ├─ Run full verification script                        │
│  ├─ Check no new activity since Pass 3                  │
│  ├─ If all pass → REPORT READY TO MERGE               │
│  └─ If any fail → Address failures, restart loop       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.6.2 Exit conditions

**Successful exit** (report ready to merge):
- All 4 passes complete
- All criteria pass on all 4 passes
- No new activity during quiet period

**Failure exit** (do not report ready):
- Any criterion fails
- New activity detected during quiet period
- Maximum loop iterations exceeded (5 iterations)

**Escalation exit** (report to user):
- Maximum iterations exceeded
- Unresolvable blocker detected
- CI appears stuck

### 3.6.3 Escalation triggers

Escalate to user immediately when:

| Trigger | Example | Escalation Message |
|---------|---------|-------------------|
| Repeated failures | Same criterion fails 3 times | "PR #X blocked by [criterion] - needs attention" |
| Unresolvable blocker | Branch protection requires manual approval | "PR #X requires [action] that I cannot perform" |
| New activity from human | Human reviewer adds comment | "Human reviewer commented on PR #X - please review" |
| CI stuck | CI pending unusually long | "CI checks for PR #X appear stuck - please investigate" |

---

## Verification Script Usage

### Full verification

```bash
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123
```

### Stage-specific verification

```bash
# Pre-review only
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123 --stage pre-review

# Post-review only
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123 --stage post-review

# CI only
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123 --stage ci

# Merge readiness only
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123 --stage merge
```

### Output interpretation

```json
{
  "complete": false,
  "criteria": {
    "reviews_addressed": true,
    "comments_acknowledged": true,
    "no_new_comments": false,
    "ci_passing": true,
    "no_unresolved_threads": true,
    "merge_eligible": true,
    "not_merged": true,
    "commits_pushed": true
  },
  "failing_criteria": ["no_new_comments"],
  "recommendation": "needs_work",
  "details": "New comment detected 10 seconds ago. Wait for quiet period."
}
```
