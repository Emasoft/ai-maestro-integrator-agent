# Memory Types

## Table of Contents

- [PR Review States](#pr-review-states)
- [Code Patterns Observed](#code-patterns-observed)
- [Integration Issues Encountered](#integration-issues-encountered)
- [Release History and Rollbacks](#release-history-and-rollbacks)
- [CI/CD Pipeline States](#cicd-pipeline-states)
- [CI State - 2025-02-04](#ci-state-2025-02-04)
- [When to Remember What](#when-to-remember-what)

## PR Review States

**What to Remember**:

- Review status (not started, in progress, changes requested, approved)
- Feedback already given (avoid repeating comments)
- Code patterns observed (good and bad)
- Suggested changes and their rationale
- Approval blockers

**Storage**: GitHub PR comment with `<!-- AMIA-SESSION-STATE -->` marker

**Example**:

```json
{
  "pr": 123,
  "status": "review_in_progress",
  "round": 2,
  "patterns_observed": ["error_handling_missing", "test_coverage_low"],
  "blockers": [],
  "timestamp": "2025-02-04T15:42:00Z"
}
```

## Code Patterns Observed

**What to Remember**:

- Recurring code quality issues (e.g., missing error handling)
- Good patterns worth reusing (e.g., clean interface design)
- Anti-patterns to flag in future reviews

**Storage**: `$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/patterns-learned.md`

**Format**: Markdown table with pattern name, description, example, frequency

## Integration Issues Encountered

**What to Remember**:

- Merge conflicts resolved and resolution approach
- CI failures diagnosed (cause, fix, prevention)
- Dependency conflicts and solutions
- Build errors and workarounds

**Storage**: GitHub issue comments or handoff documents

## Release History and Rollbacks

**What to Remember**:

- Version numbers and release dates
- Deployment targets (staging, production)
- Approval rationale (why release was greenlit)
- Rollback decisions (why, when, how)
- Post-release issues

**Storage**: `$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/release-history.md`

**Format**: Markdown table with columns: Version | Date | Target | Status | Notes

## CI/CD Pipeline States

**What to Remember**:

- Workflow success/failure patterns
- Flaky tests identified
- Pipeline configuration changes
- Quality gate pass rates

**Storage**: Issue comments linked to workflow runs, or handoff documents

**Example**:

```markdown
## CI State - 2025-02-04

**Workflow**: test-suite
**Run**: https://github.com/org/repo/actions/runs/12345
**Status**: Failed
**Cause**: Flaky test in test_integration.py::test_api_timeout
**Action**: Disabled test temporarily, created issue #456
```

## When to Remember What

| Trigger | Memory Type to Load |
|---------|-------------------|
| "Continue PR review" | PR review state |
| "Resume integration work" | Integration issues |
| "Check release history" | Release history |
| "Why did CI fail last time?" | CI/CD pipeline states |
| "Have we seen this pattern before?" | Code patterns observed |
