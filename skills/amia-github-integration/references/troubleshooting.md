# Troubleshooting

This is the main index for GitHub integration troubleshooting. Each section links to detailed troubleshooting guides for specific problem areas.

## Quick Navigation

| Problem Area | When to Read | Link |
|--------------|--------------|------|
| Authentication | Cannot login, permission denied, bad credentials | [Part 1: Authentication](troubleshooting-part1-authentication.md) |
| Projects V2 Sync | Issues not syncing, duplicates, bidirectional sync fails | [Part 2: Projects V2](troubleshooting-part2-projects-v2.md) |
| PR Linking & Labels | PRs don't link to issues, labels rejected | [Part 3: PR & Labels](troubleshooting-part3-pr-labels.md) |
| CLI, Rate Limits, Webhooks | gh command fails, API rate limits, webhooks not triggering | [Part 4: CLI & API](troubleshooting-part4-cli-api.md) |

---

## Use-Case TOC

### If you get authentication errors
See [Part 1: Authentication Issues](troubleshooting-part1-authentication.md):
- Problem: "Not authenticated" or "Permission denied"
- Problem: "HTTP 401: Bad credentials" (Persistent)
- Problem: "Resource not accessible by integration"
- Problem: "Command not found: gh"

### If Projects V2 sync fails
See [Part 2: Projects V2 Synchronization Issues](troubleshooting-part2-projects-v2.md):
- Problem: Issues created in agent system don't appear in GitHub
- Problem: GitHub changes don't sync back to agent
- Problem: Sync creates duplicate issues

### If pull requests don't link to issues
See [Part 3: Pull Request Linking Issues](troubleshooting-part3-pr-labels.md#pull-request-linking-issues):
- Problem: Pull request doesn't link to issue
- Problem: Issue doesn't close when PR merges

### If labels are rejected
See [Part 3: Label System Issues](troubleshooting-part3-pr-labels.md#label-system-issues):
- Problem: Label is rejected or doesn't appear on issue
- Problem: Multiple labels from 9-label system on one issue

### If GitHub CLI commands fail
See [Part 4: GitHub CLI Issues](troubleshooting-part4-cli-api.md#github-cli-issues):
- Problem: "gh: command not found"
- Problem: "gh: command works in terminal but not in scripts"

### If API rate limits are hit
See [Part 4: Rate Limiting Issues](troubleshooting-part4-cli-api.md#rate-limiting-issues):
- Problem: "API rate limit exceeded"
- Problem: "Secondary rate limit exceeded"

### If webhooks don't trigger
See [Part 4: Webhook Issues](troubleshooting-part4-cli-api.md#webhook-issues):
- Problem: Webhooks not triggering

---

## General Troubleshooting Steps

When encountering any issue:

1. **Check authentication** → `gh auth status`
2. **Verify GitHub CLI version** → `gh --version` (must be 2.14+)
3. **Enable verbose logging** → Add `--verbose` or `--debug` flags
4. **Check API rate limits** → `gh api rate_limit`
5. **Review error messages** → Read full error output
6. **Check GitHub status** → Visit https://www.githubstatus.com
7. **Consult logs** → Review sync and script logs
8. **Test with minimal example** → Isolate the problem
9. **Search GitHub discussions** → Look for similar issues
10. **Contact support** → If all else fails

---

## Getting Help

- **GitHub CLI Documentation**: https://cli.github.com/manual/
- **GitHub API Documentation**: https://docs.github.com/en/rest
- **GitHub Community**: https://github.community/
- **Stack Overflow**: Tag questions with `github-cli` or `github-api`
