# Gate Override Examples

## Table of Contents

- [Overview](#overview)
- [Example 1: Pre-Review Gate Override (Urgent Hotfix)](#example-1-pre-review-gate-override-urgent-hotfix)
- [Example 2: Review Gate Override (Style Issues)](#example-2-review-gate-override-style-issues)
- [Example 3: Pre-Merge Gate Override (CI Infrastructure Outage)](#example-3-pre-merge-gate-override-ci-infrastructure-outage)
- [Example 4: REJECTED Override (Security Issue)](#example-4-rejected-override-security-issue)
- [Example 5: Pre-Merge Gate Override (Stale Approval)](#example-5-pre-merge-gate-override-stale-approval)
- [Example 6: Post-Merge Gate - Revert Decision (NO Override)](#example-6-post-merge-gate---revert-decision-no-override)
- [Override Documentation Checklist](#override-documentation-checklist)
- [Override Audit Trail](#override-audit-trail)

---

## Overview

Gate overrides are **exceptions to normal quality gate enforcement**. This document provides real-world examples of proper override documentation and procedures.

---

## Example 1: Pre-Review Gate Override (Urgent Hotfix)

**Scenario**: Critical security vulnerability needs immediate fix, but PR lacks full test coverage (75% vs 80% required).

**Gate**: Pre-Review Gate (coverage warning)
**Issue**: `gate:coverage-warning` applied
**Override Authority**: Project Maintainer

**Override Documentation**:

```markdown
**GATE OVERRIDE**

**Gate**: Pre-Review Gate
**Warning Overridden**: Test coverage 75% (threshold 80%)

**Reason**: Critical security hotfix for CVE-2024-12345 (SQL injection)

**Urgency**: Production vulnerability being actively exploited

**Approved by**: @maintainer (Alice Johnson)

**Risk Mitigation**:
- Manual testing completed for all affected code paths
- Security team reviewed fix
- Additional automated tests will be added in follow-up PR #456
- Coverage gap limited to error handling paths (non-critical)

**Follow-up Actions**:
- [ ] Issue #457: Add comprehensive tests for auth module (Due: 2024-02-10)
- [ ] Code review of auth module test suite (Assigned: @security-team)

**Override Label**: `gate:override-applied`

**Approval Timestamp**: 2024-02-04 14:30 UTC
```

**Commands**:

```bash
# Apply override label
gh pr edit 123 --add-label "gate:override-applied"

# Document override
gh pr comment 123 --body "$(cat override-docs.md)"

# Proceed with merge despite warning
gh pr merge 123 --squash
```

---

## Example 2: Review Gate Override (Style Issues)

**Scenario**: PR has minor style inconsistencies but otherwise excellent code. Review score: 78% (threshold 80%).

**Gate**: Review Gate
**Issue**: Confidence score below threshold due to style dimension (60%)
**Override Authority**: Senior Reviewer

**Override Documentation**:

```markdown
**GATE OVERRIDE**

**Gate**: Review Gate
**Score**: 78% (threshold 80%)

**Reason**: Style issues are minor and non-blocking. Core functionality is excellent:
- Correctness: 95%
- Security: 100%
- Performance: 90%
- Maintainability: 85%
- Testability: 90%
- Documentation: 85%
- Architecture: 95%
- Best Practices: 60% ← style issues only

**Approved by**: @senior-reviewer (Bob Smith)

**Justification**:
- Style issues are cosmetic (inconsistent indentation in comments)
- Core code quality is exceptional
- Author is new contributor, style will improve with experience
- Blocking on style would discourage valuable contribution

**Risk Mitigation**:
- Automated formatter will be applied post-merge
- Style guide linked in PR comments for future reference
- No functional impact from style issues

**Follow-up Actions**:
- [ ] Run code formatter on merged code
- [ ] Update CONTRIBUTING.md with style guidelines
- [ ] Add pre-commit hook for automatic formatting

**Override Label**: `gate:override-applied`

**Approval Timestamp**: 2024-02-04 16:45 UTC
```

**Note**: This override is acceptable because:

- Non-security issue
- Senior reviewer has authority
- Functional code quality is high
- Style can be fixed post-merge without risk

---

## Example 3: Pre-Merge Gate Override (CI Infrastructure Outage)

**Scenario**: GitHub Actions infrastructure is down. CI cannot run, but code has been manually tested.

**Gate**: Pre-Merge Gate
**Issue**: CI status unavailable (not failed, just not running)
**Override Authority**: AMOA

**Override Documentation**:

```markdown
**GATE OVERRIDE**

**Gate**: Pre-Merge Gate
**Check Overridden**: CI Pipeline Status

**Reason**: GitHub Actions infrastructure outage (confirmed on status.github.com)

**Evidence**:
- GitHub Status: Major outage affecting Actions (https://status.github.com/...)
- CI has not run for 4 hours across all PRs
- No code-related CI failures

**Approved by**: @amoa (AI Maestro Orchestration Agent)

**Risk Mitigation**:
- Manual testing completed locally:
  - All tests pass: `pytest --all`
  - Linting passes: `ruff check .`
  - Build succeeds: `make build`
- Code reviewed and approved by 2 reviewers
- Changes are low-risk (documentation update only)
- Post-merge: Will monitor main branch when CI recovers

**Follow-up Actions**:
- [ ] Monitor GitHub Actions status recovery
- [ ] Verify CI passes on main branch once Actions recover
- [ ] If CI fails post-recovery, investigate immediately

**Override Label**: `gate:override-applied`

**Approval Timestamp**: 2024-02-04 18:20 UTC
```

**Note**: Infrastructure outages are valid override reasons when:

- Outage is confirmed external
- Manual verification completed
- Risk is assessed as acceptable
- Monitoring plan is in place

---

## Example 4: REJECTED Override (Security Issue)

**Scenario**: PR has SQL injection vulnerability, but author requests override due to urgency.

**Gate**: Review Gate
**Issue**: Security vulnerability (BLOCKING)
**Override Request**: Author requests override for urgent feature launch

**REJECTION Documentation**:

```markdown
**GATE OVERRIDE REQUEST: REJECTED**

**Gate**: Review Gate
**Issue**: SQL injection vulnerability in user query handling

**Override Requested by**: @author
**Reason Given**: "Urgent feature launch deadline"

**REJECTED by**: @senior-reviewer

**Rejection Reason**: **Security vulnerabilities have NO OVERRIDE AUTHORITY**

Per quality gate policy:
- Security issues ALWAYS block
- No urgency justifies deploying vulnerable code
- Alternative approaches available

**Alternative Solution**:
1. Fix SQL injection (estimated 1 hour):
   - Use parameterized queries
   - Add input sanitization
2. Re-submit for review
3. Fast-track review given urgency (can complete in 2 hours total)

**Recommendation**: Fix vulnerability immediately. Fast-track review process, but do NOT override security gate.

**Policy Reference**: See amia-quality-gates SKILL.md, Override Authority Matrix
```

**Key Principle**: Security issues are NEVER overridden, regardless of urgency or authority.

---

## Example 5: Pre-Merge Gate Override (Stale Approval)

**Scenario**: PR approval is technically stale (15 lines changed after approval), but changes are trivial (typo fixes).

**Gate**: Pre-Merge Gate
**Issue**: Approval stale (changes after approval)
**Override Authority**: Original Reviewer

**Override Documentation**:

```markdown
**GATE OVERRIDE**

**Gate**: Pre-Merge Gate
**Check Overridden**: Stale Approval (changes after review)

**Reason**: Post-approval changes are trivial and do not affect reviewed code

**Changes After Approval**:
- README.md: Fixed 3 typos in documentation
- CHANGELOG.md: Updated version number
- Total: 15 lines changed, 0 lines of code affected

**Approved by**: @original-reviewer (Carol Lee)

**Justification**:
- Original review covered all functional code
- Post-review changes are documentation-only
- No code logic changes
- No new files added
- Changes are immediately visible in diff

**Risk Mitigation**:
- Reviewer verified diff of post-approval changes
- Changes are non-functional (docs only)
- No possibility of introducing bugs

**Follow-up Actions**: None required

**Override Label**: `gate:override-applied`

**Approval Timestamp**: 2024-02-04 20:15 UTC
```

**Note**: Stale approval overrides acceptable when:

- Original reviewer verifies new changes
- Changes are trivial (docs, formatting, comments)
- No functional code modified
- Reviewer confirms override

---

## Example 6: Post-Merge Gate - Revert Decision (NO Override)

**Scenario**: Post-merge gate fails. Main branch CI broken. Cannot override - must revert or hotfix.

**Gate**: Post-Merge Gate
**Issue**: Main CI fails after merge
**Decision**: REVERT (override not applicable)

**Response Documentation**:

```markdown
🚨 **POST-MERGE GATE FAILED**

**PR**: #789
**Issue**: Main branch CI broken after merge

**Failure**: Integration tests failing in payment processing module

**Decision**: REVERT (within 15 minutes of detection)

**Reasoning**:
- Main branch must remain healthy (non-negotiable)
- Fix is non-trivial (unclear root cause)
- Production risk unacceptable
- Hotfix would take >1 hour

**Actions Taken**:
1. ✅ Revert PR created: #790
2. ✅ Revert merged (bypassing gates due to emergency)
3. ✅ Main CI verified healthy after revert
4. ✅ Original author notified

**Follow-up**:
- Author will fix issues in original PR
- Re-submit as new PR when fixed
- Investigate why pre-merge gate didn't catch this

**Responsible**: @amoa

**Resolution Time**: 12 minutes (detection to revert completion)

**Lesson Learned**: Integration tests need to run in pre-merge gate, not just post-merge
```

**Note**: Post-merge failures cannot be "overridden" - they require immediate corrective action (revert or hotfix).

---

## Override Documentation Checklist

When documenting any override, ensure ALL fields are completed:

- [ ] **Gate** - Which gate is being overridden
- [ ] **Issue** - What specific check/condition is being overridden
- [ ] **Reason** - Why override is necessary
- [ ] **Approved by** - Name and role of authority approving override
- [ ] **Risk Mitigation** - What steps reduce risk of override
- [ ] **Follow-up Actions** - What will be done to address the gap later
- [ ] **Override Label** - `gate:override-applied` applied to PR
- [ ] **Approval Timestamp** - When override was approved

**Incomplete override documentation is grounds for rejecting the override.**

---

## Override Audit Trail

All overrides should be:

1. Documented in PR comments (as shown above)
2. Logged in repository wiki or override log file
3. Reviewed monthly for patterns
4. Analyzed for gate improvement opportunities

**Goal**: Overrides should be rare. Frequent overrides indicate gate policies need adjustment.
