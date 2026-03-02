# Status Management - Part 1: Transitions

## Table of Contents

1. [When you need to know valid status transitions](#transition-rules)
   - 1.1 [Valid Transitions Matrix](#valid-transitions-matrix)
   - 1.2 [Backlog to Todo transition](#backlog--todo)
   - 1.3 [Todo to In Progress transition](#todo--in-progress)
   - 1.4 [In Progress to AI Review transition](#in-progress--ai-review)
   - 1.4a [AI Review to Human Review transition](#ai-review--human-review)
   - 1.4b [AI Review to Merge/Release transition](#ai-review--merge-release)
   - 1.5 [Merge/Release to Done transition](#merge-release--done)
   - 1.6 [AI Review to In Progress (changes requested)](#ai-review--in-progress-changes-requested)
   - 1.7 [Moving any status to Blocked](#any--blocked)
   - 1.8 [Unblocking items](#blocked--todoin-progress)
   - 1.9 [Cancelling items](#any--cancelled)
2. [When syncing GitHub state with project board](#synchronization-protocol)
   - 2.1 [Real-time event triggers](#real-time-triggers)
   - 2.2 [Periodic sync process](#periodic-sync-every-30-minutes)
   - 2.3 [Resolving state conflicts](#conflict-resolution)

**Parent document**: [Status Management](./status-management.md)

---

## Transition Rules

### Valid Transitions Matrix

```
FROM ↓ / TO →     | backlog | todo | in-progress | ai-review | human-review | merge-release | blocked | done | cancelled |
------------------|---------|------|-------------|-----------|--------------|---------------|---------|------|-----------|
backlog           |    -    |  ✓   |      ✗      |     ✗     |      ✗       |       ✗       |    ✗    |  ✗   |     ✓     |
todo              |    ✓    |  -   |      ✓      |     ✗     |      ✗       |       ✗       |    ✓    |  ✗   |     ✓     |
in-progress       |    ✗    |  ✓   |      -      |     ✓     |      ✗       |       ✗       |    ✓    |  ✗   |     ✓     |
ai-review         |    ✗    |  ✗   |      ✓      |     -     |      ✓       |       ✓       |    ✓    |  ✗   |     ✓     |
human-review      |    ✗    |  ✗   |      ✓      |     ✗     |      -       |       ✓       |    ✓    |  ✗   |     ✓     |
merge-release     |    ✗    |  ✗   |      ✗      |     ✗     |      ✗       |       -       |    ✓    |  ✓   |     ✓     |
blocked           |    ✗    |  ✓   |      ✓      |     ✗     |      ✗       |       ✗       |    -    |  ✗   |     ✓     |
done              |    ✗    |  ✗   |      ✗      |     ✗     |      ✗       |       ✗       |    ✗    |  -   |     ✗     |
cancelled         |    ✓    |  ✗   |      ✗      |     ✗     |      ✗       |       ✗       |    ✗    |  ✗   |     -     |
```

### Transition Conditions

#### Backlog → Todo

**Preconditions**:
- Issue has clear acceptance criteria
- Sprint/iteration assigned
- Estimated (optional but recommended)

**Actions**:
- Assign to agent/developer
- Add to sprint iteration
- Notify assignee

#### Todo → In Progress

**Preconditions**:
- Agent assigned
- Sprint iteration set
- No blocking dependencies

**Actions**:
- Create feature branch
- Add "in-progress" label
- Record start timestamp
- Send notification to orchestrator

#### In Progress → AI Review

**Preconditions**:
- Feature branch has commits
- PR created against target branch
- All local tests pass

**Actions**:
- Link PR to issue
- Add "ai-review" label
- Remove "in-progress" label
- Notify Integrator agent

#### AI Review → Human Review

**Preconditions**:
- Integrator has reviewed and approved
- Task is flagged as BIG (requires human review)

**Actions**:
- Remove "ai-review" label
- Add "human-review" label
- Notify user/human reviewer

#### AI Review → Merge/Release

**Preconditions**:
- Integrator has reviewed and approved
- Task is small (no human review needed)

**Actions**:
- Remove "ai-review" label
- Add "merge-release" label
- PR ready for merge

#### Human Review → Merge/Release

**Preconditions**:
- Human reviewer has approved

**Actions**:
- Remove "human-review" label
- Add "merge-release" label
- PR ready for merge

#### Merge/Release → Done

**Preconditions**:
- PR approved by required reviewers (see [100% Approval Rule](./iteration-cycle-rules.md#100-approval-rule))
- CI/CD pipeline passes
- No merge conflicts
- PR merged to target branch
- All review worktree checks completed (see [Review Worktree Workflow](./review-worktree-workflow.md))
- Plan file properly linked to issue (see [Plan File Linking](./plan-file-linking.md#linking-plans-to-issues))

**Actions**:
- Close linked issue
- Add "completed" label
- Archive project item (optional)
- Update parent issue progress

#### AI Review → In Progress (Changes Requested)

**Preconditions**:
- Integrator review requests changes
- Reviewer comments addressed

**Actions**:
- Remove "ai-review" label
- Add "in-progress" label
- Notify assignee of required changes

#### Any → Blocked

**Preconditions**:
- Blocker identified and documented
- Blocker cannot be resolved by assignee

**Actions**:
- Add "blocked" label
- Record blocker reason in comment
- Link to blocking issue if applicable
- Escalate if critical

#### Blocked → Todo/In Progress

**Preconditions**:
- Blocker resolved
- Ready to resume work

**Actions**:
- Remove "blocked" label
- Add appropriate status label
- Comment with resolution

#### Any → Cancelled

**Preconditions**:
- User approval required
- Reason documented

**Actions**:
- Close issue as "not planned"
- Add "cancelled" label
- Archive project item
- Update dependent items

---

## Synchronization Protocol

### Real-Time Triggers

| Event | Source | Status Update |
|-------|--------|---------------|
| Issue assigned | GitHub | Check if Todo |
| Branch created | GitHub | → In Progress |
| PR opened | GitHub | → AI Review |
| PR merged | GitHub | → Done |
| PR closed without merge | GitHub | → In Progress |
| Label "blocked" added | GitHub | → Blocked |
| Label "blocked" removed | GitHub | → Previous status |

### Periodic Sync (Every 30 minutes)

```
FOR each project item:
  1. GET current GitHub issue state
  2. GET current project status
  3. IF state mismatch:
     - DETERMINE correct status based on:
       - Issue open/closed
       - PR exists/merged
       - Labels present
       - Agent activity
     - UPDATE project status
     - LOG sync action
```

### Conflict Resolution

When GitHub state and project status conflict:

| Conflict | Resolution |
|----------|------------|
| Issue closed, status not Done | Set to Done |
| PR merged, status AI Review | Set to Done |
| No activity 24h, status In Progress | Query agent, consider Blocked |
| Agent reports complete, status not AI Review | Verify PR, update accordingly |

---

## Related References

- **[Status Management](./status-management.md)** - Parent document with status definitions
- **[Part 2: Operations](./status-management-part2-operations.md)** - API, reporting, alerts, lifecycle
- **[Iteration Cycle Rules](./iteration-cycle-rules.md)** - Complete iteration workflow
- **[Review Worktree Workflow](./review-worktree-workflow.md)** - PR review validation
