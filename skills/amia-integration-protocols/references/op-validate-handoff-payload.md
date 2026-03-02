---
name: op-validate-handoff-payload
description: "Validate structure and content of an agent handoff payload"
procedure: support-skill
workflow-instruction: support
---

# Operation: Validate Handoff Payload


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Check JSON validity](#step-1-check-json-validity)
  - [Step 2: Check required fields](#step-2-check-required-fields)
  - [Step 3: Validate field types](#step-3-validate-field-types)
  - [Step 4: Validate handoff type value](#step-4-validate-handoff-type-value)
  - [Step 5: Validate timestamp format (if present)](#step-5-validate-timestamp-format-if-present)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Validation Rules](#validation-rules)
  - [Required Fields](#required-fields)
  - [Optional Fields](#optional-fields)
  - [Recognized Handoff Types](#recognized-handoff-types)
- [Complete Validation Script](#complete-validation-script)
- [Error Handling](#error-handling)
  - [Invalid JSON](#invalid-json)
  - [Missing required field](#missing-required-field)
  - [Invalid field type](#invalid-field-type)
- [Verification](#verification)

## Purpose

Verify that a handoff payload contains all required fields and follows the correct schema before sending to another agent.

## When to Use

- Before sending a handoff to another agent
- When receiving a handoff to verify completeness
- During debugging of handoff failures
- When building handoff automation

## Prerequisites

1. A handoff payload to validate (JSON format)

## Procedure

### Step 1: Check JSON validity

```bash
echo "$PAYLOAD" | jq '.' > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "PASS: Valid JSON"
else
  echo "FAIL: Invalid JSON"
  exit 1
fi
```

### Step 2: Check required fields

Required fields:
- `handoff_type`
- `from_agent`
- `to_agent`
- `context`

```bash
REQUIRED='["handoff_type", "from_agent", "to_agent", "context"]'
MISSING=$(echo "$PAYLOAD" | jq --argjson req "$REQUIRED" '
  $req - keys | if length > 0 then . else empty end
')

if [ -z "$MISSING" ]; then
  echo "PASS: All required fields present"
else
  echo "FAIL: Missing fields: $MISSING"
fi
```

### Step 3: Validate field types

```bash
# Check that handoff_type is a string
TYPE_CHECK=$(echo "$PAYLOAD" | jq '.handoff_type | type == "string"')
if [ "$TYPE_CHECK" = "true" ]; then
  echo "PASS: handoff_type is string"
else
  echo "FAIL: handoff_type must be string"
fi

# Check that context is an object
CONTEXT_CHECK=$(echo "$PAYLOAD" | jq '.context | type == "object"')
if [ "$CONTEXT_CHECK" = "true" ]; then
  echo "PASS: context is object"
else
  echo "FAIL: context must be object"
fi
```

### Step 4: Validate handoff type value

```bash
VALID_TYPES='["task_delegation", "context_transfer", "review_request", "escalation"]'
TYPE_VALID=$(echo "$PAYLOAD" | jq --argjson valid "$VALID_TYPES" '
  .handoff_type as $t | $valid | index($t) != null
')

if [ "$TYPE_VALID" = "true" ]; then
  echo "PASS: handoff_type is valid"
else
  echo "FAIL: handoff_type must be one of: $VALID_TYPES"
fi
```

### Step 5: Validate timestamp format (if present)

```bash
# Check timestamp format (ISO 8601)
if echo "$PAYLOAD" | jq -e '.timestamp' > /dev/null 2>&1; then
  TS=$(echo "$PAYLOAD" | jq -r '.timestamp')
  if [[ "$TS" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
    echo "PASS: timestamp format valid"
  else
    echo "FAIL: timestamp must be ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)"
  fi
fi
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| payload | object | yes | The handoff payload to validate |
| strict | boolean | no | Whether to enforce optional field validation |

## Output

| Field | Type | Description |
|-------|------|-------------|
| valid | boolean | Whether payload passes all checks |
| errors | string[] | List of validation errors |
| warnings | string[] | List of validation warnings |
| fields_checked | number | Count of fields validated |

## Example Output

```json
{
  "valid": false,
  "errors": [
    "Missing required field: to_agent",
    "handoff_type 'custom' is not a recognized type"
  ],
  "warnings": [
    "timestamp field not present (recommended)"
  ],
  "fields_checked": 4
}
```

## Validation Rules

### Required Fields

| Field | Type | Validation |
|-------|------|------------|
| handoff_type | string | Must be recognized type |
| from_agent | string | Non-empty string |
| to_agent | string | Non-empty string |
| context | object | Must be JSON object |

### Optional Fields

| Field | Type | Validation |
|-------|------|------------|
| timestamp | string | ISO 8601 format |
| session_state | object | Must be JSON object |
| instructions | array | Array of strings |
| priority | string | low, normal, high, urgent |

### Recognized Handoff Types

- `task_delegation` - Work assignment
- `context_transfer` - Session continuation
- `review_request` - Review request
- `escalation` - Issue escalation

## Complete Validation Script

```bash
#!/bin/bash
# validate_handoff.sh

PAYLOAD="$1"

echo "=== Handoff Payload Validation ==="

# Check JSON validity
if ! echo "$PAYLOAD" | jq '.' > /dev/null 2>&1; then
  echo "FATAL: Invalid JSON"
  exit 1
fi

ERRORS=()

# Check required fields
for field in handoff_type from_agent to_agent context; do
  if ! echo "$PAYLOAD" | jq -e ".$field" > /dev/null 2>&1; then
    ERRORS+=("Missing required field: $field")
  fi
done

# Check handoff_type value
HT=$(echo "$PAYLOAD" | jq -r '.handoff_type // empty')
case "$HT" in
  task_delegation|context_transfer|review_request|escalation) ;;
  *) ERRORS+=("Invalid handoff_type: $HT") ;;
esac

# Check context is object
if echo "$PAYLOAD" | jq -e '.context | type != "object"' > /dev/null 2>&1; then
  ERRORS+=("context must be an object")
fi

# Report results
if [ ${#ERRORS[@]} -eq 0 ]; then
  echo "VALID: Payload passes all checks"
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

**Cause**: Payload is not valid JSON.

**Solution**: Check for syntax errors, missing quotes, trailing commas.

### Missing required field

**Cause**: One of the required fields is absent.

**Solution**: Add the missing field to the payload.

### Invalid field type

**Cause**: Field has wrong type (e.g., string instead of object).

**Solution**: Correct the field type in the payload.

## Verification

After validation, the payload should be safe to send:

```bash
# Run validation
./validate_handoff.sh "$PAYLOAD"
```

If valid (exit code 0), proceed with handoff by sending the payload as a message using the `agent-messaging` skill. The payload contents become the message content. Verify delivery by checking the `agent-messaging` skill send confirmation.
