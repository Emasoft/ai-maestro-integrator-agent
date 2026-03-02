# GitHub Projects V2 GraphQL Queries - Mutations & Utilities

## Overview

This document is the **index** for mutations and utility queries for GitHub Projects V2 API operations.

For **read-only queries** (listing, discovering, filtering), see [graphql-queries-part1-read-operations.md](./graphql-queries-part1-read-operations.md).

---

## Table of Contents

### Section 1: Item Mutations
**File**: [graphql-queries-part2-mutations-section1-item-mutations.md](./graphql-queries-part2-mutations-section1-item-mutations.md)

| Section | When to Use |
|---------|-------------|
| 1.1 Add Issue to Project | When adding an existing issue to a project board |
| 1.2 Update Item Status | When changing an item's status field (e.g., Todo → In Progress) |
| 1.3 Update Item Text Field | When setting or updating a custom text field on an item |
| 1.4 Update Item Number Field | When setting or updating a custom number field on an item |
| 1.5 Update Item Iteration | When assigning an item to a sprint/iteration |
| 1.6 Archive Item | When archiving an item (keeping it but hiding from active views) |
| 1.7 Delete Item from Project | When removing an item completely from the project |

---

### Section 2: Issue Operations
**File**: [graphql-queries-part2-mutations-section2-issue-operations.md](./graphql-queries-part2-mutations-section2-issue-operations.md)

| Section | When to Use |
|---------|-------------|
| 2.1 Get Issue Node ID | When you need the GraphQL node ID for an issue by number |
| 2.2 Create Issue | When creating a new issue in a repository |
| 2.3 Update Issue | When modifying an existing issue's content |
| 2.4 Close Issue | When closing an issue programmatically |
| 2.5 Add Comment to Issue | When adding a comment to an issue thread |
| 2.6 Add Label to Issue | When applying labels to an issue |
| 2.7 Assign User to Issue | When assigning users to an issue |

---

### Section 3: PR Operations & Utilities
**File**: [graphql-queries-part2-mutations-section3-pr-utilities.md](./graphql-queries-part2-mutations-section3-pr-utilities.md)

| Section | When to Use |
|---------|-------------|
| 3.1 Get PR Node ID | When you need the GraphQL node ID for a pull request |
| 3.2 Link PR to Issue via Project | When connecting a PR to an issue through the project board |
| 4.1 Get Repository Node ID | When you need the repository's GraphQL node ID |
| 4.2 Get User Node ID | When you need a user's GraphQL node ID |
| 4.3 Get Label Node ID | When you need a label's GraphQL node ID |
| 4.4 List All Labels | When discovering all available labels in a repository |
| 5.0 Pagination Helper | When query returns many results requiring multiple pages |
| 6.0 Error Handling | When API calls fail or need debugging |

---

## Quick Reference

### All Mutations at a Glance

| Operation | Mutation Name | Section |
|-----------|---------------|---------|
| Add item to project | `addProjectV2ItemById` | [1.1](./graphql-queries-part2-mutations-section1-item-mutations.md#add-issue-to-project) |
| Update field value | `updateProjectV2ItemFieldValue` | [1.2-1.5](./graphql-queries-part2-mutations-section1-item-mutations.md#update-item-status) |
| Archive item | `archiveProjectV2Item` | [1.6](./graphql-queries-part2-mutations-section1-item-mutations.md#archive-item) |
| Delete item | `deleteProjectV2Item` | [1.7](./graphql-queries-part2-mutations-section1-item-mutations.md#delete-item-from-project) |
| Create issue | `createIssue` | [2.2](./graphql-queries-part2-mutations-section2-issue-operations.md#create-issue) |
| Update issue | `updateIssue` | [2.3](./graphql-queries-part2-mutations-section2-issue-operations.md#update-issue) |
| Close issue | `closeIssue` | [2.4](./graphql-queries-part2-mutations-section2-issue-operations.md#close-issue) |
| Add comment | `addComment` | [2.5](./graphql-queries-part2-mutations-section2-issue-operations.md#add-comment-to-issue) |
| Add labels | `addLabelsToLabelable` | [2.6](./graphql-queries-part2-mutations-section2-issue-operations.md#add-label-to-issue) |
| Assign users | `addAssigneesToAssignable` | [2.7](./graphql-queries-part2-mutations-section2-issue-operations.md#assign-user-to-issue) |

---

## Related Files

- [graphql-queries-part1-read-operations.md](./graphql-queries-part1-read-operations.md) - Project discovery, Field operations, Item queries
