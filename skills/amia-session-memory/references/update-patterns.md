# Update Patterns

## Contents

- [Pattern 1: Immediate PR State Update](#pattern-1-immediate-pr-state-update)
- [Pattern 2: Append to Patterns Learned](#pattern-2-append-to-patterns-learned)
- [Pattern 3: Release History Update](#pattern-3-release-history-update)
- [Pattern 4: CI State Overwrite](#pattern-4-ci-state-overwrite)
- [Pattern 5: Handoff Document Write](#pattern-5-handoff-document-write)
- [Batch Update Pattern](#batch-update-pattern)
- [Update Verification Pattern](#update-verification-pattern)
- [Update Conflict Resolution](#update-conflict-resolution)
- [Update Timing Best Practices](#update-timing-best-practices)

## Pattern 1: Immediate PR State Update

**Trigger**: PR review completed (feedback given, changes requested, or approved)

**Update Logic**:

```bash
# Step 1: Prepare state JSON
STATE_JSON=$(cat <<EOF
{
  "pr": $PR_NUM,
  "status": "$STATUS",
  "round": $ROUND,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "blockers": []
}
EOF
)

# Step 2: Prepare comment body
COMMENT_BODY=$(cat <<EOF
<!-- AMIA-SESSION-STATE $STATE_JSON -->

## AMIA Review - Round $ROUND

**Status**: $STATUS
**Patterns Observed**: [list patterns]
**Next Steps**: [list next steps]
EOF
)

# Step 3: Post comment
gh pr comment $PR_NUM --body "$COMMENT_BODY"

# Step 4: Verify posted
gh pr view $PR_NUM --comments | grep "AMIA-SESSION-STATE" && echo "State saved successfully"
```

**When**: IMMEDIATELY after review actions (approve, request changes, comment)

## Pattern 2: Append to Patterns Learned

**Trigger**: New code pattern observed during review

**Update Logic**:

```bash
# Step 1: Ensure file exists
PATTERNS_FILE="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/patterns-learned.md"
mkdir -p "$(dirname "$PATTERNS_FILE")"
touch "$PATTERNS_FILE"

# Step 2: Append new pattern
cat >> "$PATTERNS_FILE" <<EOF

## $PATTERN_NAME - $(date +%Y-%m-%d)

**Description**: $DESCRIPTION
**Category**: $CATEGORY
**Observed In**: PR #$PR_NUM, file $FILE
**Frequency**: $FREQUENCY
**Severity**: $SEVERITY

### Action

$ACTION

EOF

# Step 3: Verify appended
tail -10 "$PATTERNS_FILE"
```

**When**: As soon as pattern is recognized (don't wait until end of review)

## Pattern 3: Release History Update

**Trigger**: Release approved, deployed, or rolled back

**Update Logic**:

```bash
# Step 1: Ensure file exists with header
RELEASE_FILE="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/release-history.md"
mkdir -p "$(dirname "$RELEASE_FILE")"

if [ ! -f "$RELEASE_FILE" ]; then
  cat > "$RELEASE_FILE" <<EOF
# Release History

**Last Updated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)

| Version | Date | Target | Status | Notes |
|---------|------|--------|--------|-------|
EOF
fi

# Step 2: Append new release entry
echo "| $VERSION | $(date +%Y-%m-%d) | $TARGET | $STATUS | $NOTES |" >> "$RELEASE_FILE"

# Step 3: Update "Last Updated" timestamp
sed -i '' "s/^\\*\\*Last Updated\\*\\*:.*/**Last Updated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)/" "$RELEASE_FILE"

# Step 4: Verify appended
tail -5 "$RELEASE_FILE"
```

**When**: IMMEDIATELY after release decision (don't wait)

## Pattern 4: CI State Overwrite

**Trigger**: CI workflow completes (pass or fail)

**Update Logic**:

```bash
# Step 1: Overwrite CI state file (not append, overwrite)
CI_FILE="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/ci-states.md"
mkdir -p "$(dirname "$CI_FILE")"

cat > "$CI_FILE" <<EOF
# CI/CD States

**Last Updated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Latest Workflow Run

**Workflow**: $WORKFLOW_NAME
**Status**: $STATUS
**Run URL**: $RUN_URL
**Commit SHA**: $COMMIT_SHA
**PR**: #$PR_NUM

### Notes

$NOTES

EOF

# Step 2: Verify written
cat "$CI_FILE"
```

**When**: After each significant CI event (not every run, but failures and first pass after failures)

## Pattern 5: Handoff Document Write

**Trigger**: Session ending with incomplete work

**Update Logic**:

```bash
# Step 1: Overwrite current.md (not append)
HANDOFF_FILE="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md"
mkdir -p "$(dirname "$HANDOFF_FILE")"

cat > "$HANDOFF_FILE" <<EOF
# AMIA Integration Handoff

**Last Updated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Session**: $SESSION_ID
**Created By**: AMIA (Integrator Agent)

## Current Task

$TASK_DESCRIPTION

## Progress

$PROGRESS_CHECKLIST

## Blockers

$BLOCKERS

## Next Steps

$NEXT_STEPS

## Links

$LINKS

EOF

# Step 2: Verify written
test -f "$HANDOFF_FILE" && echo "Handoff saved successfully"

# Step 3: If urgent, post issue comment with link
if [ -n "$RELATED_ISSUE" ]; then
  gh issue comment $RELATED_ISSUE --body "AMIA handoff created: \`thoughts/shared/handoffs/amia-integration/current.md\`"
fi
```

**When**: When session is ending (context compaction imminent, user says "stop", or work incomplete)

## Batch Update Pattern

**Scenario**: Multiple updates needed at once (e.g., PR approved, pattern observed, CI passing)

**Update Logic**:

```bash
# Perform updates in parallel (independent operations)
(
  # Update 1: PR state comment
  gh pr comment $PR_NUM --body "$PR_STATE_COMMENT" &

  # Update 2: Append pattern
  cat >> "$PATTERNS_FILE" <<EOF
$PATTERN_ENTRY
EOF
  &

  # Update 3: Update CI state
  cat > "$CI_FILE" <<EOF
$CI_STATE
EOF
  &

  # Wait for all to complete
  wait
)

echo "All updates completed"
```

**When**: Multiple independent memory updates triggered simultaneously

## Update Verification Pattern

**Always verify updates completed successfully**:

```bash
# Verify PR comment posted
gh pr view $PR_NUM --comments | grep "AMIA-SESSION-STATE" || echo "ERROR: PR comment failed"

# Verify file written
test -f "$FILE_PATH" && echo "File written" || echo "ERROR: File write failed"

# Verify file readable
cat "$FILE_PATH" | head -3 || echo "ERROR: File not readable"
```

## Update Conflict Resolution

**Scenario**: Multiple sessions trying to update same memory

**Resolution**:

1. PR comments: No conflict (GitHub handles sequential comments)
2. Handoff files: Last write wins (use file locking if critical)

```bash
# Optional: Use flock for critical file writes
(
  flock -x 200
  cat > "$HANDOFF_FILE" <<EOF
$CONTENT
EOF
) 200>"$HANDOFF_FILE.lock"
```

## Update Timing Best Practices

| Update Type | Timing | Rationale |
|-------------|--------|-----------|
| PR state | Immediate after review | Ensures state captured before session ends |
| Patterns learned | As observed | Don't wait until end (might forget) |
| Release history | Immediate after release | Critical for rollback decisions |
| CI state | After significant events | Avoid noise from every run |
| Handoff docs | When ending session | Last action before context compaction |
