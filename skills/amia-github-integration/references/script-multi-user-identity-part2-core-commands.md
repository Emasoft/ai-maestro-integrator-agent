# Multi-User Identity Script - Part 2: Core Commands

**Parent document:** [script-multi-user-identity.md](script-multi-user-identity.md)

## Contents

- [Setup Command](#setup-command) - Generate SSH keys for an identity
- [Test Command](#test-command) - Test SSH connections
- [Switch Command](#switch-command) - Switch between identities
- [Repo Command](#repo-command) - Configure a single repository
- [Bulk-Repo Command](#bulk-repo-command) - Configure multiple repositories

---

## Setup Command

Generate SSH key and configure SSH host alias for an identity.

**Syntax:**
```bash
python3 gh_multiuser.py setup <identity-name>
```

**Example:**
```bash
python3 gh_multiuser.py setup secondary
```

**What it does:**
1. Generates Ed25519 SSH key pair at configured path
2. Adds SSH host alias entry to `~/.ssh/config`
3. Displays public key for adding to GitHub

**Output:**
```
Setting up identity: secondary
  Generating SSH key: ~/.ssh/id_ed25519_secondary
  Key generated successfully.

  Adding SSH host alias to ~/.ssh/config...
  SSH config updated.

  Public key (add to GitHub):
  ssh-ed25519 AAAAC3NzaC1lZDI1... user@example.com

  Next steps:
  1. Copy the public key above
  2. Go to GitHub > Settings > SSH and GPG keys
  3. Click "New SSH key" and paste the key
  4. Run: python3 gh_multiuser.py test secondary
```

---

## Test Command

Test SSH connection for one or all identities.

**Syntax:**
```bash
python3 gh_multiuser.py test [identity-name]
```

**Examples:**
```bash
# Test all identities
python3 gh_multiuser.py test

# Test specific identity
python3 gh_multiuser.py test secondary
```

**Successful output:**
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

**Failed output:**
```
Permission denied (publickey).
```

---

## Switch Command

Switch the active GitHub identity for the current session.

**Syntax:**
```bash
python3 gh_multiuser.py switch <identity-name>
```

**Example:**
```bash
python3 gh_multiuser.py switch secondary
```

**What it does:**
1. Switches gh CLI to the specified account
2. Sets `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL` environment variables
3. Sets `GIT_COMMITTER_NAME`, `GIT_COMMITTER_EMAIL` environment variables

**Important:** Environment variable changes only affect the current shell session. For persistent changes, configure the repository directly with the `repo` command.

**To source environment changes in current shell:**
```bash
eval "$(python3 gh_multiuser.py switch secondary)"
```

---

## Repo Command

Configure a Git repository for a specific identity.

**Syntax:**
```bash
python3 gh_multiuser.py repo <repository-path> <identity-name>
```

**Example:**
```bash
python3 gh_multiuser.py repo /path/to/my-project secondary
```

**What it does:**
1. Sets `user.name` in repository's `.git/config`
2. Sets `user.email` in repository's `.git/config`
3. Updates `origin` remote URL to use the identity's SSH host alias

**Before:**
```
origin  git@github.com:owner/repo.git (fetch)
origin  git@github.com:owner/repo.git (push)
```

**After:**
```
origin  git@github-secondary:owner/repo.git (fetch)
origin  git@github-secondary:owner/repo.git (push)
```

---

## Bulk-Repo Command

Configure all Git repositories under a directory for a specific identity.

**Syntax:**
```bash
python3 gh_multiuser.py bulk-repo <root-directory> <identity-name>
```

**Example:**
```bash
python3 gh_multiuser.py bulk-repo ~/workspace/projects secondary
```

**What it does:**
1. Finds all directories containing `.git` under the root
2. Applies the `repo` configuration to each
3. Reports success/failure for each repository

**Output:**
```
Configuring repositories for identity: secondary
  /home/user/workspace/projects/repo1 ... OK
  /home/user/workspace/projects/repo2 ... OK
  /home/user/workspace/projects/repo3 ... SKIPPED (no origin remote)

Configured: 2, Skipped: 1, Failed: 0
```

---

## See Also

- [Part 1: Installation](script-multi-user-identity-part1-installation.md) - Initial setup instructions
- [Part 3: Advanced Commands](script-multi-user-identity-part3-advanced-commands.md) - Status, add, diagnose, fix commands
- [Part 4: Troubleshooting](script-multi-user-identity-part4-troubleshooting.md) - Common issues and integration
