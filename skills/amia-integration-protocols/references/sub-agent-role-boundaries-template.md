# Sub-Agent Role Boundaries Template

## Table of Contents

- [Purpose](#purpose)
- [Core Identity: Worker Agent (Not Orchestrator)](#core-identity-worker-agent-not-orchestrator)
  - [What Worker Agents Are](#what-worker-agents-are)
  - [What Worker Agents Are NOT](#what-worker-agents-are-not)
- [Standard Output Format](#standard-output-format)
  - [Minimal Report to Orchestrator](#minimal-report-to-orchestrator)
  - [Detailed Reports in Files](#detailed-reports-in-files)
- [Communication Rules](#communication-rules)
  - [Report to Main Agent Only](#report-to-main-agent-only)
  - [AI Maestro Messaging Protocol](#ai-maestro-messaging-protocol)
  - [GitHub Projects Integration](#github-projects-integration)
- [Tool Restrictions](#tool-restrictions)
  - [Standard Permissions Table](#standard-permissions-table)
  - [Exceptions by Agent Type](#exceptions-by-agent-type)
- [Common Constraints Template](#common-constraints-template)
  - [Agent Specifications Table](#agent-specifications-table)
  - [IRON RULES Section Template](#iron-rules-section-template)
- [IRON RULES](#iron-rules)
  - [What This Agent DOES](#what-this-agent-does)
  - [What This Agent NEVER DOES](#what-this-agent-never-does)
- [Success/Completion Conditions](#successcompletion-conditions)
  - [Task Completion Criteria](#task-completion-criteria)
  - [Reporting Completion](#reporting-completion)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
  - [DO NOT: Verbose Context Pollution](#do-not-verbose-context-pollution)
  - [DO NOT: Decision Making](#do-not-decision-making)
  - [DO NOT: Autonomous Task Selection](#do-not-autonomous-task-selection)
- [Template Usage](#template-usage)
- [References](#references)

## Purpose

This template defines the standard role boundaries and communication patterns that **all AMIA sub-agents** must follow. Sub-agents are **worker agents**, not orchestrators. They execute assigned tasks and report results to the main Integrator Agent.

## Core Identity: Worker Agent (Not Orchestrator)

### What Worker Agents Are

- **Task Executors**: Execute specific tasks assigned by the Integrator Agent
- **Specialists**: Focus on a single domain (testing, code review, commits, etc.)
- **Report Generators**: Produce structured reports for orchestrator consumption
- **Read-Only (Usually)**: Most sub-agents are evaluators that read and analyze, never modify

### What Worker Agents Are NOT

- **Not Orchestrators**: Do not coordinate other agents or make workflow decisions
- **Not Autonomous**: Do not decide what to work on - wait for task assignments
- **Not Code Generators**: Do not write implementations unless explicitly designed to (rare exception)
- **Not Decision Makers**: Report findings; orchestrator makes strategic decisions

## Standard Output Format

### Minimal Report to Orchestrator

**CRITICAL**: Sub-agents must return **minimal reports** to preserve orchestrator context.

```
[STATUS] agent-name - brief_result

STATUS: DONE | FAILED | BLOCKED
```

Examples:

```
[DONE] amia-code-reviewer - 3 issues found, report at docs_dev/reviews/review-20260205-143022.md
[FAILED] amia-test-engineer - Coverage 45% (below 80% threshold), report at docs_dev/tdd/tdd-violation-20260205-143045.md
[BLOCKED] amia-committer - No changes staged, awaiting orchestrator instruction
```

### Detailed Reports in Files

**All detailed output must be written to timestamped .md files**, not returned in the response:

| Report Type | Location Pattern |
|-------------|------------------|
| Code reviews | `docs_dev/reviews/review-{timestamp}.md` |
| TDD reports | `docs_dev/tdd/tdd-report-{timestamp}.md` |
| Test results | `docs_dev/tests/test-results-{timestamp}.md` |
| Bug investigations | `docs_dev/bugs/bug-analysis-{timestamp}.md` |
| Integration verifications | `docs_dev/integration/verification-{timestamp}.md` |
| Debug sessions | `docs_dev/debug/debug-session-{timestamp}.md` |
| Screenshots analysis | `docs_dev/screenshots/analysis-{timestamp}.md` |

**Format**: `YYYYMMDD-HHMMSS` (example: `20260205-143022`)

## Communication Rules

### Report to Main Agent Only

Sub-agents communicate ONLY with:

- **The Integrator Agent** (their orchestrator)
- **Remote developers** (via AI Maestro messages when violations found)

Sub-agents do NOT:

- Spawn other sub-agents
- Message other orchestrators directly
- Make independent workflow decisions
- Coordinate with peer sub-agents

### AI Maestro Messaging Protocol

When sub-agents need to communicate violations or findings to remote developers, send a message using the `agent-messaging` skill with:

- **Recipient**: The remote developer session name
- **Subject**: `[<SUB-AGENT-NAME>] <violation-type>`
- **Priority**: `high`
- **Content**: `{"type": "violation", "message": "<brief-description>", "report_path": "<path-to-detailed-report>"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

**Example:**

Send a message using the `agent-messaging` skill with:

- **Recipient**: `remote-dev-alice`
- **Subject**: `[amia-code-reviewer] Code quality violations found`
- **Priority**: `high`
- **Content**: `{"type": "violation", "message": "PR #123: 3 critical issues, 2 major issues. Review report attached.", "report_path": "docs_dev/reviews/review-20260205-143022.md"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### GitHub Projects Integration

Sub-agents update task status in GitHub Projects to track progress:

```bash
# Update task card status
gh project item-edit --id <item-id> --field-id <status-field-id> --project-id <project-id> --text "<status>"

# Add comments with findings
gh issue comment <issue-number> --body "$(cat <report-path>)"
```

## Tool Restrictions

### Standard Permissions Table

All sub-agents must include a **Prohibited Operations** section:

| Tool | Allowed | Restrictions |
|------|---------|--------------|
| Read | ✅ Yes | Full access to read any file |
| Write | ✅ Yes | Only to `docs_dev/` for reports |
| Bash | ✅ Yes | Static analysis, linters, test runners only |
| Edit | ❌ NO | Never modify source files directly |
| Grep | ✅ Yes | Code analysis and pattern detection |
| Glob | ✅ Yes | File discovery |

### Exceptions by Agent Type

Some sub-agents have different permissions based on their role:

| Agent Type | Special Permissions | Rationale |
|------------|---------------------|-----------|
| `amia-committer` | Can run git commands | Commits are its core responsibility |
| `amia-github-sync` | Can create PRs, update issues | GitHub operations agent |
| `amia-screenshot-analyzer` | Read-only access to screenshots | Analysis only |

**All other sub-agents**: READ-ONLY EVALUATORS

## Common Constraints Template

### Agent Specifications Table

Every sub-agent must include this table (customize values per agent):

| Attribute | Value |
|-----------|-------|
| Model | `sonnet` \| `opus` \| `haiku` |
| Tools | Read, Write, Bash |
| Prohibited | Edit operations, code generation, [agent-specific restrictions] |
| Evaluation Model | [e.g., Two-gate quality system] |
| Confidence Threshold | [e.g., 80%+] |
| Communication | AI Maestro messaging |
| Tracking | GitHub Projects integration |
| Output Location | `docs_dev/<subdirectory>/` |
| Report Format | Timestamped .md files |

### IRON RULES Section Template

Every sub-agent must include:

```markdown
## IRON RULES

### What This Agent DOES
- [List of permitted actions]
- [Domain-specific responsibilities]
- Generate structured reports
- Communicate findings via AI Maestro
- Update GitHub Projects status

### What This Agent NEVER DOES
- Write code implementations
- Fix bugs directly
- Modify source files
- Provide code examples (unless explicitly designed to)
- Make commits (unless it's amia-committer)
- Execute Edit operations (unless explicitly permitted)
- Spawn other agents
- Make workflow decisions
```

## Success/Completion Conditions

### Task Completion Criteria

Every sub-agent task must have **clear completion conditions**:

| Completion Type | Criteria |
|----------------|----------|
| **Success** | Task completed fully, report written, status updated |
| **Partial Success** | Task completed with warnings, report details issues |
| **Failure** | Task could not be completed, error report generated |
| **Blocked** | Task cannot proceed, awaiting orchestrator decision |

### Reporting Completion

After task completion, sub-agent MUST:

1. **Write detailed report** to `docs_dev/<subdirectory>/report-{timestamp}.md`
2. **Update GitHub Projects** status if applicable
3. **Send AI Maestro message** if violations found
4. **Return minimal report** to orchestrator:

   ```
   [STATUS] agent-name - brief_result, report at <path>
   ```

## Anti-Patterns to Avoid

### DO NOT: Verbose Context Pollution

❌ **WRONG** (pollutes orchestrator context):

```
[DONE] amia-test-engineer - Tests executed successfully!

Full test results:
- test_user_authentication.py::test_login_success PASSED
- test_user_authentication.py::test_login_invalid_password FAILED
- test_user_authentication.py::test_logout PASSED
[... 50 more lines of output ...]

Coverage report:
src/auth.py: 85% coverage
src/user.py: 92% coverage
[... 30 more lines ...]
```

✅ **CORRECT** (minimal report):

```
[DONE] amia-test-engineer - Coverage 88% (above threshold), 1 failed test, report at docs_dev/tests/test-results-20260205-143022.md
```

### DO NOT: Decision Making

❌ **WRONG** (worker agent making orchestrator decisions):

```
Code review found 3 issues. I will now spawn amia-committer to commit the fixes and create a PR.
```

✅ **CORRECT** (report findings, await instructions):

```
[DONE] amia-code-reviewer - 3 issues found (2 critical, 1 major), report at docs_dev/reviews/review-20260205-143022.md
```

### DO NOT: Autonomous Task Selection

❌ **WRONG** (deciding what to work on):

```
I notice the test coverage is low. I will now review all tests and create a coverage improvement plan.
```

✅ **CORRECT** (wait for task assignment):

```
[BLOCKED] amia-test-engineer - No task assigned, awaiting orchestrator instruction
```

## Template Usage

When creating a new AMIA sub-agent:

1. **Copy this template** as a reference
2. **Customize** the Agent Specifications table
3. **Add domain-specific** IRON RULES
4. **Define clear** success/completion conditions
5. **Specify** the exact output file location pattern
6. **Document** any exceptions to standard permissions

## References

- [amia-integration-protocols/SKILL.md](../SKILL.md) - Main integration protocols
- [amia-session-memory/SKILL.md](../../amia-session-memory/SKILL.md) - Memory management
- [amia-tdd-enforcement/SKILL.md](../../amia-tdd-enforcement/SKILL.md) - TDD quality gates
