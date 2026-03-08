# Label Management Reference

> **Canonical Reference**: See `amia-label-taxonomy` skill for the authoritative label taxonomy.

## Table of Contents

- 1.1 Creating labels via GitHub API
  - 1.1.1 Using gh CLI to create labels
  - 1.1.2 Specifying label colors
  - 1.1.3 Adding label descriptions
- 1.2 Label naming conventions
  - 1.2.1 Kebab-case standard
  - 1.2.2 Category prefixes
- 1.3 Priority labels (critical, high, normal, low)
  - 1.3.1 Priority definitions
  - 1.3.2 Color scheme for priorities
  - 1.3.3 When to use each priority
- 1.4 Category labels
  - 1.4.1 Type labels (bug, feature, task, docs)
  - 1.4.2 Status labels (backlog, todo, in-progress, ai-review, human-review, merge-release, blocked, done)
  - 1.4.3 Component labels
- 1.5 Auto-creating missing labels
  - 1.5.1 Detection logic
  - 1.5.2 Default colors and descriptions

---

## 1.1 Creating Labels via GitHub API

### 1.1.1 Using gh CLI to Create Labels

The `gh` command-line interface provides the `gh label create` command to create repository labels.

**Basic syntax:**

```bash
gh label create <label-name> --repo <owner/repo>
```

**Example: Create a simple label**

```bash
gh label create "bug" --repo owner/repo
```

**Example: Create label with all options**

```bash
gh label create "bug" \
  --repo owner/repo \
  --color "d73a4a" \
  --description "Something isn't working"
```

**Checking if label exists before creating:**

```bash
# List existing labels and check
gh label list --repo owner/repo --json name --jq '.[].name' | grep -q "^bug$"
if [ $? -ne 0 ]; then
  gh label create "bug" --repo owner/repo
fi
```

### 1.1.2 Specifying Label Colors

Label colors are specified as 6-character hex codes WITHOUT the leading `#`.

**Color parameter:**

```bash
gh label create "priority:high" --color "d93f0b" --repo owner/repo
```

**Common color codes:**

| Color | Hex Code | Use Case |
|-------|----------|----------|
| Red | `d73a4a` | Bugs, critical issues |
| Orange | `d93f0b` | High priority |
| Yellow | `fbca04` | Medium priority |
| Green | `0e8a16` | Good first issue, help wanted |
| Blue | `0075ca` | Documentation |
| Purple | `5319e7` | Feature requests |
| Gray | `cfd3d7` | Duplicate, wontfix |

### 1.1.3 Adding Label Descriptions

Descriptions help team members understand when to apply each label.

**Adding description:**

```bash
gh label create "backlog" \
  --repo owner/repo \
  --color "fbca04" \
  --description "Issue requires initial assessment and categorization"
```

**Description best practices:**

- Keep descriptions under 100 characters
- Explain WHEN to use the label, not what it means literally
- Use action-oriented language

**Examples of good descriptions:**

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working as expected |
| `feature` | New functionality request |
| `blocked` | Waiting on external dependency or decision |

---

## 1.2 Label Naming Conventions

### 1.2.1 Kebab-case Standard

All labels should use lowercase kebab-case (words separated by hyphens).

**Correct:**

- `bug-fix`
- `ai-review`
- `high-priority`
- `breaking-change`

**Incorrect:**

- `Bug Fix` (spaces and capitals)
- `bug_fix` (underscores)
- `BugFix` (PascalCase)
- `URGENT` (all caps)

**Why kebab-case:**

1. Consistent with GitHub's default labels
2. Easy to type in CLI commands
3. Readable in URLs
4. No quoting needed in shell scripts

### 1.2.2 Category Prefixes

Use prefixes to group related labels together. Labels sort alphabetically, so prefixes create visual groupings.

**Common prefix patterns:**

| Prefix | Purpose | Examples |
|--------|---------|----------|
| `type:` | Issue type | `type:bug`, `type:feature`, `type:task` |
| `priority:` | Priority level | `priority:critical`, `priority:high`, `priority:normal`, `priority:low` |
| `status:` | Current state | `status:backlog`, `status:todo`, `status:in-progress`, `status:ai-review`, `status:human-review`, `status:merge-release`, `status:blocked`, `status:done` |
| `area:` | Code area | `area:frontend`, `area:api`, `area:database` |
| `effort:` | Estimated effort | `effort:small`, `effort:medium`, `effort:large` |

