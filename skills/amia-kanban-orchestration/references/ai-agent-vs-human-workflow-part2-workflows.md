# AI Agent vs Human Workflow - Part 2: Workflows and Coordination

<a name="part-2-toc"></a>

## Table of Contents

- 9.5 [Review workflow differences and routing](#95-review-workflow)
- 9.5a [Review routing by task size](#95a-review-routing)
- 9.6 [Handoff protocols](#96-handoff)
- 9.7 [Mixed team coordination](#97-mixed-team)
- 9.8 [Escalation paths for AI blockers](#98-escalation)

---

## 9.5 Review Workflow

The review workflow uses three columns: AI Review, Human Review, and Merge/Release.

### AI Agent as Author (Submitting for Review)

When AI agent creates PR:

1. AI creates PR with detailed description and "Closes #N"
2. AI moves issue from In Progress to AI Review
3. Integrator agent (AMIA) reviews the PR
4. Integrator decides routing based on task size:
   - **Small task**: Integrator moves to Merge/Release
   - **Big task**: Integrator moves to Human Review

### Integrator Agent as Reviewer (AI Review Column)

The Integrator (AMIA) reviews ALL tasks in the AI Review column:

```bash
# Integrator reviews PR
gh pr review 123 --comment --body "$(cat <<'EOF'
## Integrator Review

**Code Quality:** Good
**Test Coverage:** Adequate
**Standards Compliance:** Pass

**Decision:** Approved
**Routing:** Merge/Release (small task, no human review needed)
EOF
)"

# Move to Merge/Release (small task)
# [GraphQL mutation to update status]
```

For big tasks requiring human review:

```bash
# Integrator routes to Human Review
gh pr review 123 --comment --body "$(cat <<'EOF'
## Integrator Review

**Code Quality:** Good
**Test Coverage:** Adequate
**Standards Compliance:** Pass

**Decision:** Approved (AI Review complete)
**Routing:** Human Review (big task, requires user approval)

@user This is a big task requiring your review. Please review the PR.
EOF
)"

# Move to Human Review (big task)
# [GraphQL mutation to update status]
```

### Human as Reviewer (Human Review Column)

Human reviewers in the Human Review column can:

- Approve PRs → task moves to Merge/Release
- Request changes → task moves back to In Progress
- Final authority on code quality for big tasks

### Review Routing Summary

```
Small tasks:  In Progress → AI Review → Merge/Release → Done
Big tasks:    In Progress → AI Review → Human Review → Merge/Release → Done

AI Review:     Integrator reviews ALL tasks, decides routing
Human Review:  User reviews BIG tasks only (notified via AMAMA)
Merge/Release: PR is merged (automatic → Done)
```

---

<a name="95a-review-routing"></a>

## 9.5a Review Routing by Task Size

### How Task Size Affects the Flow

| Task Size | AI Review | Human Review | Merge/Release | Who Decides |
|-----------|-----------|--------------|---------------|-------------|
| Small (`size:small` or no label) | Integrator reviews | SKIPPED | PR merged | Integrator |
| Big (`size:big`) | Integrator reviews | User reviews | PR merged | Integrator routes, User approves |

### Integrator Routing Decision

After completing AI Review, the Integrator checks:

1. Does the issue have a `size:big` label?
2. Is this a new feature, architecture change, or breaking change?
3. Does the PR modify critical paths or public APIs?

If YES to any → route to Human Review.
If NO to all → route to Merge/Release.

### Changes Requested Flow

If changes are requested at any review stage:

```
AI Review (changes requested)    → Back to In Progress (author fixes)
Human Review (changes requested) → Back to In Progress (author fixes)
```

After fixes, the task returns to AI Review (not directly to where it was rejected), so the Integrator can verify the fixes before routing again.

---

## 9.6 Handoff

### AI to AI Handoff

When one AI agent hands off to another:

```bash
# 1. Current agent documents state
gh issue comment 42 --body "$(cat <<'EOF'
## Handoff to Next Agent

**Previous Agent:** @implementer-1
**Work Done:**
- Feature branch created: feature/issue-42-auth
- Core logic implemented (src/auth/jwt.py)
- 3 commits pushed

**Work Remaining:**
- Write unit tests
- Add integration test
- Update documentation

**Notes:**
- Using PyJWT library for token handling
- See commit abc123 for token validation logic
- Test file started at tests/test_jwt.py (incomplete)

**Branch is clean and pushed.**
EOF
)"

# 2. Remove current assignee
gh issue edit 42 --remove-assignee implementer-1

# 3. Assign new agent
gh issue edit 42 --add-assignee implementer-2

# 4. Notify COS to forward assignment to new agent using the agent-messaging skill
# Send a message with Recipient: amcos-main, Subject: Assignment handoff for implementer-2, Priority: high
# (COS will forward to the new assignee)
```

### AI to Human Handoff

When AI hands off to human:

```bash
gh issue comment 42 --body "$(cat <<'EOF'
## Handoff to Human Developer

**AI Agent:** @implementer-1
**Human:** @human-dev

**What's Done:**
- Core implementation complete
- PR #123 created
- Tests written and passing

**What Needs Human Attention:**
- Code review approval
- Deployment configuration
- Final integration testing

**Ready for human takeover.**
EOF
)"
```

### Human to AI Handoff

When human hands off to AI:

```bash
gh issue comment 42 --body "$(cat <<'EOF'
## Handoff to AI Agent

**Human:** @human-dev
**AI Agent:** @implementer-2

**What I've Done:**
- Architecture design complete
- API spec finalized
- Core interfaces defined

**What AI Should Do:**
- Implement the interfaces
- Write comprehensive tests
- Follow the spec exactly

**Reference:**
- API spec: docs/api-spec.md
- Design doc: docs/auth-design.md
- Example: src/examples/auth_example.py

AI agent should have everything needed to proceed.
EOF
)"
```

---

## 9.7 Mixed Team

When AI agents and humans work together.

### Team Composition

| Role | Agent Type | Responsibilities |
|------|------------|------------------|
| Orchestrator | AI | Planning, assignment, tracking |
| Implementer | AI | Coding, testing |
| Reviewer | Human | Code approval, quality |
| Lead | Human | Architecture, decisions |

### Coordination Pattern

```
                    +---------------+
                    | Orchestrator  |
                    |   (AMOA/AI)    |
                    +-------+-------+
                            |
            +---------------+---------------+
            v               v               v
      +---------+    +-------------+   +---------+
      |Implmtr 1|    | Implementer |   |Implmtr 3|
      |  (AI)   |    |   2 (AI)    |   |  (AI)   |
      +----+----+    +------+------+   +----+----+
           |                |               |
           +----------------+---------------+
                            | PR created
                      +-----v------+
                      | AI Review  |
                      |(Integrator)|
                      +-----+------+
                            |
              +-------------+-------------+
              v (small)                   v (big)
       +------+-------+          +-------+------+
       | Merge/Release |          | Human Review |
       +------+-------+          | (User/Lead)  |
              |                   +-------+------+
              |                           |
              |                    +------+-------+
              |                    | Merge/Release |
              |                    +------+-------+
              |                           |
              +-------------+-------------+
                            v
                      +-----+-----+
                      |   Done    |
                      +-----------+
```

### Communication Flow

1. Orchestrator assigns via AI Maestro
2. AI agents report via AI Maestro + GitHub
3. Humans review via GitHub
4. Orchestrator aggregates status from board

---

## 9.8 Escalation

When AI agents cannot proceed.

### Escalation Triggers

| Trigger | Escalate To | Timeline |
|---------|-------------|----------|
| Technical blocker | Orchestrator | Immediate |
| Access issue | Orchestrator then Human | 4 hours |
| Design question | Human lead | Immediate |
| Test failure (persistent) | Human reviewer | After 3 attempts |
| External dependency | Human | 24 hours |

### Escalation Process

**Step 1: AI agent reports blocker via COS.** Send a message using the `agent-messaging` skill with:

- **Recipient**: `amcos-main` (COS will escalate to Orchestrator/Manager)
- **Subject**: `Escalation: Issue #42 Blocked`
- **Priority**: `urgent`
- **Content**: `{"type": "escalation", "message": "Cannot proceed on #42. Need human decision.", "data": {"issue_number": 42, "blocker": "Design ambiguity in API spec", "question": "Should auth tokens be stateless or server-validated?", "impact": "Cannot proceed with implementation", "options": ["Stateless JWT", "Server-side session", "Hybrid"]}}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

```bash
# 2. Orchestrator escalates to human
gh issue comment 42 --body "$(cat <<'EOF'
## Escalation to Human Lead

@human-lead AI agent needs decision:

**Question:** Should auth tokens be stateless or server-validated?

**Options:**
1. Stateless JWT (simpler, but can't revoke)
2. Server-side session (can revoke, more complexity)
3. Hybrid approach

**Impact:** Implementation blocked until decision made.

Please advise.
EOF
)"
```

### Escalation Response Flow

```
AI Agent blocks -> Orchestrator notified
                         |
          +--------------+--------------+
          v                             v
    Can Orchestrator              Needs Human
    resolve?                      Decision
          |                             |
     YES  |                             |
          v                             v
    Resolve, notify              Escalate via
    agent to continue            GitHub comment
                                       |
                                       v
                                Human responds
                                       |
                                       v
                                Orchestrator
                                updates agent
                                       |
                                       v
                                Agent continues
```

---

## Previous: Part 1

Return to [ai-agent-vs-human-workflow-part1-fundamentals.md](ai-agent-vs-human-workflow-part1-fundamentals.md) for:

- Key differences in AI vs human workflow
- Assignment strategies for AI agents
- Assignment strategies for human developers
- Communication channels

## Index

Return to [ai-agent-vs-human-workflow.md](ai-agent-vs-human-workflow.md) for the complete table of contents.
