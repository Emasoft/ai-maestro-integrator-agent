# Troubleshooting

This document provides troubleshooting guidance for common GitHub Projects Kanban issues.

## Table of Contents

### Part 1: Issue and Status Problems
See [troubleshooting-part1-issues-status.md](troubleshooting-part1-issues-status.md)

- 10.1 Issue not appearing on board after creation
  - Cause 1: Issue Not Added to Project
  - Cause 2: Issue Missing Required Fields
  - Cause 3: Board View Filtering
- 10.2 Status change not reflecting on board
  - Cause 1: Wrong Field ID
  - Cause 2: Mutation Failed Silently
  - Cause 3: Caching

### Part 2: Assignment and API Issues
See [troubleshooting-part2-assignment-api.md](troubleshooting-part2-assignment-api.md)

- 10.3 Assignment not showing correctly
  - Cause 1: User Not Found
  - Cause 2: User Not Collaborator
  - Cause 3: Assignment Limit
- 10.4 GraphQL API errors and rate limiting
  - Error: 401 Unauthorized
  - Error: 403 Forbidden
  - Error: Rate Limit Exceeded
  - Error: Bad Request

### Part 3: Permissions and Sync Issues
See [troubleshooting-part3-permissions-sync.md](troubleshooting-part3-permissions-sync.md)

- 10.5 Permission denied errors
  - Insufficient Token Scopes
  - Not Project Admin
  - Repository Access
- 10.6 Board state out of sync with reality
  - Issue Open but Shown as Done
  - PR Merged but Not Done
  - Multiple Items in Wrong Status

### Part 4: Stop Hook and Recovery Issues
See [troubleshooting-part4-hooks-recovery.md](troubleshooting-part4-hooks-recovery.md)

- 10.7 Stop hook blocking exit incorrectly
  - Stop Hook False Positive
  - Stop Hook Not Firing
  - Stop Hook Timeout
- 10.8 Recovery procedures for corrupted state
  - Full Board State Recovery
  - Orphaned Item Cleanup
  - Emergency Manual Fix

---

## Quick Reference

| Symptom | See Section |
|---------|-------------|
| Issue not on board | [Part 1 - 10.1](troubleshooting-part1-issues-status.md#101-issue-not-appearing) |
| Status not updating | [Part 1 - 10.2](troubleshooting-part1-issues-status.md#102-status-not-reflecting) |
| Assignment problems | [Part 2 - 10.3](troubleshooting-part2-assignment-api.md#103-assignment-issues) |
| API errors (401, 403, rate limit) | [Part 2 - 10.4](troubleshooting-part2-assignment-api.md#104-api-errors) |
| Permission denied | [Part 3 - 10.5](troubleshooting-part3-permissions-sync.md#105-permission-denied) |
| Board out of sync | [Part 3 - 10.6](troubleshooting-part3-permissions-sync.md#106-sync-issues) |
| Stop hook issues | [Part 4 - 10.7](troubleshooting-part4-hooks-recovery.md#107-stop-hook-issues) |
| Recovery procedures | [Part 4 - 10.8](troubleshooting-part4-hooks-recovery.md#108-recovery) |

---

## General Debugging Steps

1. **Check authentication**: `gh auth status`
2. **Check rate limits**: `gh api rate_limit --jq '.resources.graphql'`
3. **Verify project exists**: `gh project list --owner OWNER`
4. **Check issue state**: `gh issue view NUMBER --json state,stateReason`
5. **Check board status**: Query project items via GraphQL

## When to Escalate

- Persistent API errors after re-authentication
- Data corruption requiring manual intervention
- Permission issues at organization level
- Rate limiting during critical operations
