# Milestone Tracking - Part 2: Assigning Issues to Milestones

## Table of Contents

- [3.2 Assigning Issues to Milestones](#32-assigning-issues-to-milestones)
  - [3.2.1 Single Issue Assignment](#321-single-issue-assignment)
  - [3.2.2 Bulk Assignment](#322-bulk-assignment)
  - [3.2.3 Moving Between Milestones](#323-moving-between-milestones)

---

## 3.2 Assigning Issues to Milestones

### 3.2.1 Single Issue Assignment

**Using gh CLI:**

```bash
# Assign issue #123 to milestone "v2.1.0"
gh issue edit 123 --repo owner/repo --milestone "v2.1.0"
```

**Using GitHub API:**

```bash
# Get milestone number first
milestone_number=$(gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | select(.title=="v2.1.0") | .number')

# Assign to issue
gh api repos/{owner}/{repo}/issues/123 \
  --method PATCH \
  -F milestone="${milestone_number}"
```

**Python implementation:** the helper `assign_issue(repo, issue_number, milestone_title)` in [`scripts/amia_milestone_progress.py`](../scripts/amia_milestone_progress.py) wraps the same two-step logic — resolve the milestone by title, then run `gh issue edit <n> --repo <repo> --milestone <title>` — returning `True` on success. It calls `gh` through a fixed argument vector, so the title is never interpolated into a shell command.

### 3.2.2 Bulk Assignment

**Assign multiple issues to a milestone:**

```bash
# Assign issues 1, 2, 3, 4, 5 to milestone
for issue in 1 2 3 4 5; do
  gh issue edit $issue --repo owner/repo --milestone "v2.1.0"
done
```

**Assign all issues with a specific label:**

```bash
# Get all issues with label "ready-for-release"
issues=$(gh issue list --repo owner/repo \
  --label "ready-for-release" \
  --state open \
  --json number \
  --jq '.[].number')

# Assign each to milestone
for issue in $issues; do
  gh issue edit $issue --repo owner/repo --milestone "v2.1.0"
done
```

**Python bulk assignment:** run [`scripts/amia_milestone_progress.py`](../scripts/amia_milestone_progress.py) with the `bulk-assign` command:

```bash
python3 scripts/amia_milestone_progress.py bulk-assign \
  --repo owner/repo --milestone "v2.1.0" --issues 1 2 3 4 5
```

It assigns each issue in turn and returns a JSON object listing the `success` and `failed` issue numbers, so a partial failure is visible rather than silent.

### 3.2.3 Moving Between Milestones

**Move issue from one milestone to another:**

```bash
# Simply assign to new milestone (replaces old one)
gh issue edit 123 --repo owner/repo --milestone "v2.2.0"
```

**Remove from milestone (unassign):**

```bash
# Using API to set milestone to null
gh api repos/{owner}/{repo}/issues/123 \
  --method PATCH \
  -F milestone=null
```

**Bulk move - all issues from one milestone to another:**

```bash
# Get all open issues from old milestone
issues=$(gh issue list --repo owner/repo \
  --milestone "v2.0.0" \
  --state open \
  --json number \
  --jq '.[].number')

# Move to new milestone
for issue in $issues; do
  gh issue edit $issue --repo owner/repo --milestone "v2.1.0"
done
```

---

[Back to Milestone Tracking Index](milestone-tracking.md)
