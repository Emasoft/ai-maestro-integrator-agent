# Milestone Tracking - Part 3: Progress Tracking and Closing

## Table of Contents

- [3.3 Milestone Progress Tracking](#33-milestone-progress-tracking)
  - [3.3.1 Querying Completion Percentage](#331-querying-completion-percentage)
  - [3.3.2 Open vs Closed Issues Count](#332-open-vs-closed-issues-count)
  - [3.3.3 Overdue Detection](#333-overdue-detection)
- [3.4 Closing Milestones](#34-closing-milestones)
  - [3.4.1 When to Close](#341-when-to-close)
  - [3.4.2 Handling Incomplete Issues](#342-handling-incomplete-issues)
  - [3.4.3 Archive vs Delete](#343-archive-vs-delete)

---

## 3.3 Milestone Progress Tracking

### 3.3.1 Querying Completion Percentage

**Get milestone with progress:**

```bash
gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | select(.title=="v2.1.0") | {
    title: .title,
    open_issues: .open_issues,
    closed_issues: .closed_issues,
    percent_complete: (if (.open_issues + .closed_issues) > 0
      then ((.closed_issues / (.open_issues + .closed_issues)) * 100 | floor)
      else 0 end)
  }'
```

**Python progress calculation:** run [`scripts/amia_milestone_progress.py`](../scripts/amia_milestone_progress.py) with the `progress` command:

```bash
python3 scripts/amia_milestone_progress.py progress --repo owner/repo --milestone "v2.1.0"
```

Its `get_progress(repo, title)` helper fetches the milestone via `gh api`, then returns a JSON object with `open_issues`, `closed_issues`, `total_issues`, `percent_complete` (closed / total × 100, rounded to one decimal), `due_on`, and `state`. A missing milestone yields `{"error": "Milestone not found"}`.

### 3.3.2 Open vs Closed Issues Count

**List all milestones with counts:**

```bash
gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | "\(.title): \(.closed_issues)/\(.open_issues + .closed_issues) done"'
```

**Output:**

```
v2.0.0: 15/15 done
v2.1.0: 8/12 done
v2.2.0: 0/5 done
```

**Detailed breakdown by milestone:**

```bash
gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | {
    title: .title,
    state: .state,
    open: .open_issues,
    closed: .closed_issues,
    total: (.open_issues + .closed_issues)
  }' | jq -s '.'
```

### 3.3.3 Overdue Detection

**Check if milestone is overdue:**

```bash
gh api repos/{owner}/{repo}/milestones \
  --jq --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '.[] | select(.due_on != null and .due_on < $now and .state == "open") | {
    title: .title,
    due_on: .due_on,
    days_overdue: ((now | fromdate) - (.due_on | fromdate)) / 86400 | floor
  }'
```

**Python overdue check:** run [`scripts/amia_milestone_progress.py`](../scripts/amia_milestone_progress.py) with the `overdue` command:

```bash
python3 scripts/amia_milestone_progress.py overdue --repo owner/repo
```

Its `get_overdue(repo)` helper keeps only open milestones with a non-null `due_on` that is earlier than the current UTC time, computing `days_overdue` for each. Timezone-aware comparison is used throughout so a milestone is never misjudged across a TZ boundary.

---

## 3.4 Closing Milestones

### 3.4.1 When to Close

Close a milestone when:

1. All planned work is complete (all issues closed)
2. The release has been shipped
3. The sprint/quarter has ended
4. The milestone is being abandoned (document reason)

**Close milestone via CLI:**

```bash
# Get milestone number
milestone_number=$(gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | select(.title=="v2.1.0") | .number')

# Close it
gh api repos/{owner}/{repo}/milestones/${milestone_number} \
  --method PATCH \
  -f state="closed"
```

**Close only if all issues are done:**

```bash
milestone_info=$(gh api repos/{owner}/{repo}/milestones \
  --jq '.[] | select(.title=="v2.1.0")')

open_count=$(echo "$milestone_info" | jq '.open_issues')

if [ "$open_count" -eq 0 ]; then
  milestone_number=$(echo "$milestone_info" | jq '.number')
  gh api repos/{owner}/{repo}/milestones/${milestone_number} \
    --method PATCH \
    -f state="closed"
  echo "Milestone closed"
else
  echo "Cannot close: $open_count issues still open"
fi
```

### 3.4.2 Handling Incomplete Issues

When closing a milestone with open issues, decide what to do with them:

**Option 1: Move to next milestone**

```bash
# Get open issues from milestone being closed
issues=$(gh issue list --repo owner/repo \
  --milestone "v2.1.0" \
  --state open \
  --json number \
  --jq '.[].number')

# Move to next milestone
for issue in $issues; do
  gh issue edit $issue --repo owner/repo --milestone "v2.2.0"
done

# Now close the original milestone
```

**Option 2: Remove from milestone (backlog)**

```bash
issues=$(gh issue list --repo owner/repo \
  --milestone "v2.1.0" \
  --state open \
  --json number \
  --jq '.[].number')

for issue in $issues; do
  gh api repos/{owner}/{repo}/issues/$issue \
    --method PATCH \
    -F milestone=null
done
```

**Option 3: Add "deferred" label and close anyway**

```bash
issues=$(gh issue list --repo owner/repo \
  --milestone "v2.1.0" \
  --state open \
  --json number \
  --jq '.[].number')

for issue in $issues; do
  gh issue edit $issue --repo owner/repo --add-label "deferred"
done
```

### 3.4.3 Archive vs Delete

**Closing (archiving):**

- Milestone remains visible in "Closed" filter
- Historical data preserved
- Issues still reference the milestone
- **Recommended for completed work**

```bash
gh api repos/{owner}/{repo}/milestones/{number} \
  --method PATCH \
  -f state="closed"
```

**Deleting:**

- Milestone completely removed
- Issues become unassigned from milestone
- Historical tracking lost
- **Only use for accidental/test milestones**

```bash
gh api repos/{owner}/{repo}/milestones/{number} \
  --method DELETE
```

**Reopen a closed milestone:**

```bash
gh api repos/{owner}/{repo}/milestones/{number} \
  --method PATCH \
  -f state="open"
```

**Python helper for safe milestone closure:** run [`scripts/amia_milestone_progress.py`](../scripts/amia_milestone_progress.py) with the `close` command. To move still-open issues into a successor milestone first:

```bash
python3 scripts/amia_milestone_progress.py close \
  --repo owner/repo --milestone "v2.0.0" --move-open-to "v2.1.0"
```

To close even though issues remain open, pass `--force` instead of `--move-open-to`. Its `close_milestone(...)` helper guards the operation: if the milestone still has open issues and neither `--move-open-to` nor `--force` is given, it refuses with an `error` plus a `hint` rather than closing silently. When `--move-open-to` is supplied it reassigns each open issue before issuing the `PATCH state=closed` call, and reports how many issues were moved.

---

[Back to Milestone Tracking Index](milestone-tracking.md)
