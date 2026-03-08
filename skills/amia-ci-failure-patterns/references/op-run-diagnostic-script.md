# Operation: Run Diagnostic Script

## Contents

- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Procedure](#procedure)
  - [Step 1: Verify Script Availability](#step-1-verify-script-availability)
  - [Step 2: Run the Diagnostic Script](#step-2-run-the-diagnostic-script)
  - [Step 3: Interpret the Output](#step-3-interpret-the-output)
  - [Step 4: Handle Multiple Patterns](#step-4-handle-multiple-patterns)
- [Output](#output)
- [JSON Output Format](#json-output-format)
- [Verification](#verification)
- [Error Handling](#error-handling)
  - [Script not found](#script-not-found)
  - [No patterns detected](#no-patterns-detected)
  - [Invalid log file](#invalid-log-file)
- [Next Operation](#next-operation)

## Purpose

This operation runs the `amia_diagnose_ci_failure.py` script to automatically analyze CI failure logs and identify known failure patterns.

## Prerequisites

- Python 3.8+ installed
- CI failure logs collected (see [op-collect-ci-logs.md](op-collect-ci-logs.md))
- Script located at `scripts/amia_diagnose_ci_failure.py`

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| log_file | string | Yes* | Path to CI log file |
| stdin | boolean | No | Read from stdin instead of file |
| json | boolean | No | Output results as JSON |

*Either log_file or stdin is required.

## Procedure

### Step 1: Verify Script Availability

```bash
# Check script exists
test -f scripts/amia_diagnose_ci_failure.py && echo "Script found" || echo "Script missing"

# Verify Python is available
python3 --version
```

### Step 2: Run the Diagnostic Script

**From log file:**

```bash
python3 scripts/amia_diagnose_ci_failure.py --log-file ci.log
```

**From stdin (for piping):**

```bash
cat ci.log | python3 scripts/amia_diagnose_ci_failure.py --stdin
```

**With JSON output (for programmatic use):**

```bash
python3 scripts/amia_diagnose_ci_failure.py --log-file ci.log --json > diagnosis.json
```

### Step 3: Interpret the Output

The script outputs:

1. **Pattern Category** - Which failure pattern category was detected
2. **Confidence Level** - How confident the diagnosis is (high/medium/low)
3. **Suggested Fix** - Brief description of the recommended fix
4. **Reference Document** - Which reference document to read for details

Example output:

```
=== CI Failure Diagnosis ===
Pattern Category: Cross-Platform
Confidence: High
Issue: Hardcoded temp path /tmp detected
Suggested Fix: Use tempfile.gettempdir() for cross-platform compatibility
Reference: references/cross-platform-patterns.md (Section 1.1)
```

### Step 4: Handle Multiple Patterns

If multiple patterns are detected, the script lists them by confidence:

```
=== CI Failure Diagnosis ===
Detected Patterns (ordered by confidence):

1. [HIGH] Cross-Platform - Temp path issue
   Fix: Use tempfile.gettempdir()
   Reference: cross-platform-patterns.md

2. [MEDIUM] Exit Code - Non-zero exit not handled
   Fix: Add explicit exit code handling
   Reference: exit-code-patterns.md
```

## Output

| Output | Type | Description |
|--------|------|-------------|
| stdout | text | Human-readable diagnosis |
| diagnosis.json | file | JSON-formatted diagnosis (with --json flag) |
| exit code 0 | int | Pattern(s) identified |
| exit code 1 | int | No pattern identified |
| exit code 2 | int | Error reading input |

## JSON Output Format

When using `--json`:

```json
{
  "patterns_detected": [
    {
      "category": "cross-platform",
      "confidence": "high",
      "issue": "Hardcoded temp path /tmp detected",
      "suggested_fix": "Use tempfile.gettempdir()",
      "reference": "cross-platform-patterns.md",
      "section": "1.1",
      "line_numbers": [42, 87, 123]
    }
  ],
  "log_file": "ci.log",
  "analysis_timestamp": "2024-01-15T10:30:00Z"
}
```

## Verification

Verify the diagnosis is actionable:

```bash
# Check script ran successfully
echo $?  # Should be 0 if patterns found

# Verify JSON output is valid
cat diagnosis.json | python3 -m json.tool > /dev/null && echo "Valid JSON"
```

## Error Handling

### Script not found

Ensure you are in the correct directory or use absolute path:

```bash
# From skill directory
python3 scripts/amia_diagnose_ci_failure.py --log-file ci.log

# Or use absolute path
python3 /path/to/skill/scripts/amia_diagnose_ci_failure.py --log-file ci.log
```

### No patterns detected

If exit code is 1 (no patterns), proceed to:

- [op-identify-failure-pattern.md](op-identify-failure-pattern.md) - Manual decision tree analysis

### Invalid log file

Ensure the log file is a valid GitHub Actions log:

```bash
# Check for GitHub Actions markers
grep "##\[group\]" ci.log || echo "May not be a valid GitHub Actions log"
```

## Next Operation

Based on diagnosis results:

- If pattern identified: [op-apply-pattern-fix.md](op-apply-pattern-fix.md)
- If no pattern identified: [op-identify-failure-pattern.md](op-identify-failure-pattern.md)
