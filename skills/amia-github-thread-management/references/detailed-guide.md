# GitHub Thread Management -- Detailed Guide

## Contents

- [Decision Tree for Thread Operations](#decision-tree-for-thread-operations)
- [Key Concepts](#key-concepts)
- [Common Workflows](#common-workflows)
- [Script Usage Details](#script-usage-details)
- [Exit Codes](#exit-codes)
- [Error Handling](#error-handling)

## Decision Tree for Thread Operations

```
START: You need to handle a review thread
|
+-> Q: Has the requested change been implemented?
|   |
|   +-> YES: Do you need to explain what was done?
|   |   |
|   |   +-> YES: Reply THEN Resolve (two operations)
|   |   |       Use: amia_reply_to_thread.py --and-resolve
|   |   |
|   |   +-> NO: Just Resolve (no reply needed)
|   |           Use: amia_resolve_thread.py
|   |
|   +-> NO: Is clarification needed from the reviewer?
|       |
|       +-> YES: Reply only (keep thread OPEN)
|       |       Use: amia_reply_to_thread.py (without --and-resolve)
|       |
|       +-> NO: Leave thread untouched until you address it
|
+-> Q: Do you need to resolve MULTIPLE threads at once?
|   |
|   +-> YES: Use batch resolution (1 API call for N threads)
|           Use: amia_resolve_threads_batch.py
|
+-> Q: Do you need to find threads that still need attention?
    |
    +-> Find all unresolved threads:
    |   Use: amia_get_review_threads.py --unresolved-only
    |
    +-> Find comments without any replies:
        Use: amia_get_unaddressed_comments.py
```

## Key Concepts

### Thread vs Comment

- **Review Thread**: A container that holds one or more comments, anchored to a specific file/line in the PR diff.
- **Review Comment**: An individual message within a thread.
- **Thread ID**: The GraphQL node ID of the thread (PRRT_xxx format), needed for resolution operations.
- **Comment ID**: The GraphQL node ID of an individual comment.

### Thread States

| State | Meaning | When to Use |
|-------|---------|-------------|
| **Unresolved** | Thread requires attention | Default state, indicates pending work |
| **Resolved** | Thread has been addressed | After implementing requested change |

### The Reply-Resolve Separation

GitHub's API separates these operations because:

1. Replying adds a comment to the conversation
2. Resolving changes the thread's status metadata

You might reply without resolving (asking for clarification), or resolve without replying (when the code change speaks for itself).

## Common Workflows

### Workflow 1: Address All Unresolved Threads

```bash
# Step 1: Get all unresolved threads
python3 scripts/amia_get_review_threads.py --owner OWNER --repo REPO --pr 123 --unresolved-only

# Step 2: For each thread, make the code change, then resolve
python3 scripts/amia_resolve_thread.py --thread-id PRRT_xxxxx
```

### Workflow 2: Reply and Resolve in One Command

```bash
python3 scripts/amia_reply_to_thread.py \
  --thread-id PRRT_xxxxx \
  --body "Fixed by using the recommended approach" \
  --and-resolve
```

### Workflow 3: Batch Resolve After Large Refactor

```bash
python3 scripts/amia_resolve_threads_batch.py \
  --thread-ids "PRRT_aaa,PRRT_bbb,PRRT_ccc"
```

### Workflow 4: Find What Still Needs Attention

```bash
python3 scripts/amia_get_unaddressed_comments.py --owner OWNER --repo REPO --pr 123
```

## Script Usage Details

### amia_get_review_threads.py

```bash
python3 scripts/amia_get_review_threads.py \
  --owner <repository_owner> \
  --repo <repository_name> \
  --pr <pull_request_number> \
  [--unresolved-only]
```

**Output**: JSON array of thread objects with `id`, `isResolved`, `path`, `line`, `body` (first comment).

### amia_resolve_thread.py

```bash
python3 scripts/amia_resolve_thread.py --thread-id <PRRT_xxx>
```

**Output**: JSON object with `success`, `threadId`, `isResolved`.

### amia_resolve_threads_batch.py

```bash
python3 scripts/amia_resolve_threads_batch.py \
  --thread-ids "PRRT_aaa,PRRT_bbb,PRRT_ccc"
```

**Output**: JSON object with `results` array containing per-thread success/failure.

### amia_reply_to_thread.py

```bash
python3 scripts/amia_reply_to_thread.py \
  --thread-id <PRRT_xxx> \
  --body "Your reply message" \
  [--and-resolve]
```

**Output**: JSON object with `success`, `commentId`, `resolved` (if --and-resolve used).

### amia_get_unaddressed_comments.py

```bash
python3 scripts/amia_get_unaddressed_comments.py \
  --owner <repository_owner> \
  --repo <repository_name> \
  --pr <pull_request_number>
```

**Output**: JSON array of comments that have no replies, with `threadId`, `commentId`, `author`, `body`, `path`, `line`.

## Exit Codes

All scripts use standardized exit codes:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | Invalid parameters | Bad thread ID format, missing required args |
| 2 | Resource not found | Thread or PR does not exist |
| 3 | API error | Network, rate limit, timeout |
| 4 | Not authenticated | gh CLI not logged in |
| 5 | Idempotency skip | Thread already resolved (for resolve scripts) |
| 6 | Not mergeable | N/A for these scripts |

**Note:** `amia_resolve_threads_batch.py` returns exit code 0 for partial success. Check the JSON output's `summary.failed` field for individual failures.

## Error Handling

### "Thread not found" Error

**Cause**: The thread ID is incorrect or the thread was deleted.
**Solution**: Re-fetch thread IDs using `amia_get_review_threads.py`. Thread IDs start with `PRRT_`.

### Resolution Appears to Fail Silently

**Cause**: The mutation succeeded but the response wasn't checked properly.
**Solution**: The script verifies resolution by checking `isResolved` in the response. If `false`, check permissions.

### Cannot Resolve Thread - Permission Denied

**Cause**: Only the PR author and repository collaborators can resolve threads.
**Solution**: Ensure you're authenticated as a user with write access to the repository.

### Reply Added But Thread Still Unresolved

**Cause**: Expected behavior -- replying does not resolve.
**Solution**: Use `--and-resolve` flag with `amia_reply_to_thread.py`, or call `amia_resolve_thread.py` separately.

### GraphQL Rate Limiting

**Cause**: Too many API calls in short succession.
**Solution**: Use batch operations (`amia_resolve_threads_batch.py`) to resolve multiple threads in a single API call.
