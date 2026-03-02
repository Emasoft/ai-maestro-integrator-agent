---
name: ci-security-scanning
description: "How to configure CodeQL analysis, Bandit severity filtering, and scheduled weekly security scans in GitHub Actions."
---

# CI Security Scanning

## Table of Contents

- 6.1 CodeQL Setup with Language Matrix
  - 6.1.1 What CodeQL does and which languages it supports
  - 6.1.2 Configuring the language matrix
  - 6.1.3 Query suites: `security-extended` and `security-and-quality`
  - 6.1.4 Category-scoped analysis for multi-language repositories
- 6.2 Scheduled Security Scans
  - 6.2.1 Why schedule weekly scans in addition to PR scans
  - 6.2.2 Cron expression for weekly Monday scans
  - 6.2.3 Combining scheduled and event-triggered scans in one workflow
- 6.3 Bandit for Python Security Analysis
  - 6.3.1 What Bandit checks and how severity levels work
  - 6.3.2 Severity and confidence filtering with `-ll -ii`
  - 6.3.3 Bandit exit code handling
  - 6.3.4 Programmatic JSON report analysis
- 6.4 Security-Specific Workflow Permissions
  - 6.4.1 The `security-events: write` permission
  - 6.4.2 Minimal permission set for security scanning workflows
- 6.5 Timeout Guards for Security Scanners
  - 6.5.1 Why security scanners need explicit timeouts
  - 6.5.2 Recommended timeout values
- 6.6 Complete YAML Example: CodeQL + Bandit + Gate Job
  - 6.6.1 Full workflow definition
  - 6.6.2 Walkthrough of each section

---

## 6.1 CodeQL Setup with Language Matrix

### 6.1.1 What CodeQL Does and Which Languages It Supports

CodeQL is GitHub's static analysis engine. It compiles your source code into a
queryable database, then runs security queries against that database to find
vulnerabilities like SQL injection, cross-site scripting, path traversal, and
insecure deserialization.

Supported languages (as of early 2026):

| Language | Build required | Notes |
|----------|---------------|-------|
| Python | No | Interpreted, no build step needed |
| JavaScript | No | Interpreted, no build step needed |
| TypeScript | No | Analyzed as JavaScript |
| Go | Yes | Uses `autobuild` or manual build |
| Java | Yes | Uses `autobuild` or manual build |
| Kotlin | Yes | Analyzed alongside Java |
| C/C++ | Yes | Uses `autobuild` or manual build |
| C# | Yes | Uses `autobuild` or manual build |
| Ruby | No | Interpreted |
| Swift | Yes | macOS runner recommended |

### 6.1.2 Configuring the Language Matrix

Use a matrix strategy to analyze multiple languages in parallel:

```yaml
strategy:
  fail-fast: false
  matrix:
    language: ["python", "javascript"]
    # Add other languages as needed: "go", "java", "csharp", "cpp", "ruby"
```

Each matrix entry creates a separate analysis job that runs independently.

### 6.1.3 Query Suites: `security-extended` and `security-and-quality`

CodeQL offers three query suites with increasing scope:

| Suite | What it finds | Use when |
|-------|--------------|----------|
| `default` | High-confidence security vulnerabilities | Minimal false positives wanted |
| `security-extended` | Default + medium-confidence security findings | Balanced security coverage |
| `security-and-quality` | Extended + code quality issues | Maximum coverage (more false positives) |

Configure the suite in the `init` step:

```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v3
  with:
    languages: ${{ matrix.language }}
    queries: security-extended
```

### 6.1.4 Category-Scoped Analysis for Multi-Language Repositories

When analyzing multiple languages, each analysis must be uploaded with a unique
category to prevent results from overwriting each other:

```yaml
- name: Perform CodeQL analysis
  uses: github/codeql-action/analyze@v3
  with:
    category: "/language:${{ matrix.language }}"
```

The category string is arbitrary but must be unique per analysis. Using the
`/language:` prefix is the conventional pattern.

---

## 6.2 Scheduled Security Scans

### 6.2.1 Why Schedule Weekly Scans in Addition to PR Scans

