# Issue Operations for GitHub Projects V2

This section covers GraphQL queries and mutations for working with GitHub issues.

**Parent document**: [graphql-queries-part2-mutations.md](./graphql-queries-part2-mutations.md)

---

## Table of Contents

- 2.1 [Get Issue Node ID](#get-issue-node-id)
- 2.2 [Create Issue](#create-issue)
- 2.3 [Update Issue](#update-issue)
- 2.4 [Close Issue](#close-issue)
- 2.5 [Add Comment to Issue](#add-comment-to-issue)
- 2.6 [Add Label to Issue](#add-label-to-issue)
- 2.7 [Assign User to Issue](#assign-user-to-issue)

---

## Get Issue Node ID

```bash
gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      issue(number: $number) {
        id
        number
        title
        state
        projectItems(first: 10) {
          nodes {
            id
            project {
              title
              number
            }
          }
        }
      }
    }
  }
' -f owner="OWNER" -f repo="REPO" -F number=42
```

---

## Create Issue

```bash
gh api graphql -f query='
  mutation($repositoryId: ID!, $title: String!, $body: String!, $labelIds: [ID!]) {
    createIssue(input: {
      repositoryId: $repositoryId
      title: $title
      body: $body
      labelIds: $labelIds
    }) {
      issue {
        id
        number
        url
      }
    }
  }
' -f repositoryId="REPO_NODE_ID" -f title="Issue Title" -f body="Issue body"
```

---

## Update Issue

```bash
gh api graphql -f query='
  mutation($issueId: ID!, $body: String!) {
    updateIssue(input: {
      id: $issueId
      body: $body
    }) {
      issue {
        id
        body
      }
    }
  }
' -f issueId="ISSUE_NODE_ID" -f body="Updated body content"
```

---

## Close Issue

```bash
gh api graphql -f query='
  mutation($issueId: ID!) {
    closeIssue(input: {
      issueId: $issueId
      stateReason: COMPLETED
    }) {
      issue {
        id
        state
        closedAt
      }
    }
  }
' -f issueId="ISSUE_NODE_ID"
```

---

## Add Comment to Issue

```bash
gh api graphql -f query='
  mutation($subjectId: ID!, $body: String!) {
    addComment(input: {
      subjectId: $subjectId
      body: $body
    }) {
      commentEdge {
        node {
          id
          body
          createdAt
        }
      }
    }
  }
' -f subjectId="ISSUE_NODE_ID" -f body="Comment text here"
```

---

## Add Label to Issue

```bash
gh api graphql -f query='
  mutation($labelableId: ID!, $labelIds: [ID!]!) {
    addLabelsToLabelable(input: {
      labelableId: $labelableId
      labelIds: $labelIds
    }) {
      labelable {
        ... on Issue {
          labels(first: 10) {
            nodes { name }
          }
        }
      }
    }
  }
' -f labelableId="ISSUE_NODE_ID" -f labelIds='["LABEL_NODE_ID"]'
```

---

## Assign User to Issue

```bash
gh api graphql -f query='
  mutation($assignableId: ID!, $assigneeIds: [ID!]!) {
    addAssigneesToAssignable(input: {
      assignableId: $assignableId
      assigneeIds: $assigneeIds
    }) {
      assignable {
        ... on Issue {
          assignees(first: 5) {
            nodes { login }
          }
        }
      }
    }
  }
' -f assignableId="ISSUE_NODE_ID" -f assigneeIds='["USER_NODE_ID"]'
```

---

## Related Sections

- [Item Mutations](./graphql-queries-part2-mutations-section1-item-mutations.md)
- [PR Operations & Utilities](./graphql-queries-part2-mutations-section3-pr-utilities.md)
