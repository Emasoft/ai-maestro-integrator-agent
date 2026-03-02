# Troubleshooting Part 4: CLI, Rate Limiting, and Webhook Issues

[Back to Troubleshooting Index](troubleshooting.md)

## Contents
- GitHub CLI Issues
  - Problem: "gh: command not found"
  - Problem: "gh: command works in terminal but not in scripts"
- Rate Limiting Issues
  - Problem: "API rate limit exceeded"
  - Problem: "Secondary rate limit exceeded"
- Webhook Issues
  - Problem: Webhooks not triggering

---

## GitHub CLI Issues

### Problem: "gh: command not found"

**Cause:** GitHub CLI not installed or not in PATH.

**Solution:**

**Install GitHub CLI:**

**macOS:**
```bash
brew install gh
```

**Linux (Debian/Ubuntu):**
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

**Verify installation:**
```bash
gh --version
```

---

### Problem: "gh: command works in terminal but not in scripts"

**Cause:** PATH not set correctly in script environment.

**Solution:**

Add GitHub CLI to script PATH:
```bash
#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

gh issue list
```

Or use full path to `gh`:
```bash
#!/bin/bash
/usr/local/bin/gh issue list
```

---

## Rate Limiting Issues

### Problem: "API rate limit exceeded"

**Symptoms:**
```
Error: HTTP 403: API rate limit exceeded for user ID xxxxxx. (https://api.github.com/...)
```

**Cause:** Too many API requests in short time period.

**Solution:**

**Step 1: Check current rate limit status**
```bash
gh api rate_limit
```

**Step 2: Wait for rate limit reset**
Output shows when rate limit resets (usually 1 hour from first request).

**Step 3: Add rate limiting to scripts**
```bash
#!/bin/bash
# Add sleep between operations
for ISSUE in $ISSUES; do
  gh issue edit "$ISSUE" --add-label "feature"
  sleep 1  # Wait 1 second between requests
done
```

**Step 4: Use GraphQL for bulk operations**
GraphQL allows fetching more data in single request:
```bash
gh api graphql -f query='
{
  repository(owner: "owner", name: "repo") {
    issues(first: 100) {
      nodes {
        number
        title
        labels(first: 10) {
          nodes {
            name
          }
        }
      }
    }
  }
}'
```

---

### Problem: "Secondary rate limit exceeded"

**Symptoms:**
```
Error: You have exceeded a secondary rate limit
```

**Cause:** Too many write operations (creates, updates, deletes) in short time.

**Solution:**

**Slow down write operations:**
```bash
# Increase sleep time between writes
for ISSUE in $ISSUES; do
  gh issue create --title "..." --body "..."
  sleep 2  # Increase to 2+ seconds
done
```

**Batch operations when possible:**
Use GraphQL mutations to perform multiple updates in single request.

---

## Webhook Issues

### Problem: Webhooks not triggering

**Symptoms:**
- Update issue in GitHub
- Webhook endpoint not called
- No sync occurs

**Diagnosis:**

**Step 1: Verify webhook exists**
```bash
gh api repos/owner/repo/hooks
```

**Step 2: Check webhook deliveries**
```bash
gh api repos/owner/repo/hooks/<hook_id>/deliveries
```

**Step 3: View failed delivery details**
```bash
gh api repos/owner/repo/hooks/<hook_id>/deliveries/<delivery_id>
```

**Solution:**

**If webhook doesn't exist:**
Create webhook:
1. Go to repository Settings → Webhooks
2. Add webhook
3. Set Payload URL: `https://your-server.com/webhook`
4. Set Content type: `application/json`
5. Select events: Issues, Pull requests

**If webhook is failing:**
Check delivery error response:
- **404 Not Found** → Verify endpoint URL is correct
- **500 Internal Server Error** → Check webhook handler logs
- **Timeout** → Ensure endpoint responds within 10 seconds

**Test webhook manually:**
```bash
# Redeliver a webhook
gh api repos/owner/repo/hooks/<hook_id>/deliveries/<delivery_id>/attempts -X POST
```
