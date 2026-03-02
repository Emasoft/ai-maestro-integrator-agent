---
name: amia-session-memory
description: "Session memory for PR reviews and integration work. Use when resuming reviews, tracking releases, or persisting context across sessions. Trigger with session resumption."
license: Apache-2.0
version: 1.0.0
compatibility: Requires familiarity with AMIA role responsibilities (code review, integration, releases). Designed for maintaining context across Claude Code session boundaries. Requires AI Maestro installed.
triggers:
  - Resume a PR review that was started in a previous session
  - Continue integration work after context compaction
  - Recall previous feedback given on similar code patterns
  - Track release history and rollback decisions
  - Maintain CI/CD pipeline state awareness
  - Handoff integration work to another session
metadata:
  author: Emasoft
  version: 1.0.0
agent: amia-main
context: fork
workflow-instruction: "support"
procedure: "support-skill"
user-invocable: false
---

# AMIA Session Memory Skill

## Overview

This skill teaches how to **persist and retrieve session context** so that integration work can continue seamlessly across session boundaries.

**The Core Problem**: Claude Code sessions have limited context. When context compacts or sessions restart, all knowledge of ongoing reviews, patterns observed, and integration states is lost.

**The Solution**: Store memory in persistent locations (GitHub PR comments, issue comments, handoff documents) and retrieve it based on state-based triggers.

## Prerequisites

Before using this skill, ensure:
1. You understand your AMIA role (quality gates, reviews, merging, releases)
2. `gh` CLI is configured and authenticated
3. `$CLAUDE_PROJECT_DIR` is set and writable
4. You have read access to PR comments and issue comments
5. You have familiarity with the project's handoff directory structure

## Instructions

1. **When Starting a Session: Detect State-Based Triggers**
   - Check if you're resuming a PR review, integration task, or release
   - Look for GitHub URLs, PR numbers, or issue references in user prompt

2. **When Starting a Session: Load Relevant Memory**
   - If PR-related: Load PR comment state (see [references/memory-retrieval.md](references/memory-retrieval.md))
   - If integration-related: Load handoff documents from `$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/`
   - If release-related: Load release history

3. **When Starting a Session: Verify Memory Freshness**
   - Check timestamps in loaded memory
   - Compare with actual GitHub state (PR status, CI runs, release tags)

4. **When Starting a Session: Proceed with Task**
   - Use loaded memory to inform decisions
   - Update memory as work progresses

5. **When Ending a Session: Identify State to Persist**
   - PR review feedback and patterns observed
   - Integration issues diagnosed
   - Quality gate outcomes
   - Release decisions

6. **When Ending a Session: Write Memory**
   - Update PR comments with state markers (see [references/memory-updates.md](references/memory-updates.md))
   - Write handoff documents if work is incomplete
   - Log release history if applicable

7. **When Ending a Session: Verify Persistence**
   - Confirm PR comments posted
   - Verify handoff files written and readable

### Checklist

Copy this checklist and track your progress:

**Session Start Checklist:**
- [ ] Detect state-based triggers (PR review, integration task, release)
- [ ] Look for GitHub URLs, PR numbers, or issue references in user prompt
- [ ] If PR-related: Load PR comment state
- [ ] If integration-related: Load handoff documents from amia-integration/
- [ ] If release-related: Load release history
- [ ] Check timestamps in loaded memory
- [ ] Compare memory with actual GitHub state (PR status, CI runs, release tags)
- [ ] Proceed with task using loaded memory to inform decisions

**Session End Checklist:**
- [ ] Identify state to persist (PR review, integration issues, quality gates, releases)
- [ ] Update PR comments with state markers
- [ ] Write handoff documents if work is incomplete
- [ ] Log release history if applicable
- [ ] Confirm PR comments posted successfully
- [ ] Verify handoff files written and readable

## Output

Memory outputs take these forms:

| Memory Type | Storage Location | Format |
|-------------|-----------------|--------|
| **PR Review State** | GitHub PR comment | Markdown with HTML state marker |
| **Integration Patterns** | Handoff document | Markdown with timestamped entries |
| **Release History** | Handoff document | Markdown table with release metadata |
| **CI/CD State** | Issue comment or handoff | Markdown with workflow run links |

**Example PR State Comment:**
```markdown
<!-- AMIA-SESSION-STATE {"pr": 123, "status": "review_in_progress", "timestamp": "2025-02-04T15:42:00Z"} -->

## AMIA Review State

**Status**: Review in progress
**Patterns Observed**: Error handling inconsistent in middleware
**Blockers**: None
**Next Steps**: Request changes for error handling
```

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

See [references/memory-architecture.md](references/memory-architecture.md) for:
- Storage locations (PR comments, issue comments, handoff documents)
- Memory file structure
- Data persistence patterns

## What to Remember

See [references/memory-types.md](references/memory-types.md) for:
- PR review states
- Code patterns observed
- Integration issues encountered
- Release history and rollbacks
- CI/CD pipeline states

## Memory Retrieval

See [references/memory-retrieval.md](references/memory-retrieval.md) for:
- State-based triggers
- Retrieval decision tree
- Memory retrieval commands

## Memory Updates

See [references/memory-updates.md](references/memory-updates.md) for:
- State-based update triggers
- Update decision tree
- Memory update commands

## Handoff Documents

See [references/handoff-documents.md](references/handoff-documents.md) for:
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

---

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

---

## Quick Reference

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

### State Markers

Use these HTML comments for machine-readable state:

```html
<!-- AMIA-SESSION-STATE ... -->      # PR review state
<!-- AMIA-INTEGRATION-STATE ... -->  # Integration issue state
<!-- AMIA-RELEASE-STATE ... -->      # Release state
```

---

## Resources

- [references/memory-file-templates.md](references/memory-file-templates.md) - Copy-paste templates
- [references/retrieval-patterns.md](references/retrieval-patterns.md) - Detailed retrieval logic
- [references/update-patterns.md](references/update-patterns.md) - Detailed update logic

---

**Version**: 1.0.0
**Last Updated**: 2025-02-04
**Skill Type**: Session Memory Management
**Difficulty**: Intermediate
**Required Knowledge**: AMIA role responsibilities, GitHub PR/Issue workflows
