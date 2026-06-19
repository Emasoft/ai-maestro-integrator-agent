# AI Maestro Role Boundaries

**CRITICAL: This document defines the strict boundaries between agent roles. Violating these boundaries breaks the system architecture.**

---

## Role Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              AMAMA (AI Maestro Assistant Manager Agent)           │
│              Title: MANAGER                                      │
│              - User's sole interlocutor                          │
│              - Creates projects                                  │
│              - Creates teams/COS/base + AUTONOMOUS/MAINTAINER     │
│              - Supervises all operations                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│      AMCOS       │ │      AMOA        │ │      AMIA        │
│ Chief of Staff  │ │  Orchestrator   │ │   Integrator    │
│ Title: CHIEF-   │ │ Title: ORCH-    │ │ Title: INTEG-   │
│ OF-STAFF        │ │ ESTRATOR        │ │ RATOR           │
│ TEAM-SCOPED     │ │ PROJECT-        │ │ PROJECT-        │
│ (one per team)  │ │ LINKED          │ │ LINKED          │
│                 │ │ (one per proj)  │ │ (one per proj)  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Governance Titles

| Title | Role | Scope | Authority |
|-------|------|-------|-----------|
| **manager** | AMAMA | Organization-wide | Final approval, user communication |
| **chief-of-staff** | AMCOS | Team-scoped (one per team) | Agent lifecycle, configuration |
| **orchestrator** | AMOA | Project-linked | Task distribution, kanban, coordination |
| **integrator** | AMIA | Project-linked | Code review, quality gates, merging |
| **architect** | AMAA | Project-linked | Architecture, design decisions |
| **member** | AMPA | Project-linked | Task execution within role boundaries |

---

## AMCOS (Chief of Staff) - Responsibilities

### AMCOS CAN

- ✅ Create extra member agents under the MANAGER's team-build-out mandate (R30.1) — the 5-member base is auto-created with the team
- ✅ Terminate own-team agents under its mandate (R30)
- ✅ Hibernate/wake own-team agents
- ✅ Configure agents with skills and plugins
- ✅ Assign agents to project teams
- ✅ Handle handoff protocols between agents
- ✅ Monitor agent health and availability
- ✅ Replace failed own-team agents under its mandate (R30)
- ✅ Report agent performance to AMAMA

### AMCOS CANNOT

- ❌ Create projects (AMAMA only)
- ❌ Assign tasks to agents (AMOA only)
- ❌ Manage GitHub Project kanban (AMOA only)
- ❌ Make architectural decisions (AMAA only)
- ❌ Perform code review (AMIA only)
- ❌ Communicate directly with user (AMAMA only)

### AMCOS Scope

- **Team-scoped**: One AMCOS manages agents within its assigned team
- **Team-agnostic**: Creates teams but doesn't manage their work
- **Infrastructure-focused**: Ensures agents exist and are configured

---

## AMOA (Orchestrator) - Responsibilities

### AMOA CAN

- ✅ Assign tasks to agents
- ✅ Manage GitHub Project kanban for their project
- ✅ Track task progress
- ✅ Reassign tasks between agents
- ✅ Generate handoff documents
- ✅ Coordinate agent work within their project
- ✅ Request AMCOS to create/replace agents for their project

### AMOA CANNOT

- ❌ Create agents directly (request via AMCOS)
- ❌ Configure agent skills/plugins (AMCOS only)
- ❌ Create projects (AMAMA only)
- ❌ Manage agents outside their project

### AMOA Scope

- **Project-linked**: One AMOA per project
- **Task-focused**: Manages what agents DO, not what agents EXIST
- **Kanban owner**: Owns the GitHub Project board for their project

---

## AMAMA (Manager) - Responsibilities

### AMAMA CAN

- ✅ Create projects
- ✅ Create & delete teams on own authority — auto-creates the COS + 5-member base (R29.1)
- ✅ Create & delete AUTONOMOUS and MAINTAINER agents on own authority (R29.3)
- ✅ Grant the COS its team-build-out mandate (R30)
- ✅ Communicate with user
- ✅ Set strategic direction
- ✅ Override any agent decision
- ✅ Grant autonomous operation directives

### AMAMA CANNOT

- ❌ Hand-create or configure individual member agents (the COS builds out the team under its mandate)
- ❌ Assign tasks directly (delegates to AMOA)

### AMAMA Scope

- **Organization-wide**: Oversees all projects and agents
- **User-facing**: Only agent that talks to user
- **Decision authority**: Final approval on all significant operations

---

## Interaction Patterns

### Creating an Agent for a Project

```
AMOA: "I need a frontend developer agent for Project X"
  │
  ▼
AMCOS: Receives request, prepares agent specification
  │
  ▼
AMCOS: Spawns frontend-dev under its standing MANAGER mandate (R30)
  │    (no per-agent approval — the mandate was granted at team creation)
  ▼
AMCOS: Configures skills, assigns frontend-dev to the Project X team
  │
  ▼
AMCOS → AMOA: "Agent frontend-dev ready, assigned to your project"
  │
  ▼
AMOA: Assigns tasks from kanban to new agent
```

### Task Assignment

```
User/AMAMA: Creates GitHub issue in Project X
  │
  ▼
AMOA (Project X): Detects new issue, decides assignment
  │
  ▼
AMOA: Updates GitHub Project custom field "Assigned Agent"
AMOA: Sends AI Maestro notification to assigned agent
  │
  ▼
Agent: Receives task, begins work
```

### Agent Replacement

```
AMCOS: Detects agent-123 is unresponsive (terminal failure)
  │
  ▼
AMCOS: Replaces agent-123 with agent-456 under its mandate (R30)
  │    (own-team replacement — no per-replacement approval)
  ▼
AMCOS: Configures replacement agent-456
  │
  ▼
AMCOS → AMOA: "agent-123 replaced by agent-456, generate handoff"
  │
  ▼
AMOA: Generates handoff document with task context
AMOA: Reassigns kanban tasks from agent-123 to agent-456
AMOA: Sends handoff to agent-456
```

---

## Summary Table

| Responsibility | AMAMA | AMCOS | AMOA | AMIA | AMAA |
|----------------|------|------|-----|-----|-----|
| Create projects | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create teams (auto-creates COS + 5-base) | ✅ (R29.1) | ❌ | ❌ | ❌ | ❌ |
| Create AUTONOMOUS / MAINTAINER | ✅ (R29.3) | ❌ | ❌ | ❌ | ❌ |
| Create extra member agents | grants mandate (R30) | ✅ under mandate | Requests | ❌ | ❌ |
| Configure agents | ❌ | ✅ | ❌ | ❌ | ❌ |
| Assign agents to teams | ❌ | ✅ | ❌ | ❌ | ❌ |
| Assign tasks | ❌ | ❌ | ✅ | ❌ | ❌ |
| Manage kanban | ❌ | ❌ | ✅ | ❌ | ❌ |
| Code review | ❌ | ❌ | ❌ | ✅ | ❌ |
| Architecture | ❌ | ❌ | ❌ | ❌ | ✅ |
| Talk to user | ✅ | ❌ | ❌ | ❌ | ❌ |
| Governance title | manager | chief-of-staff | orchestrator | integrator | architect |

---

**Governance Note**: This document is a **local convenience reference**. The authoritative source for runtime governance rules is the `team-governance` skill. Agents MUST verify team membership and governance authorization via the `team-governance` skill before sensitive operations (merge, release, issue closure).

---

**Document Version**: 1.3.0
**Last Updated**: 2026-06-19
**Author**: ai-maestro-integrator-agent (INTEGRATOR)
