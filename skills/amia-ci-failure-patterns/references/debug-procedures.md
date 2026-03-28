# Debug Procedures for CI Failure Analysis

> **MULTI-REPO RULE:** All `gh` commands MUST include `--repo "$OWNER/$REPO"` and all `git` commands MUST use `git -C "$REPO_PATH"` since the integrator works across multiple repos.

## Table of Contents

- 1.1 When a CI/CD pipeline fails and needs systematic diagnosis
  - 1.1.1 Log collection and initial triage procedures
  - 1.1.2 Verification steps for complete data collection
- 1.2 When identifying which failure pattern category applies
  - 1.2.1 Using the diagnosis decision tree
  - 1.2.2 Pattern category reference mapping
- 1.3 When performing deep root cause analysis by category
  - 1.3.1 Cross-platform issue analysis procedures
  - 1.3.2 Exit code issue analysis procedures
  - 1.3.3 Syntax issue analysis procedures
  - 1.3.4 Dependency issue analysis procedures
  - 1.3.5 Infrastructure issue analysis procedures
  - 1.3.6 Language-specific issue analysis procedures
- 1.4 When documenting diagnostic evidence
  - 1.4.1 Diagnostic report structure
  - 1.4.2 Evidence documentation requirements
  - 1.4.3 Fix specification format
- 1.5 When delegating fixes to remote agents
  - 1.5.1 Delegation protocol (RULE 0 compliant)
  - 1.5.2 AI Maestro message format
  - 1.5.3 GitHub issue update procedures
- 1.6 When escalating unknown or complex failures
  - 1.6.1 Escalation trigger conditions
  - 1.6.2 Escalation message format
  - 1.6.3 Recommendation documentation
- 1.7 When using diagnostic scripts and tools
  - 1.7.1 CI log analysis scripts
  - 1.7.2 Platform issue detection scripts
  - 1.7.3 JSON output for structured analysis
- 1.8 When troubleshooting common diagnostic challenges
  - 1.8.1 Handling large log files
  - 1.8.2 Managing unknown patterns
  - 1.8.3 Diagnosing multiple simultaneous failures
  - 1.8.4 Detecting flaky tests
  - 1.8.5 Analyzing platform matrix complexity

---

## 1.1 When a CI/CD pipeline fails and needs systematic diagnosis

### 1.1.1 Log collection and initial triage procedures

**Purpose:** Gather complete CI failure data before attempting analysis.

**Collection methods:**

```bash
# Fetch GitHub Actions log for a specific run
gh run view <run-id> --log-failed

# Get logs from a specific workflow
gh run list --workflow=<workflow-name> --limit 1
gh run view <latest-run-id> --log-failed

# For local log files
# Read and document: timestamp, workflow, job, step, runner OS
```

**Documentation requirements:**

Document the following metadata for every CI failure:

- **Timestamp**: When the failure occurred (ISO8601 format)
- **Workflow name**: Which workflow file triggered the job
- **Job name**: Which job within the workflow failed
- **Step name**: Which step within the job failed
- **Runner OS**: Operating system (ubuntu-latest, windows-latest, macos-latest)
- **Runner architecture**: Architecture (x64, arm64)
- **Exit code**: The numeric exit code of the failed command
- **Error message**: The primary error message from logs

**Example documentation:**

```markdown
## Failure Metadata
- Timestamp: 2025-01-31T14:30:22Z
- Workflow: ci.yml
- Job: test-windows
- Step: Run pytest
- Runner: windows-latest (x64)
- Exit Code: 1
- Error: "FAILED tests/test_plugin.py::test_hook_execution"
```

### 1.1.2 Verification steps for complete data collection

Before proceeding to pattern identification, confirm:

**Verification Checklist Step 1:**

- [ ] Full failure log collected (not truncated)
- [ ] Workflow name and job identified
- [ ] Runner OS and architecture documented
- [ ] Failed step pinpointed (exact step name)
- [ ] Exit code extracted
- [ ] Primary error message isolated

**If ANY checklist item is incomplete, stop and collect missing data before proceeding.**

---

## 1.2 When identifying which failure pattern category applies

### 1.2.1 Using the diagnosis decision tree

**Purpose:** Systematically categorize the failure type to guide root cause analysis.

**Decision tree procedure:**

Apply the following checks **in order** against the error message and log context:

