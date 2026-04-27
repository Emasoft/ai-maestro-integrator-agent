---
name: amia-integration-protocols
description: "Use when accessing shared utilities and protocols. Loaded by ai-maestro-integrator-agent-main-agent."
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
  - Table of Contents
  - 1.0 Standard AI Maestro Messaging Approach
  - 2.0 Receiving Messages (via COS)
    - 2.1 Integration Request
    - 2.2 Handoff Document Rejection
  - 3.0 Delegating Tasks to Team Agents (via COS)
    - 3.1 Task Delegation Request
  - 4.0 Reporting Results (via COS)
    - 4.1 Integration Status Report (Success)
    - 4.2 Integration Status Report (In Progress)
    - 4.3 Integration Status Report (Failed)
    - 4.4 Blocker Escalation (Critical Issues)
  - 5.0 Quality Gate Communication
    - 5.1 PR Review Complete (All Gates Passed)
    - 5.2 PR Review Complete (Tests Failed)
    - 5.3 Merge Approved
    - 5.4 Merge Rejected
    - 5.5 Release Ready Notification
  - Notes
- [sub-agent-role-boundaries-template](references/sub-agent-role-boundaries-template.md) — Role boundaries:
  - Table of Contents
  - Purpose
  - Core Identity: Worker Agent (Not Orchestrator)
    - What Worker Agents Are
    - What Worker Agents Are NOT
  - Standard Output Format
    - Minimal Report to Orchestrator
    - Detailed Reports in Files
  - Communication Rules
    - Report to Main Agent Only
    - AI Maestro Messaging Protocol
    - GitHub Projects Integration
  - Tool Restrictions
    - Standard Permissions Table
    - Exceptions by Agent Type
  - Common Constraints Template
    - Agent Specifications Table
    - IRON RULES Section Template
  - IRON RULES
    - What This Agent DOES
    - What This Agent NEVER DOES
  - Success/Completion Conditions
    - Task Completion Criteria
    - Reporting Completion
  - Anti-Patterns to Avoid
    - DO NOT: Verbose Context Pollution
    - DO NOT: Decision Making
    - DO NOT: Autonomous Task Selection
  - Template Usage
  - References
- [routing-checklist](references/routing-checklist.md) — Routing checklist:
  - Table of Contents
  - Sub-Agent Routing Table
  - Routing Decision Guidelines
    - Route to code-reviewer when
    - Route to bug-investigator when
    - Handle PR directly when
    - Spawn verifier when
    - Escalate to orchestrator when
  - Priority Triage
  - Success Criteria Checklist
    - Integration Request Received
    - Routing Decision Made
    - Sub-Agent Completed
    - Quality Verified
  - Routing Decision Checklist
    - Step 1: Identify Request Type
    - Step 2: Check Request Completeness
    - Step 3: Select Appropriate Sub-Agent
    - Step 4: Prepare Handoff Context
    - Step 5: Draft Delegation Message
    - Step 6: Log Routing Decision
    - Step 7: Execute Delegation
    - Step 8: Monitor Completion
    - Step 9: Report to AMOA
- [record-keeping](references/record-keeping.md) — Record-keeping:
  - 1. Routing Log Format
  - 2. Integration Status Files
  - 3. Quality Reports
  - 4. Session State Structure
  - Best Practices
- [phase-procedures](references/phase-procedures.md) — Phase procedures:
  - Table of Contents
  - Phase 1: Request Reception
    - 1. Check AI Maestro Inbox
    - 2. Extract Request Details
    - 3. Log Request
  - Phase 2: Routing Decision
    - 1. Analyze Request Type
    - 2. Check Sub-Agent Availability
    - 3. Prepare Context Package
    - 4. Create Status Tracking File
  - Phase 3: Delegation
    - 1. Draft Delegation Message
    - 2. Send to Sub-Agent
    - 3. Log Delegation
  - Phase 4: Monitor Completion
    - 1. Wait for Sub-Agent Response
    - 2. Validate Response Format
    - 3. Read Result Details
    - 4. Update Status File
  - Phase 5: Report to AMOA
    - 1. Prepare Status Report
    - 2. Send to AMOA
    - 3. Handle Blockers (If Any)
    - 4. Final Logging
  - Verification Summary

## Examples

```bash
# Send a handoff payload from integrator to orchestrator
amp-send.sh amoa-main "Integration Complete" '{
  "handoff_type": "task_completion",
  "from_agent": "amia-main",
  "to_agent": "amoa-main",
  "context": {"pr": 42, "status": "merged", "branch": "feature/auth"},
  "timestamp": "2026-03-26T12:00:00Z"
}'
```

**Expected result:** The orchestrator receives a structured handoff payload with all required fields (`handoff_type`, `from_agent`, `to_agent`, `context`) and can update its task tracking accordingly.
