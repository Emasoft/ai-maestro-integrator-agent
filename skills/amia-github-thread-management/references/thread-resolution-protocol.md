# Thread Resolution Protocol

This document explains how to resolve and unresolve GitHub PR review threads using the GraphQL API.

## Table of Contents

- 1.1 Why thread resolution is separate from replying
- 1.2 Single thread resolution workflow
  - 1.2.1 Getting the thread's GraphQL node ID
  - 1.2.2 The resolveReviewThread mutation
  - 1.2.3 Verifying resolution succeeded
- 1.3 Batch thread resolution using GraphQL aliases
  - 1.3.1 Constructing aliased mutations
  - 1.3.2 Handling partial failures
  - 1.3.3 Performance considerations
- 1.4 When to resolve vs when to keep open
  - 1.4.1 Resolve immediately scenarios
  - 1.4.2 Keep open scenarios
- 1.5 Unresolving threads (reopening discussion)

---

## 1.1 Why Thread Resolution is Separate from Replying

GitHub designed review threads with two distinct operations:

**Adding a Reply**: Creates a new comment in the thread's conversation. This is a `addPullRequestReviewComment` mutation that appends content to the discussion.

**Resolving a Thread**: Changes the thread's `isResolved` boolean flag from `false` to `true`. This is a `resolveReviewThread` mutation that updates metadata only.

These are separate because they serve different purposes:

| Action | Effect | Use Case |
|--------|--------|----------|
| Reply only | Adds comment, thread stays open | Asking clarifying questions |
| Resolve only | Closes thread, no new comment | Code change speaks for itself |
| Reply + Resolve | Adds comment AND closes thread | Explaining what you changed |

**Common Misconception**: Many developers assume that replying to a comment automatically resolves the thread. This is FALSE. You must explicitly call the resolve mutation.

---

## 1.2 Single Thread Resolution Workflow

### 1.2.1 Getting the Thread's GraphQL Node ID

To resolve a thread, you need its GraphQL node ID (not the REST API numeric ID). Thread IDs look like: `PRRT_kwDOxxxxxx`

**Query to get thread IDs:**

```graphql
query GetPRThreads($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          path
          line
          comments(first: 1) {
            nodes {
              body
              author {
                login
              }
            }
          }
        }
      }
    }
  }
}
```

**Using gh CLI:**

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      pullRequest(number: 123) {
        reviewThreads(first: 100) {
          nodes {
            id
            isResolved
            path
          }
        }
      }
    }
  }
'
```

### 1.2.2 The resolveReviewThread Mutation

**GraphQL Mutation:**

```graphql
mutation ResolveThread($threadId: ID!) {
  resolveReviewThread(input: {threadId: $threadId}) {
    thread {
      id
      isResolved
    }
  }
}
```

**Using gh CLI:**

```bash
gh api graphql -f query='
  mutation {
    resolveReviewThread(input: {threadId: "PRRT_kwDOxxxxxx"}) {
      thread {
        id
        isResolved
      }
    }
  }
'
```

**Required Permissions:**
- Must be authenticated as the PR author OR a repository collaborator
- Read/write access to pull requests

### 1.2.3 Verifying Resolution Succeeded

The mutation response includes the thread's new state. Verify that `isResolved` is `true`:

```json
{
  "data": {
    "resolveReviewThread": {
      "thread": {
        "id": "PRRT_kwDOxxxxxx",
        "isResolved": true
      }
    }
  }
}
```

**If `isResolved` is still `false`:**
- Check authentication and permissions
- Verify the thread ID is correct
- The thread may already be deleted

---

## 1.3 Batch Thread Resolution Using GraphQL Aliases

GraphQL aliases allow you to execute multiple mutations in a single API call. This is essential for efficiency when resolving many threads.

### 1.3.1 Constructing Aliased Mutations

**Single API call to resolve 3 threads:**

```graphql
mutation BatchResolve {
  thread1: resolveReviewThread(input: {threadId: "PRRT_aaa"}) {
    thread { id isResolved }
  }
  thread2: resolveReviewThread(input: {threadId: "PRRT_bbb"}) {
    thread { id isResolved }
  }
  thread3: resolveReviewThread(input: {threadId: "PRRT_ccc"}) {
    thread { id isResolved }
  }
}
```

**Aliases (`thread1`, `thread2`, `thread3`) are required** because GraphQL doesn't allow duplicate field names. Each alias becomes a key in the response.

**Using gh CLI with constructed query:**

```bash
gh api graphql -f query='
  mutation {
    t0: resolveReviewThread(input: {threadId: "PRRT_aaa"}) {
      thread { id isResolved }
    }
    t1: resolveReviewThread(input: {threadId: "PRRT_bbb"}) {
      thread { id isResolved }
    }
  }
