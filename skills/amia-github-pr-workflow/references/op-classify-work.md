# Operation: Classify Work Needed


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
- [Classification Decision Tree](#classification-decision-tree)
- [Work Types](#work-types)
- [Output](#output)
- [Error Handling](#error-handling)
- [Example](#example)

---
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-classify-work
---

## Purpose

Analyze a PR and determine what type of work is required to move it forward.

## When to Use

- After identifying author type
- Before delegating to subagent
- When PR status changes

## Prerequisites

- PR number known
- GitHub CLI authenticated
- PR author type already identified

## Steps

1. **Get PR status details**:
   ```bash
   gh pr view <PR_NUMBER> --json state,reviewDecision,statusCheckRollup,mergeable,isDraft
   ```

2. **Check review status**:
   ```bash
   gh pr view <PR_NUMBER> --json reviews --jq '.reviews[] | {state: .state, author: .author.login}'
   ```

3. **Check CI status**:
   ```bash
   gh pr checks <PR_NUMBER>
   ```

4. **Classify based on findings**:

## Classification Decision Tree

```
Is PR a draft?
├─► Yes → Wait (author still working)
└─► No → Continue

Has review been requested?
├─► No reviews yet → Code Review needed
└─► Has reviews → Check review state

Review state?
├─► APPROVED → Check CI
├─► CHANGES_REQUESTED → Code Changes needed
└─► COMMENTED → May need response

CI status?
├─► All passing → Check merge eligibility
├─► Failing → CI Verification needed
└─► Pending → Wait

Merge eligible?
├─► Yes → Verify Completion
└─► No (conflicts) → Code Changes needed
```

## Work Types

| Work Type | Description | Subagent Type |
|-----------|-------------|---------------|
| code_review | No review yet, needs review | Review subagent |
| code_changes | Changes requested or conflicts | Implementation subagent |
| ci_verification | CI failing or needs investigation | CI monitor subagent |
| verify_completion | Ready to verify all criteria | Use verification script |
| wait | Draft, pending CI, or human response needed | No action |

## Output

| Field | Type | Description |
|-------|------|-------------|
| work_type | string | Classification result |
| reason | string | Why this classification |
| blocking_issues | array | List of blocking items |

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Conflicting signals | Multiple issues | Prioritize: conflicts > CI > review |
| Stale review | Review on old commits | Treat as needing re-review |

## Example

```bash
# Get comprehensive PR state
gh pr view 123 --json state,reviewDecision,statusCheckRollup,mergeable,isDraft

# Output
{
  "state": "OPEN",
  "reviewDecision": "CHANGES_REQUESTED",
  "statusCheckRollup": {"state": "SUCCESS"},
  "mergeable": "MERGEABLE",
  "isDraft": false
}
# Classification: code_changes (changes requested by reviewer)
```
