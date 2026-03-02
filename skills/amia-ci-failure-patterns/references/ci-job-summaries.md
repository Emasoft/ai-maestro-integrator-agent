---
name: ci-job-summaries
description: "How to write structured job summaries to GITHUB_STEP_SUMMARY for clear CI result reporting."
---

# CI Job Summaries

## Table of Contents

- 8.1 Understanding Job Summaries
  - 8.1.1 What job summaries are and where they appear
  - 8.1.2 The `GITHUB_STEP_SUMMARY` environment variable
  - 8.1.3 How multiple steps contribute to a single summary
- 8.2 Writing Summaries from Bash Steps
  - 8.2.1 Basic markdown output with echo
  - 8.2.2 Structured tables with status indicators
  - 8.2.3 Collapsible sections for verbose output
- 8.3 Writing Summaries from `actions/github-script`
  - 8.3.1 Using the `core.summary` API
  - 8.3.2 Programmatic table generation
  - 8.3.3 Conditional content based on job results
- 8.4 Common Summary Patterns
  - 8.4.1 Test result summary table
  - 8.4.2 Lint summary with violation counts
  - 8.4.3 Security findings summary
  - 8.4.4 Build artifact summary with download links
- 8.5 Complete YAML Examples
  - 8.5.1 Bash-based test summary
  - 8.5.2 github-script-based multi-section summary
- 8.6 Anti-Patterns to Avoid
  - 8.6.1 Writing to stdout instead of summary
  - 8.6.2 Excessively large summaries
  - 8.6.3 Missing summaries on failure

---

## 8.1 Understanding Job Summaries

### 8.1.1 What Job Summaries Are and Where They Appear

Job summaries are markdown content displayed on the GitHub Actions run summary
page. They appear below the job list on the main run page, providing a structured
overview of what happened without requiring developers to dig through raw log
output.

Each job can produce its own summary. All job summaries are displayed together
on the run summary page, making it a central dashboard for CI results.

### 8.1.2 The `GITHUB_STEP_SUMMARY` Environment Variable

GitHub Actions provides a special file path in the `GITHUB_STEP_SUMMARY`
environment variable. Any markdown content written to this file path appears
in the job summary:

```bash
echo "## Test Results" >> "$GITHUB_STEP_SUMMARY"
echo "All 42 tests passed." >> "$GITHUB_STEP_SUMMARY"
```

The file path is unique per job and persists across steps within the same job.

### 8.1.3 How Multiple Steps Contribute to a Single Summary

Each step can append content to `$GITHUB_STEP_SUMMARY`. The content accumulates
across all steps in the job:

```yaml
steps:
  - name: Run tests
    run: |
      echo "## Unit Tests" >> "$GITHUB_STEP_SUMMARY"
      echo "Passed: 40 | Failed: 2" >> "$GITHUB_STEP_SUMMARY"

  - name: Run linter
    run: |
      echo "## Lint Results" >> "$GITHUB_STEP_SUMMARY"
      echo "No violations found." >> "$GITHUB_STEP_SUMMARY"
```

Both sections appear in the final job summary, in the order they were written.

---

## 8.2 Writing Summaries from Bash Steps

### 8.2.1 Basic Markdown Output with Echo

```bash
echo "## Build Summary" >> "$GITHUB_STEP_SUMMARY"
echo "" >> "$GITHUB_STEP_SUMMARY"
echo "- Build target: \`production\`" >> "$GITHUB_STEP_SUMMARY"
echo "- Duration: 3m 42s" >> "$GITHUB_STEP_SUMMARY"
echo "- Artifacts: 2 packages" >> "$GITHUB_STEP_SUMMARY"
```

Use `>>` (append) not `>` (overwrite). Overwriting replaces the entire summary
with just the last step's output.

### 8.2.2 Structured Tables with Status Indicators

```bash
{
  echo "## Test Matrix Results"
  echo ""
  echo "| Platform | Python | Status | Duration |"
  echo "|----------|--------|--------|----------|"
  echo "| Linux | 3.12 | PASS | 2m 15s |"
  echo "| macOS | 3.12 | PASS | 3m 02s |"
  echo "| Windows | 3.12 | FAIL | 1m 48s |"
} >> "$GITHUB_STEP_SUMMARY"
```

