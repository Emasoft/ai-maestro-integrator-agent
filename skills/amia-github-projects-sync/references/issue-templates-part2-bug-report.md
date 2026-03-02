# Issue Templates - Part 2: Bug Report Template

## Table of Contents

- 2.1 [Bug report YAML template structure](#bug-report-template)
- 2.2 [Steps to reproduce format](#steps-to-reproduce)
- 2.3 [Expected vs actual behavior sections](#expected-vs-actual-behavior)
- 2.4 [Environment details format](#environment-section)
- 2.5 [Logs and error message formatting](#logs-and-error-messages)
- 2.6 [Severity and frequency dropdown options](#severity-and-frequency)

---

## Bug Report Template

### bug_report.yml

This YAML file defines the structure for bug report issues. Place it in `.github/ISSUE_TEMPLATE/bug_report.yml`.

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

---

## Section Details

### Steps to Reproduce

Use numbered steps for clear reproduction:
```markdown
1. Go to [location]
2. Click on [element]
3. Enter [data]
4. Observe [result]
```

**Best practices**:
- Be specific about data used (include examples)
- Note any preconditions
- Include timing if relevant
- Mention browser/environment specifics

### Expected vs Actual Behavior

**Expected Behavior**: Describe what SHOULD happen according to:
- Documentation
- Normal user expectations
- Previous working behavior

**Actual Behavior**: Describe what ACTUALLY happens:
- Include exact error messages
- Note any partial success
- Describe visual or functional differences

### Environment Section

Required environment details:
```markdown
- OS: macOS 14.0 / Windows 11 / Ubuntu 22.04
- Browser: Chrome 120 / Firefox 121 / Safari 17
- Node version: 20.10.0
- App version: 2.3.1
```

Additional context when relevant:
- Network conditions
- User role/permissions
- Data volume or scale
- Third-party integrations

### Logs and Error Messages

The `render: shell` attribute provides syntax highlighting for logs.

Include:
- Full stack traces
- Console errors
- Server logs (sanitized)
- Network request/response data

**Example format**:
```
TypeError: Cannot read property 'hash' of undefined
    at AuthService.validatePassword (src/services/auth.js:42:15)
    at async LoginController.login (src/controllers/login.js:28:12)
    at async Router.handle (node_modules/express/lib/router/index.js:284:5)
```

### Severity and Frequency

**Severity levels**:
| Level | Description | Response Time |
|-------|-------------|---------------|
| Low | Minor inconvenience | Normal backlog |
| Medium | Affects functionality, has workaround | Sprint planning |
| High | Major functionality broken | Next sprint |
| Critical | Security issue or data loss | Immediate |

**Frequency levels**:
| Level | Description | Debug Difficulty |
|-------|-------------|------------------|
| Always | 100% reproducible | Easier to debug |
| Often | Happens frequently | Moderate |
| Sometimes | Intermittent | Challenging |
| Rarely | Once or twice | Very difficult |

### Workaround Section

Document any temporary fixes users can apply while waiting for resolution. This helps:
- Unblock users immediately
- Reduce support requests
- Provide debugging hints