**Alternative: No prefix for common labels**

Some teams prefer no prefix for frequently used labels:

- `bug` instead of `type:bug`

**Note:** Priority and status labels MUST always use the `priority:` and `status:` prefixes respectively. Choose one convention and apply it consistently across all repositories.

---

## 1.3 Priority Labels (critical, high, normal, low)

### 1.3.1 Priority Definitions

| Label | Definition | Response Time |
|-------|------------|---------------|
| `priority:critical` | System down, data loss, security breach | Immediate (drop everything) |
| `priority:high` | Major feature broken, no workaround | Within 24 hours |
| `priority:normal` | Feature degraded, workaround exists | Within 1 week |
| `priority:low` | Minor issue, cosmetic problems, nice to have | Within 1 month |

### 1.3.2 Color Scheme for Priorities

Use a gradient from red (urgent) to green (low priority):

```bash
# Create priority labels with appropriate colors
gh label create "priority:critical" --color "b60205" --description "Critical: System down or security issue" --repo owner/repo
gh label create "priority:high" --color "d93f0b" --description "High: Major feature broken, no workaround" --repo owner/repo
gh label create "priority:normal" --color "fbca04" --description "Normal: Feature degraded, workaround exists" --repo owner/repo
gh label create "priority:low" --color "0e8a16" --description "Low: Minor issue, cosmetic, or nice to have" --repo owner/repo
```

### 1.3.3 When to Use Each Priority

**priority:critical:**

- Production service is completely down
- Data corruption or loss occurring
- Security vulnerability actively exploited
- Compliance violation detected

**priority:high:**

- Core feature not working for all users
- Performance degradation affecting many users
- Blocking issue for upcoming release
- Regression from recent deployment

**priority:normal:**

- Feature works but with significant friction
- Issue affects subset of users
- Workaround available but inconvenient
- Important but not blocking release

**priority:low:**

- Minor UI inconsistencies
- Edge case bugs
- Documentation improvements
- Small enhancements
- Cosmetic polish
- Code style improvements
- Speculative features
- "Would be nice" items

---

## 1.4 Category Labels

### 1.4.1 Type Labels (bug, feature, task, docs)

Type labels classify the nature of the issue:

```bash
# Create type labels
gh label create "bug" --color "d73a4a" --description "Something isn't working" --repo owner/repo
gh label create "feature" --color "5319e7" --description "New functionality request" --repo owner/repo
gh label create "task" --color "0075ca" --description "General task or chore" --repo owner/repo
gh label create "docs" --color "0075ca" --description "Documentation improvement" --repo owner/repo
gh label create "refactor" --color "1d76db" --description "Code improvement without behavior change" --repo owner/repo
gh label create "test" --color "bfd4f2" --description "Test coverage or test infrastructure" --repo owner/repo
```

**When to use:**

| Label | Use When |
|-------|----------|
| `bug` | Existing functionality is broken |
| `feature` | Requesting new capability |
| `task` | Work item that isn't a bug or feature |
| `docs` | README, comments, or documentation changes |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or fixing tests |

### 1.4.2 Status Labels (backlog, todo, in-progress, ai-review, human-review, merge-release, blocked, done)

Status labels track where an issue is in the workflow:

```bash
# Create status labels
gh label create "status:backlog" --color "d4c5f9" --description "In backlog, needs assessment and prioritization" --repo owner/repo
gh label create "status:todo" --color "c2e0c6" --description "Ready to be worked on" --repo owner/repo
gh label create "status:in-progress" --color "fbca04" --description "Currently being worked on" --repo owner/repo
gh label create "status:ai-review" --color "1d76db" --description "PR submitted, awaiting AI agent review" --repo owner/repo
gh label create "status:human-review" --color "0e8a16" --description "AI review passed, awaiting human review" --repo owner/repo
gh label create "status:merge-release" --color "0e8a16" --description "Approved, ready to merge and release" --repo owner/repo
gh label create "status:blocked" --color "d73a4a" --description "Waiting on external dependency or decision" --repo owner/repo
gh label create "status:done" --color "006b75" --description "Completed" --repo owner/repo
```

