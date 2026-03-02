# Quality Gate Troubleshooting

Common issues and solutions when working with quality gates.

## Gate Appears Stuck

**Symptom:** PR has gate label but no progress.

**Resolution:**
1. Check if all required checks are reporting status
2. Verify CI is running and completing
3. Check for infrastructure issues
4. Manually re-trigger gate evaluation if needed

## False Positive Gate Failure

**Symptom:** Gate fails but code is correct.

**Resolution:**
1. Investigate the specific failure
2. If flaky test, add `gate:flaky-test` label and re-run
3. If infrastructure issue, document and retry
4. If persistent false positive, consider override with documentation

## Escalation Not Triggering

**Symptom:** Gate failed but no escalation occurred.

**Resolution:**
1. Verify escalation automation is configured
2. Check notification channels are working
3. Manually trigger escalation if automation failed
4. Document automation gap for fixing

## Override Needed but No Authority

**Symptom:** Gate needs override but authorized person unavailable.

**Resolution:**
1. Document the urgency in PR
2. Contact alternate authorities listed in escalation path
3. If truly critical and no authority available, escalate to project maintainer
4. Never bypass security gates regardless of urgency
