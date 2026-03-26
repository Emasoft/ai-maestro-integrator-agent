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

## Reference Documents

### Handoff Protocols ([handoff-protocols](references/handoff-protocols.md))

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

- [handoff-protocols](references/handoff-protocols.md) — Complete handoff protocol reference
- [ai-maestro-message-templates](references/ai-maestro-message-templates.md) — AI Maestro message format templates (use via `agent-messaging` skill)
- [sub-agent-role-boundaries-template](references/sub-agent-role-boundaries-template.md) — Worker agent role boundary template
- [routing-checklist](references/routing-checklist.md) — Task routing checklist for agent coordination
- [record-keeping](references/record-keeping.md) — Session record-keeping formats and state management
- [phase-procedures](references/phase-procedures.md) — Integration phase procedures and workflow steps
