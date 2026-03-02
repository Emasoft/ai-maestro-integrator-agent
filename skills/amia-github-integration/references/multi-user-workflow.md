# Multi-User GitHub Workflow

This document provides a comprehensive guide to managing multiple GitHub identities on a single machine, enabling formal PR workflows where different users submit and review code.

## Table of Contents

- [Use-Case TOC](#use-case-toc)
  - [Part 1: Setup and Configuration](#part-1-setup-and-configuration)
  - [Part 2: Operations and Troubleshooting](#part-2-operations-and-troubleshooting)
- [Overview](#overview)
  - [Why Multiple Identities?](#why-multiple-identities)
  - [Identity Components](#identity-components)
- [Quick Start](#quick-start)
  - [1. Generate SSH Key for Secondary Account](#1-generate-ssh-key-for-secondary-account)
  - [2. Add Key to GitHub](#2-add-key-to-github)
  - [3. Configure SSH Host Alias](#3-configure-ssh-host-alias)
  - [4. Authenticate Secondary Account with gh CLI](#4-authenticate-secondary-account-with-gh-cli)
  - [5. Configure Repository for Secondary Identity](#5-configure-repository-for-secondary-identity)
- [Key Files and Locations](#key-files-and-locations)
- [Common Commands Quick Reference](#common-commands-quick-reference)
- [See Also](#see-also)

---

## Use-Case TOC

### Part 1: Setup and Configuration
**File**: [multi-user-workflow-part1-setup.md](multi-user-workflow-part1-setup.md)

- When you need multiple GitHub identities on the same machine → [Why Multiple Identities](multi-user-workflow-part1-setup.md#why-multiple-identities)
- When setting up SSH keys for a secondary account → [SSH Key Setup](multi-user-workflow-part1-setup.md#ssh-key-setup)
  - Step 1: Generate a Dedicated SSH Key
  - Step 2: Add Public Key to GitHub Account
  - Step 3: Add Key to SSH Agent
- When configuring SSH host aliases → [SSH Host Aliases](multi-user-workflow-part1-setup.md#ssh-host-aliases)
  - Step 1: Configure SSH Host Aliases
  - Step 2: Test SSH Connection
- When authenticating multiple accounts with gh CLI → [GitHub CLI Multi-Account Setup](multi-user-workflow-part1-setup.md#github-cli-multi-account-setup)
  - Step 1: Authenticate Primary Account
  - Step 2: Authenticate Secondary Account
  - Step 3: Verify Both Accounts
  - Step 4: Switch Active Account
- When switching between GitHub identities → [Identity Switching](multi-user-workflow-part1-setup.md#identity-switching)
  - Shell Helper Functions (use_primary, use_secondary, with_identity)
- When configuring a repository for a specific identity → [Repository Identity Configuration](multi-user-workflow-part1-setup.md#repository-identity-configuration)
  - Per-Repository Git Identity
  - Configure Remote to Use Specific Host Alias
  - Clone Using Specific Identity
  - Helper Function for Repository Configuration

### Part 2: Operations and Troubleshooting
**File**: [multi-user-workflow-part2-operations.md](multi-user-workflow-part2-operations.md)

- When running commands as a specific user → [Per-Command Identity Override](multi-user-workflow-part2-operations.md#per-command-identity-override)
  - Git Commands with Environment Variables
  - GitHub CLI Commands
- When adding collaborators to a repository → [Collaborator Management](multi-user-workflow-part2-operations.md#collaborator-management)
  - Adding a Collaborator (permission levels)
  - Accepting a Collaboration Invitation
- When troubleshooting identity issues → [Troubleshooting](multi-user-workflow-part2-operations.md#troubleshooting)
  - SSH Shows Wrong User
  - Push Permission Denied
  - Commits Show Wrong Author
  - gh CLI Uses Wrong Account
  - "Too Many Authentication Failures"
  - Key Not Persisting After Reboot (macOS)
- When securing multi-identity setup → [Security Best Practices](multi-user-workflow-part2-operations.md#security-best-practices)
- When looking up commands quickly → [Quick Reference](multi-user-workflow-part2-operations.md#quick-reference)
  - Key Files and Locations
  - Common Commands
- When using identities with agent orchestration → [Integration with Agent Orchestration](multi-user-workflow-part2-operations.md#integration-with-agent-orchestration)
  - Owner/Orchestrator Identity
  - Developer/Worker Identity
  - Workflow Example

---

## Overview

### Why Multiple Identities?

Multiple GitHub identities are needed when:

1. **Owner/Developer Separation**: The repository owner reviews and approves PRs, while a separate developer account submits PRs
2. **Agent Orchestration**: An orchestrating agent uses one identity to assign and review, while worker agents use separate identities to develop
3. **Personal/Work Separation**: Different identities for personal projects vs. organizational work
4. **Formal PR Workflow**: GitHub requires different users for formal PR approval (you cannot approve your own PR)

### Identity Components

Each GitHub identity consists of:
- **GitHub Account**: Username and associated email
- **SSH Key**: Dedicated key pair for authentication
- **Git Identity**: `user.name` and `user.email` for commits
- **gh CLI Authentication**: Token stored in keyring

---

## Quick Start

### 1. Generate SSH Key for Secondary Account

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_secondary -C "secondary@example.com" -N ""
```

### 2. Add Key to GitHub

Copy the public key and add to your secondary GitHub account under Settings → SSH and GPG keys:
```bash
cat ~/.ssh/id_ed25519_secondary.pub
```

### 3. Configure SSH Host Alias

Add to `~/.ssh/config`:
```
Host github-secondary
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_secondary
  IdentitiesOnly yes
```

### 4. Authenticate Secondary Account with gh CLI

```bash
gh auth login  # Log in as secondary account in browser
gh auth status  # Verify both accounts shown
```

### 5. Configure Repository for Secondary Identity

```bash
cd /path/to/repo
git config user.name "secondary-user"
git config user.email "secondary@example.com"
git remote set-url origin git@github-secondary:owner/repo.git
```

---

## Key Files and Locations

| Item | Location |
|------|----------|
| SSH Keys | `~/.ssh/id_ed25519_*` |
| SSH Config | `~/.ssh/config` |
| gh Auth | System keyring |
| Git Global Config | `~/.gitconfig` |
| Git Local Config | `.git/config` (per repo) |

---

## Common Commands Quick Reference

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

## See Also

- **Part 1**: [Setup and Configuration](multi-user-workflow-part1-setup.md) - Detailed SSH key setup, host aliases, gh CLI configuration, identity switching, and repository setup
- **Part 2**: [Operations and Troubleshooting](multi-user-workflow-part2-operations.md) - Per-command overrides, collaborator management, troubleshooting guide, and agent orchestration integration
