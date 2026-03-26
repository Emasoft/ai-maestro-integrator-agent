# Operation: Detect Platform Issues

## Table of Contents

- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Inputs](#inputs)
- [Procedure](#procedure)
  - [Step 1: Verify Script Availability](#step-1-verify-script-availability)
  - [Step 2: Run the Platform Issue Scanner](#step-2-run-the-platform-issue-scanner)
  - [Step 3: Interpret the Results](#step-3-interpret-the-results)
  - [Step 4: Review Findings](#step-4-review-findings)
  - [Step 5: Prioritize Fixes](#step-5-prioritize-fixes)
- [Output](#output)
- [JSON Output Format](#json-output-format)
- [Common Patterns Detected](#common-patterns-detected)
  - [Hardcoded Paths](#hardcoded-paths)
  - [Path Separators](#path-separators)
  - [OS-Specific Commands](#os-specific-commands)
  - [Environment Variables](#environment-variables)
- [Verification](#verification)
- [Error Handling](#error-handling)
  - [Permission denied](#permission-denied)
  - [Unsupported file type](#unsupported-file-type)
- [When to Use This Operation](#when-to-use-this-operation)
- [Next Operations](#next-operations)

## Purpose

This operation runs the `amia_detect_platform_issue.py` script to proactively scan source code for patterns that may cause CI failures on different platforms (Windows, Linux, macOS).

## Prerequisites

- Python 3.8+ installed
- Script located at `scripts/amia_detect_platform_issue.py`
- Source code directory to scan

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| path | string | Yes | Directory or file to scan |
| extensions | list | No | File extensions to scan (default: .py, .js, .ts, .sh, .ps1) |
| json | boolean | No | Output results as JSON |

## Procedure

### Step 1: Verify Script Availability

```bash
# Check script exists
test -f scripts/amia_detect_platform_issue.py && echo "Script found" || echo "Script missing"
```

### Step 2: Run the Platform Issue Scanner

**Scan entire project:**

```bash
python3 scripts/amia_detect_platform_issue.py --path .
```

**Scan specific directory:**

```bash
python3 scripts/amia_detect_platform_issue.py --path src/
```

**Scan specific file types:**

```bash
python3 scripts/amia_detect_platform_issue.py --path . --extensions .py .sh
```

**Output as JSON:**

```bash
python3 scripts/amia_detect_platform_issue.py --path . --json > platform-issues.json
```

### Step 3: Interpret the Results

The script scans for these pattern categories:

| Pattern | Description | Risk Level |
|---------|-------------|------------|
| Hardcoded paths | /tmp, /home, C:\\ | High |
| Path separators | Literal `\` or `/` in paths | Medium |
| OS-specific commands | `rm`, `cp` vs PowerShell equivalents | Medium |
| Line endings | CRLF assumptions | Low |
| Case sensitivity | Mixed case imports/paths | Medium |
| Environment variables | $HOME, %USERPROFILE% | Medium |

### Step 4: Review Findings

Example output:

```
=== Platform Issue Scan ===
Scanned: 47 files
Issues found: 12

HIGH RISK:
  src/utils/temp.py:23 - Hardcoded path: /tmp/cache
  src/utils/temp.py:45 - Hardcoded path: /tmp/output

MEDIUM RISK:
  scripts/build.sh:12 - OS-specific command: rm -rf
  src/config.py:8 - Path separator: data/config.json

LOW RISK:
  tests/test_io.py:5 - Environment variable: $HOME

Recommendations:
1. Replace /tmp with tempfile.gettempdir()
2. Use os.path.join() for path construction
3. Use shutil.rmtree() instead of rm -rf
```

### Step 5: Prioritize Fixes

Address issues in this order:

1. **High Risk** - Will likely cause CI failures
2. **Medium Risk** - May cause failures depending on CI configuration
3. **Low Risk** - Edge cases, fix if time permits

## Output

| Output | Type | Description |
|--------|------|-------------|
| stdout | text | Human-readable scan results |
| platform-issues.json | file | JSON-formatted results (with --json flag) |
| exit code 0 | int | Scan completed (issues may exist) |
| exit code 1 | int | Error during scan |

## JSON Output Format

```json
{
  "scan_path": ".",
  "files_scanned": 47,
  "issues": [
    {
      "file": "src/utils/temp.py",
      "line": 23,
      "risk": "high",
      "pattern": "hardcoded_path",
      "code": "output_path = \"/tmp/cache\"",
      "recommendation": "Use tempfile.gettempdir()"
    }
  ],
  "summary": {
    "high": 2,
    "medium": 2,
    "low": 1
  },
  "scan_timestamp": "2024-01-15T10:30:00Z"
}
```

## Common Patterns Detected

### Hardcoded Paths

```python
# DETECTED
path = "/tmp/output.txt"
path = "C:\\Users\\build\\cache"
path = "/home/runner/work"

# RECOMMENDED
import tempfile
path = os.path.join(tempfile.gettempdir(), "output.txt")
```

### Path Separators

```python
# DETECTED
path = "src/utils/helper.py"
path = "data\\config.json"

# RECOMMENDED
path = os.path.join("src", "utils", "helper.py")
# Or use pathlib
path = Path("src") / "utils" / "helper.py"
```

### OS-Specific Commands

```bash
# DETECTED
rm -rf build/
cp -r src/ dist/

# RECOMMENDED (in Python)
shutil.rmtree("build")
shutil.copytree("src", "dist")
```

### Environment Variables

```python
# DETECTED
home = os.environ["HOME"]  # Fails on Windows

# RECOMMENDED
home = os.path.expanduser("~")
# Or
home = Path.home()
```

## Verification

After fixing detected issues:

```bash
# Re-run scanner to verify fixes
python3 scripts/amia_detect_platform_issue.py --path .

# Should show fewer or no issues
```

## Error Handling

### Permission denied

If scanner cannot access files:

```bash
# Check file permissions
ls -la <path>

# Run with appropriate permissions
sudo python3 scripts/amia_detect_platform_issue.py --path .
```

### Unsupported file type

The scanner may skip binary or unsupported files:

```bash
# Specify only text file extensions
python3 scripts/amia_detect_platform_issue.py --path . --extensions .py .js .ts .sh .yml
```

## When to Use This Operation

Run this scanner:

1. **Before submitting PR** - Catch issues before CI runs
2. **After CI failure** - Find related platform issues
3. **During code review** - Verify cross-platform compatibility
4. **Periodically** - As part of code quality checks

## Next Operations

After detecting platform issues:

- [op-apply-pattern-fix.md](op-apply-pattern-fix.md) - Apply fixes for detected issues
- [op-verify-fix-locally.md](op-verify-fix-locally.md) - Verify fixes work on all platforms
