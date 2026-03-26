# Memory File Templates

## Table of Contents

- [PR State Comment Template](#pr-state-comment-template)
- [Current Work Handoff Template](#current-work-handoff-template)
- [Patterns Learned Template](#patterns-learned-template)
- [Release History Entry Template](#release-history-entry-template)
- [CI State Template](#ci-state-template)
- [Integration Issue Comment Template](#integration-issue-comment-template)
- [Quick Copy-Paste: State Markers](#quick-copy-paste-state-markers)

## PR State Comment Template

Copy-paste this template when posting PR review state:

```markdown
<!-- AMIA-SESSION-STATE {"pr": [PR_NUMBER], "status": "[STATUS]", "round": [N], "timestamp": "[ISO_TIMESTAMP]"} -->

## AMIA Review - Round [N]

**Status**: [not_started|in_progress|changes_requested|approved]
**Review Date**: [YYYY-MM-DD]
**Reviewer**: AMIA (Integrator Agent)

### Patterns Observed

- [Pattern 1]: [Description]
- [Pattern 2]: [Description]

### Feedback Given

- **File**: [file.py]
  - Line [N]: [Feedback]
  - Line [M]: [Feedback]

### Blockers

- [Blocker 1]: [Description]
- [Blocker 2]: [Description]

### Next Steps

- [ ] [Action required from PR author]
- [ ] [Action required from AMIA]
```

## Current Work Handoff Template

Copy-paste this template for `current.md`:

```markdown
# AMIA Integration Handoff

**Last Updated**: [ISO 8601 timestamp]
**Session**: [Session ID]
**Created By**: AMIA (Integrator Agent)

## Current Task

[One-line task description]

## Progress

- [x] [Completed action]
- [ ] [In progress action] (50% done)
- [ ] [Pending action]

## Context

[Critical context needed to continue]

### Key Decisions Made

- [Decision 1]: [Rationale]

### Patterns Observed

- [Pattern 1]: [Where observed]

## Blockers

- [Blocker 1]: [Description and workaround if available]

## Next Steps

1. [Most urgent action]
2. [Second action]
3. [Third action]

## Links

- PR: #[number]
- Issue: #[number]
- Workflow run: [URL]

## Notes

[Additional context]
```

## Patterns Learned Template

Copy-paste this template when appending to `patterns-learned.md`:

```markdown
## [Pattern Name] - [YYYY-MM-DD]

**Description**: [What the pattern is]
**Category**: [error_handling|testing|architecture|performance|security]
**Observed In**: PR #[number], file [filename]
**Frequency**: [1st occurrence|2nd occurrence|recurring]
**Severity**: [low|medium|high]

### What to Look For

[How to recognize this pattern in code]

### Action

[What to do when this pattern is observed]

### Example

```[language]
[Code example showing the pattern]
```

### Related Patterns

- [Related pattern 1]
- [Related pattern 2]

```

## Release History Entry Template

Copy-paste this template when appending to `release-history.md`:

```markdown
| v[X.Y.Z] | [YYYY-MM-DD] | [staging|production] | [deployed|rolled_back] | [Notes] |
```

**Full table header** (if starting new file):

```markdown
# Release History

**Last Updated**: [ISO 8601 timestamp]

| Version | Date | Target | Status | Notes |
|---------|------|--------|--------|-------|
| v1.0.0 | 2025-01-15 | production | deployed | Initial release |
```

## CI State Template

Copy-paste this template for `ci-states.md`:

```markdown
# CI/CD States

**Last Updated**: [ISO 8601 timestamp]

## Latest Workflow Run

**Workflow**: [workflow-name]
**Status**: [passing|failing|pending]
**Run URL**: [GitHub Actions run URL]
**Commit SHA**: [commit hash]
**PR**: #[number]

### Failures

- **Job**: [job-name]
  - **Step**: [step-name]
  - **Error**: [error message]
  - **Cause**: [root cause]
  - **Fix**: [how to fix]

### Flaky Tests

- [test-name]: [description of flakiness]

### Notes

[Any additional context about CI state]
```

## Integration Issue Comment Template

Copy-paste this template when commenting on integration issues:

```markdown
## AMIA Integration Update

**Date**: [YYYY-MM-DD]
**Status**: [investigating|diagnosed|fixing|resolved]

### Diagnosis

[Root cause analysis]

### Solution

[Proposed or implemented solution]

### Testing

- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing completed

### Links

- PR: #[number]
- Workflow run: [URL]
- Related issues: #[number]

### Next Steps

1. [Action 1]
2. [Action 2]
```

## Quick Copy-Paste: State Markers

Use these HTML comment markers in GitHub comments:

```html
<!-- AMIA-SESSION-STATE {...} -->      # PR review state
<!-- AMIA-INTEGRATION-STATE {...} -->  # Integration issue state
<!-- AMIA-RELEASE-STATE {...} -->      # Release state
<!-- AMIA-CI-STATE {...} -->           # CI/CD state
```

JSON structure inside state markers:

```json
{
  "type": "pr_review",
  "pr": 123,
  "status": "approved",
  "round": 2,
  "timestamp": "2025-02-04T15:42:00Z",
  "blockers": []
}
```
