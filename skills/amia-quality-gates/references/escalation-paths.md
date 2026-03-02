# Quality Gate Escalation Paths

When a gate fails, escalation follows a defined path based on the gate and failure type.

## Escalation Path A: Pre-Review Gate Failure

**Escalation Order:**

1. **First:** Notify PR author via PR comment
2. **Second:** If author unresponsive after 2 follow-up comments, notify AMOA (Orchestrator)
3. **Third:** If unresolved after AMOA notification, notify project maintainer

**Actions by Failure Type:**

| Failure Type | First Action | Escalation Trigger |
|--------------|--------------|-------------------|
| Tests failing | Comment with test output | Author does not fix after notification |
| Lint errors | Comment with lint output | Author does not fix after notification |
| Build failure | Comment with build log | Author does not fix after notification |
| Missing description | Request description | Author does not respond after notification |

## Escalation Path B: Review Gate Failure

**Escalation Order:**

1. **First:** Request changes via PR review
2. **Second:** If changes not addressed after re-request, notify AMOA
3. **Third:** If PR remains blocked, consider closing with explanation

**Actions by Failure Type:**

| Failure Type | First Action | Escalation Trigger |
|--------------|--------------|-------------------|
| Security issue | Block with detailed explanation | Not fixed after security guidance |
| Breaking change | Request compatibility fix | Not addressed after clarification |
| Low confidence | Request specific improvements | Score remains below threshold after changes |

**Override Authority:**

| Issue Type | Who Can Override |
|------------|------------------|
| Style issues | Senior reviewer |
| Minor docs gaps | Any reviewer with justification |
| Security issues | **No override** - must be fixed |
| Breaking changes | Project maintainer only |

## Escalation Path C: Pre-Merge Gate Failure

**Escalation Order:**

1. **First:** Automatic: Block merge, comment with failure
2. **Second:** Notify author to resolve (rebase, fix conflicts)
3. **Third:** If CI infrastructure issue, notify AMOA for investigation

**Actions by Failure Type:**

| Failure Type | First Action | Escalation Trigger |
|--------------|--------------|-------------------|
| CI failure | Re-run CI, analyze failure | Persistent failure after re-run |
| Merge conflict | Request rebase | Author unresponsive |
| Stale approval | Request re-review | Significant changes since approval |

## Escalation Path D: Post-Merge Gate Failure

**Escalation Order:**

1. **First:** Immediate notification to author and AMOA
2. **Second:** Evaluate revert vs hotfix
3. **Third:** If revert needed, execute and notify all stakeholders

**Actions by Failure Type:**

| Failure Type | Immediate Action | Follow-up |
|--------------|------------------|-----------|
| Main CI fails | Consider revert | Root cause analysis |
| Regression | Hotfix or revert decision | Post-incident review |
| Deployment fails | Rollback deployment | Deployment investigation |

**Revert Authority:**

| Severity | Who Can Revert |
|----------|----------------|
| Main branch broken | Any team member with merge access |
| Regression detected | Original author or reviewer |
| Deployment failure | DevOps or maintainer |
