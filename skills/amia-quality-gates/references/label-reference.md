# Complete Quality Gate Label Reference

This document lists all labels used in quality gate enforcement.

## Gate Status Labels

| Label | Meaning | Set When |
|-------|---------|----------|
| `gate:pre-review-pending` | Awaiting pre-review checks | PR created |
| `gate:pre-review-passed` | Pre-review checks passed | All pre-review checks green |
| `gate:pre-review-failed` | Pre-review checks failed | Any pre-review check fails |
| `gate:review-passed` | Code review passed | Review confidence >= 80% |
| `gate:review-failed` | Code review failed | Review confidence < 80% or blocking issues |
| `gate:pre-merge-passed` | Pre-merge checks passed | All pre-merge checks green |
| `gate:pre-merge-failed` | Pre-merge checks failed | Any pre-merge check fails |
| `gate:post-merge-passed` | Post-merge verification passed | Main branch healthy after merge |
| `gate:post-merge-failed` | Post-merge verification failed | Main branch issues after merge |
| `gate:override-applied` | Gate was overridden | Manual override applied |

## Warning Labels

| Label | Meaning |
|-------|---------|
| `gate:coverage-warning` | Test coverage below threshold |
| `gate:changelog-needed` | Changelog entry missing |
| `gate:large-pr` | PR has 30+ file changes |
| `gate:style-issues` | Minor style issues found |
| `gate:docs-needed` | Documentation incomplete |
| `gate:perf-review` | Performance concerns noted |
| `gate:flaky-test` | Flaky test detected |
| `gate:slow-ci` | CI duration longer than expected |
| `gate:perf-regression` | Performance regression detected |
| `gate:new-warnings` | New warnings introduced |
