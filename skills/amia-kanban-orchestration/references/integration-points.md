# Integration Points

## Contents

- [IP.1 Planning Phase workflow](#ip1-planning-phase)
- [IP.2 Orchestration Phase workflow](#ip2-orchestration-phase)
- [IP.3 Stop Hook Phase workflow](#ip3-stop-hook-phase)
- [IP.4 Assignment Flow](#ip4-assignment-flow)
- [IP.5 PR Completion Flow](#ip5-pr-completion-flow)

---

## IP.1 Planning Phase

1. Orchestrator breaks work into modules
2. Each module becomes a GitHub Issue
3. Issues are added to project board in Backlog
4. Orchestrator moves ready issues to Todo
5. Board reflects complete work breakdown

## IP.2 Orchestration Phase

1. Orchestrator assigns Todo issues to agents
2. Agent moves issue to In Progress when starting
3. Agent creates PR, moves to AI Review
4. Integrator reviews, moves to Human Review (big tasks) or Merge/Release (small tasks)
5. PR merge auto-moves to Done
6. Board reflects real-time progress

## IP.3 Stop Hook Phase

1. Stop hook queries board state
2. Checks: all assigned items Done or explicitly deferred
3. If incomplete items exist, prevents exit
4. Orchestrator must resolve or defer before exit

## IP.4 Assignment Flow

1. Orchestrator identifies next Todo item
2. Orchestrator assigns to available agent
3. Assignment appears as GitHub issue assignee
4. Agent receives notification via AI Maestro
5. Assignment visible on board

## IP.5 PR Completion Flow

1. Agent creates PR linked to issue (Closes #N)
2. Agent moves issue to AI Review
3. Integrator reviews (all tasks go through AI Review)
4. Integrator moves to Human Review (big tasks) or Merge/Release (small tasks)
5. PR merged triggers auto-move to Done
6. Issue closes automatically
