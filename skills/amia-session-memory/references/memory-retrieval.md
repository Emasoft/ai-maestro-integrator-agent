# Memory Retrieval

## Table of Contents

- State-Based Triggers
- Retrieval Decision Tree
- Memory Retrieval Commands
- Load PR State
- Load Handoff Documents
- Verify Memory Freshness
- Handling Missing Memory
- Memory Freshness Checks

## State-Based Triggers

Memory retrieval is **triggered by user prompts** that indicate continuation of prior work:

| Trigger Phrase | Memory to Load | Command |
|----------------|---------------|---------|
| "Continue PR review #N" | PR comment state | `gh pr view N --comments` |
| "Resume integration work" | Current handoff | `cat $CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md` |
| "What patterns have we seen?" | Patterns learned | `cat $CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/patterns-learned.md` |
| "Last release info" | Release history | `cat $CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/release-history.md` |
| "CI failure history" | CI states | `cat $CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/ci-states.md` |

## Retrieval Decision Tree

```
User prompt received
  ├─ Contains PR number?
  │    ├─ Yes → Load PR comments for that PR
  │    └─ No → Continue
  ├─ Mentions "continue" or "resume"?
  │    ├─ Yes → Load current.md handoff
  │    └─ No → Continue
  ├─ Asks about patterns or history?
  │    ├─ Yes → Load patterns-learned.md or release-history.md
  │    └─ No → Continue
  └─ No memory needed → Proceed without loading
```

## Memory Retrieval Commands

### Load PR State

```bash
# Get all comments with state marker
gh pr view <PR_NUMBER> --comments --json comments \
  | jq -r '.comments[] | select(.body | contains("AMIA-SESSION-STATE")) | .body'

# Extract just the JSON state
gh pr view <PR_NUMBER> --comments --json comments \
  | jq -r '.comments[] | select(.body | contains("AMIA-SESSION-STATE")) | .body' \
  | grep -oP '(?<=AMIA-SESSION-STATE ).*(?= -->)'
```

### Load Handoff Documents

```bash
# Load current work state
cat "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md"

# Load patterns learned
cat "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/patterns-learned.md"

# Load release history
cat "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/release-history.md"

# Load CI states
cat "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/ci-states.md"
```

### Verify Memory Freshness

```bash
# Check file timestamps
stat -f "%Sm" "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md"

# Compare with PR last updated
gh pr view <PR_NUMBER> --json updatedAt -q .updatedAt
```

## Handling Missing Memory

**If no memory found:**
1. DO NOT assume prior context
2. Start fresh with current information
3. Build new memory as you work

**If partial memory found:**
1. Load what exists
2. Verify against current GitHub state
3. Fill gaps from actual PR/issue data

## Memory Freshness Checks

Before trusting loaded memory, verify:

| Check | Command | Threshold |
|-------|---------|-----------|
| File age | `stat -f "%Sm" <file>` | < 7 days |
| PR updated | `gh pr view <PR> --json updatedAt` | Compare timestamps |
| Issue updated | `gh issue view <ISSUE> --json updatedAt` | Compare timestamps |

If memory is stale (> 7 days or PR updated since), re-validate against current state.
