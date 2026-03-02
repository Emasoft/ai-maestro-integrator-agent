# Failure Scenarios and Recovery

Detailed patterns for handling failures during multi-agent orchestration with GitHub Kanban boards.

---

## Table of Contents

- 1. Subtask Reports Failure After Others In Progress
- 2. Integration Reports Failures
- 3. Agent Becomes Unresponsive
- 4. Conflict Resolution Planning
- 5. Failure Communication Patterns

---

## 1. Subtask Reports Failure After Others In Progress

### Scenario

An agent reports task failure while other agents are actively working on dependent or parallel tasks.

### Orchestrator Actions

| Step | Action | GitHub/AI Maestro |
|------|--------|-------------------|
| 1 | Document failure in GitHub issue | Add failure comment to issue |
| 2 | Assess impact on other tasks | Review dependency graph |
| 3 | Determine if other tasks can continue | Check blocking relationships |
| 4 | Update dependencies in affected issues | Edit dependent issue descriptions |
| 5 | Re-plan integration sequence | Update plan.md in docs_dev/ |
| 6 | Send updated instructions to affected agents | AI Maestro messages to all affected |

### Impact Assessment Matrix

| Failure Type | Continue? | Action |
|--------------|-----------|--------|
| **Critical dependency** | NO | Halt dependent tasks, reassign failed task |
| **Parallel independent** | YES | Continue others, fix failed task separately |
| **Integration blocker** | PARTIAL | Continue non-dependent, defer dependent |
| **Test failure only** | YES | Fix tests, other tasks continue |

### Example Workflow

```
Agent A reports failure on module X
       ↓
Review dependencies
       ↓
Module Y depends on X → BLOCK agent B on module Y
Module Z independent → CONTINUE agent C on module Z
       ↓
Create recovery task for module X
       ↓
Assign to available agent or reassign agent A
       ↓
Notify all affected agents of new plan
```

### Recovery Steps

1. **Create recovery issue** for the failed task
2. **Move original issue to Blocked** with failure details
3. **Notify dependent agents** via AI Maestro
4. **Update board columns** for blocked items
5. **Assign recovery task** to available agent
6. **Monitor recovery** and unblock dependents when complete

---

## 2. Integration Reports Failures

### Scenario

Integration executor reports failures during merge or integration testing.

### Orchestrator Actions

| Step | Action | Details |
|------|--------|---------|
| 1 | Review failure details in report | Read integration logs |
| 2 | Identify root cause from logs | Categorize: conflicts, tests, build, runtime |
| 3 | Create resolution assignment | Use conflict resolution template |
| 4 | Send to appropriate agent | Original author or integration specialist |
| 5 | Request re-integration after fix | New integration issue |
| 6 | Update rollback plan if needed | Document in plan.md |

### Failure Categories

| Category | Typical Cause | Resolution Approach |
|----------|--------------|---------------------|
| **Merge conflicts** | Overlapping file changes | Conflict resolution agent |
| **Test failures** | Integration broke existing tests | Original feature author fixes |
| **Build failures** | Dependency issues, syntax errors | Original feature author fixes |
| **Runtime failures** | Logic errors in integration | Integration specialist reviews |
| **Performance regression** | New code slows system | Performance profiling and optimization |

### Integration Failure Workflow

```
Integration reports failure
       ↓
Categorize failure type
       ↓
┌─────────┬──────────┬──────────┬──────────┐
│ Conflicts│ Tests   │ Build    │ Runtime  │
│         │         │         │         │
│ Resolver│ Author  │ Author   │ Specialist│
└─────────┴──────────┴──────────┴──────────┘
       ↓
Assign resolution task
       ↓
Monitor fix
       ↓
Request re-integration
       ↓
Verify success
```

### Re-Integration Checklist

- [ ] Root cause identified and documented
- [ ] Fix implemented and tested locally
- [ ] All original tests still passing
- [ ] New tests added if needed
- [ ] Integration logs reviewed
- [ ] Ready for re-integration attempt

---

## 3. Agent Becomes Unresponsive

### Scenario

Agent stops responding to check-ins, progress requests, or completion deadlines.

### Detection Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| No status update | 4 hours | Send check-in request |
| No response to check-in | 2 hours | Send high-priority ping |
| Still no response | 4 hours | Begin reassignment |
| Total silence | 12 hours | Complete reassignment |

### Orchestrator Actions

| Step | Action | Details |
|------|--------|---------|
| 1 | Document non-response in issue | Comment with timestamp |
| 2 | Reassign task to different agent | Update GitHub issue assignee |
| 3 | Provide full context | Include all previous reports, branches |
| 4 | Update GitHub Project assignments | Move card, update assignee |
| 5 | Send assignment to new agent | AI Maestro message with context |
| 6 | Note: No work lost | Git branches preserve all work |

### Reassignment Message Template

```
=== REASSIGNMENT ===

ORIGINAL ISSUE: GH-[number]
ORIGINAL AGENT: [name] (unresponsive since [timestamp])
NEW AGENT: [name]

TASK: [task name]
OBJECTIVE: [what to deliver]

PREVIOUS WORK:
- Branch: [branch-name]
- Last commit: [hash]
- Last update: [timestamp]
- Status: [last known status]

CURRENT REQUIREMENTS:
[Same as original assignment]

ADDITIONAL CONTEXT:
Original agent became unresponsive. You are picking up from existing branch.
Review previous commits before continuing.

COMPLETION CRITERIA:
[Same as original]
```

### Work Preservation

All work is preserved in git:
- Original branch remains intact
- New agent can review commits
- Can cherry-pick completed work
- Can restart from scratch if needed

---

## 4. Conflict Resolution Planning

### When Integration Reports Conflicts

Integration executor detects merge conflicts during integration.