'
```

### 1.3.2 Handling Partial Failures

In a batch mutation, each aliased mutation is independent. If one fails, others may still succeed.

**Response with partial failure:**

```json
{
  "data": {
    "thread1": {
      "thread": { "id": "PRRT_aaa", "isResolved": true }
    },
    "thread2": null,
    "thread3": {
      "thread": { "id": "PRRT_ccc", "isResolved": true }
    }
  },
  "errors": [
    {
      "path": ["thread2"],
      "message": "Could not resolve thread"
    }
  ]
}
```

**Handling strategy:**
1. Check if `errors` array exists in response
2. For each alias in `data`, check if value is `null` (failed) or has `thread.isResolved: true` (succeeded)
3. Report failed thread IDs for retry or investigation

### 1.3.3 Performance Considerations

| Approach | API Calls | Rate Limit Impact |
|----------|-----------|-------------------|
| Individual resolution | N calls for N threads | High |
| Batch resolution | 1 call for N threads | Low |

**Recommended batch sizes:**
- Up to 50 threads per batch is safe
- GitHub may reject very large mutations (>100 threads)
- For >50 threads, split into multiple batches

---

## 1.4 When to Resolve vs When to Keep Open

### 1.4.1 Resolve Immediately Scenarios

**Resolve the thread when:**

1. **You implemented the requested change**
   - The code now matches what the reviewer asked for
   - No further discussion needed

2. **You chose an alternative approach with reviewer agreement**
   - Reviewer asked for X, you proposed Y, reviewer approved Y
   - Document the decision in a reply before resolving

3. **The comment was a typo/nitpick you fixed**
   - Simple fixes don't need discussion
   - Resolve after pushing the fix

4. **The reviewer marked it as optional/FYI**
   - Comments prefixed with "nit:", "optional:", or "FYI:"
   - Resolve after acknowledging (if at all)

5. **The comment is outdated due to subsequent changes**
   - Code was already modified in a later commit
   - Reply explaining it's addressed, then resolve

### 1.4.2 Keep Open Scenarios

**Do NOT resolve the thread when:**

1. **You need clarification from the reviewer**
   - You don't understand what change is requested
   - Keep open until you get an answer

2. **You disagree and want to discuss**
   - You think current code is correct
   - Keep open until consensus is reached

3. **You haven't implemented the change yet**
   - Don't pre-emptively resolve
   - Resolve only after the fix is pushed

4. **The thread involves multiple issues**
   - One comment mentions several problems
   - Keep open until ALL issues are addressed

5. **You're waiting for CI/tests**
   - Your fix might not work
   - Resolve after tests pass

---

## 1.5 Unresolving Threads (Reopening Discussion)

Threads can be unresolve to continue discussion:

**GraphQL Mutation:**

```graphql
mutation UnresolveThread($threadId: ID!) {
  unresolveReviewThread(input: {threadId: $threadId}) {
    thread {
      id
      isResolved
    }
  }
}
```

**Using gh CLI:**

```bash
gh api graphql -f query='
  mutation {
    unresolveReviewThread(input: {threadId: "PRRT_kwDOxxxxxx"}) {
      thread {
        id
        isResolved
      }
    }
  }
'
```

**When to unresolve:**

1. **Reviewer found the fix insufficient**
   - The change didn't fully address the concern
   - Unresolve and add a comment explaining

2. **New related issue discovered**
   - The original comment applies to new code
   - Unresolve rather than creating a new thread

3. **Accidental resolution**
   - Thread was resolved prematurely
   - Unresolve immediately

**Permissions:** Same as resolving - PR author or collaborator.
