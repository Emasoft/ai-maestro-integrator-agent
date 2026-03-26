---
name: amia-integration-protocols
description: "Use when accessing shared utilities and protocols. Trigger with cross-skill reference requests."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
context: fork
user-invocable: false
---

# Shared References

## Overview

Shared reference documents used across Integrator Agent skills. Contains common patterns, protocols, and utilities for consistent behavior.

## Prerequisites

No external dependencies required.

## Instructions

1. Identify the shared protocol or pattern needed for the current task
2. Review the relevant reference document from the list below
3. Apply the protocol or pattern to the agent workflow
4. Validate the implementation against the documented schema
5. Document any handoff or session state according to the standard format

### Checklist

Copy this checklist and track your progress:

- [ ] Verify requesting agent's team membership via `team-governance` skill
- [ ] Identify the shared protocol or pattern needed
- [ ] Review the relevant reference document
- [ ] Apply the protocol or pattern to the workflow
- [ ] Validate implementation against documented schema
- [ ] Document handoff or session state in standard format
- [ ] Verify all required fields are present in handoff payload
- [ ] Ensure datetime fields use ISO 8601 format

## Output

| Output Type | Format | Description |
|-------------|--------|-------------|
| Handoff Payload | JSON | Structured agent handoff with context and state |
| Session State | JSON | Current session state snapshot for continuity |
| Coordination Protocol | JSON | Multi-agent workflow coordination structure |

## Error Handling

Validate handoff payloads before sending. Required fields: `handoff_type`, `from_agent`, `to_agent`, `context`. All datetime fields must use ISO 8601 format.

## Resources

- [handoff-protocols](references/handoff-protocols.md) — Handoff protocol reference:
  - Document Delivery Protocol
  - Task Delegation Protocol
  - Acknowledgment Protocol
  - Completion Reporting Protocol
  - Blocker Escalation Protocol
  - Troubleshooting
- [ai-maestro-message-templates](references/ai-maestro-message-templates.md) — Message templates:
  - 1.0 Standard AI Maestro Messaging Approach
  - 2.0 Receiving Messages from Orchestrator (AMOA)
  - 3.0 Sending Messages to Sub-Agents
  - 4.0 Reporting Results to Orchestrator (AMOA)
  - 5.0 Quality Gate Communication
- [sub-agent-role-boundaries-template](references/sub-agent-role-boundaries-template.md) — Role boundaries:
  - Core Identity: Worker Agent (Not Orchestrator)
  - Standard Output Format
  - Communication Rules
  - Tool Restrictions
  - Common Constraints Template
  - Success/Completion Conditions
  - Anti-Patterns to Avoid
- [routing-checklist](references/routing-checklist.md) — Routing checklist:
  - Sub-Agent Routing Table
  - Routing Decision Guidelines
  - Priority Triage
  - Success Criteria Checklist
  - Routing Decision Checklist
- [record-keeping](references/record-keeping.md) — Record-keeping:
  - 1. Routing Log Format
  - 2. Integration Status Files
  - 3. Quality Reports
  - 4. Session State Structure
  - Best Practices
- [phase-procedures](references/phase-procedures.md) — Phase procedures:
  - Phase 1: Request Reception
  - Phase 2: Routing Decision
  - Phase 3: Delegation
  - Phase 4: Monitor Completion
  - Phase 5: Report to AMOA