| Order | Check Question | Pattern Category | Next Action |
|-------|---------------|-----------------|-------------|
| 1 | Does error mention "path not found", "file not found", or "no such file"? | Cross-Platform | See cross-platform-patterns.md |
| 2 | Is there a non-zero exit code with no clear error message? | Exit Codes | See exit-code-patterns.md |
| 3 | Does error mention "syntax error", "unexpected token", or "unexpected end of file"? | Syntax | See syntax-patterns.md |
| 4 | Does error mention "module not found", "import error", or "cannot find package"? | Dependencies | See dependency-patterns.md |
| 5 | Does error mention GitHub resources like "label not found" or "runner unavailable"? | Infrastructure | See github-infrastructure-patterns.md |
| 6 | Is the error specific to a programming language (Python, Node.js, Rust, Go)? | Language-Specific | See language-specific-patterns.md |
| 7 | None of the above match | Unknown Pattern | Escalate to orchestrator |

**Important:** Stop at the first match. If multiple patterns apply, document as "Multiple Causes" scenario.

### 1.2.2 Pattern category reference mapping

Once a category is identified, reference the appropriate pattern file:

| Category | Reference Document | Contains |
|----------|-------------------|----------|
| Cross-Platform | cross-platform-patterns.md | OS-specific path issues, line endings, case sensitivity |
| Exit Codes | exit-code-patterns.md | PowerShell exit code persistence, tool-specific codes |
| Syntax | syntax-patterns.md | Heredoc terminators, shell quoting, YAML multiline |
| Dependencies | dependency-patterns.md | Module imports, lock files, version mismatches |
| Infrastructure | github-infrastructure-patterns.md | Labels, runners, permissions |
| Language-Specific | language-specific-patterns.md | Python venv, Node.js modules, Rust cargo, Go modules |

**Verification Checklist Step 2:**

- [ ] Decision tree followed systematically (in order)
- [ ] Pattern category identified (or marked as Unknown)
- [ ] Reference document noted for next analysis phase
- [ ] If multiple patterns, all categories documented

---

## 1.3 When performing deep root cause analysis by category

### 1.3.1 Cross-platform issue analysis procedures

**When to use:** Failure identified as "Cross-Platform" category.

**Common root causes:**

1. **Temp path differences**
   - **Linux/macOS:** Uses `$TMPDIR` or `/tmp`
   - **Windows:** Uses `$env:TEMP` or `C:\Users\...\AppData\Local\Temp`
   - **Check:** Does the workflow YAML use `$TMPDIR` without Windows fallback?

