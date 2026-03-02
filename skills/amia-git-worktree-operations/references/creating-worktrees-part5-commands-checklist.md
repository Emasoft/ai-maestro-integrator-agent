# Creating Worktrees: Commands Reference and Checklist

## Overview

This document provides command reference for worktree creation and a comprehensive post-creation checklist.

## Table of Contents

### Commands Reference
1. [Basic Worktree Creation](#basic-worktree-creation)
2. [Advanced Creation Options](#advanced-creation-options)
3. [Listing and Inspecting Worktrees](#listing-and-inspecting-worktrees)
4. [Registry Management Commands](#registry-management-commands)
5. [Environment Setup Commands](#environment-setup-commands)

### Post-Creation Checklist
6. [Immediate Post-Creation (Required)](#immediate-post-creation-required)
7. [Environment Setup (Required)](#environment-setup-required)
8. [Verification (Recommended)](#verification-recommended)
9. [Documentation (Recommended)](#documentation-recommended)
10. [Optional but Useful](#optional-but-useful)

---

## Basic Worktree Creation

```bash
# Create worktree from existing branch
git worktree add <path> <existing-branch>
git worktree add ../review-GH-42 origin/feature/new-auth

# Create worktree with new branch
git worktree add <path> -b <new-branch>
git worktree add ../feature-profiles -b feature/user-profiles

# Create from specific commit
git worktree add <path> <commit-hash>
git worktree add ../bugfix-GH-55 abc123def

# Create detached HEAD (no branch)
git worktree add <path> --detach <commit-hash>
git worktree add ../inspect-commit --detach abc123def
```

---

## Advanced Creation Options

```bash
# Create worktree and track remote branch
git worktree add ../review-GH-42 -b local-branch --track origin/feature/new-auth

# Create worktree from tag
git worktree add ../release-v1.2.3 v1.2.3

# Create worktree with specific checkout strategy
git worktree add --checkout ../worktree-name branch-name
git worktree add --no-checkout ../worktree-name branch-name  # Don't populate files yet

# Force creation (overwrite existing directory)
# WARNING: Only use if you know what you're doing
git worktree add --force ../existing-dir branch-name
```

---

## Listing and Inspecting Worktrees

```bash
# List all worktrees
git worktree list

# List with more details
git worktree list --porcelain

# Show specific worktree info
git worktree list | grep "review-GH-42"
```

---

## Registry Management Commands

```bash
# View entire registry
cat .worktree-registry.json

# Pretty print registry
jq '.' .worktree-registry.json

# List all worktree names
jq -r '.worktrees[].name' .worktree-registry.json

# List all allocated ports
jq -r '.worktrees[].ports[]' .worktree-registry.json | sort -n

# Find worktree by GitHub issue
jq -r '.worktrees[] | select(.github_issue == 42)' .worktree-registry.json

# Find worktrees by purpose
jq -r '.worktrees[] | select(.purpose == "review") | .name' .worktree-registry.json
```

---

## Environment Setup Commands

```bash
# Node.js setup
cd ../worktree-name
pnpm install
cp .env.example .env
# Edit .env with worktree-specific values
pnpm run db:migrate
pnpm test
pnpm run dev

# Python setup
cd ../worktree-name
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
# Edit .env with worktree-specific values
python manage.py migrate
python manage.py test
python manage.py runserver 3002

# Ruby setup
cd ../worktree-name
bundle install
cp .env.example .env
# Edit .env with worktree-specific values
rails db:migrate
rails test
rails server -p 3002
```

---

## Post-Creation Checklist

Use this checklist after creating any worktree to ensure proper setup.

---

## Immediate Post-Creation (Required)

- [ ] **Worktree directory exists and is accessible**
  ```bash
  ls -la ../worktree-name
  ```

- [ ] **Git worktree is registered with git**
  ```bash
  git worktree list | grep "worktree-name"
  ```

- [ ] **Correct branch is checked out**
  ```bash
  cd ../worktree-name && git branch --show-current
  ```

- [ ] **Registry entry created in `.worktree-registry.json`**
  ```bash
  jq -r '.worktrees[] | select(.name == "worktree-name")' .worktree-registry.json
  ```

- [ ] **Registry entry has all required fields**
  - name
  - path
  - branch
  - purpose
  - ports (if applicable)
  - created timestamp
  - status

---

## Environment Setup (Required)

- [ ] **Dependencies installed successfully**
  ```bash
  # Check node_modules exists (Node.js)
  ls -la node_modules

  # Check .venv exists (Python)
  ls -la .venv

  # Check vendor exists (Ruby)
  ls -la vendor/bundle
  ```

- [ ] **Environment file created and configured**
  ```bash
  # Check .env exists
  ls -la .env

  # Verify ports are set correctly
  grep "PORT=" .env
  ```

- [ ] **Database created and migrated (if applicable)**
  ```bash
  # Verify database exists
  psql -l | grep "myapp_worktree"

  # Check migrations ran
  npm run db:migrate:status
  ```

- [ ] **Build/compilation successful (if applicable)**
  ```bash
  # Check build artifacts exist
  ls -la dist/  # or build/, public/, etc.
  ```

---

## Verification (Recommended)

- [ ] **Tests pass in worktree**
  ```bash
  npm test
  # All tests should pass with no errors
  ```

- [ ] **Application starts without errors**
  ```bash
  npm run dev
  # Should start successfully on allocated port
  ```

- [ ] **Port allocation correct (no conflicts)**
  ```bash
  # Check nothing else using the port
  lsof -i :3002
  # Should show only the worktree's process
  ```

- [ ] **Can access application in browser**
  ```
  Open: http://localhost:3002
  Should load successfully
  ```

---

## Documentation (Recommended)

- [ ] **Registry notes field filled**
  ```json
  {
    "notes": "Reviewing authentication refactor PR #42"
  }
  ```

- [ ] **GitHub issue/PR linked (if applicable)**
  ```json
  {
    "github_issue": 42
  }
  ```

- [ ] **Purpose clearly documented**
  ```json
  {
    "purpose": "review"  // or: "feature", "bugfix", "test"
  }
  ```

---

## Optional but Useful

- [ ] **Git remote tracking set up**
  ```bash
  cd ../worktree-name
  git branch -vv  # Should show remote tracking
  ```

- [ ] **Pre-commit hooks installed (if project uses them)**
  ```bash
  ls -la .git/hooks/
  ```

- [ ] **IDE/Editor configuration synced**
  ```bash
  # Copy IDE settings from main repo
  cp ../main-repo/.vscode/settings.json .vscode/
  ```

---

## Related Documentation

- [Standard Creation Flow](./creating-worktrees-part1-standard-flow.md)
- [Purpose-Specific Patterns](./creating-worktrees-part2-purpose-patterns.md)
- [Port Allocation Strategy](./creating-worktrees-part3-port-allocation.md)
- [Environment Setup](./creating-worktrees-part4-environment-setup.md)
- [Troubleshooting](./creating-worktrees-part6-troubleshooting.md)
