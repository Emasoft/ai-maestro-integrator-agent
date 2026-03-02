# Quick Start Workflows

## Contents
- [Workflow 1: Create Feature Worktree](#workflow-1-create-feature-worktree) - When you need to start a new feature
- [Workflow 2: Parallel Bug Fix](#workflow-2-parallel-bug-fix) - If you need to fix a bug while working on another task
- [Workflow 3: Review and Cleanup](#workflow-3-review-and-cleanup) - When you need to validate and clean up worktrees
- [Workflow 4: Testing Isolation](#workflow-4-testing-isolation) - If you need isolated test environments
- [Workflow 5: Code Review Setup](#workflow-5-code-review-setup) - When reviewing pull requests
- [Workflow 6: Hotfix Emergency](#workflow-6-hotfix-emergency) - If you need to deploy an urgent fix

---

## Workflow 1: Create Feature Worktree

Use this workflow when starting development on a new feature.

```bash
# Step 1: Create a new worktree for feature development
python scripts/worktree_create.py \
  --name feature-user-auth \
  --branch feature/user-auth \
  --port 8101

# Step 2: Navigate to the worktree
cd ../feature-user-auth

# Step 3: Verify the worktree
git status
git branch

# Step 4: Start development
# Make changes, commit, push as normal
```

**Expected Output:**
```
Created worktree 'feature-user-auth' at ../feature-user-auth
Branch: feature/user-auth
Port: 8101
Registry updated successfully
```

## Workflow 2: Parallel Bug Fix

Use this workflow when you need to fix a bug without interrupting current work.

```bash
# Step 1: List existing worktrees to check availability
python scripts/worktree_list.py

# Step 2: Create worktree for urgent bugfix
python scripts/worktree_create.py \
  --name bugfix-login \
  --branch bugfix/login-issue-42 \
  --port 8102

# Step 3: Work on the fix independently
cd ../bugfix-login
# Fix the bug, test, commit

# Step 4: Return to main worktree
cd ../main-repo
```

**Key Points:**
- Your current work remains untouched in the original worktree
- The bugfix branch is completely isolated
- Port 8102 is allocated for any services needed during testing

## Workflow 3: Review and Cleanup

Use this workflow to maintain registry health and clean up completed work.

```bash
# Step 1: Validate registry integrity
python scripts/registry_validate.py

# Step 2: Check port allocations
python scripts/port_status.py

# Step 3: Remove completed worktree
python scripts/worktree_remove.py --name feature-user-auth

# Step 4: Verify removal
python scripts/worktree_list.py
```

**Validation Output Example:**
```
Registry Validation Report
==========================
Total worktrees: 3
Valid entries: 3
Orphaned entries: 0
Port conflicts: 0
Status: HEALTHY
```

## Workflow 4: Testing Isolation

Use this workflow when you need isolated environments for parallel testing.

```bash
# Step 1: Create test worktrees
python scripts/worktree_create.py --name test-a --branch test/scenario-a --port 8110
python scripts/worktree_create.py --name test-b --branch test/scenario-b --port 8111

# Step 2: Run tests in each worktree
cd ../test-a && npm test
cd ../test-b && npm test

# Step 3: Verify results in Docker (optional)
# See references/docker-worktree-testing.md for Docker test setup

# Step 4: Clean up test worktrees
python scripts/worktree_remove.py --name test-a
python scripts/worktree_remove.py --name test-b
```

**Port Allocation:**
- Port 8110: test-a worktree services
- Port 8111: test-b worktree services
- Prevents port conflicts between parallel tests

## Workflow 5: Code Review Setup

Use this workflow when reviewing pull requests in isolation.

```bash
# Step 1: Create review worktree from PR branch
python scripts/worktree_create.py \
  --name review-pr-123 \
  --branch pr/123/head \
  --port 8120

# Step 2: Navigate and set up environment
cd ../review-pr-123
npm install  # or pip install, etc.

# Step 3: Run the application for testing
npm start --port 8120

# Step 4: After review, clean up
cd ../main-repo
python scripts/worktree_remove.py --name review-pr-123
```

**Benefits:**
- Review code without affecting your current work
- Run the PR code in isolation
- Easy cleanup after review complete

## Workflow 6: Hotfix Emergency

Use this workflow for critical production fixes requiring immediate attention.

```bash
# Step 1: Create hotfix worktree from production branch
python scripts/worktree_create.py \
  --name hotfix-critical \
  --branch hotfix/critical-security-fix \
  --base-branch production \
  --port 8100

# Step 2: Implement fix
cd ../hotfix-critical
# Make minimal fix, test thoroughly

# Step 3: Validate before merge
python scripts/merge_safeguard.py --check .

# Step 4: Push and create PR
git push -u origin hotfix/critical-security-fix
gh pr create --base production --title "Critical Security Fix"

# Step 5: After merge, clean up
cd ../main-repo
python scripts/worktree_remove.py --name hotfix-critical
```

**Critical Steps:**
1. Always branch from production for hotfixes
2. Use merge safeguards before pushing
3. Clean up immediately after merge to free resources
