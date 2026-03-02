---
name: template-docs-issue
description: "Documentation improvement issue YAML form for GitHub Issues with structured fields for documentation triage."
---

# Documentation Improvement Issue Template

## Table of Contents

- 1. When to Use This Template
  - 1.1 Installing the documentation issue form in a repository
  - 1.2 What types of documentation issues this covers
- 2. Template Fields Explained
  - 2.1 Documentation issue type dropdown
  - 2.2 Location input field for file path or URL
  - 2.3 Description textarea for the improvement
  - 2.4 Contribution willingness checkbox
- 3. Auto-Labeling Strategy
  - 3.1 Default labels for documentation issues
  - 3.2 Why "help wanted" is included by default
- 4. Complete YAML Template (Ready to Copy)
- 5. Customization Notes
  - 5.1 Adding project-specific documentation categories
  - 5.2 Adding a documentation area dropdown for large doc sets

---

## 1. When to Use This Template

### 1.1 Installing the documentation issue form in a repository

Place the YAML file at `.github/ISSUE_TEMPLATE/docs.yml` in your repository. GitHub will display it as a structured form option when users create a new issue and select the "Documentation Improvement" template from the template chooser.

```
your-repo/
  .github/
    ISSUE_TEMPLATE/
      docs.yml   <-- place the template here
```

### 1.2 What types of documentation issues this covers

This template covers four categories of documentation problems:

| Type | Description | Example |
|------|-------------|---------|
| Missing documentation | A feature, API endpoint, or configuration option has no documentation | The `--dry-run` flag is not mentioned in the CLI reference |
| Incorrect or outdated information | Documentation describes behavior that no longer matches the code | README says Python 3.8 is required but the project now requires 3.10 |
| Improvement suggestion | Documentation exists but could be clearer, better organized, or more detailed | The installation guide would benefit from a troubleshooting section |
| Typo or grammar fix | Small textual errors in existing documentation | "Recieve" should be "Receive" on the contributing guide |

The type dropdown helps maintainers prioritize: missing documentation and incorrect information are typically higher priority than typo fixes.

---

## 2. Template Fields Explained

### 2.1 Documentation issue type dropdown

```yaml
- type: dropdown
  id: docs-type
  attributes:
    label: "Type of documentation issue"
    description: "What kind of documentation problem did you find?"
    options:
      - Missing documentation
      - Incorrect or outdated information
      - Improvement suggestion
      - Typo or grammar fix
  validations:
    required: true
```

This field categorizes the issue so maintainers can filter and prioritize. Missing documentation and incorrect information typically indicate that users are blocked or misled. Improvement suggestions and typo fixes are valuable but lower urgency.

### 2.2 Location input field for file path or URL

```yaml
- type: input
  id: location
  attributes:
    label: "Location"
    description: "File path in the repository or URL of the affected documentation page."
    placeholder: "e.g., docs/getting-started.md or https://yourproject.dev/docs/api"
  validations:
    required: true
```

This field is required because documentation improvements without a specific location are difficult to act on. The reporter must point to either:
- A file path relative to the repository root (e.g., `docs/api/authentication.md`)
- A URL of the rendered documentation site (e.g., `https://docs.example.com/guides/setup`)

### 2.3 Description textarea for the improvement

```yaml
- type: textarea
  id: description
  attributes:
    label: "Description"
    description: "Describe the documentation issue in detail. What is missing, wrong, or could be improved?"
    placeholder: |
      The current documentation for the authentication module does not explain
      how to configure OAuth2 providers. Users need step-by-step instructions
      for setting up Google, GitHub, and custom OAuth2 providers.
  validations:
    required: true
```

The placeholder provides an example of a well-structured documentation improvement request. It identifies what is missing, who needs it (users), and what specific content should be added (step-by-step instructions for specific providers).

### 2.4 Contribution willingness checkbox

```yaml
- type: checkboxes
  id: contribution
  attributes:
    label: "Contribution"
    description: "Documentation improvements are a great way to contribute to open source projects."
    options:
      - label: "I would be willing to submit a pull request to fix this documentation issue"
        required: false
```

This checkbox is intentionally not required. It serves two purposes:
1. It identifies potential contributors who can be assigned the issue
2. It reminds reporters that documentation contributions are welcome and valued

When someone checks this box, a maintainer should assign them to the issue and provide guidance on the expected changes.

---

## 3. Auto-Labeling Strategy

### 3.1 Default labels for documentation issues

```yaml
labels: ["documentation", "backlog", "help wanted"]
```

- `documentation` -- identifies the issue type for filtering
- `backlog` -- signals that a maintainer has not yet reviewed and prioritized the issue
- `help wanted` -- invites community contributions

### 3.2 Why "help wanted" is included by default

Documentation issues are ideal for new contributors because:
- They require writing skills rather than deep codebase knowledge
- The scope is usually well-defined (fix this page, add this section)
- They have low risk of breaking functionality
- They provide a gentle introduction to the contribution workflow

Including `help wanted` by default increases the chance that community members pick up documentation issues.

---

## 4. Complete YAML Template (Ready to Copy)

Copy the following into `.github/ISSUE_TEMPLATE/docs.yml`:

```yaml
name: Documentation Improvement
description: Report missing, incorrect, or improvable documentation
labels: ["documentation", "backlog", "help wanted"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        Thank you for helping improve the documentation.
        Please fill out the fields below so maintainers can locate and address the issue.

  - type: dropdown
    id: docs-type
    attributes:
      label: "Type of documentation issue"
      description: "What kind of documentation problem did you find?"
      options:
        - Missing documentation
        - Incorrect or outdated information
        - Improvement suggestion
        - Typo or grammar fix
    validations:
      required: true

  - type: input
    id: location
    attributes:
      label: "Location"
      description: "File path in the repository or URL of the affected documentation page."
      placeholder: "e.g., docs/getting-started.md or https://yourproject.dev/docs/api"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: "Description"
      description: "Describe the documentation issue in detail. What is missing, wrong, or could be improved?"
      placeholder: |
        The current documentation for the authentication module does not explain
        how to configure OAuth2 providers. Users need step-by-step instructions
        for setting up Google, GitHub, and custom OAuth2 providers.
    validations:
      required: true

  - type: checkboxes
    id: contribution
    attributes:
      label: "Contribution"
      description: "Documentation improvements are a great way to contribute to open source projects."
      options:
        - label: "I would be willing to submit a pull request to fix this documentation issue"
          required: false
```

---

## 5. Customization Notes

### 5.1 Adding project-specific documentation categories

If your project has distinct documentation areas, add a second dropdown:

```yaml
- type: dropdown
  id: docs-area
  attributes:
    label: "Documentation area"
    description: "Which section of the documentation is affected?"
    options:
      - Getting started guide
      - API reference
      - Configuration reference
      - Tutorials
      - FAQ
      - Contributing guide
      - Changelog
  validations:
    required: true
```

### 5.2 Adding a documentation area dropdown for large doc sets

For projects with extensive documentation (50+ pages), consider adding a second categorization layer. Insert the area dropdown between the type dropdown and the location field so that the reporter narrows down the area before specifying the exact location.

Example for a project with multiple documentation sections:

```yaml
- type: dropdown
  id: docs-section
  attributes:
    label: "Documentation section"
    options:
      - User guide
      - Developer guide
      - API reference (REST)
      - API reference (GraphQL)
      - SDK documentation (Python)
      - SDK documentation (JavaScript)
      - Deployment guide
      - Migration guide
  validations:
    required: true
```

This helps maintainers route documentation issues to the right documentation owner, especially in projects where different teams own different sections of the docs.
