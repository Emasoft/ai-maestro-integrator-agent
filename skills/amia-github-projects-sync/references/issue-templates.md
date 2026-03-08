# Issue Templates

## Table of Contents

1. [When starting with issue templates](#overview)
2. [When setting up template file structure](#directory-structure)
3. [When configuring template options](#issue-template-configuration)
4. [When creating feature request issues](#feature-request-template) - See [issue-templates-part1-feature-request.md](issue-templates-part1-feature-request.md)
5. [When reporting bugs](#bug-report-template) - See [issue-templates-part2-bug-report.md](issue-templates-part2-bug-report.md)
6. [When creating large multi-issue features](#epic-template) - See [issue-templates-part3-epic.md](issue-templates-part3-epic.md)
7. [When proposing code refactoring](#refactor-template) - See [issue-templates-part4-refactor.md](issue-templates-part4-refactor.md)
8. [When requesting documentation improvements](#documentation-template) - See [issue-templates-part5-docs-pr-cli.md](issue-templates-part5-docs-pr-cli.md)
9. [When opening pull requests](#pull-request-template) - See [issue-templates-part5-docs-pr-cli.md](issue-templates-part5-docs-pr-cli.md)
10. [When defining code ownership](#codeowners) - See [issue-templates-part5-docs-pr-cli.md](issue-templates-part5-docs-pr-cli.md)
11. [When creating issues via GitHub CLI](#using-templates-via-cli) - See [issue-templates-part5-docs-pr-cli.md](issue-templates-part5-docs-pr-cli.md)

---

## Overview

This document provides complete issue and pull request templates for the AMOA (Emasoft Orchestrator Agent) system. All templates are designed to provide maximum context for remote developer agents.

## Directory Structure

```
.github/
├── ISSUE_TEMPLATE/
│   ├── config.yml
│   ├── feature_request.yml
│   ├── bug_report.yml
│   ├── epic.yml
│   ├── refactor.yml
│   └── documentation.yml
├── PULL_REQUEST_TEMPLATE.md
└── CODEOWNERS
```

## Issue Template Configuration

### config.yml

```yaml
blank_issues_enabled: false
contact_links:
  - name: Questions & Support
    url: https://github.com/owner/repo/discussions
    about: Ask questions and get help
```

---

## Part Files Reference

This index document links to detailed template specifications in separate files. Each part file contains the full YAML template ready for use.

### Part 1: Feature Request Template

**File**: [issue-templates-part1-feature-request.md](issue-templates-part1-feature-request.md)

**Contents**:

- 1.1 Feature request YAML template structure
- 1.2 User story format and validation
- 1.3 Acceptance criteria checklist format
- 1.4 Technical notes section
- 1.5 Priority and effort dropdown options
- 1.6 Dependencies and out-of-scope sections

### Part 2: Bug Report Template

**File**: [issue-templates-part2-bug-report.md](issue-templates-part2-bug-report.md)

**Contents**:

- 2.1 Bug report YAML template structure
- 2.2 Steps to reproduce format
- 2.3 Expected vs actual behavior sections
- 2.4 Environment details format
- 2.5 Logs and error message formatting
- 2.6 Severity and frequency dropdown options

### Part 3: Epic Template

**File**: [issue-templates-part3-epic.md](issue-templates-part3-epic.md)

**Contents**:

- 3.1 Epic YAML template structure
- 3.2 Goals and objectives section
- 3.3 Sub-issues breakdown format
- 3.4 Success criteria definition
- 3.5 Dependencies and risks sections

### Part 4: Refactor Template

**File**: [issue-templates-part4-refactor.md](issue-templates-part4-refactor.md)

**Contents**:

- 4.1 Refactoring request YAML template structure
- 4.2 Current state vs proposed change format
- 4.3 Motivation section
- 4.4 Files affected listing
- 4.5 Verification requirements

### Part 5: Documentation, PR Template, CODEOWNERS, and CLI Usage

**File**: [issue-templates-part5-docs-pr-cli.md](issue-templates-part5-docs-pr-cli.md)

**Contents**:

- 5.1 Documentation request YAML template
- 5.2 Pull request template (Markdown format)
- 5.3 CODEOWNERS file format and examples
- 5.4 Creating issues via GitHub CLI
- 5.5 CLI examples with full body content
