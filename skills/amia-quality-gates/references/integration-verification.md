# Integration Verification Procedures

## Contents

- [1. Verifying Component Integration Readiness](#1-verifying-component-integration-readiness)
  - [1.1 Environment baseline verification](#11-environment-baseline-verification)
  - [1.2 Service connectivity testing](#12-service-connectivity-testing)
  - [1.3 Configuration validation](#13-configuration-validation)
- [2. Checking Merge Readiness with Exit Code Evidence](#2-checking-merge-readiness-with-exit-code-evidence)
  - [2.1 Functional verification with complete test suite](#21-functional-verification-with-complete-test-suite)
  - [2.2 Evidence documentation requirements](#22-evidence-documentation-requirements)
  - [2.3 Merge readiness criteria checklist](#23-merge-readiness-criteria-checklist)
- [3. Verifying User Requirements Compliance Before Integration](#3-verifying-user-requirements-compliance-before-integration)
  - [3.1 Loading and parsing USER_REQUIREMENTS.md](#31-loading-and-parsing-user_requirementsmd)
  - [3.2 Creating verification checklist from requirements](#32-creating-verification-checklist-from-requirements)
  - [3.3 Handling requirement violations during integration](#33-handling-requirement-violations-during-integration)
- [4. Resolving Integration Conflicts and Failures](#4-resolving-integration-conflicts-and-failures)
  - [4.1 Interpreting exit codes and failure modes](#41-interpreting-exit-codes-and-failure-modes)
  - [4.2 Troubleshooting common integration issues](#42-troubleshooting-common-integration-issues)
  - [4.3 Documenting and reporting verification failures](#43-documenting-and-reporting-verification-failures)
- [5. Validating Deployment Configurations](#5-validating-deployment-configurations)
  - [5.1 Container image verification](#51-container-image-verification)
  - [5.2 Runtime environment validation](#52-runtime-environment-validation)
  - [5.3 Security and resource compliance checks](#53-security-and-resource-compliance-checks)

---

## 1. Verifying Component Integration Readiness

### 1.1 Environment baseline verification

**When to use**: Before starting any integration verification, establish the baseline system state.

**Procedure**:

1. **Read all configuration files** that affect the component being integrated:
   ```bash
   # Example commands with exit code capture
   cat config.yaml && echo $? > /tmp/config-read-exit.txt
   env | grep REQUIRED_VAR && echo $? > /tmp/env-check-exit.txt
   ```

2. **Verify environment variables** are set with expected values:
   - Check presence of required environment variables
   - Capture exit code 0 for successful verification
   - Document missing variables with non-zero exit codes

3. **Check system capabilities**:
   - Available ports (e.g., `netstat`, `ss`)
   - Available memory and disk space
   - Process limits and file descriptor limits
   - Network accessibility to external services

4. **Document baseline state** in timestamped report:
   - All commands executed
   - Exit codes captured
   - System resource snapshot
   - Configuration file checksums

**Verification checklist for Step 1**:
- [ ] Exit codes captured for all config validation commands
- [ ] All required environment variables present with exit code 0
- [ ] System capabilities documented with proof artifacts
- [ ] Baseline report written to `/tmp/integration-verification-{timestamp}.md`

### 1.2 Service connectivity testing

**When to use**: After environment verification, test that all integration points are reachable.

**Integration points to verify**:

1. **Service-to-service communication**:
   - Execute HTTP requests to service endpoints
   - Capture HTTP status codes (200, 404, 500, etc.)
   - Record response times and latency metrics
   - Test both successful and error response paths

2. **API endpoint availability**:
   - Health check endpoints (e.g., `/health`, `/status`)
   - Business logic endpoints
   - Authentication/authorization endpoints
   - Capture all HTTP status codes and exit codes

3. **Message queue connectivity**:
   - Test message publication with acknowledgment
   - Verify message consumption and processing
   - Check queue depth and consumer lag
   - Document broker connection exit codes

4. **Database connection pools**:
   - Test connection acquisition and release
   - Verify connection pool sizing and limits
   - Execute sample queries with timing
   - Capture database driver exit codes

5. **Cache layer functionality**:
   - Test cache writes and reads
   - Verify cache invalidation behavior
   - Check cache hit/miss ratios
   - Document cache backend connectivity

**Verification checklist for Step 2**:
- [ ] All connectivity tests return exit code 0 or documented failure codes
- [ ] Actual HTTP status codes recorded for all endpoint tests
- [ ] Network responses captured to evidence files
- [ ] Connection timing metrics documented

### 1.3 Configuration validation

**When to use**: Validate that all configuration files are syntactically correct and semantically complete before integration testing.

**Configuration aspects to verify**:

1. **Configuration file syntax**:
   - Execute syntax validators (e.g., `yamllint`, `jsonlint`)
   - Capture validator exit codes
   - Document syntax errors with line numbers
   - Example:
     ```bash
     yamllint config.yaml
     echo $? > /tmp/yaml-syntax-exit.txt
     ```

2. **Permission matrices**:
   - Verify file permissions on config files (e.g., `600` for secrets)
   - Check process user/group ownership
   - Test file access with target user context
   - Document permission issues with exit code evidence

3. **Network accessibility**:
   - Test DNS resolution for all hostnames in configs
   - Verify firewall rules allow required connections
   - Check TLS certificate validity for HTTPS endpoints
   - Capture network diagnostic exit codes

4. **Resource availability**:
   - Verify required ports are not already in use
   - Check memory limits match configuration
   - Validate disk space for logs and data
   - Document resource constraint violations

**Verification checklist for Step 3**:
- [ ] All config files pass syntax validation with exit code 0
- [ ] File permissions verified for security compliance
- [ ] Network connectivity tests completed with exit codes
- [ ] Resource availability confirmed with measurements

---

## 2. Checking Merge Readiness with Exit Code Evidence

### 2.1 Functional verification with complete test suite

**When to use**: After environment and connectivity verification pass, execute the full integration test suite to confirm merge readiness.

**Procedure**:

1. **Execute integration test suites**:
   - Run all integration tests that cover the integrated component
   - Capture exit code for each test individually
   - Record test duration for performance analysis
   - Example:
     ```bash
     pytest tests/integration/test_payment_service.py -v
     echo $? > /tmp/pytest-exit.txt
     ```

2. **Capture all exit codes**:
   - Every test MUST have an exit code recorded
   - Use `echo $?` immediately after test execution
   - Write exit codes to numbered evidence files
   - No assertions without exit code backing

3. **Document pass/fail for each component**:
   - Create per-component test result matrix
   - Include test name, exit code, duration, timestamp
   - Separate passed (exit code 0) from failed (non-zero)

4. **Verify error handling paths**:
   - Test intentional failure scenarios
   - Confirm error handlers return expected exit codes
   - Validate error messages and logging output
   - Document error path coverage with exit codes

**Verification checklist for functional tests**:
- [ ] Every test has captured exit code
- [ ] No assertions made without exit code evidence
- [ ] Test duration recorded for all tests
- [ ] Timestamps documented for reproducibility
- [ ] Error handling paths tested with exit code evidence

### 2.2 Evidence documentation requirements

**When to use**: Continuously throughout verification to ensure all evidence is properly captured and stored.

**Iron Law: Exit Code Evidence**

All verification results MUST include:

1. **Actual exit codes from all executed commands**:
   - Capture immediately after command execution: `echo $?`
   - Write to timestamped evidence files
   - Never rely on memory or assumptions about success

2. **stdout/stderr output captured to evidence files**:
   - Redirect output: `command 2>&1 | tee /tmp/command-output-{timestamp}.txt`
   - Preserve all output for failure analysis
   - Include in evidence report references

3. **Timestamps of execution**:
   - ISO8601 format: `date -u +"%Y-%m-%dT%H:%M:%SZ"`
   - Record start and end time for duration calculation
   - Include timezone information

4. **Command signatures that were executed**:
   - Exact bash commands with all arguments
   - Environment variables that affected execution
   - Working directory where command was run

5. **System state at time of verification**:
   - Process list snapshot
   - Network connection state
   - Resource utilization (CPU, memory, disk)
   - File system state (relevant files/directories)

**Report structure** (written to `/tmp/integration-verification-{timestamp}.md`):

```markdown
# Integration Verification Report
Timestamp: {ISO8601}
Agent: integration-verifier
Model: Claude Opus 4.5

## Verification Results

### Component: {name}
- Command: {exact_command}
- Exit Code: {integer}
- Duration: {seconds}s
- Status: [PASS|FAIL]
- Evidence: {file_location}

[Repeat for each component]

## Summary
- Total Tests: N
- Passed: N (exit code 0)
- Failed: N (exit code != 0)
- Inconclusive: N (no exit code - UNACCEPTABLE)
```

**Critical rule**: No assertions without exit code backing. If exit code cannot be captured, verification MUST be marked as FAILED.

### 2.3 Merge readiness criteria checklist

**When to use**: Before declaring integration verification complete and approving merge.

**Pre-merge checklist** (all items MUST be checked):

- [ ] All environment variables verified with exit codes captured
- [ ] All service endpoints tested with connectivity results documented
- [ ] All integration tests executed with exit codes recorded
- [ ] All commands have captured stdout/stderr in evidence files
- [ ] All verification results have timestamps
- [ ] Evidence report written to `/tmp/integration-verification-{timestamp}.md`
- [ ] Summary includes pass/fail counts with exit code distribution
- [ ] No assertions made without exit code backing
- [ ] All failure modes documented with specific exit codes
- [ ] Report is machine-parseable and complete

**Merge blocking conditions**:

- Missing exit code evidence for ANY test
- Incomplete verification scope (not all integration points tested)
- User requirements violations (see section 3.3)
- Security policy compliance failures
- Resource constraint violations

**Exit code interpretation for merge decision**:

- `0`: Component verified, integration intact → MERGE APPROVED
- `1-127`: Component failure with specific error → MERGE BLOCKED
- `128+`: Signal termination evidence → MERGE BLOCKED
- Missing: Unacceptable - must execute with captured exit → MERGE BLOCKED

---

## 3. Verifying User Requirements Compliance Before Integration

### 3.1 Loading and parsing USER_REQUIREMENTS.md

**When to use**: At the start of every integration verification workflow, before any technical testing.

**Procedure**:

1. **Read USER_REQUIREMENTS.md** from project root:
   ```bash
   cat USER_REQUIREMENTS.md
   ```

2. **Parse requirement structure**:
   - Identify functional requirements (features)
   - Identify non-functional requirements (performance, security)
   - Identify immutable requirements (cannot be changed)
   - Identify technology constraints (must-use technologies)

3. **Extract testable criteria**:
   - Each requirement should have acceptance criteria
   - Convert acceptance criteria to integration test assertions
   - Identify requirements that need manual verification

4. **Document requirement coverage**:
   - Create requirement-to-test mapping
   - Flag requirements without test coverage
   - Report gaps to orchestrator for addressing

### 3.2 Creating verification checklist from requirements

**When to use**: After parsing USER_REQUIREMENTS.md, translate requirements into integration test criteria.

**Procedure**:

1. **Create requirement-based checklist**:
   - Each requirement = one or more checklist items
   - Format: `[ ] REQ-001: User can authenticate via OAuth2`
   - Include requirement ID for traceability

2. **Map requirements to integration tests**:
   - Link each requirement to specific test file(s)
   - Document which tests verify which requirements
   - Identify requirements without test coverage

3. **Define pass/fail criteria**:
   - Exit code 0 = requirement verified
   - Non-zero exit code = requirement NOT met
   - Missing test = requirement unverified (FAIL)

4. **Prioritize immutable requirements**:
   - Mark IMMUTABLE requirements with highest priority
   - These MUST pass with exit code 0 for merge approval
   - Technology substitutions = automatic FAIL

**Example checklist format**:

```markdown
## User Requirement Verification Checklist

### Functional Requirements
- [ ] REQ-001: User authentication via OAuth2 (test_oauth2_flow.py) - Exit code: __
- [ ] REQ-002: Payment processing with Stripe (test_payment_integration.py) - Exit code: __

### Non-Functional Requirements
- [ ] REQ-NFR-001: API response time < 200ms (test_performance.py) - Exit code: __

### Immutable Requirements (MUST PASS)
- [ ] REQ-IMM-001: Data encryption at rest using AES-256 (test_encryption.py) - Exit code: __
```

### 3.3 Handling requirement violations during integration

**When to use**: When integration testing reveals that user requirements are not fully satisfied.

**Integration CANNOT pass if**:

1. **User-specified features are missing**:
   - Tests fail with non-zero exit codes
   - Required functionality not implemented
   - Feature scope reduced without approval

2. **User-specified technology was substituted**:
   - Required library/framework not used
   - Alternative technology chosen by developer
   - Technology constraint violated (e.g., "must use PostgreSQL" but using SQLite)

3. **Scope was reduced without user approval**:
   - Fewer features than specified
   - Partial implementation of requirements
   - Requirements marked "deferred" without user consent

4. **Any requirement marked IMMUTABLE was violated**:
   - These are non-negotiable constraints
   - Security requirements, compliance requirements
   - Cannot proceed without explicit user approval

**Violation handling procedure**:

1. **FAIL the integration verification immediately**:
   - Do not proceed with remaining tests
   - Mark verification status as FAILED
   - Generate violation report

2. **Document violation in requirement-issues/**:
   - Create file: `requirement-issues/REQ-{ID}-violation-{timestamp}.md`
   - Include:
     - Requirement ID and description
     - What was expected vs. what was implemented
     - Exit code evidence of failure
     - Impact analysis (what breaks, what's missing)

3. **Block merge until user reviews deviation**:
   - Integration verification MUST return FAILED status
   - Merge request CANNOT be approved
   - Flag in GitHub issue or pull request

4. **Only proceed after explicit user approval**:
   - User must review violation report
   - User must either:
     - Approve deviation and update requirements
     - Reject and request re-implementation
   - Document user decision with timestamp and rationale

**Minimal output format for requirement violation**:

```
[FAILED] integration-verifier - requirement-violation
Violation: REQ-IMM-001 (Data encryption) not satisfied
Details: requirement-issues/REQ-IMM-001-violation-20250205.md
```

---

## 4. Resolving Integration Conflicts and Failures

### 4.1 Interpreting exit codes and failure modes

**When to use**: When integration tests fail, interpret exit codes to understand failure types and determine resolution path.

**Exit code ranges and meanings**:

| Exit Code Range | Meaning | Action |
|-----------------|---------|--------|
| `0` | Success - component verified | Integration intact, proceed |
| `1` | General error - test failure | Review test logs, fix implementation |
| `2` | Misuse of command - wrong arguments | Fix test script syntax |
| `126` | Command cannot execute - permission denied | Fix file permissions, check executable bit |
| `127` | Command not found - missing binary | Install dependencies, check PATH |
| `128` | Invalid exit argument | Review test error handling |
| `130` | Process terminated by Ctrl+C (SIGINT) | Test was interrupted, re-run |
| `137` | Process killed by SIGKILL | Resource limit reached or timeout |
| `143` | Process terminated by SIGTERM | Graceful shutdown, may indicate timeout |

**Failure mode categorization**:

1. **Environment failures** (exit codes 126, 127):
   - Missing dependencies
   - Incorrect PATH configuration
   - Permission issues
   - **Resolution**: Fix environment, re-run verification

2. **Test logic failures** (exit codes 1, 2):
   - Assertions failed
   - Unexpected behavior
   - Logic bugs in implementation
   - **Resolution**: Fix code, re-run tests

3. **Resource failures** (exit codes 137, 143):
   - Out of memory
   - Timeout exceeded
   - Process killed externally
   - **Resolution**: Increase resources or timeout, optimize code

4. **Configuration failures** (exit code 1 with specific error messages):
   - Invalid configuration syntax
   - Missing required config keys
   - Type mismatches
   - **Resolution**: Fix configuration files, re-validate

### 4.2 Troubleshooting common integration issues

**When to use**: When integration verification encounters specific failure patterns.

#### Issue 1: Missing Exit Code in Output

**Problem**: Bash command completes but exit code not recorded in evidence.

**Symptoms**:
- Test appears to run but no exit code in report
- Evidence file missing exit code line
- Cannot determine pass/fail status

**Solution**:
1. Always use `echo $?` **immediately** after command execution
2. Write exit code to dedicated evidence file:
   ```bash
   command_to_test
   EXIT_CODE=$?
   echo $EXIT_CODE > /tmp/exit-code-{test-name}.txt
   ```
3. Never run multiple commands between test and exit code capture
4. If exit code cannot be captured, mark test as FAILED

#### Issue 2: Service Timeout

**Problem**: Integration test hangs waiting for service response, never completes.

**Symptoms**:
- Test process runs beyond expected duration
- No output from service
- Integration verification blocked

**Solution**:
1. Use `timeout` command with kill signal:
   ```bash
   timeout -s KILL 30s curl http://service/health
   echo $? > /tmp/health-check-exit.txt
   ```
2. Exit code 124 = timeout reached (command was running)
3. Exit code 137 = timeout reached and killed (SIGKILL sent)
4. Document timeout value in evidence report
5. Investigate service health if timeouts occur

#### Issue 3: Permission Denied

**Problem**: Cannot execute verification script or access required resources.

**Symptoms**:
- Exit code 126 (command cannot execute)
- Exit code 1 with "Permission denied" error message
- Cannot read configuration files

**Solution**:
1. Check file permissions with Read tool:
   ```bash
   ls -la verification-script.sh
   ```
2. Document required privileges in evidence report
3. If permissions cannot be fixed, FAIL verification with evidence:
   ```markdown
   ### Permission Failure
   - File: verification-script.sh
   - Current permissions: -rw-r--r--
   - Required permissions: -rwxr-xr-x
   - Exit code: 126
   - Status: FAILED
   ```
4. Escalate to orchestrator for permission resolution

#### Issue 4: Incomplete Evidence

**Problem**: Partial verification results without complete exit codes or proof artifacts.

**Symptoms**:
- Some tests have exit codes, others don't
- Missing stdout/stderr captures
- Incomplete evidence report

**Solution**:
1. Re-run verification with explicit exit code capture for ALL steps
2. Use consistent evidence file naming:
   ```bash
   test-name-{timestamp}-stdout.txt
   test-name-{timestamp}-stderr.txt
   test-name-{timestamp}-exit.txt
   ```
3. If complete evidence cannot be achieved, mark ENTIRE verification as FAILED
4. Do not proceed with partial evidence - abort verification

#### Issue 5: Network Connectivity Failures

**Problem**: Cannot reach external services or APIs during integration testing.

**Symptoms**:
- Exit codes indicating connection refused
- DNS resolution failures
- Timeout errors

**Solution**:
1. Verify network accessibility with diagnostic commands:
   ```bash
   ping -c 3 service.example.com
   echo $? > /tmp/ping-exit.txt

   curl -I http://service.example.com/health
   echo $? > /tmp/curl-health-exit.txt
   ```
2. Document network state in evidence report
3. Check firewall rules and DNS configuration
4. If network is required but unavailable, FAIL verification with evidence

### 4.3 Documenting and reporting verification failures

**When to use**: When any integration test fails or verification cannot complete successfully.

**Failure report structure**:

```markdown
# Integration Verification FAILURE Report
Timestamp: {ISO8601}
Agent: integration-verifier
Status: FAILED

## Failure Summary
- Component: {name}
- Total Tests: N
- Passed: N
- Failed: N
- Exit Code Distribution:
  - Exit code 0: N tests
  - Exit code 1: N tests
  - Exit code 126: N tests
  - [etc.]

## Failed Test Details

### Test: {test_name}
- Command: {exact_command}
- Exit Code: {integer}
- Duration: {seconds}s
- Error Output:
  ```
  {stderr content}
  ```
- Evidence Files:
  - stdout: /tmp/{test_name}-stdout.txt
  - stderr: /tmp/{test_name}-stderr.txt
  - exit: /tmp/{test_name}-exit.txt

[Repeat for each failed test]

## Root Cause Analysis
[Analysis of why tests failed based on exit codes and error messages]

## Recommended Actions
1. [Specific action to resolve failure]
2. [Specific action to resolve failure]
3. [Specific action to resolve failure]

## Merge Decision
**MERGE BLOCKED** - Integration verification FAILED with N test failures.
```

**Minimal output format to orchestrator**:

```
[FAILED] integration-verifier - {component_name}
Tests: {passed}/{total} | Exit codes: {0_count} success, {nonzero_count} failed
Evidence: /tmp/integration-verification-{timestamp}.md
```

**Handoff procedure**:

1. Write detailed failure report to `/tmp/integration-verification-{timestamp}.md`
2. Include ALL exit codes, error messages, and evidence file paths
3. Return minimal 3-line summary to orchestrator
4. Do NOT include verbose logs or code blocks in handoff message
5. Exit immediately after returning summary

The orchestrator will read the detailed report file to understand failures and delegate fixes to appropriate developer agents.

---

## 5. Validating Deployment Configurations

### 5.1 Container image verification

**When to use**: When integration verification includes containerized components or deployment readiness checks.

**Procedure**:

1. **Check container image presence**:
   ```bash
   docker images | grep {image_name}
   echo $? > /tmp/docker-image-check-exit.txt
   ```

2. **Execute image inspection commands**:
   ```bash
   docker inspect {image_name}:{tag} > /tmp/docker-inspect-output.json
   echo $? > /tmp/docker-inspect-exit.txt
   ```

3. **Verify all layer SHAs**:
   - Extract layer SHAs from inspect output
   - Verify each layer is complete and valid
   - Check for known vulnerable layers (CVE scanning)
   - Document layer verification with exit codes

4. **Test container spawn capability**:
   ```bash
   docker run --rm {image_name}:{tag} /bin/sh -c "echo test"
   echo $? > /tmp/docker-run-exit.txt
   ```
   - Exit code 0 = container can spawn successfully
   - Non-zero = container configuration error

5. **Validate container health checks**:
   - Extract HEALTHCHECK directive from Dockerfile
   - Execute health check command in running container
   - Verify health check returns exit code 0
   - Document health check timing and behavior

**Verification checklist**:
- [ ] Container image exists locally with exit code 0
- [ ] Image inspection completes with exit code 0
- [ ] All layer SHAs verified and documented
- [ ] Container can spawn with exit code 0
- [ ] Health check passes with exit code 0

### 5.2 Runtime environment validation

**When to use**: Before deploying or integrating components that depend on specific runtime environments.

**Runtime aspects to verify**:

1. **Binary dependency resolution**:
   - Check for required system libraries (e.g., `ldd` on Linux)
   - Verify shared object versions match requirements
   - Test binary execution with no missing dependencies
   - Example:
     ```bash
     ldd /path/to/binary
     echo $? > /tmp/ldd-exit.txt
     ```

2. **Runtime environment setup**:
   - Verify language runtime versions (Python, Node.js, Java, etc.)
   - Check installed packages match requirements.txt/package.json
   - Validate environment variable expectations
   - Example:
     ```bash
     python --version
     echo $? > /tmp/python-version-exit.txt
     ```

3. **File system layout**:
   - Verify required directories exist with correct permissions
   - Check log file locations are writable
   - Validate data directory mount points
   - Document file system state

4. **Process execution context**:
   - Verify process user/group matches expectations
   - Check ulimits (file descriptors, processes, memory)
   - Test signal handling behavior
   - Document process context with exit codes

**Verification checklist**:
- [ ] All binary dependencies resolved with exit code 0
- [ ] Runtime versions match requirements
- [ ] File system layout verified and documented
- [ ] Process context validated with exit codes

### 5.3 Security and resource compliance checks

**When to use**: Before approving integration for merge or deployment.

**Security compliance**:

1. **Security policy compliance**:
   - Verify encryption at rest (if required)
   - Test TLS/SSL for network communication
   - Check authentication/authorization mechanisms
   - Validate input sanitization and output encoding

2. **Secret management**:
   - Verify secrets are not hardcoded in config files
   - Check secret injection mechanisms (environment variables, vaults)
   - Test secret rotation capability
   - Document secret handling with exit codes

3. **Access control validation**:
   - Test role-based access control (RBAC)
   - Verify least privilege principle
   - Check file permissions on sensitive files
   - Document access control tests with exit codes

**Resource compliance**:

1. **Resource limit validation**:
   - Memory limits match configuration
   - CPU limits are enforced
   - Disk space adequate for operation
   - Network bandwidth meets requirements

2. **Health check endpoint status**:
   - Test /health endpoint returns 200
   - Verify /ready endpoint indicates readiness
   - Check /metrics endpoint exposes metrics
   - Document endpoint tests with exit codes
   - Example:
     ```bash
     curl -f http://localhost:8080/health
     echo $? > /tmp/health-endpoint-exit.txt
     ```

3. **Graceful degradation**:
   - Test behavior under resource constraints
   - Verify circuit breakers activate appropriately
   - Check fallback mechanisms work
   - Document degradation tests with exit codes

**Verification checklist**:
- [ ] Security policies verified with exit codes
- [ ] Secret management tested and documented
- [ ] Access controls validated with exit codes
- [ ] Resource limits confirmed with measurements
- [ ] Health check endpoints pass with exit code 0
- [ ] Graceful degradation tested with exit codes

**Deployment readiness decision**:

```markdown
## Deployment Readiness
- Security Compliance: [PASS/FAIL]
- Resource Compliance: [PASS/FAIL]
- Health Checks: [PASS/FAIL]
- Overall Status: [READY/NOT READY]
```

Only when all three categories pass with exit code 0 evidence can deployment be approved.

---

## Summary

This reference document provides complete integration verification procedures with emphasis on:

1. **Exit code evidence**: Every verification step must capture and document exit codes
2. **Merge readiness**: Clear criteria for when integration is ready for merge
3. **Requirement compliance**: User requirements must be verified before integration approval
4. **Conflict resolution**: Systematic troubleshooting of common integration failures
5. **Deployment validation**: Container, runtime, security, and resource checks

All procedures follow the iron law: **No assertions without exit code backing.**
