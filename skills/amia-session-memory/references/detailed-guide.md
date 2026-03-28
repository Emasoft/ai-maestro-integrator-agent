# AMIA Session Memory — Detailed Guide

## Contents

- [Error Handling](#error-handling)
- [Examples](#examples)
- [Memory Architecture](#memory-architecture)
- [What to Remember](#what-to-remember)
- [Memory Retrieval](#memory-retrieval)
- [Memory Updates](#memory-updates)
- [Handoff Documents](#handoff-documents)
- [Integration with Other Skills](#integration-with-other-skills)
- [Troubleshooting](#troubleshooting)
- [Quick Reference Commands](#quick-reference-commands)
- [State Markers](#state-markers)

## Error Handling

### Missing Memory

**If no memory found:** Start fresh. Do NOT assume prior context exists.

**If partial memory found:** Use what exists, but verify against GitHub state before trusting it.

### Stale Memory

**If timestamps > 7 days old:** Re-validate against current GitHub state. PR may have been updated.

**If PR merged but memory still active:** Archive the state, remove from active reviews.

### Write Failures

**If PR comment fails:** Fallback to handoff document in `thoughts/shared/handoffs/amia-integration/`.

**If handoff write fails:** Check directory exists and is writable. Create if needed.

## Examples

### Example 1: Resume PR Review

**User says**: "Continue reviewing PR #42"

**Actions**:

1. Load PR comment state: `gh pr view 42 --comments --json comments | jq -r '.comments[] | select(.body | contains("AMIA-SESSION-STATE"))'`
2. Check if state found:
   - If yes: Load review state, patterns observed, next steps
   - If no: Start fresh review from scratch
3. Verify PR hasn't been updated since last review (check commit SHAs)
4. Proceed with review using loaded context

### Example 2: Handoff Integration Work

**Scenario**: Session ending mid-integration

**Actions**:

1. Identify incomplete work (e.g., CI failure diagnosis in progress)
2. Create handoff document at `$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md`
3. Include:
   - Current task description
   - Progress made
   - Blockers encountered
   - Next steps
   - Relevant links (PR, issue, workflow run)
4. Post comment on related issue with handoff link

### Example 3: Log Release Decision

**Scenario**: Release approved and deployed

**Actions**:

1. Load release history: `cat $CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/release-history.md`
2. Append new entry with:
   - Version number
   - Release date
   - Deployment target (staging/production)
   - Approval rationale
   - Rollback plan
3. Write updated release history back to file

## Memory Architecture

See `references/memory-architecture.md` for:

- Storage locations (PR comments, issue comments, handoff documents)
- Memory file structure
- Data persistence patterns

## What to Remember

See `references/memory-types.md` for:

- PR review states
- Code patterns observed
- Integration issues encountered
- Release history and rollbacks
- CI/CD pipeline states

## Memory Retrieval

See `references/memory-retrieval.md` for:

- State-based triggers
- Retrieval decision tree
- Memory retrieval commands

## Memory Updates

See `references/memory-updates.md` for:

- State-based update triggers
- Update decision tree
- Memory update commands

## Handoff Documents

See `references/handoff-documents.md` for:

- When to create handoff documents
- Handoff document format
- Handoff checklist

## Integration with Other Skills

| Skill | Memory Interaction |
|-------|-------------------|
| amia-code-review-patterns | Stores review state in PR comments |
| amia-github-pr-workflow | Tracks PR lifecycle state |
| amia-ci-failure-patterns | Records failure diagnoses |
| amia-release-management | Logs release history |
| amia-quality-gates | Tracks gate pass/fail states |

## Troubleshooting

### Memory Not Found

**Symptom**: Starting fresh when continuation expected

**Diagnosis**:

1. Check if handoff directory exists: `ls -la $CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/`
2. Check PR comments for state block: `gh pr view <PR> --comments`
3. Verify file permissions

**Resolution**:

- If directory missing: Previous session did not save state - start fresh
- If files exist but empty: Previous session was interrupted - reconstruct from PR comments
- If PR has state: Load from PR comment directly

### Stale Memory

**Symptom**: Memory contains outdated information

**Diagnosis**:

1. Check timestamps in memory files
2. Compare PR comment state with actual PR status
3. Verify release-history.md against actual releases

**Resolution**:

- If PR was merged: Archive state, clear from active reviews
- If release happened: Update release-history.md from git tags/releases
- If CI config changed: Refresh pipeline status from workflow runs

### Memory Conflicts

**Symptom**: PR comment state differs from handoff document

**Diagnosis**:

1. Compare timestamps - most recent wins
2. Check if PR was updated between sessions

**Resolution**:

- PR comments are source of truth for PR-specific state
- Handoff documents are source of truth for cross-PR state
- When in conflict, re-evaluate current state rather than trusting either

## Quick Reference Commands

### Load Memory Commands

```bash
# Load all AMIA memory
HANDOFF_DIR="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"
cat "$HANDOFF_DIR/current.md"
cat "$HANDOFF_DIR/patterns-learned.md"
cat "$HANDOFF_DIR/release-history.md"

# Load PR-specific state
gh pr view <PR_NUMBER> --comments --json comments \
  | jq -r '.comments[] | select(.body | contains("AMIA-SESSION-STATE"))'
```

### Save Memory Commands

```bash
# Save session state
mkdir -p "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"
cat > "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md" << 'HANDOFF'
[Content here]
HANDOFF

# Update PR state comment
gh pr comment <PR_NUMBER> --body "[State content]"
```

## State Markers

Use these HTML comments for machine-readable state:

```html
<!-- AMIA-SESSION-STATE ... -->      # PR review state
<!-- AMIA-INTEGRATION-STATE ... -->  # Integration issue state
<!-- AMIA-RELEASE-STATE ... -->      # Release state
```

## Full Reference Document Listing

**Architecture and Types:**

- `references/memory-architecture.md` — Storage locations, file structure, persistence patterns
- `references/memory-types.md` — PR states, code patterns, integration issues, release history

**Retrieval and Updates:**

- `references/memory-retrieval.md` — State-based triggers, retrieval decision tree, commands
- `references/memory-updates.md` — Update triggers, decision tree, update commands
- `references/retrieval-patterns.md` — PR review continuation, integration work, pattern lookup
- `references/update-patterns.md` — Immediate PR state, append patterns, release history

**Handoffs and Templates:**

- `references/handoff-documents.md` — When to create, format, checklist
- `references/memory-file-templates.md` — PR state, handoff, patterns-learned templates

**Operations:**

- `references/op-detect-state-triggers.md` — Detect session triggers
- `references/op-load-pr-memory.md` — Load PR comment state
- `references/op-load-handoff-docs.md` — Load handoff documents
- `references/op-load-release-history.md` — Load release history
- `references/op-verify-memory-freshness.md` — Verify timestamps against GitHub
- `references/op-save-pr-state-comment.md` — Save PR state comment
- `references/op-create-handoff-doc.md` — Create handoff document
- `references/op-log-release-decision.md` — Log release decision
- `references/op-archive-stale-memory.md` — Archive stale memory

## Additional Prerequisites (moved from SKILL.md)

- Read access to PR and issue comments
- Handoff directory structure available
