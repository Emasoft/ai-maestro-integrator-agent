# Issue Templates - Core Templates

## Table of Contents

1. [When starting with issue templates](#overview)
2. [When setting up template file structure](#directory-structure)
3. [When configuring template options](#issue-template-configuration)
4. [When creating feature request issues](#feature-request-template)
5. [When reporting bugs](#bug-report-template)

**See also**: [issue-templates-advanced.md](./issue-templates-advanced.md) for Epic, Refactor, Documentation, PR templates, CODEOWNERS, and CLI usage.

## Overview

This document provides core issue templates for the AMOA (Emasoft Orchestrator Agent) system. All templates are designed to provide maximum context for remote developer agents.

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

## Feature Request Template

### feature_request.yml

```yaml
name: Feature Request
description: Propose new functionality
labels: ["type:feature", "status:backlog"]
body:
  - type: markdown
    attributes:
      value: |
        ## Feature Request
        Please provide detailed information to help developers understand and implement this feature.

  - type: input
    id: title
    attributes:
      label: Feature Title
      description: A concise title for this feature
      placeholder: "Add user authentication via OAuth"
    validations:
      required: true

  - type: textarea
    id: user-story
    attributes:
      label: User Story
      description: Describe the feature from the user's perspective
      placeholder: |
        As a [user type],
        I want [goal/desire],
        So that [benefit/value].
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Detailed Description
      description: Explain the feature in detail
      placeholder: |
        Provide comprehensive details about:
        - What the feature should do
        - How users will interact with it
        - Any specific requirements or constraints
    validations:
      required: true

  - type: textarea
    id: acceptance-criteria
    attributes:
      label: Acceptance Criteria
      description: List specific, testable criteria for completion
      placeholder: |
        - [ ] User can initiate OAuth flow
        - [ ] Successful auth redirects to dashboard
        - [ ] Failed auth shows error message
        - [ ] Session persists for 7 days
        - [ ] Logout clears all tokens
    validations:
      required: true

  - type: textarea
    id: technical-notes
    attributes:
      label: Technical Notes
      description: Any implementation hints, constraints, or existing code to leverage
      placeholder: |
        - Use existing auth middleware in src/middleware/auth.js
        - OAuth config should follow .env.example pattern
        - Reference: https://docs.provider.com/oauth
    validations:
      required: false

  - type: textarea
    id: out-of-scope
    attributes:
      label: Out of Scope
      description: Explicitly list what is NOT part of this feature
      placeholder: |
        - Social login (separate feature)
        - Password reset flow (separate feature)
        - Admin user management
    validations:
      required: false

  - type: textarea
    id: dependencies
    attributes:
      label: Dependencies
      description: List any issues this depends on or blocks
      placeholder: |
        Depends on: #12, #15
        Blocks: #20
    validations:
      required: false

  - type: dropdown
    id: priority
    attributes:
      label: Priority
      description: How urgent is this feature?
      options:
        - "priority:low - Nice to have"
        - "priority:normal - Standard priority"
        - "priority:high - Should complete this sprint"
        - "priority:critical - Must complete immediately"
    validations:
      required: true

  - type: dropdown
    id: effort
    attributes:
      label: Estimated Effort
      description: Rough estimate of implementation size
      options:
        - "effort:xs - Less than 1 hour"
        - "effort:s - 1-4 hours"
        - "effort:m - 4-8 hours"
        - "effort:l - 1-3 days"
        - "effort:xl - More than 3 days"
    validations:
      required: false

  - type: textarea
    id: mockups
    attributes:
      label: Mockups / Screenshots
      description: Add any visual references (drag & drop images)
    validations:
      required: false
```

## Bug Report Template

### bug_report.yml

```yaml
name: Bug Report
description: Report something that isn't working correctly
labels: ["type:bug", "status:backlog"]
body:
  - type: markdown
    attributes:
      value: |
        ## Bug Report
        Please provide detailed reproduction steps to help us identify and fix the issue.

  - type: input
    id: title
    attributes:
      label: Bug Title
      description: A concise description of the bug
      placeholder: "Login fails with special characters in password"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: Clear explanation of what's wrong
      placeholder: "When attempting to log in with a password containing special characters like @#$%, the login fails with a 500 error."
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      description: Exact steps to reproduce the behavior
      placeholder: |
        1. Go to login page
        2. Enter username: testuser
        3. Enter password: Test@123#$
        4. Click 'Login' button
        5. See error
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What should happen
      placeholder: "User should be logged in and redirected to dashboard"
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happens
      placeholder: "500 Internal Server Error is displayed. Console shows: 'TypeError: Cannot read property 'hash' of undefined'"
    validations:
      required: true

  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: Where does this occur?
      placeholder: |
        - OS: macOS 14.0
        - Browser: Chrome 120
        - Node version: 20.10.0
        - App version: 2.3.1
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Relevant Logs / Error Messages
      description: Include any error messages, stack traces, or logs
      render: shell
      placeholder: |
        TypeError: Cannot read property 'hash' of undefined
            at AuthService.validatePassword (src/services/auth.js:42:15)
            at async LoginController.login (src/controllers/login.js:28:12)
    validations:
      required: false

  - type: textarea
    id: screenshots
    attributes:
      label: Screenshots
      description: If applicable, add screenshots (drag & drop)
    validations:
      required: false

  - type: dropdown
    id: severity
    attributes:
      label: Severity
      description: How severe is this bug?
      options:
        - "Low - Minor inconvenience"
        - "Medium - Affects functionality but has workaround"
        - "High - Major functionality broken"
        - "Critical - Security issue or data loss"
    validations:
      required: true

  - type: dropdown
    id: frequency
    attributes:
      label: Frequency
      description: How often does this occur?
      options:
        - "Always - 100% reproducible"
        - "Often - Happens frequently"
        - "Sometimes - Intermittent"
        - "Rarely - Happened once or twice"
    validations:
      required: true

  - type: textarea
    id: workaround
    attributes:
      label: Workaround
      description: Is there a temporary workaround?
      placeholder: "Using passwords without special characters works correctly."
    validations:
      required: false
```
