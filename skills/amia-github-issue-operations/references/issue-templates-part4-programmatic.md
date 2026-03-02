# Issue Templates Part 4: Programmatic Template Population

This document covers how to populate issue templates programmatically using variable substitution and dynamic content injection.

Back to index: [issue-templates.md](issue-templates.md)

---

## Table of Contents

- 2.4.1 Variable substitution (placeholder syntax, Python substitution)
- 2.4.2 Dynamic content injection (system info, git info)
- 2.4.3 Template selection logic (type detection, combining selection with population)

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

**Example: Inject system information:**
```python
import platform
import subprocess

def get_system_info() -> dict:
    """Collect system information for bug reports."""
    return {
        "os": f"{platform.system()} {platform.release()}",
        "python_version": platform.python_version(),
        "gh_version": subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True
        ).stdout.split("\n")[0]
    }

def inject_environment(template: str, system_info: dict) -> str:
    """Inject system info into environment section."""
    env_section = "\n".join([
        f"- **{key}**: {value}"
        for key, value in system_info.items()
    ])
    return template.replace("{{environment}}", env_section)
```

**Example: Inject git information:**
```python
def get_git_info() -> dict:
    """Get current git state for context."""
    def run_git(args: list) -> str:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd="."
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"

    return {
        "branch": run_git(["branch", "--show-current"]),
        "commit": run_git(["rev-parse", "--short", "HEAD"]),
        "dirty": "yes" if run_git(["status", "--porcelain"]) else "no"
    }
```

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

```python
#!/usr/bin/env python3
"""
Complete example of programmatic issue creation with templates.
"""

import subprocess
import platform
from datetime import datetime
from enum import Enum
from string import Template


class IssueType(Enum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"


TEMPLATES = {
    IssueType.BUG: """## Bug Report

**Reporter**: ${reporter}
**Date**: ${date}

### Description
${description}

### Steps to Reproduce
${steps}

### Environment
${environment}

### Additional Context
${context}
""",
    IssueType.FEATURE: """## Feature Request

**Requested by**: ${reporter}
**Date**: ${date}

### Problem
${problem}

### Proposed Solution
${solution}

### Acceptance Criteria
${criteria}
""",
    IssueType.TASK: """## Task

**Created by**: ${reporter}
**Date**: ${date}

### Summary
${summary}

### Checklist
${checklist}
"""
}


def get_environment_info() -> str:
    """Gather system environment information."""
    info = {
        "OS": f"{platform.system()} {platform.release()}",
        "Python": platform.python_version(),
    }

    # Try to get git info
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True
        ).stdout.strip()
        info["Git Branch"] = branch or "detached"
    except Exception:
        pass

    return "\n".join(f"- **{k}**: {v}" for k, v in info.items())


def create_bug_report(
    description: str,
    steps: list[str],
    reporter: str = "@me",
    context: str = ""
) -> str:
    """Create a formatted bug report."""
    template = Template(TEMPLATES[IssueType.BUG])

    steps_formatted = "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1))

    return template.safe_substitute(
        reporter=reporter,
        date=datetime.now().strftime("%Y-%m-%d"),
        description=description,
        steps=steps_formatted,
        environment=get_environment_info(),
        context=context or "_None provided_"
    )


def create_and_submit_issue(
    title: str,
    body: str,
    labels: list[str],
    repo: str
) -> str:
    """Create issue using gh CLI and return the issue URL."""
    cmd = [
        "gh", "issue", "create",
        "--repo", repo,
        "--title", title,
        "--body", body
    ]

    for label in labels:
        cmd.extend(["--label", label])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout.strip()
    else:
        raise RuntimeError(f"Failed to create issue: {result.stderr}")


# Usage example
if __name__ == "__main__":
    body = create_bug_report(
        description="Application crashes when saving large files",
        steps=[
            "Open the application",
            "Create a new document",
            "Add more than 10MB of content",
            "Click Save",
            "Observe crash"
        ],
        reporter="@developer",
        context="Only happens with files > 10MB"
    )

    print(body)
```
