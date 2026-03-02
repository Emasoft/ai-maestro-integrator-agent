# Creating Git Worktrees

## Table of Contents

- [Overview](#overview)
- [Document Structure](#document-structure)
- [Quick Reference: Standard Creation Flow](#quick-reference-standard-creation-flow)
  - [STEP 1: Check Registry for Conflicts](#step-1-check-registry-for-conflicts)
  - [STEP 2: Determine Naming Based on Purpose](#step-2-determine-naming-based-on-purpose)
  - [STEP 3: Allocate Ports If Needed](#step-3-allocate-ports-if-needed)
  - [STEP 4: Create Git Worktree](#step-4-create-git-worktree)
  - [STEP 5: Register in Registry](#step-5-register-in-registry)
  - [STEP 6: Setup Environment](#step-6-setup-environment)
- [Quick Reference: Purpose-Specific Patterns](#quick-reference-purpose-specific-patterns)
  - [Review Worktrees](#review-worktrees)
  - [Feature Worktrees](#feature-worktrees)
  - [Bugfix Worktrees](#bugfix-worktrees)
  - [Testing Worktrees](#testing-worktrees)
- [Quick Reference: Port Allocation](#quick-reference-port-allocation)
  - [When to Allocate](#when-to-allocate)
  - [Standard Port Ranges](#standard-port-ranges)
- [Quick Reference: Environment Setup](#quick-reference-environment-setup)
  - [7 Setup Steps](#7-setup-steps)
- [Quick Reference: Essential Commands](#quick-reference-essential-commands)
  - [Create Worktree](#create-worktree)
  - [List Worktrees](#list-worktrees)
  - [Registry Queries](#registry-queries)
- [Quick Reference: Post-Creation Checklist](#quick-reference-post-creation-checklist)
  - [Required Checks](#required-checks)
  - [Verification Checks](#verification-checks)
- [Quick Reference: Common Errors](#quick-reference-common-errors)
- [Summary](#summary)
- [Related Documentation](#related-documentation)
  - [Part Files](#part-files)

---

## Overview

This document provides complete instructions for creating git worktrees in a systematic and safe manner. A git worktree allows you to check out multiple branches of the same repository simultaneously in different directories.

---

## Document Structure

This guide has been split into focused parts for easier navigation:

| Part | File | Topics Covered |
|------|------|----------------|
| 1 | [Standard Flow](./creating-worktrees-part1-standard-flow.md) | 6-step creation process |
| 2 | [Purpose Patterns](./creating-worktrees-part2-purpose-patterns.md) | Review, Feature, Bugfix, Testing worktrees |
| 3 | [Port Allocation](./creating-worktrees-part3-port-allocation.md) | When and how to allocate ports |
| 4 | [Environment Setup](./creating-worktrees-part4-environment-setup.md) | Dependencies, config, database, services |
| 5 | [Commands & Checklist](./creating-worktrees-part5-commands-checklist.md) | Command reference and verification checklist |
| 6 | [Troubleshooting](./creating-worktrees-part6-troubleshooting.md) | Error handling and solutions |

---

## Quick Reference: Standard Creation Flow

Follow these 6 steps **in order** when creating any worktree:

### STEP 1: Check Registry for Conflicts
Verify no name/port/branch conflicts exist.
```bash
cat .worktree-registry.json | jq -r '.worktrees[].path' | grep "review-GH-42"
```
[Full details](./creating-worktrees-part1-standard-flow.md#step-1-check-registry-for-conflicts)

### STEP 2: Determine Naming Based on Purpose
Choose appropriate naming pattern.

| Purpose | Pattern | Example |
|---------|---------|---------|
| PR Review | `review-GH-{number}` | `review-GH-42` |
| Feature | `feature-{name}` | `feature-user-profiles` |
| Bug Fix | `bugfix-GH-{number}-{desc}` | `bugfix-GH-55-crash` |
| Testing | `test-{type}-{target}` | `test-integration-api` |

[Full details](./creating-worktrees-part1-standard-flow.md#step-2-determine-naming-based-on-purpose)

### STEP 3: Allocate Ports If Needed
Reserve unique ports for services.
```bash
# Main repo: 3000, 3001
# First worktree: 3002, 3003
# Second worktree: 3004, 3005
```
[Full details](./creating-worktrees-part1-standard-flow.md#step-3-allocate-ports-if-needed)

### STEP 4: Create Git Worktree
Run the creation command.
```bash
git worktree add ../review-GH-42 origin/feature/new-auth
```
[Full details](./creating-worktrees-part1-standard-flow.md#step-4-create-git-worktree)

### STEP 5: Register in Registry
Add entry to `.worktree-registry.json`.
```json
{
  "name": "review-GH-42",
  "path": "../review-GH-42",
  "branch": "feature/new-auth",
  "purpose": "review",
  "ports": [3002, 3003],
  "status": "active"
}
```
[Full details](./creating-worktrees-part1-standard-flow.md#step-5-register-in-registry)

### STEP 6: Setup Environment
Install dependencies and configure.
```bash
cd ../review-GH-42
npm install
cp .env.example .env
npm test
```
[Full details](./creating-worktrees-part1-standard-flow.md#step-6-setup-environment)

---

## Quick Reference: Purpose-Specific Patterns

### Review Worktrees
For PR reviews. Named `review-GH-{number}`.
```bash
git fetch origin
git worktree add ../review-GH-42 origin/feature/new-auth
cd ../review-GH-42 && npm install && npm test
```
[Full details](./creating-worktrees-part2-purpose-patterns.md#review-worktrees)

### Feature Worktrees
For new features. Named `feature-{name}`.
```bash
git worktree add ../feature-user-profiles -b feature/user-profiles
cd ../feature-user-profiles && npm install
```
[Full details](./creating-worktrees-part2-purpose-patterns.md#feature-worktrees)

### Bugfix Worktrees
For bug fixes. Named `bugfix-GH-{number}-{desc}`.
```bash
git worktree add ../bugfix-GH-55-crash -b bugfix/crash-on-login origin/main
cd ../bugfix-GH-55-crash && npm install
```
[Full details](./creating-worktrees-part2-purpose-patterns.md#bugfix-worktrees)

### Testing Worktrees
For extensive tests. Named `test-{type}-{target}`.
```bash
git worktree add ../test-integration-api -b test/integration-api
cd ../test-integration-api && npm install
```
[Full details](./creating-worktrees-part2-purpose-patterns.md#testing-worktrees)

---

## Quick Reference: Port Allocation

### When to Allocate
- **Yes**: Web servers, API servers, databases, cache services
- **No**: Code review only, documentation, quick fixes

### Standard Port Ranges
| Service Type | Range |
|--------------|-------|
| Frontend | 3000-3099 |
| Backend API | 3100-3199 |
| PostgreSQL | 5400-5499 |
| Redis | 6300-6399 |

[Full details](./creating-worktrees-part3-port-allocation.md)

---

## Quick Reference: Environment Setup

### 7 Setup Steps
1. Navigate to worktree
2. Install dependencies (`npm install` / `pip install` / `bundle install`)
3. Configure environment variables (`.env` file)
4. Setup database (create + migrate)
5. Build assets (if applicable)
6. Verify tests pass
7. Start services

[Full details](./creating-worktrees-part4-environment-setup.md)

---

## Quick Reference: Essential Commands

### Create Worktree
```bash
# From existing branch
git worktree add ../review-GH-42 origin/feature/new-auth

# With new branch
git worktree add ../feature-profiles -b feature/user-profiles

# From commit (detached)
git worktree add ../inspect-commit --detach abc123def
```

### List Worktrees
```bash
git worktree list
git worktree list --porcelain
```

### Registry Queries
```bash
jq -r '.worktrees[].name' .worktree-registry.json
jq -r '.worktrees[].ports[]' .worktree-registry.json | sort -n
```

[Full commands reference](./creating-worktrees-part5-commands-checklist.md)

---

## Quick Reference: Post-Creation Checklist

### Required Checks
- [ ] Worktree directory exists
- [ ] Git worktree registered (`git worktree list`)
- [ ] Correct branch checked out
- [ ] Registry entry created
- [ ] Dependencies installed
- [ ] Environment configured

### Verification Checks
- [ ] Tests pass
- [ ] Application starts
- [ ] No port conflicts
- [ ] Accessible in browser

[Full checklist](./creating-worktrees-part5-commands-checklist.md#post-creation-checklist)

---

## Quick Reference: Common Errors

| Error | Solution |
|-------|----------|
| "path already exists" | Remove old worktree or rename directory |
| "branch already checked out" | Use different branch or remove other worktree |
| "Port already in use" | Use different port or stop conflicting process |
| "Cannot install dependencies" | Check Node/Python version, clear cache |
| "Database migration failed" | Drop and recreate database |
| "Tests fail in worktree" | Compare .env files, reset database |

[Full troubleshooting guide](./creating-worktrees-part6-troubleshooting.md)

---

## Summary

Creating git worktrees follows this standard process:

1. **Check registry** - Verify no conflicts
2. **Choose name** - Use purpose-based naming pattern
3. **Allocate ports** - Reserve unique ports if needed
4. **Create worktree** - Run `git worktree add` command
5. **Register worktree** - Add entry to `.worktree-registry.json`
6. **Setup environment** - Install dependencies, configure env, migrate DB
7. **Verify** - Run tests and start services

**Key principles**:
- One worktree = one purpose
- Consistent naming = easier management
- Separate ports = no conflicts
- Registry = single source of truth
- Tests pass = setup correct

**When in doubt**:
- Consult the registry before creating
- Follow naming conventions strictly
- Test immediately after creation
- Document in registry notes
- Ask for help if stuck

---

## Related Documentation

- [Understanding Worktrees](./worktree-fundamentals-concepts.md) - What worktrees are and when to use them
- [Worktree Registry](./registry-system.md) - Complete registry format and management
- [Managing Worktrees](./worktree-operations-management.md) - Ongoing maintenance and cleanup
- [Worktree Workflows](./quick-start-workflows.md) - Common workflows and patterns
- [Troubleshooting Guide](./troubleshooting-index.md) - In-depth troubleshooting

### Part Files
- [Part 1: Standard Creation Flow](./creating-worktrees-part1-standard-flow.md)
- [Part 2: Purpose-Specific Patterns](./creating-worktrees-part2-purpose-patterns.md)
- [Part 3: Port Allocation Strategy](./creating-worktrees-part3-port-allocation.md)
- [Part 4: Environment Setup](./creating-worktrees-part4-environment-setup.md)
- [Part 5: Commands Reference and Checklist](./creating-worktrees-part5-commands-checklist.md)
- [Part 6: Troubleshooting](./creating-worktrees-part6-troubleshooting.md)
