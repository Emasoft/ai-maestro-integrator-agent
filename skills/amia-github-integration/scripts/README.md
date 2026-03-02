# GitHub Integration Scripts

This directory contains automation scripts for GitHub integration workflows.

## Multi-User Identity Management

### Overview

The `gh_multiuser.py` script provides bulletproof cross-platform management of multiple GitHub identities. This is essential for:

- **Owner/Developer Separation**: Repository owner reviews PRs, developer submits them
- **Agent Orchestration**: Orchestrator assigns work, worker agents develop
- **Formal PR Workflow**: GitHub requires different users for PR approval

### Bulletproof Features

- **Automatic Platform Detection**: Linux, macOS, Windows, WSL, Git Bash, Cygwin
- **SSH Agent Management**: Automatic agent startup per platform (macOS Keychain, Linux ssh-agent, Windows OpenSSH)
- **Self-Diagnostics**: Detect and report configuration issues with specific fixes
- **Auto-Fix**: Automatically repair common issues (missing config, SSH keys, etc.)
- **Retry Logic**: Exponential backoff for network operations
- **Zero Dependencies**: Python 3 stdlib only - works anywhere Python runs

### Files

| File | Description |
|------|-------------|
| `identities.example.json` | Configuration template - copy to `identities.json` |
| `gh_multiuser.py` | Cross-platform Python script (Python 3, stdlib only) |

### Quick Start

1. **Copy configuration template:**
   ```bash
   cp identities.example.json identities.json
   ```

2. **Edit `identities.json`** with your GitHub account details

3. **Set up SSH keys:**
   ```bash
   python3 gh_multiuser.py setup primary
   python3 gh_multiuser.py setup secondary
   ```

4. **Add public keys to GitHub:**
   - Copy the displayed public key
   - GitHub > Settings > SSH and GPG keys > New SSH key

5. **Test connections:**
   ```bash
   python3 gh_multiuser.py test
   ```

### Commands

```bash
python3 gh_multiuser.py <command> [args...]
```

| Command | Description |
|---------|-------------|
| `setup <identity>` | Generate SSH key and configure SSH host alias |
| `test [identity]` | Test SSH connections (all or specific) |
| `switch <identity>` | Switch gh CLI and set Git environment variables |
| `repo <path> <identity>` | Configure a repository for a specific identity |
| `bulk-repo <root> <identity>` | Configure all repos under a directory |
| `status` | Show current identity status |
| `list` | List configured identities |
| `add` | Interactively add a new identity |
| `diagnose` | Run diagnostics to detect issues |
| `fix` | Auto-fix common issues |
| `--help` | Show help message |

### Platform Notes

**Linux/macOS:**
```bash
python3 gh_multiuser.py <command>
```

**Windows:**
```powershell
python gh_multiuser.py <command>
# or
py -3 gh_multiuser.py <command>
```

### Configuration File Format

```json
{
  "identities": {
    "primary": {
      "description": "Repository owner / reviewer identity",
      "github_username": "your-primary-username",
      "git_name": "Your Name",
      "git_email": "ID+username@users.noreply.github.com",
      "ssh_key_path": "~/.ssh/id_ed25519",
      "ssh_host_alias": "github.com"
    },
    "secondary": {
      "description": "Developer / worker agent identity",
      "github_username": "your-secondary-username",
      "git_name": "Secondary User",
      "git_email": "ID+secondary@users.noreply.github.com",
      "ssh_key_path": "~/.ssh/id_ed25519_secondary",
      "ssh_host_alias": "github-secondary"
    }
  },
  "defaults": {
    "active_identity": "primary"
  }
}
```

### Finding Your GitHub Noreply Email

1. Go to GitHub > Settings > Emails
2. Enable "Keep my email addresses private"
3. Your noreply email format: `ID+USERNAME@users.noreply.github.com`

See [script-multi-user-identity.md](../references/script-multi-user-identity.md) for detailed documentation.
