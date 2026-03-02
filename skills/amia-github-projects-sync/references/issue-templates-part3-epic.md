# Issue Templates - Part 3: Epic Template

## Table of Contents

- 3.1 [Epic YAML template structure](#epic-template)
- 3.2 [Goals and objectives section](#goals-and-objectives)
- 3.3 [Sub-issues breakdown format](#sub-issues-breakdown)
- 3.4 [Success criteria definition](#success-criteria)
- 3.5 [Dependencies and risks sections](#dependencies-and-risks)

---

## Epic Template

### epic.yml

This YAML file defines the structure for epic issues. Place it in `.github/ISSUE_TEMPLATE/epic.yml`.

Epics are large features that span multiple smaller issues. They provide high-level context and tracking for related work.

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

---

## Section Details

### Goals and Objectives

Define the business and technical objectives:

```markdown
Goals:
- Enable user self-registration
- Secure authentication with JWT
- User profile customization
- Admin user management

Objectives:
- Reduce onboarding friction by 50%
- Achieve SOC2 compliance
- Support 10k concurrent users
```

**Best practices**:
- Use measurable outcomes when possible
- Align with business goals
- Consider non-functional requirements

### Sub-Issues Breakdown

Use checkbox format for tracking:
```markdown
- [ ] User registration endpoint
- [ ] Email verification flow
- [ ] JWT authentication
- [ ] Password reset
- [ ] Profile management
```

**Guidelines**:
- Each sub-issue should be completable in 1-3 days
- Create actual issues from this list after epic approval
- Link sub-issues back to the epic
- Update checkboxes as issues are completed

### Success Criteria

Define completion conditions:

```markdown
- All sub-issues completed and merged
- Integration tests passing (>90% coverage)
- Documentation complete
- Security audit passed
- Performance benchmarks met
- Stakeholder sign-off obtained
```

**Types of criteria**:
- Technical: tests, coverage, performance
- Process: reviews, audits, documentation
- Business: stakeholder approval, metrics

### Dependencies and Risks

**Dependencies format**:
```markdown
Prerequisites:
- Database schema finalized (#5)
- Email service configured (#8)
- API gateway deployed (#12)

External dependencies:
- OAuth provider API access
- SSL certificates provisioned
```

**Risks format**:
```markdown
Technical risks:
- OAuth provider rate limits
- Legacy system compatibility

Business risks:
- GDPR compliance requirements
- Timeline dependencies on Q4 release

Mitigation strategies:
- Early integration testing
- Legal review of data handling
```