**Status flow:**

```
backlog → todo → in-progress → ai-review → human-review → merge-release → done
                      ↓
                   blocked
```

### 1.4.3 Component Labels

Component labels identify which part of the system is affected:

```bash
# Create component labels (customize for your project)
gh label create "area:frontend" --color "bfd4f2" --description "UI and client-side code" --repo owner/repo
gh label create "area:backend" --color "bfdadc" --description "Server-side code and APIs" --repo owner/repo
gh label create "area:database" --color "d4c5f9" --description "Database schema or queries" --repo owner/repo
gh label create "area:infra" --color "f9d0c4" --description "Infrastructure and DevOps" --repo owner/repo
gh label create "area:ci" --color "fef2c0" --description "CI/CD pipelines" --repo owner/repo
```

---

## 1.5 Auto-creating Missing Labels

### 1.5.1 Detection Logic

Before applying a label, check if it exists in the repository:

```bash
# Function to check if label exists
label_exists() {
  local repo="$1"
  local label="$2"
  gh label list --repo "$repo" --json name --jq '.[].name' | grep -qx "$label"
}

# Usage
if label_exists "owner/repo" "my-label"; then
  echo "Label exists"
else
  echo "Label does not exist"
fi
```

**Python implementation:**

```python
import subprocess
import json

def label_exists(repo: str, label: str) -> bool:
    """Check if a label exists in the repository."""
    result = subprocess.run(
        ["gh", "label", "list", "--repo", repo, "--json", "name"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return False
    labels = json.loads(result.stdout)
    return any(l["name"] == label for l in labels)
```

### 1.5.2 Default Colors and Descriptions

When auto-creating labels, use sensible defaults based on label name patterns:

```python
DEFAULT_LABEL_CONFIGS = {
    # Priority labels
    "priority:critical": {"color": "b60205", "description": "Critical priority"},
    "priority:high": {"color": "d93f0b", "description": "High priority"},
    "priority:normal": {"color": "fbca04", "description": "Normal priority"},
    "priority:low": {"color": "0e8a16", "description": "Low priority"},

    # Type labels
    "bug": {"color": "d73a4a", "description": "Something isn't working"},
    "feature": {"color": "5319e7", "description": "New functionality"},
    "task": {"color": "0075ca", "description": "General task"},
    "docs": {"color": "0075ca", "description": "Documentation"},

    # Status labels
    "status:backlog": {"color": "d4c5f9", "description": "In backlog, needs assessment"},
    "status:todo": {"color": "c2e0c6", "description": "Ready to be worked on"},
    "status:in-progress": {"color": "fbca04", "description": "Work in progress"},
    "status:ai-review": {"color": "1d76db", "description": "Ready for AI agent review"},
    "status:human-review": {"color": "0e8a16", "description": "Awaiting human review"},
    "status:merge-release": {"color": "0e8a16", "description": "Approved, ready to merge"},
    "status:blocked": {"color": "d73a4a", "description": "Blocked by dependency"},
    "status:done": {"color": "006b75", "description": "Completed"},
}

def get_label_config(label_name: str) -> dict:
    """Get color and description for a label, with fallback defaults."""
    if label_name in DEFAULT_LABEL_CONFIGS:
        return DEFAULT_LABEL_CONFIGS[label_name]

    # Fallback: gray color, generic description
    return {
        "color": "cfd3d7",
        "description": f"Label: {label_name}"
    }
```

**Auto-create function:**

```python
def ensure_label_exists(repo: str, label: str, auto_create: bool = True) -> bool:
    """Ensure a label exists, optionally creating it."""
    if label_exists(repo, label):
        return True

    if not auto_create:
        return False

    config = get_label_config(label)
    result = subprocess.run(
        [
            "gh", "label", "create", label,
            "--repo", repo,
            "--color", config["color"],
            "--description", config["description"]
        ],
        capture_output=True,
        text=True
    )
    return result.returncode == 0
```
