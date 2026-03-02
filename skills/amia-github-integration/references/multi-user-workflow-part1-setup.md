# Multi-User GitHub Workflow: Setup and Configuration

## Table of Contents

- [Use-Case TOC](#use-case-toc)
- [Why Multiple Identities](#why-multiple-identities)
  - [Identity Components](#identity-components)
- [SSH Key Setup](#ssh-key-setup)
  - [Step 1: Generate a Dedicated SSH Key](#step-1-generate-a-dedicated-ssh-key)
  - [Step 2: Add Public Key to GitHub Account](#step-2-add-public-key-to-github-account)
  - [Step 3: Add Key to SSH Agent](#step-3-add-key-to-ssh-agent)
- [SSH Host Aliases](#ssh-host-aliases)
  - [Step 1: Configure SSH Host Aliases](#step-1-configure-ssh-host-aliases)
  - [Step 2: Test SSH Connection](#step-2-test-ssh-connection)
- [GitHub CLI Multi-Account Setup](#github-cli-multi-account-setup)
  - [Step 1: Authenticate Primary Account](#step-1-authenticate-primary-account)
  - [Step 2: Authenticate Secondary Account](#step-2-authenticate-secondary-account)
  - [Step 3: Verify Both Accounts](#step-3-verify-both-accounts)
  - [Step 4: Switch Active Account](#step-4-switch-active-account)
- [Identity Switching](#identity-switching)
  - [Shell Helper Functions](#shell-helper-functions)
- [Repository Identity Configuration](#repository-identity-configuration)
  - [Per-Repository Git Identity](#per-repository-git-identity)
  - [Configure Remote to Use Specific Host Alias](#configure-remote-to-use-specific-host-alias)
  - [Clone Using Specific Identity](#clone-using-specific-identity)
  - [Helper Function for Repository Configuration](#helper-function-for-repository-configuration)

## Use-Case TOC
- When you need multiple GitHub identities on the same machine → [Why Multiple Identities](#why-multiple-identities)
- When setting up SSH keys for a secondary account → [SSH Key Setup](#ssh-key-setup)
- When configuring SSH host aliases → [SSH Host Aliases](#ssh-host-aliases)
- When authenticating multiple accounts with gh CLI → [GitHub CLI Multi-Account Setup](#github-cli-multi-account-setup)
- When switching between GitHub identities → [Identity Switching](#identity-switching)
- When configuring a repository for a specific identity → [Repository Identity Configuration](#repository-identity-configuration)

**Related Documents:**
- [Part 2: Operations and Troubleshooting](multi-user-workflow-part2-operations.md) - Per-command overrides, collaborator management, troubleshooting, and agent orchestration

---

## Why Multiple Identities

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

## SSH Key Setup

### Step 1: Generate a Dedicated SSH Key

Each GitHub account needs its own SSH key:

```bash
# Create SSH directory if needed
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Generate key for secondary account
# Use a descriptive filename that identifies the account
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_secondary -C "account-email@example.com" -N ""

# Set correct permissions
chmod 600 ~/.ssh/id_ed25519_secondary
chmod 644 ~/.ssh/id_ed25519_secondary.pub
```

**Parameters Explained:**
- `-t ed25519`: Use the Ed25519 algorithm (modern, secure, fast)
- `-f <path>`: Output file path (avoid overwriting existing keys)
- `-C "email"`: Comment field (use the GitHub noreply email for the account)
- `-N ""`: Empty passphrase (for automation; add passphrase for interactive use)

### Step 2: Add Public Key to GitHub Account

1. Display the public key:
   ```bash
   cat ~/.ssh/id_ed25519_secondary.pub
   ```

2. Copy the output

3. In the **secondary GitHub account**:
   - Go to Settings → SSH and GPG keys → New SSH key
   - Title: Descriptive name (e.g., "Development Machine - Secondary")
   - Key type: Authentication Key
   - Key: Paste the public key
   - Click "Add SSH key"

### Step 3: Add Key to SSH Agent

```bash
# Start ssh-agent if not running
eval "$(ssh-agent -s)"

# Add the key
ssh-add ~/.ssh/id_ed25519_secondary

# Verify keys loaded
ssh-add -l
```

**macOS Note:** For persistence across reboots, add to `~/.ssh/config`:
```
Host *
  AddKeysToAgent yes
  UseKeychain yes
```

---

## SSH Host Aliases

SSH host aliases allow you to use different keys for different GitHub accounts by creating virtual hostnames that map to github.com but use specific identity files.

### Step 1: Configure SSH Host Aliases

Edit `~/.ssh/config`:

```bash
# Primary GitHub account (default)
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes

# Secondary GitHub account
Host github-secondary
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_secondary
  IdentitiesOnly yes
```

**Key Configuration Options:**
- `Host`: The alias you'll use in git remotes
- `HostName`: Actual server (always github.com)
- `User`: Always `git` for GitHub
- `IdentityFile`: Path to the private key for this account
- `IdentitiesOnly yes`: **Critical** - prevents ssh-agent from offering other keys

### Step 2: Test SSH Connection

```bash
# Test primary account
ssh -T git@github.com

# Test secondary account
ssh -T git@github-secondary
```

**Expected Output:**
```
Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
```

The username shown should match the account that owns the SSH key.

---

## GitHub CLI Multi-Account Setup

GitHub CLI supports multiple authenticated accounts. Each account can be added separately.

### Step 1: Authenticate Primary Account

```bash
gh auth login
```

Choose:
- GitHub.com
- HTTPS or SSH (match your preference)
- Complete browser authentication

### Step 2: Authenticate Secondary Account

```bash
gh auth login
```

When prompted, you'll see you're already logged in. Choose to add another account:
- Complete browser authentication **while logged into the secondary GitHub account in your browser**

### Step 3: Verify Both Accounts

```bash
gh auth status
```

**Expected Output:**
```
github.com
  ✓ Logged in to github.com account primary-user (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_****

  ✓ Logged in to github.com account secondary-user (keyring)
  - Active account: false
  - Git operations protocol: https
  - Token: gho_****
```

### Step 4: Switch Active Account

```bash
# Switch to secondary account
gh auth switch --user secondary-user

# Verify switch
gh auth status
```

---

## Identity Switching

### Shell Helper Functions

Create helper functions for quick identity switching. Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Identity configuration
PRIMARY_USER="primary-user"
PRIMARY_EMAIL="primary-noreply@github.example"
PRIMARY_HOST="github.com"

SECONDARY_USER="secondary-user"
SECONDARY_EMAIL="secondary-noreply@github.example"
SECONDARY_HOST="github-secondary"

# Switch to primary identity
use_primary() {
  export GIT_AUTHOR_NAME="$PRIMARY_USER"
  export GIT_AUTHOR_EMAIL="$PRIMARY_EMAIL"
  export GIT_COMMITTER_NAME="$PRIMARY_USER"
  export GIT_COMMITTER_EMAIL="$PRIMARY_EMAIL"
  gh auth switch --user "$PRIMARY_USER" 2>/dev/null || echo "gh switch failed (maybe not authenticated)"
  echo "Switched to $PRIMARY_USER identity"
}

# Switch to secondary identity
use_secondary() {
  export GIT_AUTHOR_NAME="$SECONDARY_USER"
  export GIT_AUTHOR_EMAIL="$SECONDARY_EMAIL"
  export GIT_COMMITTER_NAME="$SECONDARY_USER"
  export GIT_COMMITTER_EMAIL="$SECONDARY_EMAIL"
  gh auth switch --user "$SECONDARY_USER" 2>/dev/null || echo "gh switch failed (maybe not authenticated)"
  echo "Switched to $SECONDARY_USER identity"
}

# Run a single command as a specific identity
with_identity() {
  local identity="$1"
  shift
  case "$identity" in
    primary)
      GIT_AUTHOR_NAME="$PRIMARY_USER" \
      GIT_AUTHOR_EMAIL="$PRIMARY_EMAIL" \
      GIT_COMMITTER_NAME="$PRIMARY_USER" \
      GIT_COMMITTER_EMAIL="$PRIMARY_EMAIL" \
      "$@"
      ;;
    secondary)
      GIT_AUTHOR_NAME="$SECONDARY_USER" \
      GIT_AUTHOR_EMAIL="$SECONDARY_EMAIL" \
      GIT_COMMITTER_NAME="$SECONDARY_USER" \
      GIT_COMMITTER_EMAIL="$SECONDARY_EMAIL" \
      "$@"
      ;;
    *)
      echo "Unknown identity: $identity"
      return 1
      ;;
  esac
}
```

**Usage:**
```bash
# Switch shell to secondary identity
use_secondary

# Run single command as secondary
with_identity secondary git commit -m "Fix bug"
with_identity secondary gh pr create
```

---

## Repository Identity Configuration

### Per-Repository Git Identity

Set git identity for a specific repository:

```bash
cd /path/to/repository

# Set local git identity (only affects this repo)
git config user.name "secondary-user"
git config user.email "secondary-noreply@github.example"

# Verify
git config user.name
git config user.email
```

### Configure Remote to Use Specific Host Alias

Change the remote URL to use the appropriate SSH host alias:

```bash
# View current remote
git remote -v

# Change origin to use secondary host alias
# From: git@github.com:owner/repo.git
# To:   git@github-secondary:owner/repo.git
git remote set-url origin git@github-secondary:owner/repo.git

# Verify
git remote -v
```

### Clone Using Specific Identity

When cloning a new repository with a specific identity:

```bash
# Clone using secondary host alias
git clone git@github-secondary:owner/repo.git

# Then configure local identity
cd repo
git config user.name "secondary-user"
git config user.email "secondary-noreply@github.example"
```

### Helper Function for Repository Configuration

```bash
# Configure a repository for a specific identity
set_repo_for_identity() {
  local repo_path="$1"
  local host_alias="$2"
  local user_name="$3"
  local user_email="$4"

  if [ ! -d "$repo_path/.git" ]; then
    echo "ERROR: $repo_path is not a git repository"
    return 1
  fi

  pushd "$repo_path" > /dev/null

  # Set git identity
  git config user.name "$user_name"
  git config user.email "$user_email"

  # Update remote URL to use host alias
  local orig_url
  orig_url="$(git remote get-url origin 2>/dev/null || true)"
  if [ -n "$orig_url" ]; then
    # Extract owner/repo from URL
    local owner_repo
    owner_repo="$(echo "$orig_url" | sed -E 's#.*github.com[:/](.*)#\1#')"
    owner_repo="${owner_repo%.git}"

    if [ -n "$owner_repo" ]; then
      local new_url="git@${host_alias}:${owner_repo}.git"
      git remote set-url origin "$new_url"
      echo "Remote updated: $new_url"
    fi
  fi

  echo "Repository configured for $user_name"
  popd > /dev/null
}

# Usage:
# set_repo_for_identity /path/to/repo github-secondary secondary-user secondary@example.com
```

---

**Next:** See [Part 2: Operations and Troubleshooting](multi-user-workflow-part2-operations.md) for per-command overrides, collaborator management, troubleshooting, and agent orchestration integration.
