# CI Notification Setup

## Table of Contents

1. [When understanding CI notification system](#overview)
2. [When configuring GitHub webhooks](#setup-steps)
3. [When understanding event types and notifications](#event-types-and-notifications)
4. [When customizing notification configuration](#configuration-options)
5. [If webhook delivery or notification issues occur](#troubleshooting)
6. [When ensuring webhook security](#security-considerations)
7. [When handling multiple repositories](#advanced-multiple-repositories)
8. [When integrating CI events with project sync](#integration-with-project-sync)

Configure GitHub webhooks to send CI events to the integrator-agent.

## Overview

The webhook handler receives GitHub events (CI status, PR changes, issue updates) and forwards them as AI Maestro notifications to the orchestrator agent.

## Setup Steps

### 1. Start the Webhook Server

**Local Development (using ngrok):**
```bash
# Start webhook handler
cd ~/.claude/skills/integrator-agent/skills/amia-github-projects-sync/scripts
python ci_webhook_handler.py --port 9000

# In another terminal, expose with ngrok
ngrok http 9000

# Note the ngrok URL (e.g., https://abc123.ngrok.io)
```

**Production (on server):**
```bash
# Run as systemd service
sudo systemctl start github-webhook-handler

# Or use PM2
pm2 start ci_webhook_handler.py --name github-webhook -- --port 9000
```

### 2. Generate Webhook Secret

Create a secure random secret for webhook verification:

```bash
# Generate secret
python -c "import secrets; print(secrets.token_hex(32))"

# Set environment variable
export GITHUB_WEBHOOK_SECRET="your_generated_secret_here"

# Add to .env file (gitignored)
echo "GITHUB_WEBHOOK_SECRET=your_generated_secret_here" >> ~/design/.env
```

### 3. Configure GitHub Webhook

**Via GitHub UI:**

1. Go to your repository settings
2. Navigate to: Settings → Webhooks → Add webhook
3. Configure:
   - **Payload URL**: `https://your-server.com:9000` or ngrok URL
   - **Content type**: `application/json`
   - **Secret**: Your `GITHUB_WEBHOOK_SECRET` value
   - **SSL verification**: Enable (required for production)
   - **Events**: Select individual events:
     - Workflow runs
     - Check runs
     - Pull requests
     - Issues
     - Pushes (optional, for branch monitoring)
   - **Active**: ✓ Checked

4. Click "Add webhook"

**Via GitHub CLI:**

```bash
# Set webhook for repository
gh api repos/OWNER/REPO/hooks \
  -X POST \
  -f name='web' \
  -f active=true \
  -F 'config[url]=https://your-server.com:9000' \
  -F 'config[content_type]=json' \
  -F 'config[secret]=YOUR_SECRET_HERE' \
  -F 'config[insecure_ssl]=0' \
  -f events[]='workflow_run' \
  -f events[]='check_run' \
  -f events[]='pull_request' \
  -f events[]='issues' \
  -f events[]='push'
```

### 4. Test Webhook

**Test with sample payload:**

```bash
# Create test payload
cat > /tmp/test_webhook.json << 'EOF'
{
  "_event_type": "workflow_run",
  "action": "completed",
  "workflow_run": {
    "id": 12345,
    "name": "CI Tests",
    "conclusion": "failure",
    "head_branch": "feature/test",
    "html_url": "https://github.com/owner/repo/actions/runs/12345"
  },
  "repository": {
    "full_name": "owner/repo"
  }
}
EOF

# Test handler
python ci_webhook_handler.py --test /tmp/test_webhook.json
```

**Trigger real webhook:**

```bash
# Push a commit to trigger workflow_run event
git commit --allow-empty -m "Test webhook"
git push

# Check webhook delivery in GitHub:
# Settings → Webhooks → Your webhook → Recent Deliveries
```

### 5. Monitor Webhook Logs

Webhook events are logged to `~/design/webhook_logs/`:

```bash
# View recent webhooks
ls -lt ~/design/webhook_logs/ | head -10

# Inspect specific event
cat ~/design/webhook_logs/20260101_123045_workflow_run.json | jq .

# Monitor in real-time
tail -f ~/design/webhook_logs/*.json
```

## Event Types and Notifications

| GitHub Event | Notification Type | Priority | Trigger Condition |
|--------------|------------------|----------|-------------------|
| `workflow_run` (success) | `ci_success` | low | All workflows pass |
| `workflow_run` (failure) | `ci_failure` | high | Any workflow fails |
| `check_run` (failure) | `ci_failure` | medium | Individual check fails |
| `pull_request` (opened) | `pr_created` | medium | New PR created |
| `pull_request` (closed+merged) | `pr_merged` | low | PR merged to main |
| `issues` (labeled: blocked) | `task_blocked` | high | Issue labeled "blocked" |
| `push` (watched branch) | generic | low | Commit to main/master/develop |

## Configuration Options

**Environment Variables:**

```bash
# Required
export GITHUB_WEBHOOK_SECRET="your_secret"

# Optional
export WEBHOOK_PORT=9000                    # Default: 9000
export WATCHED_BRANCHES="main,develop,prod" # Default: main,master,develop
export LOG_DIR="$HOME/design/webhook_logs"  # Default: ~/design/webhook_logs
```

**Handler Configuration:**

Edit `ci_webhook_handler.py` to customize:

```python
# Watched branches for push notifications
WATCHED_BRANCHES = {'main', 'master', 'develop', 'staging'}

# Notification priorities
PRIORITY_MAP = {
    'workflow_run.failure': 'high',
    'check_run.failure': 'medium',
    'pull_request.opened': 'medium',
    'issues.labeled.blocked': 'high'
}
```

## Troubleshooting

### Webhook Delivery Failures

**Check GitHub webhook delivery log:**
1. Go to Settings → Webhooks → Your webhook
2. Click "Recent Deliveries"
3. Click on failed delivery
4. Check "Response" tab for error details

**Common issues:**

- **Connection refused**: Handler not running or wrong port
  ```bash
  # Verify handler is running
  ps aux | grep ci_webhook_handler
  netstat -an | grep 9000
  ```

- **Invalid signature**: Secret mismatch
  ```bash
  # Verify secret matches GitHub configuration
  echo $GITHUB_WEBHOOK_SECRET
  ```

- **SSL verification failed**: ngrok/server certificate issue
  - For ngrok: Use HTTPS URLs only
  - For production: Ensure valid SSL certificate

### Missing Notifications

**Check handler logs:**
```bash
# View handler output
tail -f /var/log/github-webhook-handler.log

# Or if using PM2
pm2 logs github-webhook
```

**Check AI Maestro connectivity:** Check your inbox using the `agent-messaging` skill. If messages can be retrieved, connectivity is confirmed.

**Verify event routing:**
```bash
# Check webhook event was logged
ls -lt ~/design/webhook_logs/ | head -5

# Verify notification was sent
cat ~/design/webhook_logs/latest.json | jq '.payload_summary'
```

### Handler Crashes

**Enable debug logging:**
```python
# In ci_webhook_handler.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Run in foreground with debug:**
```bash
python ci_webhook_handler.py --port 9000 2>&1 | tee webhook_debug.log
```

**Check for missing dependencies:**
```bash
# Verify all imports work
python -c "from aimaestro_notify import handle_github_webhook"
python -c "from cross_platform import atomic_write_json"
```

## Security Considerations

1. **Always use webhook secret** in production
2. **Enable SSL verification** (disable only for local dev with ngrok)
3. **Restrict webhook to specific events** (don't select "Send me everything")
4. **Use firewall rules** to restrict webhook handler port access
5. **Rotate secrets periodically**:
   ```bash
   # Generate new secret
   NEW_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")

   # Update GitHub webhook
   gh api repos/OWNER/REPO/hooks/HOOK_ID \
     -X PATCH \
     -F "config[secret]=$NEW_SECRET"

   # Update environment
   export GITHUB_WEBHOOK_SECRET="$NEW_SECRET"
   ```

## Advanced: Multiple Repositories

To handle webhooks from multiple repositories:

**Option 1: One handler, multiple webhooks**
```bash
# Configure webhook for each repo pointing to same handler
# Handler automatically routes based on repository.full_name in payload
```

**Option 2: Path-based routing**
```python
# Modify handler to support path-based routing
# Example: /webhook/repo1, /webhook/repo2
class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        repo_name = self.path.split('/')[2]  # Extract from /webhook/repo_name
        # ... route to appropriate handler
```

## Integration with Project Sync

The webhook handler integrates with the project sync workflow:

1. **CI failure** → Orchestrator notified → Auto-creates issue with CI logs
2. **PR merged** → Orchestrator updates task status → Closes related issues
3. **Task blocked** → Orchestrator escalates → Sends summary to user

See `references/status-management.md` for full workflow details.
