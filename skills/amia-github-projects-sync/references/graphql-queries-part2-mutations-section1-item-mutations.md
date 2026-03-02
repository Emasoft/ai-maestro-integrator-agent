# Item Mutations for GitHub Projects V2

This section covers mutations for creating, updating, and managing project items.

**Parent document**: [graphql-queries-part2-mutations.md](./graphql-queries-part2-mutations.md)

---

## Table of Contents

- 1.1 [Add Issue to Project](#add-issue-to-project)
- 1.2 [Update Item Status](#update-item-status)
- 1.3 [Update Item Text Field](#update-item-text-field)
- 1.4 [Update Item Number Field](#update-item-number-field)
- 1.5 [Update Item Iteration](#update-item-iteration)
- 1.6 [Archive Item](#archive-item)
- 1.7 [Delete Item from Project](#delete-item-from-project)

---

## Add Issue to Project

```bash
gh api graphql -f query='
  mutation($projectId: ID!, $contentId: ID!) {
    addProjectV2ItemById(input: {
      projectId: $projectId
      contentId: $contentId
    }) {
      item {
        id
        content {
          ... on Issue {
            number
            title
          }
        }
      }
    }
  }
' -f projectId="PROJECT_NODE_ID" -f contentId="ISSUE_NODE_ID"
```

---

## Update Item Status

```bash
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
            ... on ProjectV2ItemFieldSingleSelectValue {
              name
            }
          }
        }
      }
    }
  }
' -f projectId="PROJECT_NODE_ID" -f itemId="ITEM_NODE_ID" -f fieldId="STATUS_FIELD_ID" -f optionId="NEW_STATUS_OPTION_ID"
```

---

## Update Item Text Field

```bash
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $text: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { text: $text }
    }) {
      projectV2Item {
        id
      }
    }
  }
' -f projectId="PROJECT_NODE_ID" -f itemId="ITEM_NODE_ID" -f fieldId="TEXT_FIELD_ID" -f text="New text value"
```

---

## Update Item Number Field

```bash
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $number: Float!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { number: $number }
    }) {
      projectV2Item {
        id
      }
    }
  }
' -f projectId="PROJECT_NODE_ID" -f itemId="ITEM_NODE_ID" -f fieldId="NUMBER_FIELD_ID" -F number=42
```

---

## Update Item Iteration

```bash
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $iterationId: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { iterationId: $iterationId }
    }) {
      projectV2Item {
        id
      }
    }
  }
' -f projectId="PROJECT_NODE_ID" -f itemId="ITEM_NODE_ID" -f fieldId="ITERATION_FIELD_ID" -f iterationId="ITERATION_ID"
```

---

## Archive Item

```bash
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!) {
    archiveProjectV2Item(input: {
      projectId: $projectId
      itemId: $itemId
    }) {
      item {
        id
        isArchived
      }
    }
  }
' -f projectId="PROJECT_NODE_ID" -f itemId="ITEM_NODE_ID"
```

---

## Delete Item from Project

```bash
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!) {
    deleteProjectV2Item(input: {
      projectId: $projectId
      itemId: $itemId
    }) {
      deletedItemId
    }
  }
' -f projectId="PROJECT_NODE_ID" -f itemId="ITEM_NODE_ID"
```

---

## Related Sections

- [Issue Operations](./graphql-queries-part2-mutations-section2-issue-operations.md)
- [PR Operations & Utilities](./graphql-queries-part2-mutations-section3-pr-utilities.md)
