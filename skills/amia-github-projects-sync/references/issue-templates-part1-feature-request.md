# Issue Templates - Part 1: Feature Request Template

## Table of Contents

- 1.1 [Feature request YAML template structure](#feature-request-template)
- 1.2 [User story format and validation](#user-story-section)
- 1.3 [Acceptance criteria checklist format](#acceptance-criteria-section)
- 1.4 [Technical notes section](#technical-notes-section)
- 1.5 [Priority and effort dropdown options](#priority-and-effort-dropdowns)
- 1.6 [Dependencies and out-of-scope sections](#dependencies-and-scope)

---

## Feature Request Template

### feature_request.yml

This YAML file defines the structure for feature request issues. Place it in `.github/ISSUE_TEMPLATE/feature_request.yml`.

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

---

## Section Details

### User Story Section

The user story follows the standard format:
- **As a** [user type] - identifies who benefits
- **I want** [goal/desire] - describes the action
- **So that** [benefit/value] - explains the value

This section is marked as required to ensure every feature has clear user value.

### Acceptance Criteria Section

Use checkbox format for acceptance criteria:
```markdown
- [ ] Criterion 1
- [ ] Criterion 2
```

Each criterion should be:
- Specific and measurable
- Independently testable
- Written from user perspective when possible

### Technical Notes Section

Optional section for implementation guidance:
- Existing code to leverage
- External references or documentation
- Configuration patterns to follow
- Known constraints or limitations

### Priority and Effort Dropdowns

**Priority levels**:
| Level | Label | Description |
|-------|-------|-------------|
| Low | `priority:low` | Nice to have, no deadline |
| Normal | `priority:normal` | Standard backlog priority |
| High | `priority:high` | Should complete this sprint |
| Critical | `priority:critical` | Must complete immediately |

**Effort estimates**:
| Size | Label | Time Range |
|------|-------|------------|
| XS | `effort:xs` | Less than 1 hour |
| S | `effort:s` | 1-4 hours |
| M | `effort:m` | 4-8 hours |
| L | `effort:l` | 1-3 days |
| XL | `effort:xl` | More than 3 days |

### Dependencies and Scope

**Dependencies format**:
```markdown
Depends on: #12, #15
Blocks: #20
```

**Out of Scope** section prevents scope creep by explicitly listing excluded items.
