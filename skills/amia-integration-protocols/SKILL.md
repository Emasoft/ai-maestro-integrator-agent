---
name: amia-integration-protocols
description: "Use when composing inter-agent handoff payloads, session state snapshots, multi-agent coordination protocols, or referencing shared message templates / record-keeping formats. Trigger with handoff, delegation, acknowledgment, completion report, blocker escalation, or routing decision requests. Loaded by ai-maestro-integrator-agent-main-agent."
license: MIT
compatibility: Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.1
agent: ai-maestro-integrator-agent-main-agent
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
    - 2.1 Integration Request from AMOA
    - 2.2 Handoff Document Rejection
  - 3.0 Sending Messages to Sub-Agents
    - 3.1 Task Delegation to Sub-Agent
  - 4.0 Reporting Results to Orchestrator (AMOA)
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
- [sub-agent-role-boundaries-template](references/sub-agent-role-boundaries-template.md) — Role boundaries:
  - [Purpose](#purpose)
  - [Core Identity: Worker Agent (Not Orchestrator)](#core-identity-worker-agent-not-orchestrator)
    - [What Worker Agents Are](#what-worker-agents-are)
    - [What Worker Agents Are NOT](#what-worker-agents-are-not)
  - [Standard Output Format](#standard-output-format)
    - [Minimal Report to Orchestrator](#minimal-report-to-orchestrator)
    - [Detailed Reports in Files](#detailed-reports-in-files)
  - [Communication Rules](#communication-rules)
    - [Report to Main Agent Only](#report-to-main-agent-only)
    - [AI Maestro Messaging Protocol](#ai-maestro-messaging-protocol)
    - [GitHub Projects Integration](#github-projects-integration)
  - [Tool Restrictions](#tool-restrictions)
    - [Standard Permissions Table](#standard-permissions-table)
    - [Exceptions by Agent Type](#exceptions-by-agent-type)
  - [Common Constraints Template](#common-constraints-template)
    - [Agent Specifications Table](#agent-specifications-table)
    - [IRON RULES Section Template](#iron-rules-section-template)
  - [IRON RULES](#iron-rules)
    - [What This Agent DOES](#what-this-agent-does)
    - [What This Agent NEVER DOES](#what-this-agent-never-does)
  - [Success/Completion Conditions](#successcompletion-conditions)
    - [Task Completion Criteria](#task-completion-criteria)
    - [Reporting Completion](#reporting-completion)
  - [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
    - [DO NOT: Verbose Context Pollution](#do-not-verbose-context-pollution)
    - [DO NOT: Decision Making](#do-not-decision-making)
    - [DO NOT: Autonomous Task Selection](#do-not-autonomous-task-selection)
  - [Template Usage](#template-usage)
  - [References](#references)
- [routing-checklist](references/routing-checklist.md) — Routing checklist:
  - [Sub-Agent Routing Table](#sub-agent-routing-table)
  - [Routing Decision Guidelines](#routing-decision-guidelines)
    - [Route to code-reviewer when:](#route-to-code-reviewer-when)
    - [Route to bug-investigator when:](#route-to-bug-investigator-when)
    - [Handle PR directly when:](#handle-pr-directly-when)
    - [Spawn verifier when:](#spawn-verifier-when)
    - [Escalate to orchestrator when:](#escalate-to-orchestrator-when)
  - [Priority Triage](#priority-triage)
  - [Success Criteria Checklist](#success-criteria-checklist)
    - [Integration Request Received](#integration-request-received)
    - [Routing Decision Made](#routing-decision-made)
    - [Sub-Agent Completed](#sub-agent-completed)
    - [Quality Verified](#quality-verified)
  - [Routing Decision Checklist](#routing-decision-checklist)
    - [Step 1: Identify Request Type](#step-1-identify-request-type)
    - [Step 2: Check Request Completeness](#step-2-check-request-completeness)
    - [Step 3: Select Appropriate Sub-Agent](#step-3-select-appropriate-sub-agent)
    - [Step 4: Prepare Handoff Context](#step-4-prepare-handoff-context)
    - [Step 5: Draft Delegation Message](#step-5-draft-delegation-message)
    - [Step 6: Log Routing Decision](#step-6-log-routing-decision)
    - [Step 7: Execute Delegation](#step-7-execute-delegation)
    - [Step 8: Monitor Completion](#step-8-monitor-completion)
    - [Step 9: Report to AMOA](#step-9-report-to-amoa)
- [record-keeping](references/record-keeping.md) — Record-keeping:
  - 1. Routing Log Format
  - 2. Integration Status Files
  - 3. Quality Reports
  - 4. Session State Structure
  - Best Practices
- [phase-procedures](references/phase-procedures.md) — Phase procedures:
  - [Phase 1: Request Reception](#phase-1-request-reception)
    - [1. Check AI Maestro Inbox](#1-check-ai-maestro-inbox)
    - [2. Extract Request Details](#2-extract-request-details)
    - [3. Log Request](#3-log-request)
  - [Phase 2: Routing Decision](#phase-2-routing-decision)
    - [1. Analyze Request Type](#1-analyze-request-type)
    - [2. Check Sub-Agent Availability](#2-check-sub-agent-availability)
    - [3. Prepare Context Package](#3-prepare-context-package)
    - [4. Create Status Tracking File](#4-create-status-tracking-file)
  - [Phase 3: Delegation](#phase-3-delegation)
    - [1. Draft Delegation Message](#1-draft-delegation-message)
    - [2. Send to Sub-Agent](#2-send-to-sub-agent)
    - [3. Log Delegation](#3-log-delegation)
  - [Phase 4: Monitor Completion](#phase-4-monitor-completion)
    - [1. Wait for Sub-Agent Response](#1-wait-for-sub-agent-response)
    - [2. Validate Response Format](#2-validate-response-format)
    - [3. Read Result Details](#3-read-result-details)
    - [4. Update Status File](#4-update-status-file)
  - [Phase 5: Report to AMOA](#phase-5-report-to-amoa)
    - [1. Prepare Status Report](#1-prepare-status-report)
    - [2. Send to AMOA](#2-send-to-amoa)
    - [3. Handle Blockers (If Any)](#3-handle-blockers-if-any)
    - [4. Final Logging](#4-final-logging)
  - [Verification Summary](#verification-summary)

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
