# GitHub PR Checks Skill

Monitor and interpret GitHub Pull Request CI/CD check statuses, wait for check completion, and retrieve detailed check information for orchestration decisions.

## When to Use

- Verify all CI/CD checks pass before merging a PR
- Wait for pending checks to complete with intelligent polling
- Investigate why a specific check failed
- Determine if a PR is ready for merge based on required checks

## Quick Reference

| Task | Command |
|------|---------|
| Get all check statuses | `python scripts/amia_get_pr_checks.py --pr 123` |
| Get required checks only | `python scripts/amia_get_pr_checks.py --pr 123 --required-only` |
| Quick merge readiness | `python scripts/amia_get_pr_checks.py --pr 123 --summary-only` |
| Wait for completion | `python scripts/amia_wait_for_checks.py --pr 123 --timeout 600` |
| Investigate failure | `python scripts/amia_get_check_details.py --pr 123 --check "build"` |

## Check Conclusions

| Conclusion | Meaning | Action |
|------------|---------|--------|
| `success` | Check passed | None |
| `failure` | Check failed | Investigate and fix |
| `pending` | Still running | Wait or check if stuck |
| `skipped` | Check skipped | Usually OK |
| `cancelled` | Cancelled | Re-run if needed |
| `timed_out` | Exceeded time limit | Optimize or increase timeout |
| `action_required` | Manual action needed | Review check details |
| `neutral` | Informational only | No action required |
| `stale` | Check is outdated | Push new commit to trigger |

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth login`)
- Read access to target repository
- Python 3.8+

## Full Documentation

See [SKILL.md](SKILL.md) for complete usage details, decision trees, and troubleshooting.
