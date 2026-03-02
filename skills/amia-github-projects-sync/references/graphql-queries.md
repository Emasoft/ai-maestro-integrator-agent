---
title: GraphQL Queries for GitHub Projects
category: reference
parent: github-projects-sync
related:
  - graphql-queries-index.md
  - graphql-queries-part1-read-operations.md
  - graphql-queries-part2-mutations.md
---

# GraphQL Queries for GitHub Projects

## Overview

This document provides the index to GraphQL queries for GitHub Projects V2 API operations. For detailed queries, see the linked reference files.

## Table of Contents

1. [When listing projects](#list-projects)
2. [When getting project items](#get-items)
3. [When updating item status](#update-status)
4. [When creating issues via GraphQL](#create-issues)
5. [When working with custom fields](#custom-fields)
6. [Detailed Query References](#detailed-query-references)

---

## List Projects

For listing organization or user projects:

```graphql
query($owner: String!) {
  organization(login: $owner) {
    projectsV2(first: 20) {
      nodes {
        id
        title
        number
        shortDescription
      }
    }
  }
}
```

See [graphql-queries-part1-read-operations.md](./graphql-queries-part1-read-operations.md) for complete read queries.

---

## Get Items

For retrieving project items with their fields:

```graphql
query($projectId: ID!) {
  node(id: $projectId) {
    ... on ProjectV2 {
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue { number title state }
            ... on PullRequest { number title state }
          }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field { ... on ProjectV2SingleSelectField { name } }
              }
            }
          }
        }
      }
    }
  }
}
```

See [graphql-queries-part1-read-operations.md](./graphql-queries-part1-read-operations.md) for complete read queries.

---

## Update Status

For updating item status field:

```graphql
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId
    itemId: $itemId
    fieldId: $fieldId
    value: { singleSelectOptionId: $optionId }
  }) {
    projectV2Item { id }
  }
}
```

See [graphql-queries-part2-mutations.md](./graphql-queries-part2-mutations.md) for complete mutation queries.

---

## Create Issues

For creating issues via GraphQL:

```graphql
mutation($repositoryId: ID!, $title: String!, $body: String!) {
  createIssue(input: {
    repositoryId: $repositoryId
    title: $title
    body: $body
  }) {
    issue {
      id
      number
      url
    }
  }
}
```

See [graphql-queries-part2-mutations-section2-issue-operations.md](./graphql-queries-part2-mutations-section2-issue-operations.md) for issue operations.

---

## Custom Fields

For working with project custom fields:

```graphql
query($projectId: ID!) {
  node(id: $projectId) {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2Field { id name }
          ... on ProjectV2SingleSelectField {
            id
            name
            options { id name }
          }
          ... on ProjectV2IterationField {
            id
            name
            configuration {
              iterations { id title startDate }
            }
          }
        }
      }
    }
  }
}
```

---

## Detailed Query References

For complete query documentation organized by operation type:

| Reference File | Contents |
|---------------|----------|
| [graphql-queries-index.md](./graphql-queries-index.md) | Master index of all queries |
| [graphql-queries-part1-read-operations.md](./graphql-queries-part1-read-operations.md) | All read/query operations |
| [graphql-queries-part2-mutations.md](./graphql-queries-part2-mutations.md) | All mutation operations |
| [graphql-queries-part2-mutations-section1-item-mutations.md](./graphql-queries-part2-mutations-section1-item-mutations.md) | Project item mutations |
| [graphql-queries-part2-mutations-section2-issue-operations.md](./graphql-queries-part2-mutations-section2-issue-operations.md) | Issue-specific operations |
| [graphql-queries-part2-mutations-section3-pr-utilities.md](./graphql-queries-part2-mutations-section3-pr-utilities.md) | PR-related utilities |
