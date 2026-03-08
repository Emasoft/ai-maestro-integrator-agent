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

This skill provides shared reference documents that are used across multiple Integrator Agent skills. It contains common patterns, protocols, and utilities that enable consistent behavior across the skill set.

## Prerequisites

None required. This is a reference skill with no external dependencies.

## Instructions

1. Identify the shared protocol or pattern needed for the current task
2. Review the relevant reference document from the list below
3. Apply the protocol or pattern to the agent workflow
4. Validate the implementation against the documented schema
5. Document any handoff or session state according to the standard format

### Checklist

Copy this checklist and track your progress:

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

## Reference Documents

### Handoff Protocols ([references/handoff-protocols.md](references/handoff-protocols.md))

Standard protocols for handing off work between agents:

- When you need to transfer context between agents → Handoff Format
- If you need to document session state → Session State Schema
- When coordinating multi-agent workflows → Coordination Patterns

**Contents:**

- Document Delivery Protocol
- Task Delegation Protocol
- Acknowledgment Protocol
- Completion Reporting Protocol
- Blocker Escalation Protocol

## Examples

### Example 1: Agent Handoff Format

```json
{
  "handoff_type": "task_delegation",
  "from_agent": "orchestrator",
  "to_agent": "code-reviewer",
  "context": {
    "pr_number": 123,
    "repository": "owner/repo",
    "task": "Review code changes"
  },
  "session_state": {
    "files_reviewed": [],
    "comments_made": []
  }
}
```

### Example 2: Session State Schema

```json
{
  "session_id": "sess_abc123",
  "started_at": "2025-01-30T10:00:00Z",
  "current_phase": "review",
  "completed_tasks": ["fetch_pr", "analyze_diff"],
  "pending_tasks": ["post_review"]
}
```

## Error Handling

### Issue: Handoff context incomplete

**Cause**: Required fields missing from handoff payload.

**Solution**: Validate handoff against schema before sending. Required fields: `handoff_type`, `from_agent`, `to_agent`, `context`.

### Issue: Session state deserialization fails

**Cause**: Invalid JSON or schema mismatch.

**Solution**: Validate JSON structure and ensure all datetime fields use ISO 8601 format.

## Resources

- [references/handoff-protocols.md](references/handoff-protocols.md) - Complete handoff protocol reference
  <!-- TOC: handoff-protocols.md -->
  - Document Delivery Protocol
  - Task Delegation Protocol
  - Acknowledgment Protocol
  <!-- /TOC -->
- [references/ai-maestro-message-templates.md](references/ai-maestro-message-templates.md) - AI Maestro curl command templates for inter-agent messaging
  <!-- TOC: ai-maestro-message-templates.md -->
  - 0 Standard AI Maestro Messaging Approach
  - 0 Receiving Messages from Orchestrator (AMOA)
  - 1 Integration Request from AMOA
  <!-- /TOC -->
- [references/sub-agent-role-boundaries-template.md](references/sub-agent-role-boundaries-template.md) - Worker agent role boundary template for task delegation
  <!-- TOC: sub-agent-role-boundaries-template.md -->
  - Purpose
  - Core Identity: Worker Agent (Not Orchestrator)
  - What Worker Agents Are
  <!-- /TOC -->
- [references/routing-checklist.md](references/routing-checklist.md) - Task routing checklist for agent coordination
  <!-- TOC: routing-checklist.md -->
  - Sub-Agent Routing Table
  - Routing Decision Guidelines
  - Route to code-reviewer when:
  <!-- /TOC -->
- [references/record-keeping.md](references/record-keeping.md) - Session record-keeping formats and state management
  <!-- TOC: record-keeping.md -->
  - Routing Log Format
  - Integration Status Files
  - Quality Reports
  <!-- /TOC -->
- [references/phase-procedures.md](references/phase-procedures.md) - Integration phase procedures and workflow steps
  <!-- TOC: phase-procedures.md -->
  - Phase 1: Request Reception
  - Check AI Maestro Inbox
  - Extract Request Details
  <!-- /TOC -->
