---
name: template-bug-report
description: "Universal bug report YAML form for GitHub Issues with structured fields for triage."
---

# Universal Bug Report Issue Template

## Table of Contents

- 1. When to Use This Template
  - 1.1 Installing the bug report form in a repository
  - 1.2 How GitHub Issue YAML forms work
- 2. YAML Form Syntax Overview
  - 2.1 Top-level fields (name, description, labels, assignees)
  - 2.2 Body field types (input, textarea, dropdown, checkboxes, markdown)
  - 2.3 Validation attributes (required, placeholder, render)
- 3. Template Fields Explained
  - 3.1 Duplicate check checkbox
  - 3.2 Area dropdown for module classification
  - 3.3 Operating system dropdown
  - 3.4 Version input field
  - 3.5 "What happened?" description textarea
  - 3.6 Steps to reproduce textarea
  - 3.7 Expected behavior textarea
  - 3.8 Logs and screenshots textarea with code rendering
- 4. Auto-Labeling Strategy
  - 4.1 Default labels for bug reports
  - 4.2 How labels integrate with triage workflows
- 5. Complete YAML Template (Ready to Copy)
- 6. Customization Notes
  - 6.1 Adding project-specific fields
  - 6.2 Modifying the area dropdown for your project
  - 6.3 Adding severity or priority dropdowns

---

## 1. When to Use This Template

### 1.1 Installing the bug report form in a repository

Place the YAML file at `.github/ISSUE_TEMPLATE/bug_report.yml` in your repository. GitHub will display it as a structured form when users create a new issue and select the "Bug Report" template.

```
your-repo/
  .github/
    ISSUE_TEMPLATE/
      bug_report.yml   <-- place the template here
```

### 1.2 How GitHub Issue YAML forms work

GitHub Issue forms use YAML to define structured fields that replace free-form markdown issue bodies. Each field in the YAML `body` array becomes an input element in the browser form. When the user submits the form, GitHub renders the responses as formatted markdown in the issue body.

Key concepts:
- `type: input` creates a single-line text field
- `type: textarea` creates a multi-line text area
- `type: dropdown` creates a selection menu
- `type: checkboxes` creates a list of checkboxes
- `type: markdown` inserts static text (instructions, not user input)

Each field can have:
- `id` -- unique identifier for the field (used in API access)
- `attributes.label` -- the visible label above the field
- `attributes.description` -- helper text below the label
- `attributes.placeholder` -- grey hint text inside the field
- `validations.required` -- whether the field must be filled (true or false)

---

## 2. YAML Form Syntax Overview

### 2.1 Top-level fields

```yaml
name: Bug Report
description: Report a bug or unexpected behavior
labels: ["bug", "backlog"]
assignees: []
```

- `name` -- displayed in the template chooser
- `description` -- shown below the name in the chooser
- `labels` -- automatically applied to every issue created with this template
- `assignees` -- GitHub usernames to auto-assign (usually left empty for community repos)

### 2.2 Body field types

The `body` key contains an ordered list of form fields. Each entry has a `type` and `attributes` object.

Example of each type:

```yaml
# Single-line text
- type: input
  id: version
  attributes:
    label: "Version"
    placeholder: "e.g., 2.1.0"
  validations:
    required: true

# Multi-line text
- type: textarea
  id: description
  attributes:
    label: "What happened?"
    placeholder: "Describe the bug..."
  validations:
    required: true

# Dropdown selection
- type: dropdown
  id: os
  attributes:
    label: "Operating System"
    options:
      - macOS
      - Windows
      - Linux
  validations:
    required: true

# Checkboxes
- type: checkboxes
  id: checks
  attributes:
    label: "Pre-submission"
    options:
      - label: "I searched existing issues"
        required: true

# Static markdown (no user input)
- type: markdown
  attributes:
    value: "**Please fill out all required fields.**"
```

### 2.3 Validation attributes

The `render` attribute on textarea fields tells GitHub to format the content as a specific language in the rendered issue. This is useful for log output:

```yaml
- type: textarea
  id: logs
  attributes:
    label: "Logs"
    render: shell
```

When `render: shell` is set, GitHub wraps the user's input in a code block with shell syntax highlighting automatically.

---

## 3. Template Fields Explained

### 3.1 Duplicate check checkbox

Forces the reporter to confirm they searched existing issues before filing:

```yaml
- type: checkboxes
  id: duplicate-check
  attributes:
    label: "Pre-submission checklist"
    options:
      - label: "I have searched existing issues and confirmed this is not a duplicate"
        required: true
```

This reduces duplicate reports. The `required: true` on the checkbox means the form cannot be submitted without checking it.

### 3.2 Area dropdown for module classification

```yaml
- type: dropdown
  id: area
  attributes:
    label: "Area"
    description: "Which part of the project is affected?"
    options:
      - Core library
      - CLI interface
      - API server
      - Documentation
      - Build system
      - Tests
      - Other
  validations:
    required: true
```

Customize the options list for your project. The area helps maintainers route the issue to the right person.

### 3.3 Operating system dropdown

```yaml
- type: dropdown
  id: operating-system
  attributes:
    label: "Operating System"
    options:
      - macOS
      - Windows 10
      - Windows 11
      - Ubuntu / Debian
      - Fedora / RHEL
      - Arch Linux
      - Other Linux
      - Not applicable
  validations:
    required: true
```

