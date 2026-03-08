---
name: amia-github-thread-management
description: "Use when managing PR review threads. Reply does NOT auto-resolve threads. Trigger with /manage-threads."
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: "1.0.0"
  author: Emasoft
  tags: "github, pull-request, code-review, thread-management"
  triggers: "resolve review thread, unresolve thread, reply to comment, track review comments, unaddressed comments, batch resolve threads"
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub Thread Management Skill

## Overview

Manage GitHub PR review threads: list, reply, resolve, and batch-resolve. Replying to a thread does NOT auto-resolve it -- resolution requires a separate GraphQL mutation.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+ for automation scripts
- Repository collaborator access (required for resolving)
- GraphQL API access

## Instructions

1. **List unresolved threads**: Run `amia_get_review_threads.py --unresolved-only`
2. **Decide action per thread**: Reply only (needs clarification), resolve only (code speaks for itself), or reply+resolve (explain and close)
3. **Execute**: Run the appropriate script with required parameters
4. **Verify**: Check JSON output `success` field
5. **Track**: Re-run listing to confirm all threads addressed

### Checklist

- [ ] List unresolved threads with `amia_get_review_threads.py --unresolved-only`
- [ ] Determine action per thread (reply / resolve / both)
- [ ] For implemented changes: resolve (optionally with reply via `--and-resolve`)
- [ ] For clarification needed: reply only (keep open)
- [ ] For batch operations: use `amia_resolve_threads_batch.py`
- [ ] Verify each operation via JSON output
- [ ] Re-run listing to confirm completion
- [ ] Check for unreplied comments with `amia_get_unaddressed_comments.py`

## Output

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the operation completed |
| `threadId` | string | GraphQL node ID (PRRT_xxx format) |
| `isResolved` | boolean | Resolution state after operation |
| `commentId` | string | (Reply ops) Created comment node ID |
| `results` | array | (Batch ops) Per-thread results |
| `error` | string | (On failure) Error message |

> **Output discipline:** All scripts support `--output-file <path>`. With flag: JSON to file, summary to stderr. Without: JSON to stdout.

## Reference Documents

**Protocols:**

- `references/thread-resolution-protocol.md` -- Resolution workflow, GraphQL mutations, batch operations, when to resolve vs keep open
- `references/thread-conversation-tracking.md` -- Thread history queries, addressed vs unaddressed tracking, comment threading model

**Detailed Guide:**

- `references/detailed-guide.md` -- Decision tree, key concepts, error handling, script usage details, exit codes, common workflows

## Available Scripts

| Script | Purpose | Key Parameters |
|--------|---------|----------------|
| `amia_get_review_threads.py` | List review threads | `--owner`, `--repo`, `--pr`, `--unresolved-only` |
| `amia_resolve_thread.py` | Resolve single thread | `--thread-id` |
| `amia_resolve_threads_batch.py` | Batch resolve (1 API call) | `--thread-ids` (comma-separated) |
| `amia_reply_to_thread.py` | Reply to thread | `--thread-id`, `--body`, `--and-resolve` |
| `amia_get_unaddressed_comments.py` | Find unreplied comments | `--owner`, `--repo`, `--pr` |

## Examples

### Example: Reply and Resolve

```bash
# List unresolved threads
python3 scripts/amia_get_review_threads.py --owner myorg --repo myrepo --pr 123 --unresolved-only

# Reply and resolve in one command
python3 scripts/amia_reply_to_thread.py \
  --thread-id PRRT_xyz \
  --body "Fixed by refactoring validation logic" \
  --and-resolve
# Output: {"success": true, "commentId": "...", "resolved": true}
```