PR-triggered scans catch vulnerabilities in new code. But security databases
are updated continuously with newly discovered vulnerabilities in existing
patterns. A weekly scan re-analyzes the entire codebase against the latest
vulnerability database, catching issues that did not exist when the code was
originally written.

### 6.2.2 Cron Expression for Weekly Monday Scans

```yaml
on:
  schedule:
    - cron: "0 0 * * 1"
```

This runs every Monday at 00:00 UTC. The cron expression fields are:
- Minute: 0
- Hour: 0
- Day of month: * (any)
- Month: * (any)
- Day of week: 1 (Monday)

### 6.2.3 Combining Scheduled and Event-Triggered Scans in One Workflow

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 0 * * 1"
```

The same workflow definition runs on pushes, pull requests, and the weekly
schedule. The `github.event_name` context variable can differentiate the trigger
if needed:

```yaml
- name: Extra deep scan on schedule
  if: github.event_name == 'schedule'
  run: echo "Running extended analysis"
```

---

## 6.3 Bandit for Python Security Analysis

### 6.3.1 What Bandit Checks and How Severity Levels Work

Bandit is a Python-specific static analysis tool that finds common security
issues in Python code. It checks for:

- Use of `eval()`, `exec()`, `pickle.loads()` (code injection)
- Hardcoded passwords and secret keys
- Use of insecure hash functions (MD5, SHA1 for security)
- SQL injection via string formatting
- Insecure SSL/TLS configurations
- Subprocess calls with `shell=True`

Each finding has a severity (LOW, MEDIUM, HIGH) and a confidence (LOW, MEDIUM, HIGH).

### 6.3.2 Severity and Confidence Filtering with `-ll -ii`

The `-ll` flag sets the minimum severity to MEDIUM (skips LOW severity).
The `-ii` flag sets the minimum confidence to MEDIUM (skips LOW confidence).

```bash
bandit -r src/ -ll -ii -f json -o bandit-report.json
```

This reports only findings that are at least MEDIUM severity AND at least
MEDIUM confidence, reducing noise from low-priority findings.

Flag reference:

| Flag | Meaning |
|------|---------|
| `-l` | Show LOW severity and above (all findings) |
| `-ll` | Show MEDIUM severity and above |
| `-lll` | Show HIGH severity only |
| `-i` | Show LOW confidence and above (all findings) |
| `-ii` | Show MEDIUM confidence and above |
| `-iii` | Show HIGH confidence only |

### 6.3.3 Bandit Exit Code Handling

Bandit exit codes:

| Exit code | Meaning |
|-----------|---------|
| 0 | No findings at the specified severity/confidence |
| 1 | Findings detected at the specified severity/confidence |
| 2 | Bandit encountered an error (invalid config, file not found, etc.) |

A finding (exit code 1) is expected behavior -- it means Bandit found something
to report. Exit code 2 indicates a scanner error that should always fail the job.

To differentiate in a workflow step:

```bash
bandit -r src/ -ll -ii -f json -o bandit-report.json || exit_code=$?
if [[ "${exit_code:-0}" -eq 2 ]]; then
  echo "Bandit encountered an error"
  exit 2
fi
# Exit code 0 or 1: Bandit ran successfully (may or may not have findings)
```

### 6.3.4 Programmatic JSON Report Analysis

After Bandit produces a JSON report, you can programmatically decide whether
to fail the job based on severity:

```bash
# Count HIGH severity findings
high_count=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' bandit-report.json)

# Report all findings to the summary
echo "## Bandit Security Report" >> "$GITHUB_STEP_SUMMARY"
echo "| Severity | Count |" >> "$GITHUB_STEP_SUMMARY"
echo "|----------|-------|" >> "$GITHUB_STEP_SUMMARY"

for severity in HIGH MEDIUM LOW; do
  count=$(jq "[.results[] | select(.issue_severity == \"$severity\")] | length" bandit-report.json)
  echo "| $severity | $count |" >> "$GITHUB_STEP_SUMMARY"
done

# Fail only on HIGH severity
if [[ "$high_count" -gt 0 ]]; then
  echo "Found $high_count HIGH severity issues -- failing the job"
  exit 1
