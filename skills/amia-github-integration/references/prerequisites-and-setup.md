# Prerequisites and Setup

## Use-Case TOC
- When you need to authenticate GitHub CLI → [GitHub CLI Authentication](#github-cli-authentication)
- When you need to verify authentication status → [Verify Authentication](#verify-authentication)
- If authentication fails or is expired → [Re-authentication](#re-authentication)
- When setting up a new machine or environment → [Initial Setup Requirements](#initial-setup-requirements)

## Table of Contents

- [Initial Setup Requirements](#initial-setup-requirements)
  - [Installing GitHub CLI](#installing-github-cli)
  - [Verifying GitHub CLI Version](#verifying-github-cli-version)
- [GitHub CLI Authentication](#github-cli-authentication)
  - [Step 1: Execute Authentication](#step-1-execute-authentication)
  - [Step 2: Choose Authentication Method](#step-2-choose-authentication-method)
  - [Step 3: Grant Permissions](#step-3-grant-permissions)
  - [Step 4: Initial Verification](#step-4-initial-verification)
- [Verify Authentication](#verify-authentication)
- [Re-authentication](#re-authentication)
- [Troubleshooting Authentication](#troubleshooting-authentication)
  - [Problem: "Command not found: gh"](#problem-command-not-found-gh)
  - [Problem: "Not logged into any GitHub hosts"](#problem-not-logged-into-any-github-hosts)
  - [Problem: "HTTP 401: Bad credentials"](#problem-http-401-bad-credentials)
  - [Problem: "Resource not accessible by integration"](#problem-resource-not-accessible-by-integration)
- [Security Best Practices](#security-best-practices)
- [Next Steps](#next-steps)

---

## Initial Setup Requirements

Before using this skill, you must have:

- **GitHub Account**: A personal GitHub account with access to target repositories
- **GitHub CLI**: Installed and available on your system (version 2.14 or higher)
- **Authentication**: One-time GitHub CLI authentication using `gh auth login`
- **Repository Access**: Write permissions to target repositories
- **Basic Git Knowledge**: Understanding of Git commits, branches, and pull requests

### Installing GitHub CLI

If you don't have GitHub CLI installed:

**macOS:**
```bash
brew install gh
```

**Linux:**
```bash
# Debian/Ubuntu
sudo apt install gh

# Fedora/RHEL
sudo dnf install gh
```

**Windows:**
```bash
# Using winget
winget install --id GitHub.cli

# Using Chocolatey
choco install gh
```

### Verifying GitHub CLI Version

Ensure you have version 2.14 or higher:
```bash
gh --version
```

Expected output:
```
gh version 2.14.0 (2023-01-01)
```

If your version is older, upgrade using your package manager.

## GitHub CLI Authentication

To use any GitHub integration operations, you must first authenticate GitHub CLI. This authentication is persistent and only needs to be performed once per machine.

### Step 1: Execute Authentication

```bash
gh auth login
```

### Step 2: Choose Authentication Method

The system will prompt you to choose between:
- **HTTPS with Web-based Login** (Recommended) - Opens browser, logs you in via web interface
- **SSH Key Authentication** - Uses your SSH keys for authentication
- **Personal Access Token** - Uses a manually created token

For most users, HTTPS with web-based login is simplest.

### Step 3: Grant Permissions

When the browser opens (for web-based login), authorize GitHub CLI to access:
- Repository administration and pull requests
- Issues and projects
- User profile information

Click "Authorize github" to complete the process.

### Step 4: Initial Verification

After authentication completes, verify it was successful:

```bash
gh auth status
```

**Expected Success Output:**
```
github.com
  ✓ Logged in to github.com as username (oauth_token)
  ✓ Git operations for github.com configured to use https protocol.
  ✓ Token: *******************
```

If you see the green checkmarks (✓), authentication was successful.

## Verify Authentication

To check your current authentication status at any time:

```bash
gh auth status
```

This command confirms:
- Whether you are logged in
- Which GitHub account you are using
- Which protocol (HTTPS/SSH) is configured for Git operations
- Token validity status

## Re-authentication

If authentication expires or you get permission errors, re-authenticate:

```bash
# First, log out
gh auth logout

# Then log back in
gh auth login
```

Follow the same steps as initial authentication.

## Troubleshooting Authentication

### Problem: "Command not found: gh"

**Cause:** GitHub CLI is not installed or not in your PATH.

**Solution:** Install GitHub CLI following the installation steps above, or add it to your PATH:
```bash
export PATH="$PATH:/path/to/gh"
```

### Problem: "Not logged into any GitHub hosts"

**Cause:** Authentication has not been completed or has expired.

**Solution:** Run `gh auth login` and complete authentication.

### Problem: "HTTP 401: Bad credentials"

**Cause:** Token has expired or been revoked.

**Solution:** Re-authenticate using `gh auth logout` followed by `gh auth login`.

### Problem: "Resource not accessible by integration"

**Cause:** Insufficient permissions granted during authentication.

**Solution:** Re-authenticate and ensure you grant all requested permissions (repo, project, user).

## Security Best Practices

- **Never share your authentication token** - The token grants full access to your GitHub account
- **Use web-based login** - More secure than personal access tokens
- **Revoke tokens** - If you suspect a token has been compromised, revoke it in GitHub settings
- **Scope permissions appropriately** - Only grant the minimum permissions needed

## Next Steps

Once authentication is complete:
1. Verify you have write access to your target repository: `gh repo view owner/repo`
2. Proceed to creating the 9-label system in your repository
3. Set up GitHub Projects V2 board
