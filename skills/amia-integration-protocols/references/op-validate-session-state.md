---
name: op-validate-session-state
description: "Validate session state structure and content before use"
procedure: support-skill
workflow-instruction: support
---

# Operation: Validate Session State


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Check JSON validity](#step-1-check-json-validity)
  - [Step 2: Check required fields](#step-2-check-required-fields)
  - [Step 3: Validate timestamp formats](#step-3-validate-timestamp-formats)
  - [Step 4: Validate array fields](#step-4-validate-array-fields)
  - [Step 5: Check for staleness](#step-5-check-for-staleness)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Validation Rules](#validation-rules)
  - [Required Fields](#required-fields)
  - [Optional Fields](#optional-fields)
  - [Checkpoint Object](#checkpoint-object)
- [Complete Validation Script](#complete-validation-script)
- [Error Handling](#error-handling)
  - [Invalid JSON](#invalid-json)
  - [Missing required field](#missing-required-field)
  - [Stale state](#stale-state)
- [Verification](#verification)

## Purpose

Verify that a session state object is properly structured and contains valid data before using it to resume work.

## When to Use

- When loading session state from storage
- Before resuming work from a previous session
- When receiving state from another agent
- During debugging of state-related issues

## Prerequisites

1. Session state object to validate (JSON format)

## Procedure

### Step 1: Check JSON validity

```bash
echo "$STATE" | jq '.' > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "PASS: Valid JSON"
else
  echo "FAIL: Invalid JSON"
  exit 1
fi
```

### Step 2: Check required fields

```bash
REQUIRED='["session_id", "started_at", "current_phase"]'

for field in session_id started_at current_phase; do
  if echo "$STATE" | jq -e ".$field" > /dev/null 2>&1; then
    echo "PASS: $field present"
  else
    echo "FAIL: Missing required field: $field"
  fi
done
```

### Step 3: Validate timestamp formats

```bash
# Validate started_at
STARTED=$(echo "$STATE" | jq -r '.started_at')
if [[ "$STARTED" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
  echo "PASS: started_at format valid"
else
  echo "FAIL: started_at must be ISO 8601 format"
fi

# Validate last_updated if present
if echo "$STATE" | jq -e '.last_updated' > /dev/null 2>&1; then
  UPDATED=$(echo "$STATE" | jq -r '.last_updated')
  if [[ "$UPDATED" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
    echo "PASS: last_updated format valid"
  else
    echo "FAIL: last_updated must be ISO 8601 format"
  fi
fi
```

### Step 4: Validate array fields

```bash
# Check completed_tasks is array (if present)
if echo "$STATE" | jq -e '.completed_tasks' > /dev/null 2>&1; then
  if echo "$STATE" | jq -e '.completed_tasks | type == "array"' > /dev/null 2>&1; then
    echo "PASS: completed_tasks is array"
  else
    echo "FAIL: completed_tasks must be array"
  fi
fi

# Check pending_tasks is array (if present)
if echo "$STATE" | jq -e '.pending_tasks' > /dev/null 2>&1; then
  if echo "$STATE" | jq -e '.pending_tasks | type == "array"' > /dev/null 2>&1; then
    echo "PASS: pending_tasks is array"
  else
    echo "FAIL: pending_tasks must be array"
  fi
fi
```

### Step 5: Check for staleness

```bash
# Check if state is older than 7 days
if echo "$STATE" | jq -e '.last_updated // .started_at' > /dev/null 2>&1; then
  LAST_TS=$(echo "$STATE" | jq -r '.last_updated // .started_at')
  LAST_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$LAST_TS" "+%s" 2>/dev/null || date -d "$LAST_TS" "+%s")
  NOW_EPOCH=$(date "+%s")
  AGE_DAYS=$(( (NOW_EPOCH - LAST_EPOCH) / 86400 ))

  if [ $AGE_DAYS -gt 7 ]; then
    echo "WARN: State is $AGE_DAYS days old - may be stale"
  else
    echo "PASS: State age ($AGE_DAYS days) is acceptable"
  fi
fi
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| state | object | yes | Session state object to validate |
| max_age_days | number | no | Maximum acceptable age (default: 7) |
| strict | boolean | no | Whether to treat warnings as errors |

## Output

| Field | Type | Description |
|-------|------|-------------|
| valid | boolean | Whether state passes all required checks |
| errors | string[] | List of validation errors |
| warnings | string[] | List of validation warnings |
| age_days | number | Age of state in days |

## Example Output

```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "State is 3 days old"
  ],
  "age_days": 3
}
```

## Validation Rules

### Required Fields

| Field | Type | Validation |
|-------|------|------------|
| session_id | string | Non-empty, starts with "sess_" |
| started_at | string | ISO 8601 format |
| current_phase | string | Non-empty |

### Optional Fields

| Field | Type | Validation |
|-------|------|------------|
| last_updated | string | ISO 8601 format, >= started_at |
| completed_tasks | array | Array of strings |
| pending_tasks | array | Array of strings |
| accumulated_data | object | Valid JSON object |
| checkpoints | array | Array of checkpoint objects |

### Checkpoint Object

```json
{
  "phase": "string",
  "completed_at": "ISO 8601 timestamp"
}
```

## Complete Validation Script

```bash
#!/bin/bash
# validate_session_state.sh

STATE="$1"
MAX_AGE_DAYS="${2:-7}"

echo "=== Session State Validation ==="

ERRORS=()
WARNINGS=()

# Check JSON validity
if ! echo "$STATE" | jq '.' > /dev/null 2>&1; then
  echo "FATAL: Invalid JSON"
  exit 1
fi

# Check required fields
for field in session_id started_at current_phase; do
  if ! echo "$STATE" | jq -e ".$field" > /dev/null 2>&1; then
    ERRORS+=("Missing required field: $field")
  fi
done

# Check session_id format
SID=$(echo "$STATE" | jq -r '.session_id // empty')
if [[ ! "$SID" =~ ^sess_ ]]; then
  WARNINGS+=("session_id should start with 'sess_'")
fi

# Check timestamp format
for ts_field in started_at last_updated; do
  TS=$(echo "$STATE" | jq -r ".$ts_field // empty")
  if [ -n "$TS" ] && [[ ! "$TS" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
    ERRORS+=("$ts_field must be ISO 8601 format")
  fi
done

# Check array types
for arr_field in completed_tasks pending_tasks checkpoints; do
  if echo "$STATE" | jq -e ".$arr_field" > /dev/null 2>&1; then
    if ! echo "$STATE" | jq -e ".$arr_field | type == \"array\"" > /dev/null 2>&1; then
      ERRORS+=("$arr_field must be an array")
    fi
  fi
done

# Report results
if [ ${#ERRORS[@]} -eq 0 ]; then
  echo "VALID: State passes all required checks"
  if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo "Warnings:"
    for warn in "${WARNINGS[@]}"; do
      echo "  - $warn"
    done
  fi
  exit 0
else
  echo "INVALID: ${#ERRORS[@]} error(s) found:"
  for err in "${ERRORS[@]}"; do
    echo "  - $err"
  done
  exit 1
fi
```

## Error Handling

### Invalid JSON

**Cause**: State is not valid JSON.

**Solution**: Check for syntax errors in stored state.

### Missing required field

**Cause**: Required field is absent.

**Solution**: Reconstruct state with required fields.

### Stale state

**Cause**: State is older than acceptable threshold.

**Solution**: Re-validate against current system state before using.

## Verification

After validation:

```bash
# If valid, proceed to use state
if ./validate_session_state.sh "$STATE"; then
  # Extract current phase
  PHASE=$(echo "$STATE" | jq -r '.current_phase')
  echo "Resuming from phase: $PHASE"

  # Load pending tasks
  PENDING=$(echo "$STATE" | jq -r '.pending_tasks[]')
  echo "Pending tasks: $PENDING"
fi
```
