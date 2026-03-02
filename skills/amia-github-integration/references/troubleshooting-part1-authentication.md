# Troubleshooting Part 1: Authentication Issues

[Back to Troubleshooting Index](troubleshooting.md)

## Contents
- Problem: "Not authenticated" or "Permission denied"
- Problem: "HTTP 401: Bad credentials" (Persistent)
- Problem: "Resource not accessible by integration"
- Problem: "Command not found: gh"

---

## Problem: "Not authenticated" or "Permission denied"

**Symptoms:**
```
Error: HTTP 401: Bad credentials (https://api.github.com/user)
To get started with GitHub CLI, please run: gh auth login
```

**Cause:** GitHub CLI is not authenticated or authentication has expired.

**Solution:**

**Step 1: Log out**
```bash
gh auth logout
```

**Step 2: Log back in**
```bash
gh auth login
```

**Step 3: Follow interactive prompts**
- Choose "HTTPS" as protocol (recommended)
- Choose "Login with a web browser"
- Authorize GitHub CLI with all permissions

**Step 4: Verify authentication**
```bash
gh auth status
```

Expected output:
```
github.com
  ✓ Logged in to github.com as username (oauth_token)
  ✓ Git operations for github.com configured to use https protocol.
```

---

## Problem: "HTTP 401: Bad credentials" (Persistent)

**Cause:** Token has been revoked or corrupted.

**Solution:**

**Step 1: Clear stored credentials**
```bash
rm -rf ~/.config/gh/hosts.yml
```

**Step 2: Re-authenticate**
```bash
gh auth login
```

---

## Problem: "Resource not accessible by integration"

**Cause:** Insufficient permissions granted during authentication.

**Solution:**

Re-authenticate and ensure you grant ALL requested permissions:
- Repository administration
- Pull requests
- Issues
- Projects
- User profile

```bash
gh auth logout
gh auth login
# When prompted, authorize ALL permissions
```

---

## Problem: "Command not found: gh"

**Cause:** GitHub CLI is not installed or not in PATH.

**Solution:**

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

**Verify installation:**
```bash
gh --version
```
