# Issue Templates Part 4: Programmatic Template Population

## Table of Contents

- 2.4.1 Variable substitution (placeholder syntax, Python substitution)
- 2.4.2 Dynamic content injection (system info, git info)
- 2.4.3 Template selection logic (type detection, combining selection with population)

---

This document covers how to populate issue templates programmatically using variable substitution and dynamic content injection.

Back to index: [issue-templates.md](issue-templates.md)

---

## 2.4 Populating Templates Programmatically

### 2.4.1 Variable Substitution

Use placeholder variables in templates that get replaced at runtime.

**Template with variables:**

```markdown
## Bug Report

**Reporter**: {{reporter}}
**Date**: {{date}}
**Version**: {{version}}

### Description

{{description}}

### Environment

- OS: {{os}}
- Browser: {{browser}}
```

**Python substitution:**

```python
import string
from datetime import datetime

template = """
## Bug Report

**Reporter**: ${reporter}
**Date**: ${date}
**Version**: ${version}

### Description

${description}
"""

# Using string.Template for safe substitution
t = string.Template(template)
body = t.safe_substitute(
    reporter="@username",
    date=datetime.now().strftime("%Y-%m-%d"),
    version="2.1.0",
    description="Application crashes when clicking save button"
)
```

**Jinja2 substitution (more powerful):**

```python
from jinja2 import Template

template = Template("""
## Bug Report

**Reporter**: {{ reporter }}
**Date**: {{ date }}
**Version**: {{ version }}

### Description

{{ description }}

{% if screenshots %}
### Screenshots
{% for screenshot in screenshots %}
- {{ screenshot }}
{% endfor %}
{% endif %}
""")

body = template.render(
    reporter="@username",
    date="2024-01-15",
    version="2.1.0",
    description="Application crashes on save",
    screenshots=["error-dialog.png", "console-log.png"]
)
```

---

### 2.4.2 Dynamic Content Injection

Insert computed or fetched content into templates.

**Example: Inject system information.** The `get_environment_info()` helper in [`scripts/amia_populate_template.py`](../scripts/amia_populate_template.py) collects OS, Python version, and the current git branch and formats them as a `- **key**: value` bullet list ready to drop into an Environment section. It reads the git branch through a fixed argument vector, so no value is interpolated into a shell.

**Example: Inject git information.** The `run_git(args)` helper in [`scripts/amia_populate_template.py`](../scripts/amia_populate_template.py) shows the safe pattern for reading git state: it invokes `git` with a fixed argument vector (`["git"] + args`) and falls back to `"unknown"` on a non-zero exit. Compose it for the current branch (`branch --show-current`), short commit (`rev-parse --short HEAD`), and dirty status (`status --porcelain`).

**Example: Inject error logs:**

```python
def get_recent_errors(log_file: str, max_lines: int = 20) -> str:
    """Extract recent error entries from log file."""
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()

        error_lines = [
            line for line in lines
            if "ERROR" in line or "Exception" in line
        ]

        recent = error_lines[-max_lines:] if error_lines else []
        return "```\n" + "".join(recent) + "\n```"
    except FileNotFoundError:
        return "_No log file found_"
```

---

### 2.4.3 Template Selection Logic

Choose the appropriate template based on context.

```python
from enum import Enum
from typing import Optional

class IssueType(Enum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"
    DOCS = "docs"

TEMPLATES = {
    IssueType.BUG: """## Bug Report

### Description
{description}

### Steps to Reproduce
{steps}

### Expected Behavior
{expected}

### Actual Behavior
{actual}

### Environment
{environment}
""",
    IssueType.FEATURE: """## Feature Request

### Problem Statement
{problem}

### Proposed Solution
{solution}

### Acceptance Criteria
{criteria}
""",
    IssueType.TASK: """## Task

### Summary
{summary}

### Details
{details}

### Checklist
{checklist}
""",
    IssueType.DOCS: """## Documentation Update

### Section
{section}

### Current Content Issue
{issue}

### Proposed Change
{change}
"""
}

def select_template(issue_type: IssueType) -> str:
    """Get the template for the specified issue type."""
    return TEMPLATES.get(issue_type, TEMPLATES[IssueType.TASK])

def detect_issue_type(title: str, body: str) -> IssueType:
    """Attempt to detect issue type from content."""
    title_lower = title.lower()
    body_lower = body.lower()

    if any(word in title_lower for word in ["bug", "crash", "error", "broken", "fix"]):
        return IssueType.BUG
    if any(word in title_lower for word in ["feature", "add", "implement", "support"]):
        return IssueType.FEATURE
    if any(word in title_lower for word in ["doc", "readme", "comment", "typo"]):
        return IssueType.DOCS

    return IssueType.TASK
```

**Combining template selection with population:**

```python
def create_issue_body(
    issue_type: IssueType,
    context: dict,
    auto_inject_env: bool = True
) -> str:
    """Create a fully populated issue body."""
    template = select_template(issue_type)

    if auto_inject_env:
        context["environment"] = format_environment(get_system_info())

    # Use safe substitution to handle missing keys gracefully
    from string import Template
    t = Template(template.replace("{", "${"))
    return t.safe_substitute(context)
```

---

## Complete Programmatic Example

The full end-to-end flow — select a template by issue type, inject dynamic
system/git context, substitute the variables safely, and optionally submit
the result as a GitHub issue — is shipped as the runnable script
[`scripts/amia_populate_template.py`](../scripts/amia_populate_template.py).

Print a populated bug-report body without creating anything:

```bash
python3 scripts/amia_populate_template.py --type bug \
  --title "Crash on save" \
  --description "Application crashes when saving large files"
```

Populate and submit in one step (adds labels, prints the created issue URL):

```bash
python3 scripts/amia_populate_template.py --type bug \
  --title "Crash on save" \
  --description "Application crashes when saving large files" \
  --repo owner/repo --label bug --submit
```

The script combines the `string.Template` substitution shown above with the
`get_environment_info()` helper, then calls `gh issue create` through a fixed
argument vector. Issue creation failure raises a clear error and exits
non-zero rather than failing silently.
