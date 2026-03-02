# Multi-User GitHub Workflow: Operations and Troubleshooting

## Table of Contents

- [Use-Case TOC](#use-case-toc)
- [Per-Command Identity Override](#per-command-identity-override)
  - [Git Commands with Environment Variables](#git-commands-with-environment-variables)
  - [GitHub CLI Commands](#github-cli-commands)
- [Collaborator Management](#collaborator-management)
  - [Adding a Collaborator](#adding-a-collaborator)
  - [Accepting a Collaboration Invitation](#accepting-a-collaboration-invitation)
- [Troubleshooting](#troubleshooting)
  - [Problem: SSH Shows Wrong User](#problem-ssh-shows-wrong-user)
  - [Problem: Push Permission Denied](#problem-push-permission-denied)
  - [Problem: Commits Show Wrong Author](#problem-commits-show-wrong-author)
  - [Problem: gh CLI Uses Wrong Account](#problem-gh-cli-uses-wrong-account)
  - [Problem: "Too Many Authentication Failures"](#problem-too-many-authentication-failures)
  - [Problem: Key Not Persisting After Reboot (macOS)](#problem-key-not-persisting-after-reboot-macos)
- [Security Best Practices](#security-best-practices)
- [Quick Reference](#quick-reference)
  - [Key Files and Locations](#key-files-and-locations)
  - [Common Commands](#common-commands)
- [Integration with Agent Orchestration](#integration-with-agent-orchestration)
  - [Owner/Orchestrator Identity](#ownerorchestrator-identity)
  - [Developer/Worker Identity](#developerworker-identity)
  - [Workflow Example](#workflow-example)

## Use-Case TOC
- When running commands as a specific user → [Per-Command Identity Override](#per-command-identity-override)
- When adding collaborators to a repository → [Collaborator Management](#collaborator-management)
- When troubleshooting identity issues → [Troubleshooting](#troubleshooting)
- When securing multi-identity setup → [Security Best Practices](#security-best-practices)
- When looking up commands quickly → [Quick Reference](#quick-reference)
- When using identities with agent orchestration → [Integration with Agent Orchestration](#integration-with-agent-orchestration)

**Related Documents:**
- [Part 1: Setup and Configuration](multi-user-workflow-part1-setup.md) - SSH keys, host aliases, gh CLI setup, identity switching, and repository configuration

---

## Per-Command Identity Override

For single commands without switching the entire shell:

### Git Commands with Environment Variables

```bash
GIT_AUTHOR_NAME="secondary-user" \
GIT_AUTHOR_EMAIL="secondary@example.com" \
GIT_COMMITTER_NAME="secondary-user" \
GIT_COMMITTER_EMAIL="secondary@example.com" \
git commit -m "Commit as secondary user"
```

### GitHub CLI Commands

```bash
# First switch gh auth context
gh auth switch --user secondary-user

# Then run the command
gh pr create --title "Feature" --body "Description"

# Switch back if needed
gh auth switch --user primary-user
```

---

## Collaborator Management

### Adding a Collaborator

As the repository owner:

```bash
# Switch to owner identity
gh auth switch --user owner-username

# Add collaborator
gh api repos/OWNER/REPO/collaborators/COLLABORATOR_USERNAME -X PUT

# Or with specific permission
gh api repos/OWNER/REPO/collaborators/COLLABORATOR_USERNAME -X PUT -f permission=push
```

**Permission Levels:**
- `pull`: Read-only access
- `push`: Read and write access
- `admin`: Full administration
- `maintain`: Manage without admin access
- `triage`: Manage issues and PRs without write access

### Accepting a Collaboration Invitation

As the invited user:

```bash
# Switch to invited user identity
gh auth switch --user invited-username

# List pending invitations
gh api user/repository_invitations --jq '.[] | {repo: .repository.full_name, id: .id}'

# Accept invitation (using invitation ID from above)
gh api user/repository_invitations/INVITATION_ID -X PATCH

# Verify access
gh api repos/OWNER/REPO --jq '.full_name'
```

---

## Troubleshooting

### Problem: SSH Shows Wrong User

**Symptom:**
```
$ ssh -T git@github-secondary
Hi wrong-user! You've successfully authenticated...
```

**Cause:** SSH agent is offering the wrong key.

**Solution:**
```bash
# Clear all keys from agent
ssh-add -D

# Add only the correct key
ssh-add ~/.ssh/id_ed25519_secondary

# Test again
ssh -T git@github-secondary
```

### Problem: Push Permission Denied

**Symptom:**
```
ERROR: Permission to owner/repo.git denied to wrong-user.
```

**Cause:** Remote URL uses wrong host alias or wrong key is being used.

**Solution:**
```bash
# Check remote URL
git remote -v

# Update to correct host alias
git remote set-url origin git@github-secondary:owner/repo.git

# Clear and reload SSH key
ssh-add -D
ssh-add ~/.ssh/id_ed25519_secondary

# Test
ssh -T git@github-secondary
```

### Problem: Commits Show Wrong Author

**Symptom:** Commits appear with wrong username/email in GitHub.

**Cause:** Local git config has wrong identity.

**Solution:**
```bash
# Check current config
git config user.name
git config user.email

# Set correct identity
git config user.name "correct-username"
git config user.email "correct-email@example.com"

# Amend last commit if needed (only if not pushed)
git commit --amend --reset-author --no-edit
```

### Problem: gh CLI Uses Wrong Account

**Symptom:** gh commands operate on wrong account.

**Solution:**
```bash
# Check current account
gh auth status

# Switch to correct account
gh auth switch --user correct-username
```

### Problem: "Too Many Authentication Failures"

**Symptom:** SSH connection fails with authentication errors.

**Cause:** SSH agent offers too many keys before the correct one.

**Solution:** Ensure `IdentitiesOnly yes` is in your `~/.ssh/config`:
```
Host github-secondary
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_secondary
  IdentitiesOnly yes
```

### Problem: Key Not Persisting After Reboot (macOS)

**Symptom:** Keys disappear from ssh-agent after restart.

**Solution:** Add to `~/.ssh/config`:
```
Host *
  AddKeysToAgent yes
  UseKeychain yes
```

Then add the key with:
```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519_secondary
```

---

## Security Best Practices

1. **Separate Keys Per Account**: Never share SSH keys between accounts
2. **Use SSH Keychain**: Enable keychain integration for key persistence
3. **Fine-Grained PATs**: If using tokens, create fine-grained PATs with minimal scope
4. **Token Rotation**: Rotate authentication tokens periodically
5. **Never Commit Tokens**: Ensure tokens and keys are never committed to repositories
6. **Use Noreply Emails**: Use GitHub's noreply email addresses to protect real email addresses

---

## Quick Reference

### Key Files and Locations

| Item | Location |
|------|----------|
| SSH Keys | `~/.ssh/id_ed25519_*` |
| SSH Config | `~/.ssh/config` |
| gh Auth | System keyring |
| Git Global Config | `~/.gitconfig` |
| Git Local Config | `.git/config` (per repo) |

### Common Commands

| Action | Command |
|--------|---------|
| Test SSH identity | `ssh -T git@<host-alias>` |
| Check gh accounts | `gh auth status` |
| Switch gh account | `gh auth switch --user <username>` |
| Check repo identity | `git config user.name && git config user.email` |
| Set repo identity | `git config user.name "<name>" && git config user.email "<email>"` |
| Update remote URL | `git remote set-url origin git@<host-alias>:owner/repo.git` |
| Clear SSH agent | `ssh-add -D` |
| Add specific key | `ssh-add ~/.ssh/<keyfile>` |

---

## Integration with Agent Orchestration

When using multiple identities with agent orchestration:

### Owner/Orchestrator Identity
- Reviews and approves PRs
- Creates and assigns issues
- Has admin/owner permissions
- Uses primary SSH host alias and gh authentication

### Developer/Worker Identity
- Submits code changes via PRs
- Has push (collaborator) permissions
- Uses secondary SSH host alias and gh authentication
- Commits are attributed to this identity

### Workflow Example

1. **Orchestrator (as owner)**: Creates issue, assigns to worker agent
2. **Worker (as developer)**: Clones repo using developer host alias, sets local identity
3. **Worker**: Creates feature branch, implements changes, submits PR
4. **Orchestrator**: Reviews PR, requests changes or approves
5. **Worker**: Addresses feedback if needed
6. **Orchestrator**: Merges approved PR

This separation ensures:
- Clear attribution of work
- Formal review process (different users required for PR approval)
- Audit trail showing distinct responsibilities

---

**See Also:** [Part 1: Setup and Configuration](multi-user-workflow-part1-setup.md) for initial SSH and gh CLI setup.
