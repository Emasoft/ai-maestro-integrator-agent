# Quality Gate Enforcement Checklist

Copy and use this checklist when processing a PR through quality gates.

## Pre-Review Gate
- [ ] Verify all tests pass locally
- [ ] Verify no linting errors
- [ ] Verify build succeeds
- [ ] Verify PR description present
- [ ] Verify issue linked
- [ ] Check for warning conditions
- [ ] Apply appropriate labels
- [ ] If passed: proceed to Review Gate
- [ ] If failed: follow Escalation Path A

## Review Gate
- [ ] Perform Stage 1: Quick Scan
- [ ] Perform Stage 2: Deep Dive (all 8 dimensions)
- [ ] Calculate confidence score
- [ ] Check for blocking issues
- [ ] Apply appropriate labels
- [ ] If passed (>= 80%): proceed to Pre-Merge Gate
- [ ] If failed: follow Escalation Path B

## Pre-Merge Gate
- [ ] Verify CI pipeline passes
- [ ] Verify no merge conflicts
- [ ] Verify review approval still valid
- [ ] Verify branch is up to date
- [ ] Apply appropriate labels
- [ ] If passed: proceed to merge
- [ ] If failed: follow Escalation Path C

## Post-Merge Gate
- [ ] Verify main branch builds
- [ ] Verify no regressions
- [ ] Verify deployment succeeds (if applicable)
- [ ] Apply appropriate labels
- [ ] If passed: close issue, integration complete
- [ ] If failed: follow Escalation Path D
