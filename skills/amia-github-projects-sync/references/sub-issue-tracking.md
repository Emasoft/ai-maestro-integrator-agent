# Sub-Issue Tracking

## Table of Contents

1. [When breaking down large features into sub-issues](#overview)
2. [When creating parent/child issue relationships](#creating-sub-issues)
3. [When tracking progress across sub-issues](#tracking-progress)
4. [When automating progress updates](#automated-progress-update)
5. [When using task lists for tracking](#task-list-best-practices)
6. [When querying sub-issue status](#querying-sub-issues)

## Overview

Complex features should be broken into smaller, independently assignable sub-issues. This enables parallel work by multiple agents and provides clear progress tracking.

**When to Use Sub-Issues:**
- Feature requires more than 3 days of work
- Feature has distinct, parallelizable components
- Multiple agents can work on different parts
- Feature needs incremental delivery

## Creating Sub-Issues

### Step 1: Create Parent Issue (Epic)

```bash
gh issue create \
  --title "Epic: User Management System" \
  --body "$(cat <<'EOF'
## Summary
Implement complete user management including registration, authentication, profile management, and role-based access control.

## Goals
- Enable user self-registration
- Secure authentication with JWT
- User profile customization
- Admin user management

## Progress

- [ ] #TBD User Registration
- [ ] #TBD User Authentication
- [ ] #TBD Password Reset
- [ ] #TBD User Profile

**Progress**: 0/4 (0%)
EOF
)" \
  --label "type:epic"
```

### Step 2: Create Sub-Issues with Reference

```bash
# Create first sub-issue
gh issue create \
  --title "Implement User Registration" \
  --body "$(cat <<'EOF'
Part of #42 (Epic: User Management System)

## Description
Implement user registration endpoint with email verification.

## Acceptance Criteria
- [ ] POST /api/register endpoint
- [ ] Email validation
- [ ] Password strength check
- [ ] Confirmation email sent
- [ ] User stored in database

## Technical Notes
- Use bcrypt for password hashing
- JWT for email confirmation token
EOF
)" \
  --label "type:feature"
```

### Step 3: Update Parent with Sub-Issue Numbers

After creating sub-issues, update the parent's progress section:

```bash
gh issue edit 42 --body "$(cat <<'EOF'
## Summary
Implement complete user management including registration, authentication, profile management, and role-based access control.

## Goals
- Enable user self-registration
- Secure authentication with JWT
- User profile customization
- Admin user management

## Progress

- [ ] #43 User Registration
- [ ] #44 User Authentication
- [ ] #45 Password Reset
- [ ] #46 User Profile

**Progress**: 0/4 (0%)
EOF
)"
```

## Tracking Progress

### Manual Progress Update

When a sub-issue is completed:

```bash
gh issue edit 42 --body "$(cat <<'EOF'
## Summary
Implement complete user management.

## Progress

- [x] #43 User Registration - MERGED
- [x] #44 User Authentication - MERGED
- [ ] #45 Password Reset - IN PROGRESS
- [ ] #46 User Profile - TODO

**Progress**: 2/4 (50%)
EOF
)"
```

### Progress Comment

Add a comment to the parent issue when sub-issues complete:

```bash
gh issue comment 42 --body "$(cat <<'EOF'
## Progress Update

**Sub-Issue Completed**: #44 User Authentication
**Merged**: 2024-01-15 via PR #52

**Current Progress**: 2/4 (50%)
- [x] #43 User Registration - MERGED
- [x] #44 User Authentication - MERGED
- [ ] #45 Password Reset - IN PROGRESS
- [ ] #46 User Profile - TODO

**Next**: Password Reset feature in progress.
EOF
)"
```

## Automated Progress Update

### Progress Update Script

```bash
#!/bin/bash
# update-epic-progress.sh PARENT_ISSUE

PARENT_ISSUE="$1"
OWNER="$2"
REPO="$3"

# Get parent issue body
BODY=$(gh issue view "$PARENT_ISSUE" --repo "$OWNER/$REPO" --json body --jq '.body')

# Extract sub-issue numbers
SUB_ISSUES=$(echo "$BODY" | grep -oE '#[0-9]+' | tr -d '#' | sort -u)

# Count completed
TOTAL=0
COMPLETED=0

for ISSUE_NUM in $SUB_ISSUES; do
  if [ "$ISSUE_NUM" != "$PARENT_ISSUE" ]; then
    TOTAL=$((TOTAL + 1))
    STATE=$(gh issue view "$ISSUE_NUM" --repo "$OWNER/$REPO" --json state --jq '.state')
    if [ "$STATE" = "CLOSED" ]; then
      COMPLETED=$((COMPLETED + 1))
    fi
  fi
done

# Calculate percentage
if [ "$TOTAL" -gt 0 ]; then
  PERCENT=$((COMPLETED * 100 / TOTAL))
else
  PERCENT=0
fi

# Update progress comment
gh issue comment "$PARENT_ISSUE" --repo "$OWNER/$REPO" --body "$(cat <<EOF
## Automated Progress Update

**Completed**: $COMPLETED/$TOTAL ($PERCENT%)

_Generated at $(date -u +"%Y-%m-%d %H:%M UTC")_
EOF
)"

echo "Progress: $COMPLETED/$TOTAL ($PERCENT%)"
```

## Task List Best Practices

### Format

Use GitHub-flavored markdown task lists:

```markdown
## Progress

- [ ] #43 User Registration
- [x] #44 User Authentication - MERGED
- [ ] #45 Password Reset - BLOCKED (see #47)
- [ ] #46 User Profile
```

### Status Annotations

Add status annotations for clarity:

| Annotation | Meaning |
|------------|---------|
| `- MERGED` | Sub-issue completed and merged |
| `- IN PROGRESS` | Currently being worked on |
| `- BLOCKED (see #X)` | Blocked by another issue |
| `- CANCELLED` | Will not be implemented |

### Progress Summary

Always include a summary line:

```markdown
**Progress**: 2/4 (50%)
```

Or with more detail:

```markdown
**Progress**: 2/4 (50%) | In Progress: 1 | Blocked: 0
```

## Querying Sub-Issues

### Find All Sub-Issues of an Epic

```bash
# Search issues mentioning the epic
gh issue list --search "Part of #42" --state all --json number,title,state
```

### Get Sub-Issue Status Summary

```bash
#!/bin/bash
# sub-issue-summary.sh EPIC_NUMBER

EPIC="$1"

echo "Sub-issues for Epic #$EPIC:"
echo "=========================="

# Find issues mentioning this epic
gh issue list --search "Part of #$EPIC" --state all --json number,title,state --jq '
  .[] | "\(.state)\t#\(.number)\t\(.title)"
'

# Count by state
echo ""
echo "Summary:"
OPEN=$(gh issue list --search "Part of #$EPIC" --state open --json number --jq 'length')
CLOSED=$(gh issue list --search "Part of #$EPIC" --state closed --json number --jq 'length')
TOTAL=$((OPEN + CLOSED))

echo "  Open:   $OPEN"
echo "  Closed: $CLOSED"
echo "  Total:  $TOTAL"

if [ "$TOTAL" -gt 0 ]; then
  PERCENT=$((CLOSED * 100 / TOTAL))
  echo "  Progress: $PERCENT%"
fi
```

### GraphQL Query for Linked Issues

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      issue(number: $number) {
        title
        body
        timelineItems(first: 100, itemTypes: [CROSS_REFERENCED_EVENT]) {
          nodes {
            ... on CrossReferencedEvent {
              source {
                ... on Issue {
                  number
                  title
                  state
                }
              }
            }
          }
        }
      }
    }
  }
' -f owner="OWNER" -f repo="REPO" -F number=42
```
