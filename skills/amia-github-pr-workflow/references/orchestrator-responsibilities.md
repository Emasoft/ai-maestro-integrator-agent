# Orchestrator Responsibilities

## Table of Contents

- 1.1 What the orchestrator MUST do
  - 1.1.1 Monitor PR status periodically
  - 1.1.2 Delegate review work to subagents
  - 1.1.3 Track completion status
  - 1.1.4 Report to user
- 1.2 What the orchestrator MUST NOT do
  - 1.2.1 Write code directly
  - 1.2.2 Block on long operations
  - 1.2.3 Make unilateral merge decisions

---

## 1.1 What the orchestrator MUST do

The orchestrator is the coordination layer between the user, GitHub, and specialized subagents. Its responsibilities are strictly bounded to orchestration activities.

### 1.1.1 Monitor PR status periodically

**Definition**: Periodically check the state of all relevant PRs to identify what actions are needed.

**Implementation**:
1. Run the `amia_orchestrator_pr_poll.py` script every 10-15 minutes
2. Parse the output to identify PRs needing attention
3. Prioritize based on urgency and user preferences
4. Queue actions for delegation

**Example polling command**:
```bash
python scripts/amia_orchestrator_pr_poll.py --repo owner/repo
```

**What to monitor**:
- PR open/closed/merged state
- Review request status
- CI check results
- Comment activity
- Merge eligibility
- Thread resolution state

**How to interpret results**:
| Status | Meaning | Action |
|--------|---------|--------|
| `needs_review` | PR awaiting review | Delegate review to subagent |
| `needs_changes` | Review requested changes | Delegate implementation work |
| `ready` | All criteria met | Verify completion, report to user |
| `blocked` | Cannot proceed | Identify blocker, escalate |

### 1.1.2 Delegate review work to subagents

**Definition**: Spawn specialized subagents to perform actual work, never do the work yourself.

**Delegation types**:

1. **Review delegation**: Spawn a code review subagent to analyze code quality, logic, and adherence to standards
2. **Implementation delegation**: Spawn an implementation subagent to make code changes
3. **CI monitoring delegation**: Spawn a CI monitor subagent to watch for build completion
4. **Verification delegation**: Spawn a verification subagent to run completion checks

**Prompt structure for subagents**:
```
You are a [role] subagent. Your single task is:
[Clear, specific task description]

Context:
- Repository: [repo]
- PR: [number]
- Branch: [branch]

Success criteria:
[Explicit, verifiable conditions]

Return format:
[DONE/FAILED] task_name - brief_result
If details needed, write to docs_dev/[filename].md
```

**Critical rule**: Each subagent gets ONE task only. Complex work is broken into multiple subagent tasks.

### 1.1.3 Track completion status

**Definition**: Maintain awareness of what work has been delegated and what remains.

**Tracking mechanisms**:

1. **Checklist in markdown file**: For complex PRs, maintain a checklist in `docs_dev/pr-[number]-status.md`
2. **GitHub issue checklist**: If PR corresponds to an issue, use the issue's checklist
3. **Mental model**: For simple PRs, track in conversation context

**Status file format**:
```markdown
# PR #123 Status

## Review Phase
- [x] Initial review delegated
- [x] Review completed
- [ ] Review comments addressed

## Implementation Phase
- [ ] Changes delegated
- [ ] Changes implemented
- [ ] Tests passing

## Completion Phase
- [ ] All criteria verified
- [ ] User notified
- [ ] Merge decision pending
```

**Update frequency**: Update status immediately after each subagent returns.

### 1.1.4 Report to user

**Definition**: Provide clear, actionable status updates to the user at key milestones.

**When to report**:
- PR becomes ready for review
- All review comments have been addressed
- CI checks complete (pass or fail)
- PR is merge-ready
- Any blocking issue is identified
- Subagent encounters an error

**Report format**:
```
## PR #[number] Status Update

**State**: [ready|blocked|in_progress|complete]

**Summary**: [1-2 sentence overview]

**Action needed**: [what user should do, if anything]

**Details**: [link to status file if complex]
```

**Critical rule**: Reports should be concise. Details go in files, summaries go to user.

---

## 1.2 What the orchestrator MUST NOT do

These are hard boundaries. Violating them defeats the purpose of orchestration.

### 1.2.1 Write code directly

**The rule**: The orchestrator NEVER writes, modifies, or deletes code in the repository.

**Why**:
- The orchestrator's context is for coordination, not implementation
- Writing code blocks the orchestrator from handling other tasks
- Code changes require focused attention that a coordinator cannot provide

**What to do instead**:
1. Identify what code needs to change
2. Formulate clear requirements
3. Delegate to implementation subagent
4. Verify result when subagent returns

**Exception**: The orchestrator MAY edit orchestration-related files:
- Status tracking files in `docs_dev/`
- Checklist updates in issues
- Script outputs and logs

### 1.2.2 Block on long operations

**The rule**: The orchestrator NEVER waits synchronously for operations that take more than a few seconds.

**Why**:
- Blocking prevents the orchestrator from handling urgent user requests
- Blocking consumes context tokens on waiting
- Blocking creates a bottleneck in the workflow

**Long operations (NEVER block on these)**:
- CI pipeline runs (minutes to hours)
- Code review by subagent (minutes)
- Implementation work (minutes to hours)
- API responses with high latency
- Network transfers

**What to do instead**:
1. Delegate the operation to a subagent
2. Set up polling to check completion
3. Continue with other orchestration tasks
4. Process result when ready

**Example - WRONG**:
```
# Orchestrator waits for CI
while not ci_complete:
    sleep(30)
    check_ci()
```

**Example - CORRECT**:
```
# Orchestrator delegates and moves on
delegate_ci_monitoring_to_subagent()
continue_with_other_tasks()
# Subagent will report when complete
```

### 1.2.3 Make unilateral merge decisions

**The rule**: The orchestrator NEVER merges a PR without explicit user approval.

**Why**:
- Merging is an irreversible action
- The user is accountable for repository state
- There may be context the orchestrator lacks

**The correct workflow**:
1. Verify all completion criteria are met
2. Report to user: "PR #X is ready to merge"
3. Wait for user's explicit instruction: "merge it" or similar
4. ONLY THEN delegate the merge operation

**What "ready to merge" means**:
- All review comments addressed
- All PR comments acknowledged
- No new comments in 45 seconds
- CI checks passing
- No unresolved threads
- GitHub shows merge eligible
- PR not already merged

**Even then**: Report and wait. Do not merge.

---

## Summary Matrix

| Activity | Orchestrator Does? | Who Does It |
|----------|-------------------|-------------|
| Monitor PR status | YES | Orchestrator via script |
| Identify needed work | YES | Orchestrator analysis |
| Write code | NO | Implementation subagent |
| Review code | NO | Review subagent |
| Wait for CI | NO | CI monitor subagent |
| Verify completion | YES | Orchestrator via script |
| Report to user | YES | Orchestrator directly |
| Decide to merge | NO | User decides |
| Execute merge | NO | Only after user approval |
