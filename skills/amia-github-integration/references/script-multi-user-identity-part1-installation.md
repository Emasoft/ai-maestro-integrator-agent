# Multi-User Identity Script - Part 1: Installation and Overview

**Parent document:** [script-multi-user-identity.md](script-multi-user-identity.md)

## Contents

- [Overview](#overview)
- [Installation and Setup](#installation-and-setup)
  - [Step 1: Copy Configuration Template](#step-1-copy-configuration-template)
  - [Step 2: Edit Configuration](#step-2-edit-configuration)
  - [Step 3: Generate SSH Keys](#step-3-generate-ssh-keys)
  - [Step 4: Add Keys to GitHub](#step-4-add-keys-to-github)
  - [Step 5: Test Connections](#step-5-test-connections)
  - [Step 6: Authenticate gh CLI](#step-6-authenticate-gh-cli)

---

## Overview

The `gh_multiuser.py` script provides cross-platform management of multiple GitHub identities. It handles:

- SSH key generation and configuration
- SSH host alias configuration
- Git identity configuration per repository
- GitHub CLI account switching
- Bulk repository configuration

### Script Files

| File | Description |
|------|-------------|
| `gh_multiuser.py` | Main script (Python 3, stdlib only, cross-platform) |
| `identities.example.json` | Configuration template |

### Running the Script

**Linux/macOS:**
```bash
python3 gh_multiuser.py <command> [args...]
```

**Windows:**
```powershell
python gh_multiuser.py <command> [args...]
# or
py -3 gh_multiuser.py <command> [args...]
```

---

## Installation and Setup

### Step 1: Copy Configuration Template

```bash
cd /path/to/skill/scripts
cp identities.example.json identities.json
```

### Step 2: Edit Configuration

Edit `identities.json` with your account details:

```json
{
  "identities": {
    "primary": {
      "description": "Repository owner / reviewer identity",
      "github_username": "your-primary-username",
      "git_name": "Your Display Name",
      "git_email": "ID+username@users.noreply.github.com",
      "ssh_key_path": "~/.ssh/id_ed25519",
      "ssh_host_alias": "github.com"
    },
    "secondary": {
      "description": "Developer / worker agent identity",
      "github_username": "your-secondary-username",
      "git_name": "Secondary Name",
      "git_email": "ID+secondary@users.noreply.github.com",
      "ssh_key_path": "~/.ssh/id_ed25519_secondary",
      "ssh_host_alias": "github-secondary"
    }
  },
  "defaults": {
    "active_identity": "primary",
    "ssh_key_type": "ed25519",
    "git_protocol": "ssh"
  }
}
```

**Finding Your Noreply Email:**
1. GitHub > Settings > Emails
2. Enable "Keep my email addresses private"
3. Copy the noreply email shown (format: `ID+USERNAME@users.noreply.github.com`)

### Step 3: Generate SSH Keys

```bash
python3 gh_multiuser.py setup primary
python3 gh_multiuser.py setup secondary
```

### Step 4: Add Keys to GitHub

For each identity:
1. Copy the public key displayed by the setup command
2. Log into GitHub as that user
3. Go to Settings > SSH and GPG keys > New SSH key
4. Paste the key and save

### Step 5: Test Connections

```bash
python3 gh_multiuser.py test
```

Expected output:
```
Testing identity: primary
  SSH: git@github.com
  Result: Hi primary-user! You've successfully authenticated...

Testing identity: secondary
  SSH: git@github-secondary
  Result: Hi secondary-user! You've successfully authenticated...
```

### Step 6: Authenticate gh CLI

For each account:
1. Log into GitHub in your browser as that user
2. Run `gh auth login`
3. Complete the browser authentication

Verify:
```bash
gh auth status
```

---

## Next Steps

After completing the installation, see:
- [Part 2: Core Commands](script-multi-user-identity-part2-core-commands.md) - For setup, test, switch, repo commands
- [Part 3: Advanced Commands](script-multi-user-identity-part3-advanced-commands.md) - For status, add, diagnose, fix commands
- [Part 4: Troubleshooting](script-multi-user-identity-part4-troubleshooting.md) - For common issues and integration examples
