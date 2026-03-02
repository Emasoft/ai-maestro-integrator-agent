# Troubleshooting Part 2: Projects V2 Synchronization Issues

[Back to Troubleshooting Index](troubleshooting.md)

## Contents
- Problem: Issues created in agent system don't appear in GitHub
- Problem: GitHub changes don't sync back to agent
- Problem: Sync creates duplicate issues

---

## Problem: Issues created in agent system don't appear in GitHub

**Symptoms:**
- Agent tasks show as created
- GitHub issues list is empty or missing tasks
- Sync script reports success but no issues visible

**Diagnosis:**

**Step 1: Verify authentication**
```bash
gh auth status
```

**Step 2: Verify project exists**
```bash
gh project list --owner "@username"
```

**Step 3: Check sync logs**
```bash
tail -f sync-projects-v2.log
```

**Solution:**

**If project doesn't exist:**
```bash
gh project create --title "Project Name" --owner "@username"
```

**If authentication failed:**
Follow authentication troubleshooting steps in [Part 1](troubleshooting-part1-authentication.md).

**If sync script has errors:**
Run sync with verbose logging:
```bash
python3 scripts/sync-projects-v2.py \
  --owner "username" \
  --repo "repository" \
  --project "1" \
  --verbose
```

Review error messages and address specific issues.

---

## Problem: GitHub changes don't sync back to agent

**Symptoms:**
- Update issue in GitHub
- Agent task remains unchanged
- Sync script runs without errors

**Diagnosis:**

**Step 1: Verify bidirectional sync is enabled**
```bash
python3 scripts/sync-projects-v2.py --help
# Check that --direction parameter supports "from-github" or "both"
```

**Step 2: Check sync direction**
Verify sync is running with correct direction:
```bash
python3 scripts/sync-projects-v2.py \
  --owner "username" \
  --repo "repository" \
  --project "1" \
  --direction "both" \
  --verbose
```

**Step 3: Verify webhook configuration (if using webhooks)**
```bash
gh api repos/owner/repo/hooks
```

**Solution:**

**For polling-based sync:**
Ensure sync runs frequently (hourly):
```bash
# Add to crontab
0 * * * * cd /path/to/project && python3 scripts/sync-projects-v2.py ...
```

**For webhook-based sync:**
Configure GitHub webhook to call sync endpoint on issue updates:
1. Go to repository Settings → Webhooks
2. Add webhook with URL: `https://your-server.com/sync-webhook`
3. Select events: Issues, Pull requests, Projects v2 items
4. Ensure webhook delivers successfully

---

## Problem: Sync creates duplicate issues

**Symptoms:**
- Same issue appears multiple times in GitHub
- Agent tasks are duplicated

**Cause:** Sync script not properly tracking issue-to-task mapping.

**Solution:**

**Step 1: Stop sync temporarily**
```bash
# Remove cron job or stop continuous sync
```

**Step 2: Deduplicate manually**
```bash
# List all issues
gh issue list --limit 1000 --json number,title,createdAt

# Identify duplicates by title and creation time
# Close duplicate issues manually
gh issue close <duplicate_number> --comment "Duplicate issue, closing"
```

**Step 3: Fix sync mapping**
Ensure sync script maintains proper mapping table between agent tasks and GitHub issues.

**Step 4: Restart sync**
```bash
python3 scripts/sync-projects-v2.py ...
```
