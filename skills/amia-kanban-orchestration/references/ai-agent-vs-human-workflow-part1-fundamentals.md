# AI Agent vs Human Workflow - Part 1: Fundamentals and Communication

<a name="part-1-toc"></a>
## Table of Contents

- 9.1 [Key differences in AI vs human workflow](#91-key-differences)
- 9.1a [Review routing: AI Review vs Human Review](#91a-review-routing)
- 9.2 [Assignment strategies for AI agents](#92-ai-assignment)
- 9.3 [Assignment strategies for human developers](#93-human-assignment)
- 9.4 [Communication channels](#94-communication)

---

## 9.1 Key Differences

AI agents and human developers interact with the Kanban board differently.

### Comparison Matrix

| Aspect | AI Agent | Human Developer |
|--------|----------|-----------------|
| Availability | 24/7 while session active | Working hours |
| Response time | Immediate | Minutes to hours |
| Context | Limited to session | Long-term memory |
| Communication | AI Maestro messages | GitHub comments, Slack |
| Self-assignment | No (orchestrator assigns) | Yes (can self-assign) |
| Status updates | Should update immediately | May delay updates |
| Blockers | Reports immediately | May investigate first |
| Code review | Cannot self-approve | Can approve others' PRs |

### Workflow Timing

```
AI Agent Timeline (small task):
  Assigned -> Start (seconds) -> PR (hours) -> AI Review -> Merge/Release -> Done

AI Agent Timeline (big task):
  Assigned -> Start (seconds) -> PR (hours) -> AI Review -> Human Review -> Merge/Release -> Done

Human Developer Timeline (small task):
  Assigned -> Start (hours/days) -> PR (days) -> AI Review -> Merge/Release -> Done

Human Developer Timeline (big task):
  Assigned -> Start (hours/days) -> PR (days) -> AI Review -> Human Review -> Merge/Release -> Done
```

### Session Considerations

| Factor | AI Agent | Human Developer |
|--------|----------|-----------------|
| Session end | Work must be deferred | Work continues next day |
| Context loss | Complete on session end | Partial (notes help) |
| Branch ownership | May need handoff | Continues |
| PR ownership | May need handoff | Continues |

---

<a name="91a-review-routing"></a>
## 9.1a Review Routing: AI Review vs Human Review

The 8-column kanban system splits the old single "Review" column into three distinct columns with specific routing rules.

### The Three Review-Phase Columns

| Column | Code | Who Reviews | Which Tasks |
|--------|------|-------------|-------------|
| AI Review | `ai-review` | Integrator agent (AMIA) | ALL tasks (both small and big) |
| Human Review | `human-review` | Human user (via AMAMA) | BIG tasks only |
| Merge/Release | `merge-release` | Automatic (CI/merge) | All approved tasks |

### Task Size Routing

```
                    ┌─────────────┐
                    │ In Progress │
                    └──────┬──────┘
                           │ PR created
                           ▼
                    ┌─────────────┐
                    │  AI Review  │ ← Integrator reviews ALL tasks
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │ (changes   │            │ (changes
              │  requested)│            │  requested)
              ▼            │            ▼
       ┌─────────────┐    │     ┌──────────────┐
       │ In Progress  │    │     │ In Progress   │
       └─────────────┘    │     └──────────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼ SMALL task                ▼ BIG task
     ┌──────────────┐          ┌──────────────┐
     │Merge/Release │          │ Human Review  │ ← User reviews via AMAMA
     └──────┬───────┘          └──────┬───────┘
            │                         │
            │                  ┌──────┴────────┐
            │                  │               │
            │                  ▼ approved      ▼ changes requested
            │           ┌──────────────┐  ┌─────────────┐
            │           │Merge/Release │  │ In Progress  │
            │           └──────┬───────┘  └─────────────┘
            │                  │
            └────────┬─────────┘
                     ▼
              ┌─────────────┐
              │    Done     │
              └─────────────┘
```

### How Task Size Is Determined

Task size is determined by labels on the GitHub issue:

| Label | Routing | Examples |
|-------|---------|---------|
| `size:small` | AI Review → Merge/Release (skip Human Review) | Bug fixes, minor refactors, documentation updates |
| `size:big` | AI Review → Human Review → Merge/Release | New features, architecture changes, breaking changes |
| No size label | Treated as small (default) | Quick tasks without explicit sizing |

### Who Decides the Routing

The **Integrator agent (AMIA)** decides the routing after completing AI Review:

1. Integrator reviews the PR (code quality, tests, standards)
2. If changes needed → moves back to In Progress
3. If approved AND task is small → moves to Merge/Release
4. If approved AND task is big → moves to Human Review

### Human Review via AMAMA

When a big task reaches Human Review:

1. AMAMA (Assistant Manager) notifies the user that a review is needed
2. User reviews the PR on GitHub
3. User approves → Orchestrator or user moves to Merge/Release
4. User requests changes → moves back to In Progress

---

## 9.2 AI Assignment

### Assignment Rules for AI Agents

1. **Orchestrator assigns** - AI agents do not self-assign
2. **One primary task** - Focus on one In Progress item
3. **Clear completion criteria** - Must know when done
4. **Session-aware scope** - Completable within session

### Assignment Process

```bash
# 1. Identify available agent
AGENT="implementer-1"

# 2. Assign issue
gh issue edit 42 --add-assignee $AGENT

# 3. Update board status to Todo (if not already)
# [GraphQL mutation]

# 4. Notify agent via AI Maestro
# Send a message using the agent-messaging skill with:
#   Recipient: implementer-1
#   Subject: Assignment: Issue #42
#   Priority: high
#   Content: {"type": "assignment", "message": "You are assigned to issue #42: [MODULE] auth-core. Move to In Progress when starting.", "data": {"issue_number": 42, "issue_url": "https://github.com/owner/repo/issues/42", "priority": "high", "estimated_hours": 4}}
#   Verify: Confirm delivery via the agent-messaging skill send confirmation.
```

### AI Agent Capacity

| Agent Type | Concurrent Items | Typical Duration |
|------------|------------------|------------------|
| Implementer | 1 In Progress | 2-8 hours |
| Code Reviewer (Integrator) | 2-3 AI Review | 30 min each |
| Helper | 1 task | 15-60 min |

### Reassignment on Session End

If AI agent session ends with work incomplete:

```bash
# 1. Document state
gh issue comment 42 --body "$(cat <<'EOF'
## Session Ended

Agent: @implementer-1
Session ended with work incomplete.

**Progress:**
- [x] Created feature branch
- [x] Implemented core logic
- [ ] Write tests
- [ ] Documentation

**Branch:** feature/issue-42-auth-core
**Commits:** 3 commits pushed

Ready for new agent assignment.
EOF
)"

# 2. Remove assignee or reassign
gh issue edit 42 --remove-assignee implementer-1

# 3. Move back to Todo if needed
# [GraphQL mutation]
```

---

## 9.3 Human Assignment

### Assignment Rules for Humans

1. **Self-assignment allowed** - Humans can pick up work
2. **Multiple items OK** - Can juggle several tasks
3. **Longer timelines** - Days, not hours
4. **Less structured updates** - May batch status changes

### Assignment via Board

Humans typically:
1. View project board in browser
2. Drag unassigned Todo item
3. Assign themselves
4. Move to In Progress when starting

### Assignment via Orchestrator

Orchestrator can also assign to humans:

```bash
# Assign to human developer
gh issue edit 42 --add-assignee human-dev

# Comment with context (more detailed for humans)
gh issue comment 42 --body "$(cat <<'EOF'
@human-dev This is assigned to you for Sprint 3.

**Context:**
- This is part of the auth system epic (#30)
- Related to #35 (API client) which is in progress
- Priority is high due to Q1 deadline

**Questions?** Ping me in Slack or comment here.
EOF
)"
```

### Human Developer Workflow

```
Day 1: Assigned, reads issue, asks questions
Day 2: Starts work, moves to In Progress
Day 3-5: Development, commits
Day 6: Creates PR, moves to AI Review
Day 7+: Addresses review feedback
Final: Merged, moves to Done
```

---

## 9.4 Communication

### AI Agent Communication

| Channel | Use Case | Example |
|---------|----------|---------|
| AI Maestro | Task assignment | "You are assigned #42" |
| AI Maestro | Status requests | "Report progress on #42" |
| AI Maestro | Urgent notifications | "Blocker on #42 resolved" |
| GitHub comment | Documentation | Status updates, blockers |

### Human Developer Communication

| Channel | Use Case | Example |
|---------|----------|---------|
| GitHub comment | Official record | Progress, blockers, questions |
| Slack | Quick questions | "Is the API spec final?" |
| Email | External notifications | PR reviews, mentions |
| Standup | Team sync | Daily progress |

### Orchestrator Communication

To AI agents: Send a message using the `agent-messaging` skill with the recipient agent name, subject, content, and priority.

To humans:
```bash
# GitHub comment (tagged)
gh issue comment 42 --body "@human-dev Please review the blockers section"

# Or direct mention in issue body
```

---

## Next: Part 2

Continue to [ai-agent-vs-human-workflow-part2-workflows.md](ai-agent-vs-human-workflow-part2-workflows.md) for:
- Review workflow differences
- Handoff protocols
- Mixed team coordination
- Escalation paths
