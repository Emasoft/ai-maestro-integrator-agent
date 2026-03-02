# Issue Templates Part 1: Bug Report Templates

This document covers the structure and format for creating effective bug reports.

Back to index: [issue-templates.md](issue-templates.md)

---

## Table of Contents

- 2.1.1 Required sections (description, steps, expected/actual behavior)
- 2.1.2 Environment information (web, CLI, mobile formats)
- 2.1.3 Reproduction steps format (numbered steps, prerequisites)

---

## 2.1 Bug Report Template

### 2.1.1 Required Sections

A complete bug report should include these sections:

```markdown
## Bug Description

A clear and concise description of what the bug is.

## Steps to Reproduce

1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior

A clear description of what you expected to happen.

## Actual Behavior

What actually happened instead.

## Environment

- OS: [e.g., macOS 14.0, Ubuntu 22.04]
- Browser: [e.g., Chrome 120, Firefox 121]
- Version: [e.g., v2.1.0]

## Additional Context

Add any other context about the problem here.

## Screenshots

If applicable, add screenshots to help explain your problem.
```

**Minimal required sections:**
1. Bug Description - What is broken
2. Steps to Reproduce - How to trigger the bug
3. Expected vs Actual Behavior - What should happen vs what does happen

---

### 2.1.2 Environment Information

Environment details help developers reproduce issues:

**For web applications:**
```markdown
## Environment

- **Browser**: Chrome 120.0.6099.109
- **OS**: macOS 14.2 (Sonoma)
- **Screen Resolution**: 1920x1080
- **Application Version**: 2.1.0
- **User Agent**: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...
```

**For CLI tools:**
```markdown
## Environment

- **OS**: Ubuntu 22.04 LTS
- **Shell**: bash 5.1.16
- **Tool Version**: 1.5.2
- **Python Version**: 3.11.5 (if applicable)
- **Node Version**: 20.10.0 (if applicable)
```

**For mobile applications:**
```markdown
## Environment

- **Device**: iPhone 15 Pro
- **OS Version**: iOS 17.2
- **App Version**: 3.0.1
- **Network**: WiFi / Cellular
```

---

### 2.1.3 Reproduction Steps Format

Clear reproduction steps are critical for bug resolution.

**Format rules:**
1. Use numbered steps
2. Start each step with an action verb
3. Be specific about locations and elements
4. Include exact values for any input
5. Specify timing if relevant

**Good example:**
```markdown
## Steps to Reproduce

1. Navigate to the login page at `/login`
2. Enter username: `testuser@example.com`
3. Enter password: `Test123!`
4. Click the "Sign In" button
5. Wait for the dashboard to load (approximately 2 seconds)
6. Click the "Settings" icon in the top-right corner
7. Select "Profile" from the dropdown menu
8. Observe the error message displayed
```

**Bad example:**
```markdown
## Steps to Reproduce

1. Login
2. Go to settings
3. It breaks
```

**Including state prerequisites:**
```markdown
## Prerequisites

- User account with admin role
- At least one project created
- Feature flag `new-dashboard` enabled

## Steps to Reproduce

1. Log in as admin user
2. ...
```

---

## Complete Bug Report Example

```markdown
# Login fails with valid credentials on Safari

## Bug Description

Users on Safari cannot log in with valid credentials. The login button appears to submit but then returns to the login page without error messages.

## Steps to Reproduce

1. Open Safari 17.2 on macOS
2. Navigate to https://app.example.com/login
3. Enter email: testuser@example.com
4. Enter password: (valid password)
5. Click "Sign In" button
6. Observe: Page refreshes and returns to login form

## Expected Behavior

User should be redirected to the dashboard after successful authentication.

## Actual Behavior

Page refreshes and returns to the login form with no error message. No network errors in console.

## Environment

- **Browser**: Safari 17.2
- **OS**: macOS 14.2 (Sonoma)
- **Application Version**: 2.1.0

## Additional Context

- Works correctly on Chrome 120 and Firefox 121
- Started occurring after the December 15th deployment
- Affects approximately 12% of our users (Safari market share)

## Screenshots

[Screenshot of login page with filled credentials]
[Screenshot of network tab showing the request]
```
