# Status Transitions

## Table of Contents

- 5.1 [Valid transition matrix](#51-transition-matrix)
- 5.2 [Transition preconditions and postconditions](#52-preconditions-and-postconditions)
- 5.3 [Who can move cards](#53-who-can-move)
- 5.4 [Backlog to Todo transition rules](#54-backlog-to-todo)
- 5.5 [Todo to In Progress transition rules](#55-todo-to-in-progress)
- 5.6 [In Progress to AI Review transition rules](#56-in-progress-to-ai-review)
- 5.6a [AI Review to Human Review transition rules (big tasks)](#56a-ai-review-to-human-review)
- 5.6b [AI Review to Merge/Release transition rules (small tasks)](#56b-ai-review-to-merge-release)
- 5.6c [Human Review to Merge/Release transition rules](#56c-human-review-to-merge-release)
- 5.7 [Merge/Release to Done transition rules](#57-merge-release-to-done)
- 5.8 [Any status to Blocked transition rules](#58-any-to-blocked)
- 5.9 [Blocked to previous status transition rules](#59-blocked-to-previous)
- 5.10 [Invalid transitions and handling](#510-invalid-transitions)

---

## 5.1 Transition Matrix

```
FROM ↓ / TO →    │ Backlog │ Todo │ In Progress │ AI Review │ Human Review │ Merge/Release │ Done │ Blocked │
─────────────────┼─────────┼──────┼─────────────┼───────────┼──────────────┼───────────────┼──────┼─────────┤
Backlog          │    -    │  ✓   │      ✗      │     ✗     │      ✗       │       ✗       │  ✗   │    ✗    │
Todo             │    ✓    │  -   │      ✓      │     ✗     │      ✗       │       ✗       │  ✗   │    ✓    │
In Progress      │    ✗    │  ✓   │      -      │     ✓     │      ✗       │       ✗       │  ✗   │    ✓    │
AI Review        │    ✗    │  ✗   │      ✓      │     -     │      ✓       │       ✓       │  ✗   │    ✓    │
Human Review     │    ✗    │  ✗   │      ✓      │     ✗     │      -       │       ✓       │  ✗   │    ✓    │
Merge/Release    │    ✗    │  ✗   │      ✗      │     ✗     │      ✗       │       -       │  ✓   │    ✓    │
Done             │    ✗    │  ✗   │      ✗      │     ✗     │      ✗       │       ✗       │  -   │    ✗    │
Blocked          │    ✗    │  ✓   │      ✓      │     ✗     │      ✗       │       ✗       │  ✗   │    -    │
```

**Legend:**

- ✓ = Valid transition
- ✗ = Invalid transition
- `-` = Same status (no transition)

**Task Routing Rules:**

- **Small tasks**: In Progress → AI Review → Merge/Release → Done (skip Human Review)
- **Big tasks**: In Progress → AI Review → Human Review → Merge/Release → Done
- The Integrator agent (AMIA) reviews ALL tasks in AI Review
- Only BIG tasks go to Human Review (user reviews via AMAMA Assistant Manager)
- Any status can move to Blocked (and back)

---

## 5.2 Preconditions and Postconditions

### Preconditions

Conditions that MUST be true BEFORE a transition can occur:

| Transition | Preconditions |
|------------|---------------|
| Backlog → Todo | Acceptance criteria defined, dependencies identified |
| Todo → In Progress | Assignee set, no blocking dependencies |
| In Progress → AI Review | PR created, tests passing, PR linked to issue |
| AI Review → Human Review | Integrator approved, task flagged as BIG |
| AI Review → Merge/Release | Integrator approved, task is SMALL (no human review needed) |
| Human Review → Merge/Release | Human approved the changes |
| Merge/Release → Done | PR merged, CI passed |
| Any → Blocked | Blocker documented with reason |
| Blocked → Previous | Blocker resolved, documented in comment |

### Postconditions

Actions that MUST happen AFTER a transition:

| Transition | Postconditions |
|------------|----------------|
| Backlog → Todo | Notify assignee if set |
| Todo → In Progress | Feature branch created, start time recorded |
| In Progress → AI Review | Integrator notified for review |
| AI Review → Human Review | User notified via AMAMA (Assistant Manager requests review) |
| AI Review → Merge/Release | PR ready to merge, CI must pass |
| Human Review → Merge/Release | Human approval recorded, PR ready to merge |
| Merge/Release → Done | Issue closed, parent progress updated |
| Any → Blocked | Escalation timer started |
| Blocked → Previous | Blocker resolution documented |

---

## 5.3 Who Can Move

### Permission Matrix

| Transition | Orchestrator | Integrator | Assigned Agent | Any Agent | Human/User | Automatic |
|------------|--------------|------------|----------------|-----------|------------|-----------|
| Backlog → Todo | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Todo → Backlog | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Todo → In Progress | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |
| In Progress → Todo | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |
| In Progress → AI Review | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| AI Review → In Progress | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| AI Review → Human Review | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| AI Review → Merge/Release | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Human Review → In Progress | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Human Review → Merge/Release | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Merge/Release → Done | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ (PR merge) |
| Any → Blocked | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Blocked → Previous | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |

### Key Rules

> **Note:** The Integrator's kanban movement permissions described below are delegated by COS/MANAGER as part of the INTEGRATOR's assigned role.

1. **Only orchestrator moves from Backlog** - Prioritization control
2. **Assigned agent moves In Progress → AI Review** - Author submits for review
3. **Integrator moves from AI Review** - Integrator decides routing (Human Review for big, Merge/Release for small), as delegated by COS/MANAGER
4. **Only Human/User moves from Human Review** - User has final say on big tasks
5. **Anyone can block** - Safety first
6. **Done is automatic** - PR merge triggers

---

## 5.4 Backlog to Todo

### When to Transition

Move from Backlog to Todo when:

- Item is prioritized for current or next sprint
- All prerequisites are satisfied
- Capacity exists to work on it

### Preconditions Checklist

- [ ] Clear title and description
- [ ] Acceptance criteria defined
- [ ] Dependencies identified (and not blocking)
- [ ] Effort estimated (recommended)
- [ ] Assignee identified (recommended)

### CLI Command

```bash
# Get project and field IDs first, then:
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $optionId }
    }) {
      projectV2Item { id }
    }
  }
' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$STATUS_FIELD_ID" -f optionId="$TODO_OPTION_ID"
```

### Comment Template

```markdown
Moved to **Todo** for Sprint 3.
Priority: High
Assigned to: @agent-1
```

---

## 5.5 Todo to In Progress

### When to Transition

Move from Todo to In Progress when:

- Agent starts working on the issue
- Feature branch is created (or about to be)

### Preconditions Checklist

- [ ] Assignee is set
- [ ] Agent is ready to start
- [ ] No blocking dependencies
- [ ] Sprint/iteration allows starting

### Postconditions

After moving to In Progress:

1. Create feature branch: `git checkout -b feature/issue-42-auth-core`
2. Record start timestamp in comment
3. Notify orchestrator (optional)

### Comment Template

```markdown
Started work.
Branch: `feature/issue-42-auth-core`
Started: 2024-01-15 14:30 UTC
```

---

## 5.6 In Progress to AI Review

### When to Transition

Move from In Progress to AI Review when:

- Implementation is complete (from author's perspective)
- PR is created and linked to issue
- All local tests pass

### Preconditions Checklist

- [ ] Code complete for acceptance criteria
- [ ] PR created with "Closes #N" in body
- [ ] Tests written and passing locally
- [ ] PR description explains changes
- [ ] No obvious issues remaining

### PR Body Template

```markdown
## Summary

[Brief description of changes]

Closes #42

## Changes

- [Change 1]
- [Change 2]

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing done

## Checklist

- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings
```

### Comment on Issue

```markdown
Ready for AI review.
PR: #123
All tests passing locally.
Integrator will review and route to Human Review (big tasks) or Merge/Release (small tasks).
```

---

## 5.6a AI Review to Human Review

### When to Transition

Move from AI Review to Human Review when:

- Integrator agent (AMIA) has reviewed and approved the code changes
- The task is flagged as BIG (requires human review)

This transition applies ONLY to big tasks. Small tasks skip Human Review and go directly to Merge/Release (see section 5.6b).

### Preconditions Checklist

- [ ] Integrator review is complete
- [ ] Task has `size:big` label or equivalent size indicator
- [ ] All AI review comments are resolved
- [ ] No blocking issues found by Integrator

### Who Can Move

The **Integrator agent (AMIA)** moves cards from AI Review to Human Review. These permissions are delegated by the COS/MANAGER as part of the INTEGRATOR's assigned role.

### Postconditions

After moving to Human Review:

1. AMAMA (Assistant Manager) notifies the user that a big task needs human review
2. PR link and summary are included in the notification
3. Review request is recorded on the PR

### Comment Template

```markdown
AI Review complete. Routing to Human Review (big task).
Integrator review: Approved.
@user please review PR #123.
```

---

## 5.6b AI Review to Merge/Release

### When to Transition

Move from AI Review to Merge/Release when:

- Integrator agent (AMIA) has reviewed and approved the code changes
- The task is SMALL (does not require human review)

This is the fast path for small tasks that do not need human approval.

### Preconditions Checklist

- [ ] Integrator review is complete
- [ ] Task has `size:small` label or no size label (defaults to small)
- [ ] All CI checks pass
- [ ] No blocking issues found by Integrator

### Who Can Move

The **Integrator agent (AMIA)** moves cards from AI Review to Merge/Release. These permissions are delegated by the COS/MANAGER as part of the INTEGRATOR's assigned role.

### Postconditions

After moving to Merge/Release:

1. PR is marked as ready to merge
2. CI pipeline must pass before merge can proceed

### Comment Template

```markdown
AI Review complete. Small task approved. Ready to merge.
Integrator review: Approved.
PR #123 is ready for merge.
```

---

## 5.6c Human Review to Merge/Release

### When to Transition

Move from Human Review to Merge/Release when:

- Human user has reviewed and approved the big task
- User gives explicit approval on the PR or issue

### Preconditions Checklist

- [ ] Human has reviewed the PR
- [ ] Human has given explicit approval (PR approval or comment)
- [ ] No outstanding human review comments

### Who Can Move

Only the **Human/User** can move cards from Human Review to Merge/Release. The Orchestrator may also perform this transition after receiving explicit human approval.

### Postconditions

After moving to Merge/Release:

1. Human approval is recorded on the PR
2. PR is marked as ready to merge
3. CI pipeline must pass before merge can proceed

### Comment Template

```markdown
Human review complete. Approved for merge.
Reviewed by: @user
PR #123 is ready for merge.
```

---

## 5.7 Merge/Release to Done

### When to Transition

Move from Merge/Release to Done when:

- PR is merged (not just approved)
- This transition should be AUTOMATIC via GitHub

### Automatic Trigger

When PR body contains "Closes #N" and PR is merged:

1. GitHub closes issue #N automatically
2. Board should reflect Done status

### Manual Transition (Exceptional)

If automatic transition fails:

```bash
# Check PR is actually merged
gh pr view 123 --json merged

# If merged but issue not closed, close manually
gh issue close 42

# Update board status
# [GraphQL mutation to set status to Done]
```

### Verification

Before marking Done, verify:

- [ ] PR is actually merged (not just closed)
- [ ] CI checks passed
- [ ] No follow-up issues created

---

## 5.8 Any to Blocked

### When to Transition

Move to Blocked when:

- External dependency is preventing progress
- Agent cannot proceed without intervention
- Resource or access is unavailable

### What Constitutes a Blocker

| Blocker Type | Example |
|--------------|---------|
| Technical | Dependency not available |
| Access | Missing permissions |
| Clarification | Requirements unclear |
| External | Third-party API down |
| Resource | Server not provisioned |

### Required Information

When moving to Blocked, MUST provide:

```markdown
## Blocked

**Blocker:** [description]
**Type:** Technical / Access / Clarification / External / Resource
**Blocking Issue:** #XX (if applicable)
**What's Needed:** [specific action to unblock]
**Impact:** [what can't proceed]
**Discovered:** YYYY-MM-DD HH:MM UTC
```

### CLI Commands

```bash
# Update status to Blocked
# [GraphQL mutation]

# Add blocked label
gh issue edit 42 --add-label "blocked"

# Comment with blocker details
gh issue comment 42 --body "## Blocked
**Blocker:** Missing database credentials
**Type:** Access
**What's Needed:** DBA to provide staging DB credentials
**Discovered:** 2024-01-15 15:00 UTC"
```

---

## 5.9 Blocked to Previous

### When to Transition

Move from Blocked back to previous status when:

- Blocker is resolved
- Agent can continue work
- Resolution is verified

### Determining Previous Status

Track the status before blocking in the blocker comment:

```markdown
## Blocked

**Previous Status:** In Progress
[... blocker details ...]
```

### Resolution Process

1. Verify blocker is actually resolved
2. Document resolution in comment
3. Remove "blocked" label
4. Update status to previous (usually In Progress)
5. Notify agent to resume

### Resolution Comment Template

```markdown
## Unblocked

**Resolution:** Database credentials received from DBA
**Resolved:** 2024-01-15 18:00 UTC
**Next Action:** Resume implementation

Returning to **In Progress**.
```

---

## 5.10 Invalid Transitions

### Invalid Transition Attempts

| Attempted | Why Invalid | What to Do |
|-----------|-------------|------------|
| Backlog → In Progress | Skips Todo | Move to Todo first |
| Todo → AI Review | Skips In Progress | Move to In Progress first, create PR |
| In Progress → Human Review | Skips AI Review | Must go through AI Review first |
| In Progress → Merge/Release | Skips review | Must go through AI Review (and optionally Human Review) |
| In Progress → Done | Skips review and merge | Must go through full review pipeline |
| AI Review → Done | Skips Merge/Release | Must go through Merge/Release |
| Human Review → Done | Skips Merge/Release | Must go through Merge/Release |
| Done → Any | Done is terminal | Create new issue if more work needed |

### Handling Invalid Requests

If an agent requests an invalid transition:

1. **Reject the request**
2. **Explain why it's invalid**
3. **Suggest correct path**

Example response:

```
Cannot move directly from Todo to AI Review.
The correct path is:
1. Todo → In Progress (start work, create branch)
2. In Progress → AI Review (create PR, submit for review)

Please move to In Progress first.
```

### Script: Validate Transition

```python
VALID_TRANSITIONS = {
    "Backlog": ["Todo"],
    "Todo": ["Backlog", "In Progress", "Blocked"],
    "In Progress": ["Todo", "AI Review", "Blocked"],
    "AI Review": ["In Progress", "Human Review", "Merge/Release", "Blocked"],
    "Human Review": ["In Progress", "Merge/Release", "Blocked"],
    "Merge/Release": ["Done", "Blocked"],
    "Done": [],  # Terminal
    "Blocked": ["Todo", "In Progress"],
}

def is_valid_transition(from_status, to_status):
    return to_status in VALID_TRANSITIONS.get(from_status, [])
```
