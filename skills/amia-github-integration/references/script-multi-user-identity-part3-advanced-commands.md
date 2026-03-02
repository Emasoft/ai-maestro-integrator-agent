# Multi-User Identity Script - Part 3: Advanced Commands

**Parent document:** [script-multi-user-identity.md](script-multi-user-identity.md)

## Contents

- [Status Command](#status-command) - Check current identity status
- [Add Command](#add-command) - Add a new identity interactively
- [Diagnose Command](#diagnose-command) - Detect configuration issues
- [Fix Command](#fix-command) - Automatically fix common issues

---

## Status Command

Show current identity status across all systems.

**Syntax:**
```bash
python3 gh_multiuser.py status
```

**Output:**
```
Current Identity Status
=======================

Git Global Config:
  user.name: Primary User
  user.email: primary@example.com

Git Environment:
  GIT_AUTHOR_NAME: (not set)
  GIT_AUTHOR_EMAIL: (not set)

gh CLI:
  Active account: primary-user
  All accounts: primary-user, secondary-user

SSH Agent:
  Loaded keys:
    ~/.ssh/id_ed25519 (RSA)
    ~/.ssh/id_ed25519_secondary (ED25519)
```

---

## Add Command

Interactively add a new identity to the configuration.

**Syntax:**
```bash
python3 gh_multiuser.py add
```

**Interactive prompts:**
```
Add New Identity
================
Identity name (e.g., 'tertiary'): work
GitHub username: work-account
Display name for commits: Work Account
GitHub noreply email: 12345+work-account@users.noreply.github.com
SSH key path [~/.ssh/id_ed25519_work]:
SSH host alias [github-work]:

Identity 'work' added to configuration.
Run 'python3 gh_multiuser.py setup work' to generate SSH key.
```

---

## Diagnose Command

Detect configuration issues across all identities.

**Syntax:**
```bash
python3 gh_multiuser.py diagnose
```

**What it checks:**
1. SSH keys exist for each identity
2. SSH config has proper host aliases
3. SSH agent is running and has keys loaded
4. gh CLI is authenticated for each identity
5. Configuration file is valid

**Output:**
```
=== Running Diagnostics ===

Found 2 issue(s):

  1. [secondary] SSH key missing: ~/.ssh/id_ed25519_secondary
     Fix: Run: python3 gh_multiuser.py setup secondary
  2. [secondary] gh CLI not authenticated for secondary-user
     Fix: Run: gh auth login (while logged into secondary-user in browser)

Run 'python3 gh_multiuser.py fix' to auto-fix some issues
```

---

## Fix Command

Automatically fix common issues detected by diagnose.

**Syntax:**
```bash
python3 gh_multiuser.py fix
```

**What it can fix:**
- Missing SSH keys (generates new ones)
- Missing SSH config entries (adds them)
- SSH agent not running (starts it)
- Missing configuration file (copies template)

**What it cannot fix (requires manual action):**
- gh CLI authentication (needs browser login)
- Adding SSH keys to GitHub (needs web interface)
- Repository permissions (needs GitHub settings)

**Output:**
```
=== Auto-Fixing Issues ===

  1. [secondary] SSH key missing
     Action: Generating SSH key...
     Result: OK

  2. [secondary] SSH config missing
     Action: Adding SSH host alias...
     Result: OK

Fixed 2 issue(s). 1 issue(s) require manual action.

Manual fixes needed:
  - [secondary] gh CLI not authenticated
    Run: gh auth login (while logged into secondary-user in browser)
```

---

## See Also

- [Part 1: Installation](script-multi-user-identity-part1-installation.md) - Initial setup instructions
- [Part 2: Core Commands](script-multi-user-identity-part2-core-commands.md) - Setup, test, switch, repo commands
- [Part 4: Troubleshooting](script-multi-user-identity-part4-troubleshooting.md) - Common issues and integration
