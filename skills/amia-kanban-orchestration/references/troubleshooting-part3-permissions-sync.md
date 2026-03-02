# Troubleshooting Part 3: Permissions and Sync Issues

## Table of Contents

- [10.5 Permission Denied](#105-permission-denied)
  - [Insufficient Token Scopes](#insufficient-token-scopes)
  - [Not Project Admin](#not-project-admin)
  - [Repository Access](#repository-access)
- [10.6 Sync Issues](#106-sync-issues)
  - [Issue Open but Shown as Done](#issue-open-but-shown-as-done)
  - [PR Merged but Not Done](#pr-merged-but-not-done)
  - [Multiple Items in Wrong Status](#multiple-items-in-wrong-status)

## 10.5 Permission Denied

### Insufficient Token Scopes

**Symptom:** Operation fails with permissions error.

**Diagnosis:**
```bash
gh auth status --show-token | grep -i scope
```

**Required Scopes:**
- `repo` - Full repository access
- `project` - Project access
- `read:org` - Organization read (for org projects)

**Solution:**
```bash
gh auth refresh --scopes repo,project,read:org
```

### Not Project Admin

**Symptom:** Cannot modify project settings.

**Diagnosis:**
- Check project role in GitHub UI
- Owner > Admin > Write > Read

**Solution:**
Request admin access from project owner.

### Repository Access

**Symptom:** Cannot access issues in repository.

**Diagnosis:**
```bash
gh repo view OWNER/REPO --json defaultBranch
```

**Solution:**
- Request repository access
- Or check if private repo

---

## 10.6 Sync Issues

**Symptom:** Board state doesn't match actual work state.

### Issue Open but Shown as Done

**Cause:** Issue moved to Done but PR not merged, or manual error.

**Diagnosis:**
```bash
# Check issue state
gh issue view 42 --json state,stateReason

# Check linked PR
gh pr list --search "closes:#42" --json state,merged
```

**Solution:**
```bash
# If PR not merged, move back to AI Review
# [GraphQL mutation to set Status = "AI Review"]

# Or close issue if actually done
gh issue close 42
```

### PR Merged but Not Done

**Cause:** PR merged but board not updated (automation failed).

**Diagnosis:**
```bash
# Check PR status
gh pr view 123 --json merged,mergedAt

# Check issue status
gh issue view 42 --json state
```

**Solution:**
```bash
# Close issue
gh issue close 42 --reason completed

# Update board status
# [GraphQL mutation to set Status = "Done"]
```

### Multiple Items in Wrong Status

**Cause:** Mass sync failure or manual errors.

**Solution: Reconciliation Script**
```bash
# Get all items and their actual state
gh api graphql -f query='...' | jq '...' > board_state.json

# Compare with GitHub state
for item in $(jq -r '.[] | .issue' board_state.json); do
  ACTUAL_STATE=$(gh issue view $item --json state --jq '.state')
  BOARD_STATUS=$(jq -r --arg i "$item" '.[] | select(.issue == ($i | tonumber)) | .status' board_state.json)

  if [ "$ACTUAL_STATE" == "CLOSED" ] && [ "$BOARD_STATUS" != "Done" ]; then
    echo "Issue #$item: Closed but status is $BOARD_STATUS"
    # Fix: update to Done
  fi
done
```
