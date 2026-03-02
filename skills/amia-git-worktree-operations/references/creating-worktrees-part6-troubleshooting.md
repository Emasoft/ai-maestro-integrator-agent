# Creating Worktrees: Troubleshooting

## Overview

This document covers error handling and troubleshooting for worktree creation issues.

## Table of Contents

1. [Error: "fatal: 'path' already exists"](#error-fatal-path-already-exists)
2. [Error: "fatal: 'branch' is already checked out"](#error-fatal-branch-is-already-checked-out)
3. [Error: "Port already in use"](#error-port-already-in-use)
4. [Error: "Cannot install dependencies"](#error-cannot-install-dependencies)
5. [Error: "Database migration failed"](#error-database-migration-failed)
6. [Error: "Tests fail in worktree but pass in main repo"](#error-tests-fail-in-worktree-but-pass-in-main-repo)
7. [Error: "Registry entry not created"](#error-registry-entry-not-created)
8. [Error: "Permission denied" errors](#error-permission-denied-errors)
9. [Warning: "Detached HEAD state"](#warning-detached-head-state)
10. [Preventing Common Issues](#preventing-common-issues)

---

## Error: "fatal: 'path' already exists"

**Meaning**: A directory with that name already exists.

**Solution**:
```bash
# Check if directory exists
ls -la ../worktree-name

# If it's an old worktree, remove it properly
git worktree remove ../worktree-name

# If it's not a worktree, delete or rename it
rm -rf ../worktree-name  # CAREFUL: This deletes everything
# or
mv ../worktree-name ../worktree-name.old
```

---

## Error: "fatal: 'branch' is already checked out"

**Meaning**: Git prevents checking out the same branch in multiple worktrees.

**Why this happens**: Git's safety mechanism to prevent conflicts.

**Solution**:
```bash
# Option 1: Use a different branch
git worktree add ../worktree-name -b new-branch-name origin/feature/branch

# Option 2: Remove the existing worktree first
git worktree list  # Find which worktree has the branch
git worktree remove ../other-worktree

# Option 3: Create from the branch at a specific commit (detached HEAD)
git worktree add ../worktree-name --detach origin/feature/branch
```

---

## Error: "Port already in use"

**Meaning**: Another process is using the port you're trying to allocate.

**Diagnosis**:
```bash
# Find what's using the port
lsof -i :3002

# Or on Linux
netstat -tulpn | grep 3002
```

**Solution**:
```bash
# Option 1: Stop the conflicting process
kill <PID>  # Use PID from lsof output

# Option 2: Use a different port
# Update .env file:
PORT=3004  # Use next available port

# Option 3: Update registry with correct port
jq '.worktrees[] | select(.name == "worktree-name") | .ports = [3004, 3005]' \
  .worktree-registry.json
```

---

## Error: "Cannot install dependencies"

**Common causes and solutions**:

**Wrong Node.js version**:
```bash
# Check required version
cat .nvmrc  # or check package.json "engines" field

# Install correct version
nvm install 18  # or whatever version required
nvm use 18
```

**Wrong Python version**:
```bash
# Check required version
cat .python-version  # or check pyproject.toml

# Use correct version
uv venv --python 3.12
source .venv/bin/activate
```

**Lockfile conflicts**:
```bash
# Delete lockfile and reinstall
rm package-lock.json  # or pnpm-lock.yaml, yarn.lock
npm install
```

**Network issues**:
```bash
# Clear npm cache
npm cache clean --force

# Try again
npm install
```

---

## Error: "Database migration failed"

**Diagnosis**:
```bash
# Check database exists
psql -l | grep myapp

# Check database is accessible
psql -h localhost -p 5433 -d myapp_worktree_name
```

**Solution**:
```bash
# Drop and recreate database
dropdb -p 5433 myapp_worktree_name
createdb -p 5433 myapp_worktree_name

# Run migrations again
npm run db:migrate
```

---

## Error: "Tests fail in worktree but pass in main repo"

**Common causes**:

1. **Wrong environment variables**:
```bash
# Compare .env files
diff .env ../main-repo/.env
```

2. **Database state issues**:
```bash
# Reset database
npm run db:reset
```

3. **Stale build artifacts**:
```bash
# Clean and rebuild
rm -rf dist/ build/ .next/
npm run build
```

4. **Different dependency versions**:
```bash
# Compare lockfiles
diff package-lock.json ../main-repo/package-lock.json

# Use exact same versions
rm -rf node_modules package-lock.json
cp ../main-repo/package-lock.json .
npm ci  # ci = clean install from lockfile
```

---

## Error: "Registry entry not created"

**Symptoms**: Worktree exists but not in `.worktree-registry.json`.

**Solution**:
```bash
# Manually add entry
jq '.worktrees += [{
  "name": "worktree-name",
  "path": "../worktree-name",
  "branch": "'$(cd ../worktree-name && git branch --show-current)'",
  "purpose": "review",
  "ports": [3002, 3003],
  "created": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
  "status": "active",
  "notes": "Add description here"
}]' .worktree-registry.json > .worktree-registry.tmp.json && \
mv .worktree-registry.tmp.json .worktree-registry.json
```

---

## Error: "Permission denied" errors

**Common on macOS/Linux**:

**Solution**:
```bash
# Fix directory permissions
chmod -R u+rwX ../worktree-name

# Fix git directory permissions
chmod -R u+rwX ../worktree-name/.git
```

---

## Warning: "Detached HEAD state"

**Meaning**: Not on any branch, just viewing a specific commit.

**Is this a problem?**:
- No, if you created worktree with `--detach` intentionally
- Yes, if you expected to be on a branch

**Solution** (if unexpected):
```bash
cd ../worktree-name

# Create a branch at current position
git checkout -b new-branch-name

# Or switch to existing branch
git checkout existing-branch-name
```

---

## Preventing Common Issues

**Best practices to avoid errors**:

1. **Always check registry first**:
```bash
jq '.' .worktree-registry.json
```

2. **Use consistent naming**:
```bash
# Good: review-GH-42, feature-auth, bugfix-GH-55-crash
# Bad: temp, test, asdf, my-worktree
```

3. **Allocate ports before creating worktree**:
```bash
# Check ports first
jq -r '.worktrees[].ports[]' .worktree-registry.json | sort -n
```

4. **Verify branch exists before creating**:
```bash
git fetch origin
git branch -r | grep feature/new-auth
```

5. **Test immediately after creation**:
```bash
cd ../worktree-name
npm install
npm test
```

---

## Related Documentation

- [Standard Creation Flow](./creating-worktrees-part1-standard-flow.md)
- [Purpose-Specific Patterns](./creating-worktrees-part2-purpose-patterns.md)
- [Port Allocation Strategy](./creating-worktrees-part3-port-allocation.md)
- [Environment Setup](./creating-worktrees-part4-environment-setup.md)
- [Commands Reference and Checklist](./creating-worktrees-part5-commands-checklist.md)
