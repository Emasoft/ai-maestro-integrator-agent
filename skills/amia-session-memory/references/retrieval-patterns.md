# Retrieval Patterns

## Contents

- [Pattern 1: PR Review Continuation](#pattern-1-pr-review-continuation)
- [Pattern 2: Integration Work Continuation](#pattern-2-integration-work-continuation)
- [Pattern 3: Pattern Lookup](#pattern-3-pattern-lookup)
- [Pattern 4: Release History Lookup](#pattern-4-release-history-lookup)
- [Pattern 5: CI State Lookup](#pattern-5-ci-state-lookup)
- [Combining Multiple Memory Sources](#combining-multiple-memory-sources)
- [Retrieval Performance Optimization](#retrieval-performance-optimization)

## Pattern 1: PR Review Continuation

**Trigger**: User says "continue PR review" or "resume PR #N"

**Retrieval Logic**:

```bash
# Step 1: Extract PR number from user prompt or context
PR_NUM=[extracted number]

# Step 2: Load PR comments
gh pr view $PR_NUM --comments --json comments -q '.comments[]' > /tmp/pr_comments.json

# Step 3: Find AMIA state comment
cat /tmp/pr_comments.json | jq -r 'select(.body | contains("AMIA-SESSION-STATE")) | .body' > /tmp/amia_state.txt

# Step 4: Check if state found
if [ -s /tmp/amia_state.txt ]; then
  echo "Found prior review state"
  cat /tmp/amia_state.txt
else
  echo "No prior state found, starting fresh"
fi

# Step 5: Verify PR not updated since last review
LAST_REVIEW_TS=$(cat /tmp/amia_state.txt | grep -oP '(?<="timestamp": ")[^"]+')
PR_UPDATED_TS=$(gh pr view $PR_NUM --json updatedAt -q .updatedAt)

if [[ "$PR_UPDATED_TS" > "$LAST_REVIEW_TS" ]]; then
  echo "WARNING: PR updated since last review, state may be stale"
fi
```

**Decision Matrix**:

| State Found? | PR Updated? | Action |
|--------------|-------------|--------|
| Yes | No | Use loaded state |
| Yes | Yes | Load state, but re-verify against current PR |
| No | N/A | Start fresh review |

## Pattern 2: Integration Work Continuation

**Trigger**: User says "continue integration" or "resume [task]"

**Retrieval Logic**:

```bash
# Step 1: Check for current handoff
HANDOFF_DIR="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"

if [ -f "$HANDOFF_DIR/current.md" ]; then
  echo "Found handoff document"

  # Step 2: Check freshness
  AGE_DAYS=$(( ($(date +%s) - $(stat -f %m "$HANDOFF_DIR/current.md")) / 86400 ))

  if [ $AGE_DAYS -gt 7 ]; then
    echo "WARNING: Handoff is $AGE_DAYS days old, verify state"
  fi

  # Step 3: Load handoff
  cat "$HANDOFF_DIR/current.md"
else
  echo "No handoff found, starting fresh"
fi
```

**Decision Matrix**:

| Handoff Found? | Age | Action |
|----------------|-----|--------|
| Yes | < 7 days | Use handoff as-is |
| Yes | > 7 days | Load handoff, verify against GitHub |
| No | N/A | Start fresh |

## Pattern 3: Pattern Lookup

**Trigger**: User asks "have we seen [pattern]?" or "what patterns have we learned?"

**Retrieval Logic**:

```bash
# Step 1: Load patterns file
PATTERNS_FILE="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/patterns-learned.md"

if [ -f "$PATTERNS_FILE" ]; then
  # Step 2: Search for pattern by keyword
  KEYWORD="[user query keyword]"
  grep -i "$KEYWORD" "$PATTERNS_FILE" -A 10
else
  echo "No patterns file found"
fi
```

## Pattern 4: Release History Lookup

**Trigger**: User asks "last release", "release history", or "when was [version] released?"

**Retrieval Logic**:

```bash
# Step 1: Load release history
RELEASE_FILE="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/release-history.md"

if [ -f "$RELEASE_FILE" ]; then
  # Step 2: If specific version requested, grep it
  if [ -n "$VERSION" ]; then
    grep "$VERSION" "$RELEASE_FILE"
  else
    # Show last 5 releases
    tail -5 "$RELEASE_FILE"
  fi
else
  # Fallback to git tags
  git tag --sort=-creatordate | head -5
fi
```

## Pattern 5: CI State Lookup

**Trigger**: User asks "CI status", "why did tests fail?", or "what's the pipeline state?"

**Retrieval Logic**:

```bash
# Step 1: Load CI state file
CI_FILE="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/ci-states.md"

if [ -f "$CI_FILE" ]; then
  # Step 2: Check freshness (CI state should be recent)
  AGE_HOURS=$(( ($(date +%s) - $(stat -f %m "$CI_FILE")) / 3600 ))

  if [ $AGE_HOURS -lt 24 ]; then
    cat "$CI_FILE"
  else
    echo "CI state is $AGE_HOURS hours old, fetching fresh data..."
    # Fetch latest workflow run
    gh run list --limit 1 --json conclusion,url,createdAt
  fi
else
  # No state file, fetch from GitHub
  gh run list --limit 5 --json conclusion,url,createdAt
fi
```

## Combining Multiple Memory Sources

Sometimes multiple memory sources are needed:

**Example**: User says "continue PR #42 and check if we've seen similar issues"

**Retrieval Logic**:

```bash
# Load PR state
gh pr view 42 --comments --json comments | jq -r '.comments[] | select(.body | contains("AMIA-SESSION-STATE"))'

# Load patterns learned
cat "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/patterns-learned.md"

# Load related issues (if linked in PR)
gh pr view 42 --json closingIssuesReferences -q '.closingIssuesReferences[] | .number' \
  | xargs -I {} gh issue view {} --comments
```

## Retrieval Performance Optimization

**Rule**: Only load what you need, when you need it.

**Anti-pattern**: Loading all memory files at session start
**Correct pattern**: Load on-demand based on user trigger

**Optimization tips**:
- Use `grep` to search large files before loading fully
- Cache loaded memory in session context (don't re-fetch)
- Set timeouts on GitHub API calls (3s max)
- Fallback to empty state if retrieval takes > 5s
