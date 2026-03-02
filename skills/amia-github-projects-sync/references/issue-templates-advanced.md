# Issue Templates - Advanced Templates

## Table of Contents

1. [When creating large multi-issue features](#epic-template)
2. [When proposing code refactoring](#refactor-template)
3. [When requesting documentation improvements](#documentation-template)
4. [When opening pull requests](#pull-request-template)
5. [When defining code ownership](#codeowners)
6. [When creating issues via GitHub CLI](#using-templates-via-cli)

**See also**: [issue-templates-core.md](./issue-templates-core.md) for Overview, Directory Structure, Config, Feature Request, and Bug Report templates.

## Epic Template

### epic.yml

```yaml
name: Epic
description: Large feature spanning multiple issues
labels: ["type:epic", "status:backlog"]
body:
  - type: markdown
    attributes:
      value: |
        ## Epic
        Epics are large features broken down into multiple smaller issues.

  - type: input
    id: title
    attributes:
      label: Epic Title
      description: Name for this epic
      placeholder: "User Management System"
    validations:
      required: true

  - type: textarea
    id: summary
    attributes:
      label: Epic Summary
      description: High-level description of this epic
      placeholder: "Implement complete user management including registration, authentication, profile management, and role-based access control."
    validations:
      required: true

  - type: textarea
    id: goals
    attributes:
      label: Goals & Objectives
      description: What does this epic achieve?
      placeholder: |
        - Enable user self-registration
        - Secure authentication with JWT
        - User profile customization
        - Admin user management
    validations:
      required: true

  - type: textarea
    id: sub-issues
    attributes:
      label: Sub-Issues
      description: Break down into smaller issues (will be created separately)
      placeholder: |
        - [ ] User registration endpoint
        - [ ] Email verification flow
        - [ ] JWT authentication
        - [ ] Password reset
        - [ ] Profile management
        - [ ] Role-based access control
        - [ ] Admin dashboard
    validations:
      required: true

  - type: textarea
    id: success-criteria
    attributes:
      label: Success Criteria
      description: How do we know the epic is complete?
      placeholder: |
        - All sub-issues completed and merged
        - Integration tests passing
        - Documentation complete
        - Security audit passed
    validations:
      required: true

  - type: textarea
    id: dependencies
    attributes:
      label: Dependencies
      description: What must be done before this epic can start?
      placeholder: |
        - Database schema finalized (#5)
        - Email service configured (#8)
    validations:
      required: false

  - type: textarea
    id: risks
    attributes:
      label: Risks & Considerations
      description: Potential challenges or risks
      placeholder: |
        - OAuth provider rate limits
        - GDPR compliance requirements
        - Legacy system migration
    validations:
      required: false
```

## Refactor Template

### refactor.yml

```yaml
name: Refactoring
description: Code improvement without behavior change
labels: ["type:refactor", "status:backlog"]
body:
  - type: markdown
    attributes:
      value: |
        ## Refactoring Request
        Refactoring improves code without changing its behavior.

  - type: input
    id: title
    attributes:
      label: Refactoring Title
      placeholder: "Extract authentication logic into service class"
    validations:
      required: true

  - type: textarea
    id: current-state
    attributes:
      label: Current State
      description: What does the code look like now?
      placeholder: |
        Authentication logic is scattered across multiple controllers:
        - src/controllers/login.js (50 lines)
        - src/controllers/register.js (40 lines)
        - src/controllers/reset-password.js (60 lines)
    validations:
      required: true

  - type: textarea
    id: proposed-change
    attributes:
      label: Proposed Change
      description: What should the code look like after?
      placeholder: |
        Extract all auth logic into AuthService:
        - src/services/AuthService.js (new)
        - Controllers become thin wrappers
        - Shared validation in one place
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Motivation
      description: Why is this refactoring needed?
      placeholder: |
        - Reduce code duplication
        - Make testing easier
        - Single point of change for auth logic
        - Prepare for adding OAuth support
    validations:
      required: true

  - type: textarea
    id: files-affected
    attributes:
      label: Files Affected
      description: Which files will change?
      placeholder: |
        - src/services/AuthService.js (new)
        - src/controllers/login.js (modify)
        - src/controllers/register.js (modify)
        - tests/services/AuthService.test.js (new)
    validations:
      required: true

  - type: textarea
    id: verification
    attributes:
      label: Verification
      description: How to verify behavior is unchanged?
      placeholder: |
        - All existing auth tests pass
        - Manual testing of login/register/reset flows
        - No changes to API contracts
    validations:
      required: true
```

## Documentation Template

### documentation.yml

```yaml
name: Documentation
description: Documentation improvements
labels: ["type:docs", "status:backlog"]
body:
  - type: markdown
    attributes:
      value: |
        ## Documentation Request
        Help us improve our documentation.

  - type: dropdown
    id: doc-type
    attributes:
      label: Documentation Type
      options:
        - "API Documentation"
        - "User Guide"
        - "Developer Guide"
        - "README"
        - "Code Comments"
        - "Other"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: What needs to be documented?
      placeholder: |
        The new authentication endpoints need documentation including:
        - Endpoint URLs and methods
        - Request/response formats
        - Authentication requirements
        - Error codes
    validations:
      required: true

  - type: textarea
    id: location
    attributes:
      label: Where should this documentation live?
      placeholder: |
        - docs/api/authentication.md
        - README.md (add section)
    validations:
      required: false
```

## Pull Request Template

### PULL_REQUEST_TEMPLATE.md

```markdown
## Description

<!-- Brief description of what this PR does -->

## Related Issue

<!-- Link to the GitHub issue -->
Closes #

## Changes Made

<!-- List the specific changes -->
-
-
-

## Type of Change

<!-- Check all that apply -->
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Refactoring (no functional changes)
- [ ] Documentation update
- [ ] Test improvements

## Testing

<!-- Describe testing performed -->

### Tests Added/Modified
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests

### Test Results
```
Paste test output here
```

### Manual Testing
<!-- Steps to manually verify -->
1.
2.
3.

## Checklist

<!-- Ensure all items are complete -->
- [ ] My code follows the project style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Screenshots (if applicable)

<!-- Add screenshots for UI changes -->

## Additional Notes

<!-- Any additional context for reviewers -->

---
**Agent ID**: <!-- dev-agent-1, dev-agent-2, etc. -->
**Time Spent**: <!-- e.g., 3.5 hours -->
```

## CODEOWNERS

```
# Default owners for everything
*       @owner

# Frontend team
/src/components/**  @frontend-team
/src/styles/**      @frontend-team

# Backend team
/src/api/**         @backend-team
/src/services/**    @backend-team
/src/models/**      @backend-team

# Infrastructure
/.github/**         @devops-team
/docker/**          @devops-team
/k8s/**             @devops-team

# Documentation
/docs/**            @docs-team
*.md                @docs-team
```

## Using Templates via CLI

### Create Issue from Template

```bash
# Feature request
gh issue create \
  --title "Add OAuth2 support" \
  --template "feature_request.yml" \
  --label "type:feature,priority:high"

# Bug report
gh issue create \
  --title "Login fails with special chars" \
  --template "bug_report.yml" \
  --label "type:bug,priority:critical"
```

### Create Issue with Full Body

```bash
gh issue create \
  --title "Implement User Registration" \
  --body "$(cat <<'EOF'
## User Story
As a new user, I want to register an account so that I can access the platform.

## Acceptance Criteria
- [ ] Registration form with email, password, name
- [ ] Email validation
- [ ] Password strength requirements
- [ ] Confirmation email sent
- [ ] Redirect to login after registration

## Technical Notes
- Use existing EmailService for sending confirmation
- Store password hash with bcrypt (12 rounds)
- JWT token in confirmation link (24h expiry)

## Out of Scope
- Social registration (OAuth) - separate feature
- Admin approval workflow
EOF
)" \
  --label "type:feature,priority:high,effort:m"
```
