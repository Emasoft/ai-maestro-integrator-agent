# AI Agent vs Human Workflow

This document covers the differences between AI agent and human developer workflows in GitHub Kanban management.

## Contents

### Part 1: Fundamentals and Communication
See [ai-agent-vs-human-workflow-part1-fundamentals.md](ai-agent-vs-human-workflow-part1-fundamentals.md)

- 9.1 Key differences in AI vs human workflow
  - 9.1.1 Comparison matrix (availability, response time, context)
  - 9.1.2 Workflow timing differences
  - 9.1.3 Session considerations
- 9.2 Assignment strategies for AI agents
  - 9.2.1 Assignment rules (orchestrator assigns, one task, clear criteria)
  - 9.2.2 Assignment process with AI Maestro
  - 9.2.3 AI agent capacity by type
  - 9.2.4 Reassignment on session end
- 9.3 Assignment strategies for human developers
  - 9.3.1 Assignment rules (self-assignment, multiple items)
  - 9.3.2 Assignment via board
  - 9.3.3 Assignment via orchestrator
  - 9.3.4 Human developer workflow timeline
- 9.4 Communication channels
  - 9.4.1 AI agent communication (AI Maestro, GitHub)
  - 9.4.2 Human developer communication (GitHub, Slack, email)
  - 9.4.3 Orchestrator communication methods

### Part 2: Workflows and Coordination
See [ai-agent-vs-human-workflow-part2-workflows.md](ai-agent-vs-human-workflow-part2-workflows.md)

- 9.5 Review workflow differences
  - 9.5.1 AI agent as PR author
  - 9.5.2 AI agent as reviewer (cannot approve)
  - 9.5.3 Human as reviewer (can approve, merge)
  - 9.5.4 Review escalation flow
- 9.6 Handoff protocols
  - 9.6.1 AI to AI handoff (document state, reassign)
  - 9.6.2 AI to human handoff
  - 9.6.3 Human to AI handoff
- 9.7 Mixed team coordination
  - 9.7.1 Team composition (orchestrator, implementer, reviewer, lead)
  - 9.7.2 Coordination pattern diagram
  - 9.7.3 Communication flow
- 9.8 Escalation paths for AI blockers
  - 9.8.1 Escalation triggers and timelines
  - 9.8.2 Escalation process via AI Maestro
  - 9.8.3 Escalation response flow diagram

---

## Quick Reference

### When to Read Part 1

Read Part 1 when you need to:
- Understand fundamental differences between AI and human workflows
- Assign tasks to AI agents or human developers
- Set up communication channels for a mixed team
- Know AI agent capacity and session constraints

### When to Read Part 2

Read Part 2 when you need to:
- Set up code review workflows with AI and humans
- Handle work handoffs between agents or humans
- Coordinate a mixed team of AI agents and humans
- Handle blockers and escalations from AI agents

---

## Key Concepts Summary

| Concept | AI Agent | Human Developer |
|---------|----------|-----------------|
| Assignment | Orchestrator assigns | Self-assignment OK |
| Concurrent work | 1 primary task | Multiple tasks |
| Communication | AI Maestro + GitHub | GitHub + Slack + Email |
| Code review | Cannot approve | Can approve |
| Escalation | Via orchestrator | Direct to lead |

---

## Related References

- [status-transitions.md](status-transitions.md) - Issue state transitions
- [agent-assignment-via-board.md](agent-assignment-via-board.md) - Agent coordination patterns
