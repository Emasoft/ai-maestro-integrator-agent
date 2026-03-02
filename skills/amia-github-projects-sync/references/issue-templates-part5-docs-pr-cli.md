# Issue Templates - Part 5: Documentation, PR Template, CODEOWNERS, and CLI Usage

## Table of Contents

- 5.1 [Documentation request YAML template](#documentation-template)
- 5.2 [Pull request template (Markdown format)](#pull-request-template)
- 5.3 [CODEOWNERS file format and examples](#codeowners)
- 5.4 [Creating issues via GitHub CLI](#using-templates-via-cli)
- 5.5 [CLI examples with full body content](#cli-examples-with-full-body)

---

## Documentation Template

### documentation.yml

This YAML file defines the structure for documentation requests. Place it in `.github/ISSUE_TEMPLATE/documentation.yml`.

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

---

## Pull Request Template

### PULL_REQUEST_TEMPLATE.md

Place this file in `.github/PULL_REQUEST_TEMPLATE.md`.

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

---

## CODEOWNERS

Place this file in `.github/CODEOWNERS`.

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

### CODEOWNERS Syntax

| Pattern | Description |
|---------|-------------|
| `*` | All files |
| `/src/**` | All files under src directory |
| `*.js` | All JavaScript files |
| `/docs/*.md` | Markdown files in docs root only |
| `/docs/**/*.md` | All Markdown files under docs |

---

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

### CLI Examples with Full Body

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

### Batch Issue Creation

Create multiple related issues:

```bash
# Create epic first
EPIC=$(gh issue create \
  --title "User Management System" \
  --label "type:epic" \
  --body "Epic for user management features" \
  | grep -oE '[0-9]+$')

# Create sub-issues linked to epic
for feature in "Registration" "Authentication" "Profile"; do
  gh issue create \
    --title "User $feature" \
    --label "type:feature" \
    --body "Part of epic #$EPIC"
done
```