Using a brace group `{ ... }` with a single redirect is cleaner than repeating
`>> "$GITHUB_STEP_SUMMARY"` on every line.

### 8.2.3 Collapsible Sections for Verbose Output

Use HTML `<details>` tags to hide verbose output by default:

```bash
{
  echo "## Dependency Audit"
  echo ""
  echo "Found 3 vulnerabilities (0 critical, 1 high, 2 moderate)"
  echo ""
  echo "<details>"
  echo "<summary>Click to see full audit report</summary>"
  echo ""
  echo '```'
  cat audit-report.txt
  echo '```'
  echo ""
  echo "</details>"
} >> "$GITHUB_STEP_SUMMARY"
```

The audit report is hidden by default. Developers click "Click to see full audit
report" to expand it. This keeps the summary clean while preserving full details.

---

## 8.3 Writing Summaries from `actions/github-script`

### 8.3.1 Using the `core.summary` API

The `core` object in `actions/github-script` provides a fluent API for building
summaries:

```javascript
await core.summary
  .addHeading('Build Results', 2)
  .addList(['Target: production', 'Duration: 3m 42s', 'Artifacts: 2 packages'])
  .write();
```

Methods can be chained. Call `.write()` at the end to flush the summary to the
file.

### 8.3.2 Programmatic Table Generation

```javascript
const results = [
  { name: 'unit', passed: 40, failed: 0 },
  { name: 'integration', passed: 15, failed: 2 },
  { name: 'e2e', passed: 8, failed: 1 },
];

const header = [
  { data: 'Suite', header: true },
  { data: 'Passed', header: true },
  { data: 'Failed', header: true },
  { data: 'Status', header: true },
];

const rows = results.map(r => [
  r.name,
  String(r.passed),
  String(r.failed),
  r.failed === 0 ? 'PASS' : 'FAIL',
]);

await core.summary
  .addHeading('Test Results', 2)
  .addTable([header, ...rows])
  .write();
```

### 8.3.3 Conditional Content Based on Job Results

```javascript
const failed = results.some(r => r.failed > 0);

const summary = core.summary.addHeading('Test Results', 2);

if (failed) {
  summary.addRaw('**Some tests failed.** See details below.\n\n');
} else {
  summary.addRaw('All tests passed.\n\n');
}

