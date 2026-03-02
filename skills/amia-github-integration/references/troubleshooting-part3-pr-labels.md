# Troubleshooting Part 3: Pull Request Linking and Label Issues

[Back to Troubleshooting Index](troubleshooting.md)

## Contents
- Pull Request Linking Issues
  - Problem: Pull request doesn't link to issue
  - Problem: Issue doesn't close when PR merges
- Label System Issues
  - Problem: Label is rejected or doesn't appear on issue
  - Problem: Multiple labels from 9-label system on one issue

---

## Pull Request Linking Issues

### Problem: Pull request doesn't link to issue

**Symptoms:**
- Create PR with "Closes #123" in body
- Issue doesn't show linked PR
- Issue doesn't close when PR merges

**Diagnosis:**

**Step 1: Verify linking keyword**
Check PR body contains exact keyword:
```bash
gh pr view <pr_number> --json body --jq '.body'
```

Look for: `Closes #123`, `Fixes #123`, or `Resolves #123`

**Step 2: Verify issue number**
Ensure issue number is correct:
```bash
gh issue view 123
```

**Solution:**

**Fix PR body:**
```bash
gh pr edit <pr_number> --body "$(gh pr view <pr_number> --json body --jq '.body')

Closes #123"
```

**Common mistakes to avoid:**
- "Close #123" (missing 's')
- "closes: #123" (extra colon)
- "#123" (no keyword)
- "Closes #123" (correct)
- "Fixes #123" (correct)
- "Resolves #123" (correct)

---

### Problem: Issue doesn't close when PR merges

**Symptoms:**
- PR is merged successfully
- Issue remains open
- PR shows as linked to issue

**Cause:** Linking keyword in PR body was not recognized or PR was merged to non-default branch.

**Solution:**

**Verify default branch:**
```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

PR must be merged to default branch (usually `main` or `master`) for auto-close to work.

**If merged to wrong branch:**
Issue will not auto-close. Close manually:
```bash
gh issue close 123 --comment "Resolved by PR #456 (merged to feature branch)"
```

**If linking keyword was missing:**
Close manually and add reference:
```bash
gh issue close 123 --comment "Resolved by PR #456"
```

---

## Label System Issues

### Problem: Label is rejected or doesn't appear on issue

**Symptoms:**
```
Error: label "feature" not found in repository
```

**Cause:**
- Label doesn't exist in repository
- Label name is misspelled
- Label case doesn't match (labels are case-sensitive)

**Solution:**

**Step 1: List all available labels**
```bash
gh label list --limit 100
```

**Step 2: Verify label exists**
Look for exact label name in the list.

**Step 3: Create missing label**
```bash
gh label create "feature" \
  --description "New feature or functionality" \
  --color "0e8a16"
```

**Step 4: Retry adding label to issue**
```bash
gh issue edit <issue_number> --add-label "feature"
```

---

### Problem: Multiple labels from 9-label system on one issue

**Symptoms:**
- Issue has both "feature" and "bug" labels
- Violates 9-label system rule

**Cause:** Manual error or script malfunction.

**Solution:**

**Identify issues with multiple 9-label system labels:**
```bash
#!/bin/bash
# find-multiple-labels.sh

LABELS=("feature" "bug" "refactor" "test" "docs" "performance" "security" "dependencies" "workflow")

gh issue list --limit 1000 --json number,labels | jq -r '
  .[] |
  select([.labels[].name] | map(select(. == "feature" or . == "bug" or . == "refactor" or . == "test" or . == "docs" or . == "performance" or . == "security" or . == "dependencies" or . == "workflow")) | length > 1) |
  "\(.number): \([.labels[].name] | join(", "))"
'
```

**Fix by removing incorrect label:**
```bash
# For each issue, determine which label is correct
gh issue edit <issue_number> --remove-label "incorrect-label"
```