### 3.4 Version input field

```yaml
- type: input
  id: version
  attributes:
    label: "Version"
    description: "Run your-tool --version or check package.json / pyproject.toml"
    placeholder: "e.g., 3.2.1"
  validations:
    required: true
```

### 3.5 "What happened?" description textarea

```yaml
- type: textarea
  id: what-happened
  attributes:
    label: "What happened?"
    description: "Describe the bug clearly. What did you observe?"
    placeholder: "When I run X, Y happens instead of Z..."
  validations:
    required: true
```

### 3.6 Steps to reproduce textarea

```yaml
- type: textarea
  id: steps-to-reproduce
  attributes:
    label: "Steps to reproduce"
    description: "Provide exact steps so a maintainer can reproduce the issue."
    placeholder: |
      1. Install version X
      2. Run command Y with arguments Z
      3. Observe error message in terminal
  validations:
    required: true
```

The numbered placeholder guides reporters toward precise reproduction steps.

### 3.7 Expected behavior textarea

```yaml
- type: textarea
  id: expected-behavior
  attributes:
    label: "Expected behavior"
    description: "What did you expect to happen instead?"
    placeholder: "I expected the command to complete successfully and output..."
  validations:
    required: true
```

### 3.8 Logs and screenshots textarea with code rendering

```yaml
- type: textarea
  id: logs
  attributes:
    label: "Relevant log output or screenshots"
    description: "Paste terminal output, error messages, or attach screenshots."
    render: shell
  validations:
    required: false
```

The `render: shell` attribute automatically wraps pasted text in a code block. This keeps log output readable and prevents markdown rendering artifacts.

---

## 4. Auto-Labeling Strategy

### 4.1 Default labels for bug reports

```yaml
labels: ["bug", "backlog"]
```

- `bug` -- identifies the issue type for filtering and project boards
- `backlog` -- signals that a maintainer has not yet reviewed and prioritized the issue

### 4.2 How labels integrate with triage workflows

After a maintainer reviews the issue:
1. Remove `backlog`
2. Add priority label (e.g., `priority-high`, `priority-low`)
3. Add area label if different from the dropdown selection
4. Assign to a milestone if applicable

---

## 5. Complete YAML Template (Ready to Copy)

Copy the following into `.github/ISSUE_TEMPLATE/bug_report.yml`:

```yaml
name: Bug Report
description: Report a bug or unexpected behavior
labels: ["bug", "backlog"]
assignees: []
body:
  - type: checkboxes
    id: duplicate-check
    attributes:
      label: "Pre-submission checklist"
      options:
        - label: "I have searched existing issues and confirmed this is not a duplicate"
          required: true

  - type: dropdown
    id: area
    attributes:
      label: "Area"
      description: "Which part of the project is affected?"
      options:
        - Core library
        - CLI interface
        - API server
        - Documentation
        - Build system
        - Tests
        - Other
    validations:
      required: true

  - type: dropdown
    id: operating-system
    attributes:
      label: "Operating System"
      options:
        - macOS
        - Windows 10
        - Windows 11
        - Ubuntu / Debian
        - Fedora / RHEL
        - Arch Linux
        - Other Linux
        - Not applicable
    validations:
      required: true

  - type: input
    id: version
    attributes:
      label: "Version"
      description: "Run your-tool --version or check package.json / pyproject.toml"
      placeholder: "e.g., 3.2.1"
    validations:
      required: true

  - type: textarea
    id: what-happened
    attributes:
      label: "What happened?"
      description: "Describe the bug clearly. What did you observe?"
      placeholder: "When I run X, Y happens instead of Z..."
    validations:
      required: true

  - type: textarea
    id: steps-to-reproduce
    attributes:
      label: "Steps to reproduce"
      description: "Provide exact steps so a maintainer can reproduce the issue."
      placeholder: |
        1. Install version X
        2. Run command Y with arguments Z
        3. Observe error message in terminal
    validations:
      required: true

  - type: textarea
    id: expected-behavior
    attributes:
      label: "Expected behavior"
      description: "What did you expect to happen instead?"
      placeholder: "I expected the command to complete successfully and output..."
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: "Relevant log output or screenshots"
      description: "Paste terminal output, error messages, or attach screenshots."
      render: shell
    validations:
      required: false
```

---

## 6. Customization Notes

### 6.1 Adding project-specific fields

Insert additional fields in the `body` array at the position that makes sense for your workflow. For example, add a "Browser" dropdown for web projects or a "Device" input for mobile projects.

### 6.2 Modifying the area dropdown for your project

Replace the generic area options with your project's actual module names:

```yaml
options:
  - Authentication
  - Payment processing
  - Email notifications
  - Admin dashboard
  - REST API
  - GraphQL API
```

### 6.3 Adding severity or priority dropdowns

If you want reporters to self-classify severity:

```yaml
- type: dropdown
  id: severity
  attributes:
    label: "Severity"
    description: "How severe is the impact?"
    options:
      - Critical -- application crashes or data loss
      - Major -- feature is broken but workaround exists
      - Minor -- cosmetic issue or minor inconvenience
  validations:
    required: true
```

Note that reporter-assigned severity is a suggestion. Maintainers should verify and adjust during triage.
