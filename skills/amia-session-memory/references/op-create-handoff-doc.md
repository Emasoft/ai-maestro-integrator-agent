# Operation: Create Handoff Document

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Create handoff directory](#step-1-create-handoff-directory)
  - [Step 2: Archive existing handoff (if present)](#step-2-archive-existing-handoff-if-present)
  - [Step 3: Prepare handoff content](#step-3-prepare-handoff-content)
  - [Step 4: Create handoff document](#step-4-create-handoff-document)
- [Task](#task)
- [Progress](#progress)
- [Findings](#findings)
  - [Security Issues Found](#security-issues-found)
  - [Code Quality Notes](#code-quality-notes)
- [Blockers](#blockers)
- [Next Steps](#next-steps)
- [Context Links](#context-links)
- [Session Context](#session-context)
  - [Step 5: Verify handoff was created](#step-5-verify-handoff-was-created)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Handoff Document Template](#handoff-document-template)
- [Task](#task)
- [Progress](#progress)
- [Findings](#findings)
- [Blockers](#blockers)
- [Next Steps](#next-steps)
- [Context Links](#context-links)
- [Session Context](#session-context)
- [Error Handling](#error-handling)
  - [Directory creation fails](#directory-creation-fails)
  - [Archive fails](#archive-fails)
  - [Write fails](#write-fails)
- [Complete Script](#complete-script)
- [Task](#task)
- [Progress](#progress)
- [Blockers](#blockers)
- [Next Steps](#next-steps)
- [Context Links](#context-links)
- [Verification](#verification)

## Purpose

Create a structured handoff document that captures the current state of work, enabling another session to continue seamlessly.

## When to Use

- Before ending a session with incomplete work
- When context compaction is imminent
- When handing off work to another agent
- Before taking a break from extended work

## Prerequisites

1. `$CLAUDE_PROJECT_DIR` environment variable set
2. Write access to handoff directory
3. Clear understanding of current work state

## Procedure

### Step 1: Create handoff directory

```bash
HANDOFF_DIR="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"
mkdir -p "$HANDOFF_DIR"
```

### Step 2: Archive existing handoff (if present)

```bash
CURRENT_HANDOFF="$HANDOFF_DIR/current.md"
if [ -f "$CURRENT_HANDOFF" ]; then
  # Archive with timestamp
  ARCHIVE_TS=$(date +%Y%m%d_%H%M%S)
  mkdir -p "$HANDOFF_DIR/archive"
  mv "$CURRENT_HANDOFF" "$HANDOFF_DIR/archive/handoff_$ARCHIVE_TS.md"
  echo "Archived previous handoff"
fi
```

### Step 3: Prepare handoff content

```bash
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
AGENT="amia-main"
TASK="Review PR #123 for security issues"
PROGRESS="Reviewed auth module, found 2 issues"
BLOCKERS="None"
NEXT_STEPS="Review middleware changes"
PR_URL="https://github.com/owner/repo/pull/123"
```

### Step 4: Create handoff document

```bash
cat > "$CURRENT_HANDOFF" << EOF
# AMIA Integration Handoff

**Created**: $TIMESTAMP
**Last Updated**: $TIMESTAMP
**Agent**: $AGENT

## Task

$TASK

## Progress

- [x] Fetched PR details
- [x] Analyzed diff
- [x] Reviewed auth module
- [ ] Review middleware
- [ ] Post review comments

## Findings

### Security Issues Found
1. Missing input validation in auth/login.py:42
2. SQL query concatenation in auth/users.py:88

### Code Quality Notes
- Error handling is inconsistent across modules
- Some functions exceed recommended complexity

## Blockers

$BLOCKERS

## Next Steps

1. $NEXT_STEPS
2. Check for SQL injection vulnerabilities
3. Post review comments with findings

## Context Links

- PR: $PR_URL
- Issue: (if applicable)
- CI Run: (if applicable)

## Session Context

This handoff was created because: [session ending / context compaction / deliberate pause]

To resume:
1. Load this handoff document
2. Review the Progress section
3. Continue from Next Steps

---
*Auto-generated AMIA handoff document*
EOF

echo "Created handoff document at $CURRENT_HANDOFF"
```

### Step 5: Verify handoff was created

```bash
if [ -f "$CURRENT_HANDOFF" ]; then
  echo "Handoff created successfully"
  # Display summary
  head -20 "$CURRENT_HANDOFF"
else
  echo "ERROR: Failed to create handoff"
  exit 1
fi
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task | string | yes | Description of the task |
| progress | string[] | yes | List of progress items (with completion status) |
| findings | string | no | Findings or results discovered |
| blockers | string[] | no | Blocking issues |
| next_steps | string[] | yes | Steps to continue |
| context_links | object | no | URLs for PR, issue, CI, etc. |
| reason | string | no | Why handoff is being created |

## Output

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether handoff was created |
| path | string | Path to handoff document |
| archived_previous | boolean | Whether previous handoff was archived |
| timestamp | string | Creation timestamp |

## Example Output

```json
{
  "success": true,
  "path": "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md",
  "archived_previous": true,
  "timestamp": "2025-02-05T14:30:00Z"
}
```

## Handoff Document Template

```markdown
# AMIA Integration Handoff

**Created**: [ISO timestamp]
**Last Updated**: [ISO timestamp]
**Agent**: [agent-id]

## Task

[Clear description of what was being worked on]

## Progress

- [x] Completed step 1
- [x] Completed step 2
- [ ] Pending step 3
- [ ] Pending step 4

## Findings

[Any discoveries, issues found, or results]

## Blockers

[Blocking issues or "None"]

## Next Steps

1. [First thing to do when resuming]
2. [Second thing]
3. [Third thing]

## Context Links

- PR: [URL]
- Issue: [URL]
- CI Run: [URL]

## Session Context

[Why handoff was created and how to resume]
```

## Error Handling

### Directory creation fails

**Cause**: No write permission to CLAUDE_PROJECT_DIR.

**Solution**: Verify path is correct and writable.

### Archive fails

**Cause**: Cannot move existing handoff.

**Solution**: Check archive directory permissions.

### Write fails

**Cause**: Disk full or permission denied.

**Solution**: Check disk space, verify permissions.

## Complete Script

```bash
#!/bin/bash
# create_handoff_doc.sh

TASK="$1"
NEXT_STEPS="$2"
PR_URL="$3"

HANDOFF_DIR="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"
CURRENT="$HANDOFF_DIR/current.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Ensure directory exists
mkdir -p "$HANDOFF_DIR"
mkdir -p "$HANDOFF_DIR/archive"

# Archive existing
if [ -f "$CURRENT" ]; then
  mv "$CURRENT" "$HANDOFF_DIR/archive/handoff_$(date +%Y%m%d_%H%M%S).md"
fi

# Create new handoff
cat > "$CURRENT" << EOF
# AMIA Integration Handoff

**Created**: $TIMESTAMP
**Last Updated**: $TIMESTAMP
**Agent**: amia-main

## Task

$TASK

## Progress

(To be filled)

## Blockers

None

## Next Steps

$NEXT_STEPS

## Context Links

- PR: $PR_URL

---
*Auto-generated AMIA handoff document*
EOF

echo "Handoff created: $CURRENT"
```

## Verification

After creation:

```bash
# Verify handoff exists and is readable
if [ -f "$CURRENT_HANDOFF" ]; then
  echo "=== Handoff Summary ==="
  grep -E "^##|^-" "$CURRENT_HANDOFF" | head -20
else
  echo "ERROR: Handoff not found"
fi
```
