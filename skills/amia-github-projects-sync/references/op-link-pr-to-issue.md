# Operation: Link PR to Issue


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Linking Methods](#linking-methods)
  - [Method 1: PR Description Keywords](#method-1-pr-description-keywords)
  - [Method 2: PR Title](#method-2-pr-title)
  - [Method 3: Commit Messages](#method-3-commit-messages)
- [Procedure](#procedure)
- [Command: Create Linked PR](#command-create-linked-pr)
- [Changes](#changes)
- [Command: Update Existing PR](#command-update-existing-pr)
- [Verify Link](#verify-link)
- [Output](#output)
- [Cross-Repository Linking](#cross-repository-linking)
- [Behavior on Merge](#behavior-on-merge)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-link-pr-to-issue |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | GitHub Projects Sync |
| **Agent** | api-coordinator |

## Purpose

Link a Pull Request to a GitHub Issue so that merging the PR automatically closes the issue and moves it to Done.

## Preconditions

- Issue exists and is open
- PR is created
- PR is in the same repository as the issue (or linked repo)

## Linking Methods

### Method 1: PR Description Keywords

Add closing keywords in the PR body:

| Keyword | Example |
|---------|---------|
| `Closes` | `Closes #42` |
| `Fixes` | `Fixes #42` |
| `Resolves` | `Resolves #42` |

Multiple issues:
```markdown
Closes #42, #43, #44
```

### Method 2: PR Title

Include the issue reference in the PR title:
```
feat: Implement authentication (Closes #42)
```

### Method 3: Commit Messages

Use closing keywords in commit messages:
```
git commit -m "Add login endpoint (Fixes #42)"
```

## Procedure

1. Identify the issue number(s) to link
2. Add closing keyword to PR body/title/commits
3. Push the PR
4. Verify link appears in GitHub UI

## Command: Create Linked PR

```bash
gh pr create \
  --title "Implement feature X" \
  --body "## Summary
Implements the authentication module.

Closes #42

## Changes
- Added login endpoint
- Added token validation" \
  --base main \
  --head feature/auth
```

## Command: Update Existing PR

```bash
gh pr edit 50 --body "$(gh pr view 50 --json body -q .body)

Closes #42"
```

## Verify Link

```bash
# Check issue for linked PRs
gh issue view 42 --json timelineItems | \
  jq '.timelineItems[] | select(.type == "CROSS_REFERENCED_EVENT")'

# Check PR for linked issues
gh pr view 50 --json closingIssuesReferences
```

## Output

```json
{
  "pr_number": 50,
  "linked_issues": [42, 43],
  "auto_close_enabled": true
}
```

## Cross-Repository Linking

For issues in different repos:
```markdown
Closes owner/other-repo#42
```

## Behavior on Merge

When the PR is merged:
1. Linked issues are automatically closed
2. On the Kanban board, issues move to Done
3. Timeline shows the closing PR

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Issue not closed on merge | Keyword misspelled | Use exact keywords: Closes, Fixes, Resolves |
| Link not showing | Wrong issue number | Verify issue exists and number is correct |
| Cross-repo link fails | No permission | Ensure access to both repositories |

## Best Practices

1. Always include closing keyword in PR body (most visible)
2. Use "Closes" for feature implementations
3. Use "Fixes" for bug fixes
4. Reference issue in PR title for quick identification
5. One PR should close one primary issue (avoid many-to-one)

## Related Operations

- [op-update-item-status.md](op-update-item-status.md) - Manual status update
- [op-add-issue-comment.md](op-add-issue-comment.md) - Add comment linking to PR
