# Operation: Delegate to Subagent


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Steps](#steps)
- [Prompt Template](#prompt-template)
- [Task](#task)
- [Context](#context)
- [Success Criteria](#success-criteria)
- [Output Requirements](#output-requirements)
- [Constraints](#constraints)
- [Output](#output)
- [Critical Rules](#critical-rules)
- [Error Handling](#error-handling)
- [Example](#example)
- [Task](#task)
- [Context](#context)
- [Success Criteria](#success-criteria)
- [Output Requirements](#output-requirements)
- [Constraints](#constraints)

---
procedure: proc-request-pr-review
workflow-instruction: Step 20 - PR Review Request
operation-id: op-delegate-subagent
---

## Purpose

Spawn a specialized subagent to perform PR review work. The coordinator delegates but never does the work itself.

## When to Use

- After classifying work type
- When work_type is: code_review, code_changes, or ci_verification
- Never for simple status checks (use scripts directly)

## Prerequisites

- Work type classified
- PR details gathered
- Author type identified

## Steps

1. **Select subagent type** based on work classification:

   | Work Type | Subagent | Description |
   |-----------|----------|-------------|
   | code_review | Review subagent | Perform code review |
   | code_changes | Implementation subagent | Make code changes |
   | ci_verification | CI monitor subagent | Investigate CI failures |

2. **Prepare subagent prompt** with required elements:
   - Task description (clear, single task)
   - PR number and repository
   - Success criteria (verifiable)
   - Output format requirements
   - Context from previous work

3. **Spawn subagent** using Task tool (never block waiting)

4. **Log delegation** in orchestration log

5. **Set up monitoring** via polling (see op-monitor-progress)

## Prompt Template

```
You are a <subagent_type> for PR #<number> in <repo>.

## Task
<single, clear task description>

## Context
- PR Title: <title>
- Author: <author> (<author_type>)
- Current Status: <status>
- Previous Work: <summary of prior work if any>

## Success Criteria
<specific, verifiable conditions>

## Output Requirements
Return a minimal report: 1-2 lines max.
Format: `[DONE/FAILED] task_name - brief_result`
Write detailed findings to: <output_file_path>

## Constraints
- Do not merge the PR
- Do not communicate with PR author directly (report back to coordinator)
- Complete within <timeout> or report blocker
```

## Output

| Field | Type | Description |
|-------|------|-------------|
| subagent_id | string | Spawned subagent identifier |
| task_description | string | What was delegated |
| expected_completion | string | Estimated completion |

## Critical Rules

1. **One task per subagent** - Never give multiple tasks
2. **Clear success criteria** - Must be verifiable
3. **Never block** - Spawn and continue, monitor via polling
4. **Minimal output** - Require brief reports to save context

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Subagent spawn fails | Resource limits | Reduce concurrent agents |
| Unclear output | Prompt too vague | Refine prompt, re-delegate |
| Task too large | Scope creep | Break into smaller tasks |

## Example

```python
# Delegation for code review
task_prompt = """
You are a code review subagent for PR #123 in Emasoft/project.

## Task
Review code changes in PR #123 for quality, security, and best practices.

## Context
- PR Title: Add user authentication
- Author: ai-developer (ai_agent)
- Current Status: needs_review
- Files changed: 5 (src/auth/*.py)

## Success Criteria
- All files reviewed
- Issues documented with line numbers
- Overall assessment provided (approve/request changes)

## Output Requirements
Return: `[DONE] review_pr_123 - <approve|request_changes> - N issues found`
Write full review to: docs_dev/pr-reviews/pr-123-review.md

## Constraints
- Do not approve if security issues found
- Report back to coordinator, do not comment on PR directly
"""
```