2. **Path separator differences**
   - **Linux/macOS:** Forward slash `/`
   - **Windows:** Backslash `\` (though PowerShell accepts both)
   - **Check:** Are paths hardcoded with `/` instead of using cross-platform path construction?

3. **Line ending differences**
   - **Linux/macOS:** LF (`\n`)
   - **Windows:** CRLF (`\r\n`)
   - **Check:** Are shell scripts failing due to CRLF line endings on Windows?

4. **Case sensitivity differences**
   - **Linux/macOS:** Case-sensitive filesystems
   - **Windows:** Case-insensitive by default
   - **Check:** Are file references using incorrect case that works on Windows but fails on Linux?

**Analysis procedure:**

1. **Extract the exact error message** from logs
2. **Identify which file or path** is mentioned in the error
3. **Check how that path is constructed** in the workflow YAML or script
4. **Compare against the runner OS** where failure occurred
5. **Document the discrepancy** with specific examples

**Evidence to collect:**

- The YAML line where the path is defined
- The error message showing the path that failed
- The runner OS where the failure occurred
- The expected vs actual path format

### 1.3.2 Exit code issue analysis procedures

**When to use:** Failure identified as "Exit Codes" category.

**Common root causes:**

1. **PowerShell $LASTEXITCODE persistence**
   - **Issue:** PowerShell does NOT reset `$LASTEXITCODE` automatically
   - **Symptom:** Step fails with exit 1 even though command succeeded
   - **Check:** Was there a previous command that set exit code?

2. **Tool-specific exit codes**
   - **Issue:** Tools use non-zero exit codes for warnings (not errors)
   - **Example:** `git diff --exit-code` returns 1 if differences found (not an error)
   - **Check:** Is the tool expected to return non-zero for valid states?

3. **GitHub Actions step failure detection**
   - **Issue:** Actions detects failure but error message is unclear
   - **Symptom:** Red X on step with no obvious error in logs
   - **Check:** Look earlier in log for hidden warnings or stderr output

**Analysis procedure:**

1. **Identify the exit code** (usually 1, but could be other values)
2. **Check previous commands** in the same step or previous steps
3. **Look for exit code resets** (or lack thereof) in PowerShell scripts
4. **Verify tool documentation** for expected exit codes
5. **Trace causality chain** from error back to root command

**Evidence to collect:**

- The exact exit code value
- All commands executed before the failure
- PowerShell variable state (if applicable)
- Tool documentation for exit code meanings

### 1.3.3 Syntax issue analysis procedures

**When to use:** Failure identified as "Syntax" category.

**Common root causes:**

1. **Heredoc terminator not at column 0**
   - **Issue:** Bash heredoc terminators (e.g., `EOF`) must start at column 0
   - **Symptom:** "Unexpected end of file" error
   - **Check:** Is the heredoc terminator indented?

2. **Shell quoting differences**
   - **Issue:** Single quotes vs double quotes behave differently
   - **Symptom:** Variable not expanded or escaping issues
   - **Check:** Are variables inside single quotes (won't expand)?

3. **YAML multiline string indentation**
   - **Issue:** YAML `|` or `>` blocks require consistent indentation
   - **Symptom:** Syntax error in parsed YAML
   - **Check:** Is indentation consistent in multiline blocks?

**Analysis procedure:**

1. **Locate the syntax error line number** in the error message
2. **Extract the surrounding code** (5 lines before and after)
3. **Check indentation** character-by-character (spaces vs tabs)
4. **Verify quote matching** (opening and closing quotes)
5. **Test heredoc terminators** for leading whitespace

**Evidence to collect:**

- The exact line number of the syntax error
- The code block with visible whitespace characters
- The shell or parser producing the error
- The expected vs actual syntax

### 1.3.4 Dependency issue analysis procedures

**When to use:** Failure identified as "Dependencies" category.

**Common root causes:**

1. **Relative import path issues**
   - **Issue:** Python relative imports fail when run from different directories
   - **Symptom:** `ModuleNotFoundError` or `ImportError`
   - **Check:** Are imports using relative paths like `from .module import`?

2. **Lock file synchronization**
   - **Issue:** `package-lock.json` or `requirements.txt` out of sync with actual code
   - **Symptom:** Module version mismatch or missing dependencies
   - **Check:** When was lock file last updated vs code changes?

3. **Version mismatches**
   - **Issue:** Dependency version conflicts between packages
   - **Symptom:** Import errors or runtime exceptions after dependency install
   - **Check:** Are there conflicting version constraints?

**Analysis procedure:**

1. **Identify the missing module** from error message
2. **Check if module exists** in lock file or requirements
3. **Verify module path** in source code vs expected location
4. **Compare dependency versions** across lock files
5. **Check virtual environment activation** (Python) or node_modules presence (Node.js)

**Evidence to collect:**

- The exact module name that failed to import
- The import statement from source code
- The lock file entry (or absence) for the module
- The directory structure where module should exist

### 1.3.5 Infrastructure issue analysis procedures

**When to use:** Failure identified as "Infrastructure" category.

**Common root causes:**

1. **Missing labels**
   - **Issue:** GitHub labels not created before workflow assigns them
   - **Symptom:** "Label not found" error in workflow
   - **Check:** Does `.github/workflows/*.yml` reference labels that don't exist in repo?

2. **Runner availability**
   - **Issue:** Self-hosted runner offline or not matching labels
   - **Symptom:** Workflow stuck in "Queued" state or "No runner available"
   - **Check:** Are runners online and matching required labels?

3. **Permission issues**
   - **Issue:** Workflow lacks required permissions (e.g., write to repo)
   - **Symptom:** "403 Forbidden" or "Permission denied"
   - **Check:** Does workflow YAML specify required permissions?

**Analysis procedure:**

1. **Extract the GitHub resource** mentioned in error (label, runner, permission)
2. **Check repository settings** for existence of that resource
3. **Verify workflow permissions** in YAML `permissions:` section
4. **Compare required vs available** resources
5. **Document gap** between expected and actual state

**Evidence to collect:**

- The GitHub resource name from error
- Repository settings showing resource presence/absence
- Workflow YAML showing resource usage
- GitHub Actions logs showing permission errors

### 1.3.6 Language-specific issue analysis procedures

**When to use:** Failure identified as "Language-Specific" category.

**Common root causes by language:**

**Python:**

- **Virtual environment not activated:** Commands run outside venv, can't find packages
- **Check:** Is `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\Activate.ps1` (Windows) called before Python commands?

**JavaScript/Node.js:**

- **node_modules not cached or installed:** Packages missing after checkout
- **Check:** Is `npm install` or `yarn install` run before using modules?

**Rust:**

- **Cargo target directory pollution:** Old build artifacts cause errors
- **Check:** Is `cargo clean` needed before rebuild?

**Go:**

- **Module resolution failure:** Go modules not downloaded or incorrect version
- **Check:** Is `go mod download` run before build?

**Analysis procedure:**

1. **Identify the language** from error message or workflow context
2. **Check activation/installation steps** in workflow YAML
3. **Verify tool versions** match expected versions in code
4. **Compare local vs CI environment** configurations
5. **Document language-specific setup gaps**

**Evidence to collect:**

- Language version from error or workflow
- Setup steps from workflow YAML
- Expected vs actual tool versions
- Environment variable differences between local and CI

---

## 1.4 When documenting diagnostic evidence

### 1.4.1 Diagnostic report structure

**Purpose:** Create a complete record of the diagnosis for delegation and tracking.

**Report template:**

```markdown
# CI Failure Diagnosis Report
Timestamp: {ISO8601 timestamp}
Agent: amia-debug-specialist
Workflow: {workflow_name}
Job: {job_name}
Runner: {os}-{arch}

## Failure Summary
- Failed Step: {step_name}
- Exit Code: {code}
- Pattern Category: {category}
- Primary Error: {error_message}

## Root Cause Analysis
{Detailed analysis explaining the causality chain from root cause to failure symptom}

### Step-by-step Causation
1. {First event or condition that triggered the chain}
2. {Second event caused by the first}
3. {Continue until reaching the final failure}

### Why Local Tests Passed
{Explanation of why this issue only manifests in CI, not local development}

## Evidence
{Relevant log sections with line numbers}

### Log Excerpt 1: {Description}
```

Line {N}: {log line}
Line {N+1}: {log line}
...

```

### Log Excerpt 2: {Description}
```

Line {M}: {log line}
Line {M+1}: {log line}
...

```

## Recommended Fix Category
{What type of fix is needed, NOT how to implement it}

### Expected Outcome After Fix
{How to verify the fix worked}

## Reference
See: amia-ci-failure-patterns/references/{pattern-file}.md
Section: {specific section in reference file}
```

### 1.4.2 Evidence documentation requirements

**Minimum evidence to include:**

1. **Failure metadata** (timestamp, workflow, job, step, runner, exit code)
2. **Pattern category** (from decision tree)
3. **Root cause explanation** (causality chain)
4. **Log excerpts** (with line numbers, showing the error and context)
5. **Discrepancy documentation** (local vs CI, expected vs actual)
6. **Reference to pattern file** (specific section)

**Evidence quality checks:**

- [ ] Log excerpts show the **exact error line** plus surrounding context
- [ ] Line numbers included for all log excerpts
- [ ] Root cause explanation traces **from trigger to symptom**
- [ ] Discrepancy clearly stated (e.g., "Works locally because X, fails in CI because Y")
- [ ] Reference section in pattern file specified (not just file name)

### 1.4.3 Fix specification format

**Purpose:** Document WHAT needs to change (not HOW) for delegation to developer agents.

**Fix specification structure:**

```markdown
## Recommended Fix Category
Category: {Cross-Platform | Exit-Code | Syntax | Dependency | Infrastructure | Language-Specific}

### What Needs to Change
{Describe the WHAT, not the HOW}

Example:
- File: .github/workflows/ci.yml
- Change Type: Add platform-specific temp path handling
- Affected Lines: 42-45
- Current Behavior: Uses $TMPDIR which doesn't expand on Windows
- Required Behavior: Use cross-platform temp path detection

### Expected Outcome After Fix
{How to verify the fix worked}

Example:
- Windows CI runs should pass the temp file creation step
- Temp files should be created in the correct OS-specific location
- No "file not found" errors related to temp paths

### Reference Implementation Pattern
See: amia-ci-failure-patterns/references/{pattern-file}.md
Section: {specific section showing the fix pattern}
```

**Verification Checklist Step 4:**

- [ ] Report written to `docs_dev/ci-debug/CI-DEBUG-{timestamp}.md`
- [ ] All sections completed (no placeholders)
- [ ] Evidence includes specific log excerpts with line numbers
- [ ] Fix specification describes WHAT, not HOW
- [ ] Expected outcome is verifiable (testable)
- [ ] Reference section specified

---

## 1.5 When delegating fixes to remote agents

### 1.5.1 Delegation protocol (RULE 0 compliant)

**CRITICAL:** The debug-specialist agent does NOT fix code. Fixes are delegated to remote agents via AI Maestro.

**Delegation workflow:**

1. **COMPLETE** the diagnostic report (all sections filled)
2. **DOCUMENT** the fix specification (WHAT needs to change)
3. **PREPARE** AI Maestro message for delegation
4. **SEND** message to appropriate remote agent
5. **UPDATE** GitHub issue with diagnostic findings
6. **RETURN** to orchestrator with minimal report

**Do NOT:**

- Write or modify code in the codebase
- Use the Edit tool
- Implement the fix directly
- Make assumptions about fix implementation details

**Do:**

- Document the root cause completely
- Specify what type of change is needed
- Provide reference patterns for implementation
- Delegate to the correct agent type

### 1.5.2 AI Maestro message format

**Action:** Send a message using the `agent-messaging` skill with:

- **Recipient**: `{remote-agent-name}` (see routing table below)
- **Subject**: `[FIX REQUEST] CI failure - {pattern_category}`
- **Priority**: `high`
- **Content**:

  ```json
  {
    "type": "fix_request",
    "message": "Root cause: {one_line_summary}\nFix spec: docs_dev/ci-debug/CI-DEBUG-{timestamp}.md\nReference: amia-ci-failure-patterns/references/{pattern-file}.md"
  }
  ```

- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

**Agent routing by fix category:**

| Fix Category | Target Agent | Reason |
|--------------|--------------|--------|
| Cross-Platform | python-code-fixer or js-code-fixer | Platform-specific code changes |
| Exit-Code | python-code-fixer or js-code-fixer | Script or workflow fixes |
| Syntax | python-code-fixer or js-code-fixer | Syntax corrections |
| Dependency | python-code-fixer or js-code-fixer | Dependency updates |
| Infrastructure | helper-agent-generic | GitHub settings or workflow config |
| Language-Specific | python-code-fixer or js-code-fixer | Language tool setup |

### 1.5.3 GitHub issue update procedures

**Purpose:** Keep GitHub issue thread up-to-date with diagnostic findings.

**Update format:**

```bash
# Add comment to existing issue
gh issue comment {issue-number} --body "$(cat <<'EOF'
## CI Failure Diagnosis Complete

**Pattern Category:** {category}
**Root Cause:** {one_line_summary}

**Detailed Report:** `docs_dev/ci-debug/CI-DEBUG-{timestamp}.md`
**Reference:** `amia-ci-failure-patterns/references/{pattern-file}.md`

**Next Steps:**
- Fix delegated to {remote-agent-name}
- Expected outcome: {verification_criteria}
EOF
)"
```

**Verification Checklist Step 5:**

- [ ] Fix specification documented (NOT implemented)
- [ ] AI Maestro message prepared for delegation
- [ ] Correct remote agent identified for fix category
- [ ] GitHub issue updated with findings
- [ ] NO CODE WRITTEN by this agent

---

## 1.6 When escalating unknown or complex failures

### 1.6.1 Escalation trigger conditions

**Escalate to orchestrator when:**

1. **Unknown Pattern**
   - Failure does not match any category in the decision tree
   - Error message is ambiguous or missing
   - No clear root cause after analysis

2. **Multiple Causes**
   - Failure has multiple interacting root causes
   - Fixing one issue may not resolve the full failure
   - Dependencies between fixes require coordination

3. **Infrastructure Blocked**
   - GitHub Actions runner unavailable or offline
   - Repository permissions prevent diagnosis
   - External service dependency failure

4. **Permission Required**
   - Fix requires elevated permissions (repo admin, org owner)
   - Fix requires user approval (architectural change)
   - Fix affects other repositories or services

5. **Human Decision**
   - Fix has architectural implications (design choice)
   - Fix involves trade-offs that need user input
   - Multiple fix approaches with no clear winner

### 1.6.2 Escalation message format

**Escalation report structure:**

```markdown
# Escalation Report: CI Failure Diagnosis
Timestamp: {ISO8601}
Agent: amia-debug-specialist
Escalation Reason: {Unknown Pattern | Multiple Causes | Infrastructure Blocked | Permission Required | Human Decision}

## Failure Context
- Workflow: {workflow_name}
- Job: {job_name}
- Runner: {os}-{arch}
- Failed Step: {step_name}

## Investigation Summary
{Brief summary of what was analyzed}

### Pattern Analysis Attempted
- [ ] Cross-Platform checks: {result}
- [ ] Exit Code checks: {result}
- [ ] Syntax checks: {result}
- [ ] Dependency checks: {result}
- [ ] Infrastructure checks: {result}
- [ ] Language-Specific checks: {result}

### Why Escalating
{Detailed explanation of why this cannot be resolved without orchestrator intervention}

## Evidence Collected
See: docs_dev/ci-debug/CI-DEBUG-{timestamp}.md

## Recommendation
{Suggested next step for orchestrator}

Example recommendations:
- "Require user input on which fix approach to use"
- "Contact GitHub support for runner availability"
- "Request repository admin permissions for workflow changes"
```

### 1.6.3 Recommendation documentation

**Guidelines for escalation recommendations:**

- **Be specific:** Don't say "investigate further", say "check with user if X approach is acceptable"
- **Provide options:** If multiple paths exist, list them with pros/cons
- **Include context:** Explain why each option matters
- **Suggest owner:** Recommend who should handle next (user, orchestrator, specific agent)

**Example recommendations:**

```markdown
## Recommendation
Issue requires architectural decision:

### Option A: Refactor temp file handling to use cross-platform library
- **Pro:** Solves root cause completely
- **Con:** Requires code refactoring in 5 modules
- **Effort:** High (3-4 hours)

### Option B: Add Windows-specific fallback to current implementation
- **Pro:** Minimal code change
- **Con:** Adds platform-specific code paths
- **Effort:** Low (30 minutes)

**Suggested Owner:** User (architectural decision)
**Blocking:** Yes (cannot proceed without decision)
```

**Escalation output format:**

```
[ESCALATE] debug-specialist - {reason}
Evidence: docs_dev/ci-debug/CI-DEBUG-{timestamp}.md
Recommendation: {suggested_next_step}
```

---

## 1.7 When using diagnostic scripts and tools

### 1.7.1 CI log analysis scripts

**Script:** `amia_diagnose_ci_failure.py`

**Purpose:** Automated pattern detection in CI logs.

**Usage:**

```bash
# Basic analysis
python scripts/amia_diagnose_ci_failure.py --log-file /path/to/ci.log

# JSON output for structured analysis
python scripts/amia_diagnose_ci_failure.py --log-file /path/to/ci.log --json

# Specify runner OS for platform-specific checks
python scripts/amia_diagnose_ci_failure.py --log-file ci.log --os windows
```

**Output interpretation:**

```json
{
  "pattern_category": "Cross-Platform",
  "confidence": 0.85,
  "evidence": [
    {"line": 42, "text": "TMPDIR: No such file or directory"},
    {"line": 43, "text": "Runner: windows-latest"}
  ],
  "recommendation": "See cross-platform-patterns.md section 2.1"
}
```

**When to use:**

- Large log files (>1000 lines) that are hard to analyze manually
- Multiple potential patterns need to be checked
- Structured output needed for further processing

### 1.7.2 Platform issue detection scripts

**Script:** `amia_detect_platform_issue.py`

**Purpose:** Scan codebase for potential platform-specific issues before CI runs.

**Usage:**

```bash
# Scan entire project
python scripts/amia_detect_platform_issue.py --path /path/to/project

# Scan specific file
python scripts/amia_detect_platform_issue.py --path /path/to/file.py

# Output as JSON
python scripts/amia_detect_platform_issue.py --path project/ --json
```

**Detection patterns:**

- Hardcoded forward slash paths `/tmp/file`
- Windows-only environment variables `$env:TEMP`
- Unix-only commands `chmod`, `chown`
- Line ending inconsistencies

**Output example:**

```json
{
  "issues": [
    {
      "file": "scripts/setup.sh",
      "line": 15,
      "issue": "Hardcoded Unix path: /tmp/data",
      "category": "Cross-Platform",
      "severity": "high"
    }
  ],
  "summary": {
    "total_issues": 3,
    "high_severity": 1,
    "medium_severity": 2
  }
}
```

**When to use:**

- Before making CI workflow changes
- After adding new scripts to the project
- When platform-specific failures are suspected

### 1.7.3 JSON output for structured analysis

**Purpose:** Generate machine-readable diagnostic output for integration with other tools.

**When to use JSON output:**

1. **Automated processing:** Diagnostic results need to feed into another script or tool
2. **Batch analysis:** Multiple failures need to be analyzed and compared
3. **Reporting:** Results need to be displayed in a dashboard or tracking system
4. **Testing:** Validating that diagnostic logic works correctly

**JSON schema for diagnostic output:**

```json
{
  "diagnostic": {
    "timestamp": "2025-01-31T14:30:22Z",
    "workflow": "ci.yml",
    "job": "test-windows",
    "step": "Run pytest",
    "runner": {
      "os": "windows-latest",
      "arch": "x64"
    },
    "failure": {
      "exit_code": 1,
      "error_message": "TMPDIR: No such file or directory",
      "pattern_category": "Cross-Platform",
      "confidence": 0.85
    },
    "root_cause": {
      "summary": "Windows temp path not expanded in YAML",
      "evidence": [
        {"line": 42, "text": "TMPDIR: No such file or directory"},
        {"line": 43, "text": "Runner: windows-latest"}
      ],
      "reference": "cross-platform-patterns.md",
      "section": "2.1"
    },
    "fix_specification": {
      "category": "Cross-Platform",
      "files_affected": [".github/workflows/ci.yml"],
      "change_type": "Add platform-specific temp path handling",
      "expected_outcome": "Windows CI runs pass temp file creation step"
    }
  }
}
```

---

## 1.8 When troubleshooting common diagnostic challenges

### 1.8.1 Handling large log files

**Problem:** CI log exceeds memory limits or takes too long to analyze manually.

**Solution:**

1. **Focus on failed step only:**

   ```bash
   gh run view <run-id> --log-failed
   ```

   This returns only the output from the failed step, not the entire workflow log.

2. **Use log excerpts:**
   Instead of reading the entire log, extract excerpts around the error:

   ```bash
   # Get 10 lines before and after error line
   grep -C 10 "error message" ci.log
   ```

3. **Use automated analysis:**

   ```bash
   python scripts/amia_diagnose_ci_failure.py --log-file ci.log --json
   ```

   The script scans the log and extracts relevant patterns automatically.

**When NOT to use:**

- Do NOT try to load the entire log into memory if it's >10MB
- Do NOT manually read logs >1000 lines without automated assistance

### 1.8.2 Managing unknown patterns

**Problem:** Error does not match any known category in the decision tree.

**Solution:**

1. **Document the unknown pattern:**
   Create a detailed report with all available evidence:
   - Exact error message
   - Full log context (before and after error)
   - Runner environment details
   - What was ruled out during analysis

2. **Escalate with evidence:**

   ```
   [ESCALATE] debug-specialist - Unknown failure pattern
   Root cause: [Unknown] - No matching pattern in decision tree
   Details: docs_dev/ci-debug/CI-DEBUG-20250131-150000.md
   ```

3. **Propose pattern addition:**
   If the pattern is identified after escalation, propose adding it to the decision tree:
   - New pattern description
   - Detection criteria
   - Example evidence
   - Suggested reference document section

**When to escalate:**

- After systematically checking all 6 pattern categories
- When error message is too ambiguous to categorize
- When multiple patterns apply simultaneously

### 1.8.3 Diagnosing multiple simultaneous failures

**Problem:** Several unrelated failures in the same workflow run.

**Solution:**

1. **Diagnose each failure separately:**
   Create a separate diagnostic report for each failure:
   - `CI-DEBUG-20250131-143000-failure1.md`
   - `CI-DEBUG-20250131-143000-failure2.md`
   - `CI-DEBUG-20250131-143000-failure3.md`

2. **Document dependencies between failures:**
   If one failure causes another, note the dependency:

   ```markdown
   ## Failure Dependencies
   - Failure 2 is caused by Failure 1 (temp file not created)
   - Failure 3 is independent of Failures 1 and 2
   ```

3. **Prioritize fixes:**
   Recommend fix order based on dependencies:

   ```markdown
   ## Recommended Fix Order
   1. Fix Failure 1 first (creates temp file)
   2. Fix Failure 3 (independent, can be parallel)
   3. Retest Failure 2 after Failure 1 is fixed (may be resolved)
   ```

**Output format for multiple failures:**

```
[DONE] debug-specialist - Multiple CI failures diagnosed
Root cause: [Exit-Code + Syntax] - PowerShell heredoc and exit code issues
Details: docs_dev/ci-debug/CI-DEBUG-20250131-160000-summary.md
```

### 1.8.4 Detecting flaky tests

**Problem:** Same test passes/fails randomly across runs without code changes.

**Solution:**

1. **Document test flakiness:**
   Note the test name and failure frequency:

   ```markdown
   ## Flaky Test Detection
   - Test: tests/test_plugin.py::test_hook_execution
   - Pass rate: 70% (7/10 runs passed)
   - Failure pattern: Intermittent timeout on Windows only
   ```

2. **Identify potential causes:**
   - Race conditions (timing-dependent logic)
   - External service dependencies (network calls)
   - Insufficient timeouts
   - Resource contention (CPU/memory limits)

3. **Recommend two-phase fix:**
   - **Phase 1 (immediate):** Add retry mechanism to mitigate flakiness
   - **Phase 2 (permanent):** Investigate and fix root cause

**Flaky test report format:**

```markdown
## Root Cause Analysis
Test exhibits flaky behavior (passes/fails randomly).

### Potential Race Condition
The test does not wait for async operation to complete before assertion.

### Recommended Fix Category
1. **Immediate:** Add retry logic or increase timeout
2. **Permanent:** Add explicit wait for async completion
```

**Verification:** After fix, run test 20+ times to confirm stability.

### 1.8.5 Analyzing platform matrix complexity

**Problem:** Different failures on different OS runners (Windows, Linux, macOS).

**Solution:**

1. **Create separate diagnosis for each platform:**
   - `CI-DEBUG-20250131-143000-windows.md`
   - `CI-DEBUG-20250131-143000-linux.md`
   - `CI-DEBUG-20250131-143000-macos.md`

2. **Identify common vs platform-specific issues:**

   ```markdown
   ## Cross-Platform Analysis

   ### Common Issue (all platforms)
   - Root cause: Module import path incorrect
   - Affects: Windows, Linux, macOS

   ### Platform-Specific Issues
   - **Windows only:** Temp path not expanded ($TMPDIR)
   - **Linux only:** None
   - **macOS only:** None
   ```

3. **Recommend platform-specific fixes:**

   ```markdown
   ## Recommended Fix Category

   ### Fix 1: Common Issue (all platforms)
   - File: src/plugin/loader.py
   - Change: Correct module import path
   - Affects: All platforms

   ### Fix 2: Windows-Specific Issue
   - File: .github/workflows/ci.yml
   - Change: Add Windows temp path fallback
   - Affects: Windows only
   ```

**Output format for platform matrix:**

```
[DONE] debug-specialist - Platform matrix failures diagnosed
Root cause: [Cross-Platform + Dependency] - Windows temp path + import path issues
Details: docs_dev/ci-debug/CI-DEBUG-20250131-143000-matrix-summary.md
```

---

## Summary

This reference document provides complete procedures for:

1. **Collecting CI failure data** systematically with verification steps
2. **Identifying failure pattern categories** using the decision tree
3. **Performing root cause analysis** by category with specific checks
4. **Documenting evidence** with structured reports and fix specifications
5. **Delegating fixes** to remote agents via AI Maestro (RULE 0 compliant)
6. **Escalating complex cases** with detailed recommendations
7. **Using diagnostic scripts** for automated analysis
8. **Troubleshooting common challenges** with specific solutions

**CRITICAL RULE:** The debug-specialist agent does NOT fix code. It diagnoses, documents, and delegates.

**Verification checklist before returning to orchestrator:**

- [ ] CI failure log collected and analyzed
- [ ] Pattern category identified using decision tree
- [ ] Root cause determined with specific evidence
- [ ] Platform/OS/architecture documented
- [ ] Diagnostic report written to `docs_dev/ci-debug/`
- [ ] Fix specification created (WHAT, not HOW)
- [ ] Delegation message prepared for appropriate agent
- [ ] GitHub issue updated (if applicable)
- [ ] No code written or modified by this agent
- [ ] Minimal 3-line report prepared for orchestrator
