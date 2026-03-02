# Troubleshooting Part 1: Issue and Status Problems

## Table of Contents

- [10.1 Issue Not Appearing](#101-issue-not-appearing)
  - [Cause 1: Issue Not Added to Project](#cause-1-issue-not-added-to-project)
  - [Cause 2: Issue Missing Required Fields](#cause-2-issue-missing-required-fields)
  - [Cause 3: Board View Filtering](#cause-3-board-view-filtering)
- [10.2 Status Not Reflecting](#102-status-not-reflecting)
  - [Cause 1: Wrong Field ID](#cause-1-wrong-field-id)
  - [Cause 2: Mutation Failed Silently](#cause-2-mutation-failed-silently)
  - [Cause 3: Caching](#cause-3-caching)

## 10.1 Issue Not Appearing

**Symptom:** Created an issue but it doesn't show on the project board.

### Cause 1: Issue Not Added to Project

Issue was created but not added to the project.

**Diagnosis:**
```bash
# Check if issue is in project
gh project item-list PROJECT_NUMBER --owner OWNER --format json | jq '.items[] | select(.content.number == 42)'
```

**Solution:**
```bash
# Add issue to project
gh project item-add PROJECT_NUMBER --owner OWNER --url https://github.com/OWNER/REPO/issues/42
```

### Cause 2: Issue Missing Required Fields

Issue exists in project but fields not set, so it appears in wrong view.

**Diagnosis:**
```bash
# Check item field values
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            content { ... on Issue { number } }
            fieldValues(first: 10) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue { name }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq '.data.node.items.nodes[] | select(.content.number == 42)'
```

**Solution:**
```bash
# Set status field
# [GraphQL mutation to set Status = "Backlog"]
```

### Cause 3: Board View Filtering

Board view has filters that exclude the item.

**Diagnosis:**
- Check board filters in GitHub UI
- Look for filter icons on columns

**Solution:**
- Clear filters
- Or adjust item to match filter criteria

---

## 10.2 Status Not Reflecting

**Symptom:** Changed item status but board doesn't show the change.

### Cause 1: Wrong Field ID

Using incorrect field ID or option ID.

**Diagnosis:**
```bash
# Get correct field IDs
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        field(name: "Status") {
          ... on ProjectV2SingleSelectField {
            id
            options { id name }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID"
```

**Solution:**
Use the returned field ID and option IDs in your mutation.

### Cause 2: Mutation Failed Silently

GraphQL mutation returned success but didn't actually update.

**Diagnosis:**
```bash
# Check the response
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $optionId }
    }) {
      projectV2Item {
        id
        fieldValues(first: 5) {
          nodes {
            ... on ProjectV2ItemFieldSingleSelectValue { name }
          }
        }
      }
    }
  }
' ... 2>&1
```

**Solution:**
Check for errors in response, verify all IDs are correct.

### Cause 3: Caching

Browser or API caching showing stale data.

**Diagnosis:**
- Hard refresh browser (Cmd+Shift+R)
- Query API directly

**Solution:**
- Wait a moment and refresh
- Query directly instead of relying on cached view
