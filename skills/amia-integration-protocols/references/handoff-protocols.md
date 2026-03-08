# Handoff Protocols Reference

## Contents

- [Document Delivery Protocol](#document-delivery-protocol)
- [Task Delegation Protocol](#task-delegation-protocol)
- [Acknowledgment Protocol](#acknowledgment-protocol)
- [Completion Reporting Protocol](#completion-reporting-protocol)
- [Blocker Escalation Protocol](#blocker-escalation-protocol)

---

## Purpose

This document defines the standard protocols for handing off tasks, documents, and communications between the orchestrator and remote agents in the AMOA ecosystem.

---


## Document Delivery Protocol

All documents (.md files) shared between agents MUST follow this protocol:

### Delivery Rules

1. **NEVER embed full document content in AI Maestro messages**
2. Save document to local handoff directory: `docs_dev/handoffs/`
3. Use standard filename format: `handoff-{uuid}-{from}-to-{to}.md`
4. Send AI Maestro message with local file path only
5. Recipient reads from local handoff directory

**NOTE:** This matches the standard protocol defined in `amoa-messaging-templates`.

### Message Format

> **Note**: Use the `agent-messaging` skill to send messages. The JSON structure below shows the message content.

```json
{
  "to": "{{AGENT_SESSION}}",
  "subject": "document_delivery",
  "priority": "high",
  "content": {
    "type": "document_delivery",
    "message": "Document ready. Path: docs_dev/handoffs/handoff-{{UUID}}-{{FROM}}-to-{{TO}}.md"
  }
}
```

### Storage Structure

```
docs_dev/handoffs/
  handoff-{uuid}-{from}-to-{to}.md  # All handoff documents
```

### Integration with GitHub Issues

When handoff relates to a GitHub issue:

1. Save handoff document locally first
2. Optionally link in issue comment: `See handoff: docs_dev/handoffs/handoff-{uuid}.md`
3. Primary delivery remains via AI Maestro with local path

---

## Task Delegation Protocol

When orchestrator delegates a task to a remote agent:

1. **Compile task template** with all variables substituted
2. **Save to local handoff directory**: `docs_dev/handoffs/`
3. **Send AI Maestro message** with local file path
4. **Wait for ACK** within timeout period
5. **Track progress** via handoff status updates

### Template Reference

See: [handoff-templates.md](./handoff-templates.md#task-delegation)

---

## Acknowledgment Protocol

Remote agents MUST acknowledge task receipt:

### ACK Format

```
[ACK] {{TASK_ID}} - {{STATUS}}
Understanding: {{ONE_LINE_SUMMARY}}
```

### Status Values

| Status | Meaning |
|--------|---------|
| RECEIVED | Task received, will begin work immediately |
| CLARIFICATION_NEEDED | Need more info (list questions) |
| REJECTED | Cannot accept task (explain why) |
| QUEUED | Have prior tasks, will start after them |

### Escalation Rules

- If no ACK received: Orchestrator sends reminder
- If still no response: Orchestrator sends urgent reminder
- If still unresponsive: Mark agent as unresponsive, consider reassignment

### Template Reference

See: [handoff-templates.md](./handoff-templates.md#acknowledgment)

---

## Completion Reporting Protocol

When agent completes a task:

1. **Create completion report** using template
2. **Upload to GitHub issue** as comment
3. **Update GitHub issue labels** (status:complete)
4. **Send AI Maestro message** with URL
5. **Wait for orchestrator sign-off**

### Template Reference

See: [handoff-templates.md](./handoff-templates.md#completion-report)

---

## Blocker Escalation Protocol

When agent encounters a blocker:

1. **Document blocker** with context and impact
2. **Upload to GitHub issue** as comment
3. **Update GitHub issue labels** (status:blocked)
4. **Send AI Maestro message** with URGENT priority
5. **Wait for orchestrator response**

### Blocker Categories

| Category | Example |
|----------|---------|
| Missing dependency | Required package not available |
| Auth failure | Cannot access required resource |
| Spec ambiguity | Requirements unclear |
| Technical block | API limit, rate limiting |
| Conflict | Merge conflict, resource contention |

### Template Reference

See: [handoff-templates.md](./handoff-templates.md#blocker-report)

---

## Integration with Other Protocols

This protocol integrates with:

- **echo-acknowledgment-protocol.md** - ACK timing and retries
- **messaging-protocol.md** - AI Maestro message format
- **artifact-sharing-protocol.md** - Large file sharing
- **document-storage-protocol.md** - Local storage rules

---

## Troubleshooting

### Document Not Received

1. Check GitHub issue for uploaded document
2. Verify AI Maestro message was sent
3. Check recipient agent is online
4. Resend with explicit URL

### ACK Not Received

1. Wait for timeout period
2. Send explicit ACK reminder
3. If still no response, mark unresponsive
4. Consider reassigning task

### Document Corrupted

1. Re-download from GitHub URL
2. Verify SHA256 hash if available
3. Contact sender for re-upload if needed

---

**Version**: 1.0.0
**Last Updated**: 2026-01-15
