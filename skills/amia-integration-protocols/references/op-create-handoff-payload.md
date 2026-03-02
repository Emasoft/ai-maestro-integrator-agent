---
name: op-create-handoff-payload
description: "Create a structured agent handoff payload for task delegation"
procedure: support-skill
workflow-instruction: support
---

# Operation: Create Handoff Payload


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify handoff type](#step-1-identify-handoff-type)
  - [Step 2: Gather context data](#step-2-gather-context-data)
  - [Step 3: Build the payload](#step-3-build-the-payload)
  - [Step 4: Validate required fields](#step-4-validate-required-fields)
  - [Step 5: Add timestamps](#step-5-add-timestamps)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Handoff Type Templates](#handoff-type-templates)
  - [Task Delegation](#task-delegation)
  - [Review Request](#review-request)
  - [Escalation](#escalation)
- [Error Handling](#error-handling)
  - [Missing required field](#missing-required-field)
  - [Invalid timestamp format](#invalid-timestamp-format)
  - [Unknown handoff type](#unknown-handoff-type)
- [Verification](#verification)

## Purpose

Create a properly structured JSON payload for handing off work between agents in a multi-agent workflow.

## When to Use

- Delegating a task from orchestrator to worker agent
- Transferring context between agent sessions
- Coordinating multi-agent workflows
- Documenting task context for subagent processing

## Prerequisites

1. Clear understanding of source and target agents
2. Complete context data for the task being handed off
3. Knowledge of the session state to preserve

## Procedure

### Step 1: Identify handoff type

Determine the handoff type based on the workflow:
- `task_delegation` - Assigning work to a worker agent
- `context_transfer` - Passing context to continuation session
- `review_request` - Requesting review from another agent
- `escalation` - Escalating issue to higher authority

### Step 2: Gather context data

Collect all information the receiving agent needs:
- Task description
- Relevant identifiers (PR number, issue number, etc.)
- Current progress state
- Constraints or requirements

### Step 3: Build the payload

```json
{
  "handoff_type": "task_delegation",
  "from_agent": "orchestrator",
  "to_agent": "code-reviewer",
  "timestamp": "2025-02-05T10:30:00Z",
  "context": {
    "task": "Review PR changes for security issues",
    "pr_number": 123,
    "repository": "owner/repo",
    "branch": "feature/auth-update",
    "priority": "high",
    "deadline": "2025-02-05T18:00:00Z"
  },
  "session_state": {
    "files_reviewed": [],
    "comments_made": [],
    "blockers_found": []
  },
  "instructions": [
    "Focus on authentication flow changes",
    "Check for SQL injection vulnerabilities",
    "Verify input validation"
  ]
}
```

### Step 4: Validate required fields

Ensure all required fields are present:
- `handoff_type` - Type of handoff
- `from_agent` - Source agent identifier
- `to_agent` - Target agent identifier
- `context` - Task context object

### Step 5: Add timestamps

All datetime fields must use ISO 8601 format:
```
2025-02-05T10:30:00Z
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| handoff_type | string | yes | Type: task_delegation, context_transfer, review_request, escalation |
| from_agent | string | yes | Source agent identifier |
| to_agent | string | yes | Target agent identifier |
| context | object | yes | Task-specific context data |
| session_state | object | no | Current session state to preserve |
| instructions | string[] | no | Specific instructions for target agent |

## Output

| Field | Type | Description |
|-------|------|-------------|
| payload | object | Complete handoff payload |
| valid | boolean | Whether payload passes validation |
| errors | string[] | Any validation errors |

## Example Output

```json
{
  "payload": {
    "handoff_type": "task_delegation",
    "from_agent": "orchestrator",
    "to_agent": "code-reviewer",
    "timestamp": "2025-02-05T10:30:00Z",
    "context": {
      "task": "Review PR #123",
      "pr_number": 123,
      "repository": "owner/repo"
    },
    "session_state": {},
    "instructions": []
  },
  "valid": true,
  "errors": []
}
```

## Handoff Type Templates

### Task Delegation

```json
{
  "handoff_type": "task_delegation",
  "from_agent": "orchestrator",
  "to_agent": "worker-agent",
  "context": {
    "task": "Description of work to do",
    "resources": ["file1.py", "file2.py"],
    "constraints": ["Must not modify API", "Tests must pass"]
  },
  "instructions": ["Step 1", "Step 2", "Step 3"]
}
```

### Review Request

```json
{
  "handoff_type": "review_request",
  "from_agent": "implementer",
  "to_agent": "code-reviewer",
  "context": {
    "pr_number": 123,
    "changes_summary": "Added authentication middleware",
    "areas_of_concern": ["Security", "Performance"]
  }
}
```

### Escalation

```json
{
  "handoff_type": "escalation",
  "from_agent": "worker-agent",
  "to_agent": "orchestrator",
  "context": {
    "original_task": "Fix bug #456",
    "blocker": "Requires database schema change",
    "attempted_solutions": ["Approach A", "Approach B"]
  }
}
```

## Error Handling

### Missing required field

**Cause**: Required field not provided in payload.

**Solution**: Ensure `handoff_type`, `from_agent`, `to_agent`, and `context` are all present.

### Invalid timestamp format

**Cause**: Timestamp not in ISO 8601 format.

**Solution**: Use format `YYYY-MM-DDTHH:MM:SSZ` for all datetime fields.

### Unknown handoff type

**Cause**: Using unrecognized handoff type.

**Solution**: Use one of: `task_delegation`, `context_transfer`, `review_request`, `escalation`.

## Verification

Validate payload before sending:

```bash
# Validate JSON structure
echo "$PAYLOAD" | jq '.' > /dev/null && echo "Valid JSON"

# Check required fields
echo "$PAYLOAD" | jq 'has("handoff_type") and has("from_agent") and has("to_agent") and has("context")'
```
