# Orchestrator PR Workflow

Defines when and how the orchestrator coordinates Pull Request review work, including delegation rules, verification workflows, and completion criteria. The orchestrator is a **coordinator**, not a worker.

## When to Use This Skill

- Coordinating PR review across multiple subagents
- Determining when to delegate vs escalate PR work
- Verifying PR completion criteria before merge
- Handling human vs AI contributor PRs differently
- Setting up polling schedules for PR monitoring

## Core Principle

The orchestrator **NEVER** does direct work on PRs. It orchestrates, delegates, monitors, and reports.

## Quick Reference

| Decision | Action |
|----------|--------|
| Human PR | Escalate to user for guidance |
| AI/Bot PR | Direct delegation allowed |
| Code review needed | Delegate to review subagent |
| Code changes needed | Delegate to implementation subagent |
| CI verification | Delegate to CI monitor subagent |
| Status check | Use polling script directly |
| Long operation | NEVER block - use background tasks |

## Critical Rules

1. **Never Block** - All long-running tasks must be delegated or backgrounded
2. **Never Write Code** - Code writing is ALWAYS delegated to subagents
3. **Never Merge Without User** - Always require explicit user approval
4. **Always Verify Before Reporting** - Run verification scripts before status reports
5. **Human PRs Require Escalation** - Different handling for human contributors

## Scripts

- `scripts/amia_orchestrator_pr_poll.py` - Survey all open PRs and prioritize actions
  ```bash
  python scripts/amia_orchestrator_pr_poll.py --repo owner/repo
  ```
- `scripts/amia_verify_pr_completion.py` - Verify all completion criteria for a PR
  ```bash
  python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123
  ```

## References

See `references/` for detailed documentation:
- [orchestrator-responsibilities.md](references/orchestrator-responsibilities.md) - What orchestrator MUST and MUST NOT do
- [delegation-rules.md](references/delegation-rules.md) - When/how to spawn subagents
- [verification-workflow.md](references/verification-workflow.md) - Pre/post review checklists, 4-verification-loop
- [worktree-coordination.md](references/worktree-coordination.md) - Parallel work isolation
- [human-vs-ai-assignment.md](references/human-vs-ai-assignment.md) - Author type identification and handling
- [completion-criteria.md](references/completion-criteria.md) - 8 criteria for merge readiness
- [polling-schedule.md](references/polling-schedule.md) - Adaptive polling and notification triggers
