# GitHub Thread Management Skill

Manage GitHub Pull Request review threads - resolve, unresolve, reply to comments, and track unaddressed feedback. **Critical**: Replying to a thread does NOT automatically resolve it; resolution requires a separate API call.

## When to Use

- Resolve review threads after implementing requested changes
- Reply to reviewer comments (with or without resolving)
- Find unresolved or unaddressed comments needing attention
- Batch-resolve multiple threads efficiently (single API call)

## Quick Reference

### Available Scripts

| Script | Purpose |
|--------|---------|
| `amia_get_review_threads.py` | List all review threads (optionally unresolved only) |
| `amia_get_thread_by_id.py` | Get a single thread by its GraphQL ID |
| `amia_resolve_thread.py` | Resolve a single thread |
| `amia_unresolve_thread.py` | Unresolve (reopen) a resolved thread |
| `amia_resolve_threads_batch.py` | Resolve multiple threads in one API call |
| `amia_reply_to_thread.py` | Reply to a thread (optional `--and-resolve`) |
| `amia_get_unaddressed_comments.py` | Find comments without replies |

### Common Commands

```bash
# Get unresolved threads
python3 scripts/amia_get_review_threads.py --owner OWNER --repo REPO --pr 123 --unresolved-only

# Reply and resolve in one command
python3 scripts/amia_reply_to_thread.py --thread-id PRRT_xxx --body "Fixed" --and-resolve

# Batch resolve after large refactor
python3 scripts/amia_resolve_threads_batch.py --thread-ids "PRRT_aaa,PRRT_bbb"

# Reopen a resolved thread for further discussion
python3 scripts/amia_unresolve_thread.py --thread-id PRRT_xxx
```

## Documentation

- **SKILL.md** - Full skill instructions with decision tree and workflows
- **references/thread-resolution-protocol.md** - GraphQL mutations and batch operations
- **references/thread-conversation-tracking.md** - Query structure and comment tracking

## Key Concept

Thread states: **Unresolved** (needs attention) vs **Resolved** (addressed). Reply and resolve are separate operations - use `--and-resolve` flag when you need both.