// Add the table regardless
summary.addTable([header, ...rows]);
await summary.write();
```

---

## 8.4 Common Summary Patterns

### 8.4.1 Test Result Summary Table

```bash
{
  echo "## Test Results"
  echo ""
  echo "| Suite | Tests | Passed | Failed | Skipped | Duration |"
  echo "|-------|-------|--------|--------|---------|----------|"
  echo "| Unit | 142 | 140 | 2 | 0 | 45s |"
  echo "| Integration | 38 | 35 | 1 | 2 | 2m 30s |"
  echo "| E2E | 12 | 12 | 0 | 0 | 5m 10s |"
  echo ""
  echo "**Total**: 192 tests, 187 passed, 3 failed, 2 skipped"
} >> "$GITHUB_STEP_SUMMARY"
```

### 8.4.2 Lint Summary with Violation Counts

```bash
{
  echo "## Lint Report"
  echo ""
  echo "| Linter | Errors | Warnings | Status |"
  echo "|--------|--------|----------|--------|"
  echo "| ruff | 0 | 3 | PASS |"
  echo "| eslint | 2 | 5 | FAIL |"
  echo "| biome | 0 | 0 | PASS |"
} >> "$GITHUB_STEP_SUMMARY"
```

### 8.4.3 Security Findings Summary

```bash
{
  echo "## Security Scan"
  echo ""
  echo "| Scanner | Critical | High | Medium | Low |"
  echo "|---------|----------|------|--------|-----|"
  echo "| CodeQL | 0 | 1 | 3 | 5 |"
  echo "| Bandit | 0 | 0 | 2 | 8 |"
  echo ""
  echo "<details>"
  echo "<summary>High severity findings (1)</summary>"
  echo ""
  echo "- **CWE-89**: SQL injection in \`src/db/query.py:142\`"
  echo ""
  echo "</details>"
} >> "$GITHUB_STEP_SUMMARY"
```

### 8.4.4 Build Artifact Summary with Download Links

```bash
{
  echo "## Build Artifacts"
  echo ""
  echo "| Artifact | Size | Type |"
  echo "|----------|------|------|"
  echo "| my-package-1.2.3.tar.gz | 2.4 MB | Source distribution |"
  echo "| my_package-1.2.3-py3-none-any.whl | 1.8 MB | Wheel |"
  echo ""
  echo "Download from the Artifacts section below."
} >> "$GITHUB_STEP_SUMMARY"
```

---

## 8.5 Complete YAML Examples

### 8.5.1 Bash-Based Test Summary

```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -e ".[test]"

      - name: Run tests and generate summary
        run: |
          # Run pytest with JUnit XML output
          pytest tests/ -v --junitxml=results.xml || test_exit=$?

          # Parse results for summary
          total=$(python3 -c "
          import xml.etree.ElementTree as ET
          tree = ET.parse('results.xml')
          root = tree.getroot()
          ts = root.find('.//testsuite')
          print(ts.get('tests', '0'))
          ")
          failures=$(python3 -c "
          import xml.etree.ElementTree as ET
          tree = ET.parse('results.xml')
          root = tree.getroot()
          ts = root.find('.//testsuite')
          print(ts.get('failures', '0'))
          ")
          errors=$(python3 -c "
          import xml.etree.ElementTree as ET
          tree = ET.parse('results.xml')
          root = tree.getroot()
          ts = root.find('.//testsuite')
          print(ts.get('errors', '0'))
          ")
          passed=$((total - failures - errors))

          {
            echo "## Test Results"
            echo ""
            echo "| Metric | Count |"
            echo "|--------|-------|"
            echo "| Total | $total |"
            echo "| Passed | $passed |"
            echo "| Failed | $failures |"
            echo "| Errors | $errors |"
          } >> "$GITHUB_STEP_SUMMARY"

          # Exit with the original test exit code
          exit "${test_exit:-0}"

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: results.xml
```

### 8.5.2 github-script-Based Multi-Section Summary

```yaml
  summary:
    needs: [test, lint, build]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Generate combined summary
        uses: actions/github-script@v7
        with:
          script: |
            const results = {
              test:  '${{ needs.test.result }}',
              lint:  '${{ needs.lint.result }}',
              build: '${{ needs.build.result }}',
            };

            const statusIcon = (r) => r === 'success' ? 'PASS' : r === 'skipped' ? 'SKIP' : 'FAIL';

            await core.summary
              .addHeading('CI Summary', 2)
              .addTable([
                [
                  { data: 'Job', header: true },
                  { data: 'Result', header: true },
                  { data: 'Status', header: true },
                ],
                ['Test', results.test, statusIcon(results.test)],
                ['Lint', results.lint, statusIcon(results.lint)],
                ['Build', results.build, statusIcon(results.build)],
              ])
              .write();
```

---

## 8.6 Anti-Patterns to Avoid

### 8.6.1 Writing to Stdout Instead of Summary

```bash
# BAD: This goes to the log, not the summary page
echo "Tests passed: 42"

# GOOD: This appears on the summary page
echo "Tests passed: 42" >> "$GITHUB_STEP_SUMMARY"
```

Stdout output is buried in the step log and requires clicking into the step
to see it. Summary output is immediately visible on the run page.

### 8.6.2 Excessively Large Summaries

GitHub limits job summaries to 1 MB per step and 128 KB per job. Writing
raw test logs or full dependency trees to the summary will be truncated.

Use collapsible `<details>` sections for verbose content, or link to uploaded
artifacts instead of embedding large outputs.

### 8.6.3 Missing Summaries on Failure

Many workflows only write summaries in success paths. When a step fails and the
workflow exits early, no summary is written. Use `if: always()` on the summary
step to ensure it runs regardless of earlier failures:

```yaml
- name: Write summary
  if: always()
  run: |
    echo "## Build Results" >> "$GITHUB_STEP_SUMMARY"
    if [[ -f results.json ]]; then
      echo "Results available." >> "$GITHUB_STEP_SUMMARY"
    else
      echo "Build failed before results were generated." >> "$GITHUB_STEP_SUMMARY"
    fi
```