### Orchestrator Actions (Planning Only)

| Step | Action | Deliverable |
|------|--------|-------------|
| 1 | Review conflict report from integration executor | Understand scope |
| 2 | Identify conflicting files and agents | List conflicts |
| 3 | Determine resolution strategy | Strategy document |
| 4 | Create resolution instructions | Use template |
| 5 | Assign resolution to appropriate agent | AI Maestro message |
| 6 | Monitor resolution progress | Check-in requests |
| 7 | Approve re-integration | Merge authorization |

### Resolution Strategy Considerations

| Factor | Resolution Approach |
|--------|---------------------|
| Feature A is critical | Prioritize Feature A changes |
| Feature B has more coverage | Prioritize Feature B implementation |
| Both features needed | Manual merge preserving both |
| One feature is refinement | Keep original, add refinement |
| Architectural conflict | Escalate to architect or human |

### Resolution Strategy Template

```markdown
## Conflict Resolution Strategy - GH-[number]

### Conflicting Features
- Feature A: [description] - Agent: [name]
- Feature B: [description] - Agent: [name]

### Conflict Files
- [file1.py]: Both modified function X
- [file2.py]: Different approaches to same feature

### Analysis
[Why conflict occurred]

### Resolution Approach
[Which strategy to use and why]

### Expected Outcome
[What final code should look like]

### Verification
- [ ] Both feature requirements met
- [ ] All tests passing
- [ ] No functionality lost
- [ ] Documentation reflects final implementation
```

### Post-Resolution Verification

Before approving re-integration:
- All tests passing
- Both feature sets preserved (or omissions explained)
- Documentation updated for final implementation
- No functionality lost from either branch
- Performance not degraded

---

## 5. Failure Communication Patterns

### AI Maestro Message Types for Failures

| Message Type | Priority | Use Case |
|--------------|----------|----------|
| `failure_report` | high | Agent reports task failure |
| `blocker` | high | Agent blocked, needs help |
| `escalation` | urgent | Critical issue requiring immediate attention |
| `clarification` | normal | Agent needs more information |
| `recovery_assignment` | high | Reassigning failed task |

### Failure Report Format

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "orchestrator-master",
  "subject": "FAILED: GH-42 - Authentication Module",
  "priority": "high",
  "content": {
    "type": "failure_report",
    "message": "[FAILED] GH-42 auth_module\nReason: OAuth library incompatible with Python 3.12\nTests: 15 passing, 8 failures\nBlocker: Library version constraint\nDetails: See GitHub issue #42"
  }
}
```

### Orchestrator Response Pattern

1. **Acknowledge receipt** within 15 minutes
2. **Review failure details** thoroughly
3. **Assess impact** on other work
4. **Create recovery plan**
5. **Communicate plan** to all affected agents
6. **Monitor execution** of recovery

### Escalation Criteria

Escalate to human when:
- Multiple integration failures
- Blocker persists >48 hours
- Architectural decision needed
- Security issue discovered
- Budget/timeline impact significant
- Agent conflict or ambiguity in requirements

### Escalation Message Template

```markdown
@human-owner Escalation Required

**Issue:** GH-[number]
**Severity:** [Critical|High|Medium]
**Impact:** [description]

**Situation:**
[What happened]

**Attempted Resolutions:**
1. [Action 1] - Result: [outcome]
2. [Action 2] - Result: [outcome]

**Recommendation:**
[Suggested next steps]

**Timeline Impact:**
[How this affects delivery]

**Awaiting Decision On:**
[Specific question or approval needed]
```

---

## Examples

### Example 1: Subtask Fails, Halt Dependents

```bash
# Agent reports failure on GH-42 (auth module)
# GH-43 (user profile) depends on GH-42

# Step 1: Document failure in GH-42
gh issue comment 42 --body "Task failed: OAuth library incompatible. Creating recovery task."

# Step 2: Block dependent task GH-43
gh issue edit 43 --add-label "blocked"
gh issue comment 43 --body "Blocked by GH-42 failure. Awaiting recovery."

# Step 3: Notify agent on GH-43 using the agent-messaging skill:
#   Recipient: agent-2
#   Subject: GH-43 Blocked
#   Priority: high
#   Content: {"type": "blocker", "message": "GH-43 is blocked due to GH-42 failure. Pause work until unblocked."}
#   Verify: Confirm delivery via the agent-messaging skill send confirmation.

# Step 4: Create recovery task
gh issue create --title "Recovery: Fix OAuth compatibility in auth module" \
  --body "Original task GH-42 failed. Fix OAuth library version constraint."
```

### Example 2: Integration Fails, Reassign Resolution

```bash
# Integration executor reports merge conflicts

# Step 1: Review conflict details in integration issue
gh issue view 50

# Step 2: Create resolution assignment
gh issue create --title "Resolve merge conflicts for feature X integration" \
  --body "Conflicts in: auth.py, users.py. Strategy: Preserve auth logic from GH-42, merge user fields from GH-44."

# Step 3: Assign to conflict resolver
gh issue edit 51 --add-assignee conflict-resolver-agent

# Step 4: Notify resolver using the agent-messaging skill:
#   Recipient: conflict-resolver-agent
#   Subject: ASSIGNMENT: Resolve conflicts for GH-50
#   Priority: high
#   Content: {"type": "assignment", "message": "Resolve merge conflicts following strategy in GH-51."}
#   Verify: Confirm delivery via the agent-messaging skill send confirmation.
```

---

## Resources

- [instruction-templates.md](instruction-templates.md) - Templates for all assignments
- [blocking-workflow.md](blocking-workflow.md) - Detailed blocker handling
- [agent-assignment-via-board.md](agent-assignment-via-board.md) - Assignment patterns
- [status-transitions.md](status-transitions.md) - Valid board transitions