fi
echo "No HIGH severity issues found"
```

---

## 6.4 Security-Specific Workflow Permissions

### 6.4.1 The `security-events: write` Permission

CodeQL needs the `security-events: write` permission to upload analysis results
to the GitHub Security tab. Without this permission, the `analyze` step fails
with a permission error.

### 6.4.2 Minimal Permission Set for Security Scanning Workflows

```yaml
permissions:
  contents: read           # Read repository contents
  actions: read            # Read workflow runs
  security-events: write   # Upload CodeQL/SARIF results
```

Do not grant `contents: write` or `pull-requests: write` unless the security
workflow also needs to create comments or modify files (which is unusual for
scanning workflows).

---

## 6.5 Timeout Guards for Security Scanners

### 6.5.1 Why Security Scanners Need Explicit Timeouts

Security scanners analyze code paths that can be combinatorially explosive.
A pathologically complex function can cause CodeQL to run for hours. Without
a timeout, the job consumes runner time indefinitely.

### 6.5.2 Recommended Timeout Values

| Scanner | Recommended timeout | Rationale |
|---------|-------------------|-----------|
| CodeQL (init + autobuild + analyze) | 30 minutes | Large codebases need time; 30 min is generous |
| Bandit | 10 minutes | Pure Python analysis, should be fast |
| SARIF upload | 5 minutes | Network operation, should be near-instant |

Set timeouts at the job level:

```yaml
jobs:
  codeql:
    timeout-minutes: 30
  bandit:
    timeout-minutes: 10
```

---

## 6.6 Complete YAML Example: CodeQL + Bandit + Gate Job

### 6.6.1 Full Workflow Definition

```yaml
name: Security

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 0 * * 1"

permissions:
  contents: read
  actions: read
  security-events: write

jobs:
  codeql:
    name: CodeQL (${{ matrix.language }})
    runs-on: ubuntu-latest
    timeout-minutes: 30
    strategy:
      fail-fast: false
      matrix:
        language: ["python", "javascript"]
    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-extended

      - name: Autobuild
        uses: github/codeql-action/autobuild@v3

      - name: Perform CodeQL analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"

  bandit:
    name: Bandit (Python)
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Bandit
        run: pip install bandit

      - name: Run Bandit
        run: |
          bandit -r src/ -ll -ii -f json -o bandit-report.json || exit_code=$?
          if [[ "${exit_code:-0}" -eq 2 ]]; then
            echo "Bandit scanner error"
            exit 2
          fi

          high_count=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' bandit-report.json)

          echo "## Bandit Security Report" >> "$GITHUB_STEP_SUMMARY"
          for severity in HIGH MEDIUM LOW; do
            count=$(jq "[.results[] | select(.issue_severity == \"$severity\")] | length" bandit-report.json)
            echo "- $severity: $count" >> "$GITHUB_STEP_SUMMARY"
          done

          if [[ "$high_count" -gt 0 ]]; then
            echo "Found $high_count HIGH severity issues"
            exit 1
          fi

  security-gate:
    name: Security Gate
    needs: [codeql, bandit]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Check security scan results
        run: |
          echo "CodeQL: ${{ needs.codeql.result }}"
          echo "Bandit: ${{ needs.bandit.result }}"

          failed=0
          for result in \
            "${{ needs.codeql.result }}" \
            "${{ needs.bandit.result }}"; do
            if [[ "$result" != "success" ]] && [[ "$result" != "skipped" ]]; then
              failed=1
            fi
          done

          if [[ "$failed" -eq 1 ]]; then
            echo "SECURITY GATE FAILED"
            exit 1
          fi
          echo "SECURITY GATE PASSED"
```

### 6.6.2 Walkthrough of Each Section

- **codeql job**: Runs CodeQL with `security-extended` queries for each language
  in the matrix. Each language gets its own category for result isolation. Timeout
  is 30 minutes to handle large codebases.

- **bandit job**: Runs Bandit on the Python source directory with MEDIUM
  severity/confidence thresholds. Produces a JSON report, counts HIGH severity
  findings, and writes a summary to the job summary page. Fails only on HIGH
  severity; reports MEDIUM and LOW without blocking.

- **security-gate job**: Aggregates results from CodeQL and Bandit. Uses the
  `if: always()` pattern to run even if upstream jobs fail. Allows `skipped`
  status for path-filtered scenarios.
