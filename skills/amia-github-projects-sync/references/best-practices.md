# Best Practices

## Table of Contents

1. [When following GitHub Projects best practices](#overview)
2. [When managing project board state](#do---project-board-management)
3. [When handling issues and PRs](#do---issue-and-pr-management)
4. [When avoiding common mistakes](#dont---common-mistakes)
5. [When handling inactive issues](#issue-lifecycle-reminders)
6. [When documenting changes](#documentation-practices)

## Overview

This document consolidates best practices for using GitHub Projects Sync effectively. Following these practices ensures consistent, reliable project management.

## DO - Project Board Management

### Keep Project Board in Sync

Always update project status when actual work state changes:

```bash
# When agent starts work
gh issue edit ISSUE --add-label "status:in-progress"
# Also update project item status via GraphQL

# When PR created
gh issue edit ISSUE --add-label "status:ai-review"
```

### Add Meaningful Comments

Document status changes with context:

```bash
gh issue comment ISSUE --body "$(cat <<'EOF'
## Status Update

**Previous**: Todo
**Current**: In Progress
**Agent**: dev-agent-1
**Time**: 2024-01-15 10:30 UTC

Started implementation of login endpoint.
Expected completion: 2024-01-16
EOF
)"
```

### Use Labels Consistently

Apply labels from the defined taxonomy (see [label-taxonomy.md](./label-taxonomy.md)):

- Always include `type:*` label
- Always include `priority:*` label
- Update `status:*` labels with state changes
- Add `component:*` labels for affected areas

### Link All Related Issues and PRs

- Reference parent issues: `Part of #42`
- Use closing keywords: `Closes #42`, `Fixes #42`
- Link related issues in body

### Track Progress in Parent Issues

Keep epic/parent issues updated:

```markdown
## Progress

- [x] #43 User Registration - MERGED
- [ ] #44 User Authentication - IN PROGRESS
- [ ] #45 Password Reset - TODO

**Progress**: 1/3 (33%)
```

### Document All Bug Reproduction Attempts

Before closing bugs, document attempts:

```markdown
## Reproduction Attempts

- [x] Attempt 1 (2024-01-15): Tried on macOS Chrome 120, could not reproduce
- [x] Attempt 2 (2024-01-16): Used reporter's exact steps, still no issue
- [x] Attempt 3 (2024-01-17): Tested on Windows Firefox, no reproduction

**Conclusion**: Unable to reproduce after 3 documented attempts.
```

### Keep Issues OPEN Until Genuinely Resolved

An issue is resolved ONLY when:

- Feature: Implemented, tested, and merged
- Bug: Fixed and verified OR cannot reproduce after 3 attempts
- Chore: Completed and verified

## DO - Issue and PR Management

### Verify Before Updating Status

Check actual state before changing status:

```bash
# Verify PR exists before marking "AI Review"
gh pr list --head BRANCH --json number,state

# Verify CI passes before approving
gh pr checks PR_NUMBER
```

### Use Synchronization Scripts

Run kanban sync regularly:

```bash
python scripts/amia_kanban_sync.py --owner OWNER --repo REPO --project NUMBER
```

### Respond to Blocked Items Promptly

When items are blocked:

1. Document blocker in comment
2. Add `status:blocked` label
3. Link to blocking issue if applicable
4. Escalate if critical

### Archive Completed Items

After sprint completion:

```bash
# Archive done items older than 30 days
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!) {
    archiveProjectV2Item(input: {
      projectId: $projectId
      itemId: $itemId
    }) { item { id } }
  }
' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID"
```

## DON'T - Common Mistakes

### DON'T Update Status Without Verification

**Wrong:**

```bash
# Blindly updating status
gh issue edit ISSUE --add-label "status:done"
```

**Right:**

```bash
# Verify PR merged first
STATE=$(gh pr view PR_NUMBER --json state --jq '.state')
if [ "$STATE" = "MERGED" ]; then
  gh issue edit ISSUE --add-label "status:done"
fi
```

### DON'T Create Duplicate Issues

Before creating, search for existing:

```bash
gh issue list --search "login authentication" --state all
```

### DON'T Ignore Blocked Items

Blocked items need attention. Set up alerts:

```bash
# Check for blocked items daily
gh issue list --label "status:blocked" --state open
```

### DON'T Remove Labels Arbitrarily

Labels should be updated, not arbitrarily removed:

```bash
# Wrong: just removing
gh issue edit ISSUE --remove-label "priority:high"

# Right: update with reason
gh issue comment ISSUE --body "Priority changed: high → normal (no longer urgent)"
gh issue edit ISSUE --remove-label "priority:high" --add-label "priority:normal"
```

### DON'T Close Issues Without Confirmation

Always verify before closing:

1. Acceptance criteria met
2. Tests passing
3. PR merged (for features/bugs)
4. Documentation updated (if applicable)

### DON'T Use Stale Bots or Auto-Close

**PROHIBITED:**

- Stale bots that close inactive issues
- Auto-close after X days of inactivity
- Bulk closing of old issues

### DON'T Close Issues Due to Inactivity

Inactivity means the issue needs attention, not closure.

Use labels instead:

- `needs-attention`
- `awaiting-response`
- `low-priority`

### DON'T Close Bugs Without 3 Reproduction Attempts

Every bug closure must have 3 documented attempts.

## Issue Lifecycle Reminders

### For Inactive Issues

| Situation | Action |
|-----------|--------|
| No activity 30+ days | Add `needs-attention`, ping assignee |
| No response 14+ days | Add `awaiting-response` |
| Blocked externally | Add `blocked`, link dependency |
| Low priority | Keep OPEN, add `low-priority` |

### For Bug Closure

1. Bug fixed and verified: Close as completed
2. Cannot reproduce after 3 attempts: Close with `cannot-reproduce`
3. Duplicate: Close with reference to original
4. By design: Close with explanation

### For Feature Closure

1. Implemented and merged: Close as completed
2. Explicitly declined: Close with reason documented
3. Superseded: Close with reference to replacement
4. Never close due to inactivity

## Documentation Practices

### Always Comment on Transitions

Every status change should have a comment explaining:

- What changed
- Why it changed
- What's next

### Update Related Documentation

When closing issues:

- Update README if behavior changed
- Update API docs if endpoints changed
- Update CHANGELOG

### Maintain Traceability

Every commit, PR, and issue should be linked:

- Commits reference issues: `fix: login validation (#42)`
- PRs reference issues: `Closes #42`
- Issues reference related issues
