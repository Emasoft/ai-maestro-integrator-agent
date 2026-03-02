# Operation: Verify PR Completion Criteria


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
- [Completion Criteria Explained](#completion-criteria-explained)
- [Output](#output)
- [Recommendations](#recommendations)
- [Error Handling](#error-handling)
- [Example](#example)
- [Critical Rule](#critical-rule)

---
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-verify-completion
---

## Purpose

Verify all completion criteria for a PR before reporting it as ready to merge.

## When to Use

- Before reporting PR ready to user
- After subagent completes review/fix work
- Before any merge operation
- When user asks if PR is ready

## Prerequisites

- PR number known
- All delegated work completed
- Verification script available

## Steps

1. **Run verification script**:
   ```bash
   python scripts/amia_verify_pr_completion.py --repo owner/repo --pr <PR_NUMBER>
   ```

2. **Parse output** - all criteria must pass:
   ```json
   {
     "pr_number": 123,
     "complete": true,
     "criteria": {
       "reviews_addressed": true,
       "comments_acknowledged": true,
       "no_new_comments": true,
       "ci_passing": true,
       "no_unresolved_threads": true,
       "merge_eligible": true,
       "not_merged": true,
       "commits_pushed": true
     },
     "failing_criteria": [],
     "recommendation": "ready_to_merge"
   }
   ```

3. **If complete: true** - Report to user, await merge decision

4. **If complete: false** - Identify failing criteria and delegate fixes

## Completion Criteria Explained

| Criterion | Meaning | How to Fix |
|-----------|---------|------------|
| reviews_addressed | All review comments have responses | Reply to each comment |
| comments_acknowledged | PR conversation comments addressed | Reply or resolve |
| no_new_comments | 45s quiet period (no new activity) | Wait and re-verify |
| ci_passing | All CI checks green | Fix failing tests/builds |
| no_unresolved_threads | All review threads resolved | Resolve each thread |
| merge_eligible | No conflicts, branch up to date | Rebase or merge base |
| not_merged | PR still open | Nothing to do (already done) |
| commits_pushed | Latest work is pushed | Push pending commits |

## Output

| Field | Type | Description |
|-------|------|-------------|
| complete | boolean | True if all criteria pass |
| failing_criteria | array | List of failing criterion names |
| recommendation | string | ready_to_merge, needs_work, or blocked |

## Recommendations

| Value | Meaning | Action |
|-------|---------|--------|
| ready_to_merge | All criteria pass | Report to user |
| needs_work | Fixable issues | Delegate fixes |
| blocked | Unfixable without user | Escalate |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Script fails | API error or PR not found | Check PR exists, retry |
| Intermittent failure | Race condition | Wait 45s and re-verify |
| Persistent failure | Real issue | Identify and delegate fix |

## Example

```bash
# Run verification
python scripts/amia_verify_pr_completion.py --repo Emasoft/project --pr 123

# Output showing failure
{
  "pr_number": 123,
  "complete": false,
  "criteria": {
    "reviews_addressed": true,
    "comments_acknowledged": true,
    "no_new_comments": true,
    "ci_passing": false,
    "no_unresolved_threads": true,
    "merge_eligible": true,
    "not_merged": true,
    "commits_pushed": true
  },
  "failing_criteria": ["ci_passing"],
  "recommendation": "needs_work"
}
# Action: Delegate CI fix to implementation subagent
```

## Critical Rule

**Always verify before reporting.** Never tell user a PR is ready without running verification. False positives damage trust.
