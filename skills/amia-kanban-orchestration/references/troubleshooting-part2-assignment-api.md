# Troubleshooting Part 2: Assignment and API Issues

## Table of Contents

- [10.3 Assignment Issues](#103-assignment-issues)
  - [Cause 1: User Not Found](#cause-1-user-not-found)
  - [Cause 2: User Not Collaborator](#cause-2-user-not-collaborator)
  - [Cause 3: Assignment Limit](#cause-3-assignment-limit)
- [10.4 API Errors](#104-api-errors)
  - [Error: 401 Unauthorized](#error-401-unauthorized)
  - [Error: 403 Forbidden](#error-403-forbidden)
  - [Error: Rate Limit Exceeded](#error-rate-limit-exceeded)
  - [Error: Bad Request](#error-bad-request)

## 10.3 Assignment Issues

**Symptom:** Assignee not showing on issue or board.

### Cause 1: User Not Found

Username doesn't exist or is misspelled.

**Diagnosis:**
```bash
# Check if user exists
gh api users/agent-1
```

**Solution:**
```bash
# Use correct username
gh issue edit 42 --add-assignee correct-username
```

### Cause 2: User Not Collaborator

User cannot be assigned because they're not a collaborator.

**Diagnosis:**
```bash
# Check collaborators
gh api repos/OWNER/REPO/collaborators --jq '.[].login'
```

**Solution:**
```bash
# Add as collaborator first
gh api repos/OWNER/REPO/collaborators/username --method PUT
```

### Cause 3: Assignment Limit

GitHub limits assignees (usually 10).

**Diagnosis:**
```bash
# Check current assignees
gh issue view 42 --json assignees --jq '.assignees | length'
```

**Solution:**
Remove some assignees before adding new ones.

---

## 10.4 API Errors

### Error: 401 Unauthorized

**Symptom:** `401 Unauthorized` from API calls.

**Diagnosis:**
```bash
gh auth status
```

**Solution:**
```bash
# Re-authenticate
gh auth login

# Or refresh token
gh auth refresh
```

### Error: 403 Forbidden

**Symptom:** `403 Forbidden` - usually rate limiting or permissions.

**Diagnosis:**
```bash
# Check rate limit
gh api rate_limit --jq '.resources.graphql'
```

**Solution:**
- If rate limited: Wait for reset
- If permissions: Check token scopes

### Error: Rate Limit Exceeded

**Symptom:** `API rate limit exceeded`

**Diagnosis:**
```bash
gh api rate_limit --jq '{
  limit: .resources.graphql.limit,
  remaining: .resources.graphql.remaining,
  reset: .resources.graphql.reset | todate
}'
```

**Solution:**
- Wait until reset time
- Batch operations
- Use conditional requests (ETags)

### Error: Bad Request

**Symptom:** `400 Bad Request` - malformed query.

**Diagnosis:**
Check query syntax, especially:
- Missing variables
- Wrong types
- Invalid field names

**Solution:**
Validate GraphQL query in GitHub GraphQL Explorer first.
