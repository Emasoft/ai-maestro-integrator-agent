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

**Python progress calculation:**
```python
def get_milestone_progress(repo: str, milestone_title: str) -> dict:
    """Get milestone completion percentage and issue counts."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/milestones",
         "--jq", f'.[] | select(.title=="{milestone_title}")'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0 or not result.stdout.strip():
        return {"error": "Milestone not found"}

    milestone = json.loads(result.stdout)

    open_count = milestone.get("open_issues", 0)
    closed_count = milestone.get("closed_issues", 0)
    total = open_count + closed_count

    percent = (closed_count / total * 100) if total > 0 else 0

    return {
        "title": milestone["title"],
        "open_issues": open_count,
        "closed_issues": closed_count,
        "total_issues": total,
        "percent_complete": round(percent, 1),
        "due_on": milestone.get("due_on"),
        "state": milestone.get("state")
    }
```

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

**Python overdue check:**
```python
from datetime import datetime

def check_overdue_milestones(repo: str) -> list[dict]:
    """Find all overdue open milestones."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/milestones",
         "--jq", '[.[] | select(.state=="open" and .due_on != null)]'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return []

    milestones = json.loads(result.stdout)
    now = datetime.utcnow()
    overdue = []

    for ms in milestones:
        due_on = datetime.fromisoformat(ms["due_on"].replace("Z", "+00:00"))
        due_on = due_on.replace(tzinfo=None)  # Remove timezone for comparison

        if due_on < now:
            days_overdue = (now - due_on).days
            overdue.append({
                "title": ms["title"],
                "due_on": ms["due_on"],
                "days_overdue": days_overdue,
                "open_issues": ms["open_issues"],
                "closed_issues": ms["closed_issues"]
            })

    return overdue
```

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

**Python helper for safe milestone closure:**
```python
def close_milestone(
    repo: str,
    milestone_title: str,
    move_open_to: str | None = None,
    force: bool = False
) -> dict:
    """
    Close a milestone, optionally moving open issues.

    Args:
        repo: Repository in owner/repo format
        milestone_title: Title of milestone to close
        move_open_to: Title of milestone to move open issues to
        force: Close even if issues are open (without moving)

    Returns:
        dict with result status
    """
    progress = get_milestone_progress(repo, milestone_title)

    if "error" in progress:
        return progress

    if progress["open_issues"] > 0:
        if move_open_to:
            # Move issues to new milestone
            issues = get_milestone_issues(repo, milestone_title, state="open")
            for issue_num in issues:
                assign_issue_to_milestone(repo, issue_num, move_open_to)
        elif not force:
            return {
                "error": f"Cannot close: {progress['open_issues']} issues still open",
                "hint": "Use move_open_to or force=True"
            }

    # Close the milestone
    milestone_number = get_milestone_number(repo, milestone_title)
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/milestones/{milestone_number}",
         "--method", "PATCH", "-f", "state=closed"],
        capture_output=True,
        text=True
    )

    return {
        "success": result.returncode == 0,
        "milestone": milestone_title,
        "issues_moved": progress["open_issues"] if move_open_to else 0
    }
```

---

[Back to Milestone Tracking Index](milestone-tracking.md)
