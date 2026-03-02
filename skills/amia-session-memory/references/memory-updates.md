# Memory Updates

## Contents

- [State-Based Update Triggers](#state-based-update-triggers)
- [Update Decision Tree](#update-decision-tree)
- [Memory Update Commands](#memory-update-commands)
  - [Update PR State Comment](#update-pr-state-comment)
  - [Append to Patterns Learned](#append-to-patterns-learned)
  - [Update Release History](#update-release-history)
  - [Update CI States](#update-ci-states)
  - [Write Handoff Document](#write-handoff-document)
- [Update Patterns](#update-patterns)
  - [Write-Through (Immediate)](#write-through-immediate)
  - [Append (Accumulate)](#append-accumulate)
  - [Overwrite (Latest State)](#overwrite-latest-state)
- [Verification](#verification)
- [Error Handling](#error-handling)

## State-Based Update Triggers

Memory should be **updated immediately** after these events:

| Event | Memory to Update | Location |
|-------|------------------|----------|
| PR review completed | PR review state | GitHub PR comment |
| Pattern observed | Patterns learned | handoffs/patterns-learned.md |
| Integration issue resolved | Integration history | GitHub issue comment |
| Release approved/deployed | Release history | handoffs/release-history.md |
| CI failure diagnosed | CI states | handoffs/ci-states.md |
| Session ending with incomplete work | Current work state | handoffs/current.md |

## Update Decision Tree

```
Action completed
  ├─ PR-specific? (review, feedback, approval)
  │    └─ Yes → Update PR comment with state marker
  ├─ Pattern observed? (code quality, anti-pattern)
  │    └─ Yes → Append to patterns-learned.md
  ├─ Release decision made?
  │    └─ Yes → Update release-history.md
  ├─ CI failure diagnosed?
  │    └─ Yes → Update ci-states.md
  ├─ Session ending?
  │    └─ Yes → Write current.md handoff
  └─ No update needed → Continue
```

## Memory Update Commands

### Update PR State Comment

```bash
# Post new comment with state marker
gh pr comment <PR_NUMBER> --body "$(cat <<'EOF'
<!-- AMIA-SESSION-STATE {"pr": 123, "status": "approved", "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"} -->

## AMIA Review - Round 2

**Status**: Approved
**Patterns Observed**: Error handling improved, test coverage adequate
**Next Steps**: Ready to merge
EOF
)"
```

### Append to Patterns Learned

```bash
# Append new pattern
cat >> "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/patterns-learned.md" <<'EOF'

## [Pattern Name] - $(date +%Y-%m-%d)

**Description**: [What the pattern is]
**Observed In**: PR #123
**Frequency**: 2nd occurrence
**Action**: [What to do when seen]

EOF
```

### Update Release History

```bash
# Append release entry
cat >> "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/release-history.md" <<'EOF'

| v1.2.3 | 2025-02-04 | production | deployed | Approved after successful staging run |

EOF
```

### Update CI States

```bash
# Overwrite with latest state
cat > "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/ci-states.md" <<'EOF'
# CI/CD States

**Last Updated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Latest Workflow Run

**Workflow**: test-suite
**Status**: Passing
**Run**: https://github.com/org/repo/actions/runs/12345
**Notes**: All tests passing after flaky test fix

EOF
```

### Write Handoff Document

```bash
# Create/overwrite current work state
cat > "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md" <<'EOF'
# AMIA Integration Handoff

**Last Updated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Session**: [Session ID if available]

## Current Task

[Describe what you're working on]

## Progress

- [x] Completed step 1
- [ ] In progress: step 2
- [ ] Pending: step 3

## Blockers

[List any blockers]

## Next Steps

1. [First action for next session]
2. [Second action]

## Context

[Any important context for next session]

## Links

- PR: #123
- Issue: #456
- Workflow run: https://github.com/org/repo/actions/runs/12345

EOF
```

## Update Patterns

### Write-Through (Immediate)

For PR-specific state, write **immediately after event**:
- Review completed → Post PR comment
- Approval given → Post PR comment

### Append (Accumulate)

For patterns and history, **append new entries**:
- Pattern observed → Append to patterns-learned.md
- Release deployed → Append to release-history.md

### Overwrite (Latest State)

For current states, **overwrite with latest**:
- CI state changed → Overwrite ci-states.md
- Session ending → Overwrite current.md

## Verification

After writing memory, **verify persistence**:

```bash
# Verify PR comment posted
gh pr view <PR_NUMBER> --comments | grep "AMIA-SESSION-STATE"

# Verify file written
test -f "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md" && echo "OK"

# Verify file readable
cat "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md" | head -5
```

## Error Handling

**If PR comment fails:**
- Fallback to handoff document: `$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/pr-<PR_NUMBER>-state.md`

**If file write fails:**
- Check directory exists: `mkdir -p $CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/`
- Check permissions: `ls -ld $CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/`
