# Multi-User Identity Script - Part 4: Troubleshooting and Integration

**Parent document:** [script-multi-user-identity.md](script-multi-user-identity.md)

## Contents

- [Troubleshooting](#troubleshooting)
  - [SSH Key Not Found](#ssh-key-not-found)
  - [Wrong User on SSH Test](#wrong-user-on-ssh-test)
  - [SSH Config Not Updated](#ssh-config-not-updated)
  - [Permission Denied on Push](#permission-denied-on-push)
  - [gh CLI Not Switching](#gh-cli-not-switching)
  - [Configuration File Not Found](#configuration-file-not-found)
- [Environment Variables](#environment-variables)
- [Integration Examples](#integration-examples)
  - [Agent Orchestration Setup](#agent-orchestration-setup)
  - [CI/CD Pipeline](#cicd-pipeline)
  - [Shell Profile Integration](#shell-profile-integration)

---

## Troubleshooting

### SSH Key Not Found

**Error:** `FileNotFoundError: SSH key not found`

**Solution:**
```bash
# Run setup to generate the key
python3 gh_multiuser.py setup <identity>
```

### Wrong User on SSH Test

**Error:** `Hi wrong-user! You've successfully authenticated...`

**Cause:** SSH agent is offering the wrong key first.

**Solution:**
```bash
# Clear agent and reload correct key
ssh-add -D
ssh-add ~/.ssh/id_ed25519_secondary
python3 gh_multiuser.py test secondary
```

### SSH Config Not Updated

**Error:** SSH test fails after setup

**Solution:** Check `~/.ssh/config` manually:
```
Host github-secondary
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_secondary
  IdentitiesOnly yes
```

### Permission Denied on Push

**Error:** `Permission to owner/repo.git denied to wrong-user`

**Solution:**
```bash
# Reconfigure the repository
python3 gh_multiuser.py repo /path/to/repo correct-identity

# Verify remote
git remote -v
```

### gh CLI Not Switching

**Error:** `gh auth switch` fails

**Solution:**
```bash
# Verify accounts are authenticated
gh auth status

# Re-authenticate if needed
gh auth login
```

### Configuration File Not Found

**Error:** `identities.json not found`

**Solution:**
```bash
# Copy template
cp identities.example.json identities.json
# Edit with your details
```

---

## Environment Variables

The script respects these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GH_MULTIUSER_CONFIG` | Path to identities.json | `./identities.json` |
| `SSH_AUTH_SOCK` | SSH agent socket | System default |

---

## Integration Examples

### Agent Orchestration Setup

```bash
# Orchestrator environment
export GH_MULTIUSER_CONFIG=/etc/orchestrator/identities.json
python3 gh_multiuser.py switch primary

# Worker agent environment
export GH_MULTIUSER_CONFIG=/etc/orchestrator/identities.json
python3 gh_multiuser.py switch secondary
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Configure Git Identity
  run: |
    python3 scripts/gh_multiuser.py repo . ci-bot
  env:
    GH_MULTIUSER_CONFIG: .github/identities.json
```

### Shell Profile Integration

Add to `~/.bashrc` or `~/.zshrc`:
```bash
alias gh-primary='python3 /path/to/gh_multiuser.py switch primary'
alias gh-secondary='python3 /path/to/gh_multiuser.py switch secondary'
```

---

## See Also

- [Part 1: Installation](script-multi-user-identity-part1-installation.md) - Initial setup instructions
- [Part 2: Core Commands](script-multi-user-identity-part2-core-commands.md) - Setup, test, switch, repo commands
- [Part 3: Advanced Commands](script-multi-user-identity-part3-advanced-commands.md) - Status, add, diagnose, fix commands
- [Multi-User Workflow](multi-user-workflow.md) - Conceptual guide to multi-user workflows
- [Prerequisites and Setup](prerequisites-and-setup.md) - Initial GitHub CLI setup
- [Troubleshooting](troubleshooting.md) - General troubleshooting guide
