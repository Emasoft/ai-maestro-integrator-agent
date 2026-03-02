# Worktree Automation Scripts Guide - Part 4: Common Workflows

**Related Documents:**
- [Main Index](scripts-guide.md)
- [Part 1: Core Scripts](scripts-guide-part1-core-scripts.md)
- [Part 2: Management Scripts](scripts-guide-part2-management-scripts.md)
- [Part 3: Port Scripts](scripts-guide-part3-port-scripts.md)
- [Part 5: Troubleshooting](scripts-guide-part5-troubleshooting.md)

---

## Table of Contents

- [Common Workflows](#common-workflows)
  - [Workflow 1: Code Review Setup](#workflow-1-code-review-setup)
  - [Workflow 2: Feature Development with Multiple Services](#workflow-2-feature-development-with-multiple-services)
  - [Workflow 3: Cleanup Old Worktrees](#workflow-3-cleanup-old-worktrees)
  - [Workflow 4: Emergency Hotfix](#workflow-4-emergency-hotfix)
  - [Workflow 5: Experiment Without Risk](#workflow-5-experiment-without-risk)
  - [Workflow 6: Validate and Fix Registry After Manual Operations](#workflow-6-validate-and-fix-registry-after-manual-operations)

---

## Common Workflows

This section provides step-by-step procedures for typical worktree operations.

---

### Workflow 1: Code Review Setup

**Goal:** Create isolated environment to review and test a pull request.

**Steps:**

1. **Create review worktree with ports**
   ```bash
   python scripts/worktree_create.py --purpose review --identifier GH-42 --branch feature/auth --ports
   ```

2. **Verify port allocation**
   ```bash
   python scripts/port_status.py --worktree review-GH-42
   ```
   Note the allocated ports (e.g., web:8001, api:9001)

3. **Navigate to worktree and start services**
   ```bash
   cd worktrees/review-GH-42
   npm install
   npm run dev -- --port 8001
   ```

4. **Test the feature in browser**
   ```
   Open: http://localhost:8001
   ```

5. **After review is complete, mark as done and remove**
   ```bash
   # Manually mark as completed in registry, or use helper script
   # Then remove:
   python scripts/worktree_remove.py review-GH-42
   ```

**Why this workflow:**
- Isolated from your main development work
- Dedicated ports prevent conflicts
- Easy cleanup after review

---

### Workflow 2: Feature Development with Multiple Services

**Goal:** Develop new feature requiring web frontend, API backend, and database.

**Steps:**

1. **Create feature worktree with automatic port allocation**
   ```bash
   python scripts/worktree_create.py --purpose feature --identifier user-auth --branch feature/user-authentication --ports
   ```

2. **Check allocated ports**
   ```bash
   python scripts/port_status.py --worktree feature-user-auth
   ```
   Example output: web:8001, api:9001, db:5433

3. **Navigate to worktree**
   ```bash
   cd worktrees/feature-user-auth
   ```

4. **Start all services with allocated ports**
   ```bash
   # Terminal 1: Frontend
   npm run dev -- --port 8001

   # Terminal 2: Backend
   npm run api -- --port 9001

   # Terminal 3: Database
   docker run -p 5433:5432 postgres:15
   ```

5. **Develop and test feature**
   - Frontend: http://localhost:8001
   - API: http://localhost:9001
   - DB: localhost:5433

6. **When feature is complete**
   ```bash
   # Commit changes
   git add .
   git commit -m "Implement user authentication"

   # Mark worktree as completed (edit registry or use helper)
   # Then remove:
   python scripts/worktree_remove.py feature-user-auth
   ```

**Why this workflow:**
- All services have unique ports, no conflicts with other work
- Can run main development and feature development simultaneously
- Clean separation of concerns

---

### Workflow 3: Cleanup Old Worktrees

**Goal:** Remove all completed worktrees to free disk space and ports.

**Steps:**

1. **List all worktrees to see what's active**
   ```bash
   python scripts/worktree_list.py --status all
   ```

2. **Preview what will be removed**
   ```bash
   python scripts/worktree_remove.py --all-completed --dry-run
   ```

3. **Review the list and confirm removal**
   ```bash
   python scripts/worktree_remove.py --all-completed
   ```
   Type 'y' when prompted

4. **Validate registry is consistent after cleanup**
   ```bash
   python scripts/registry_validate.py
   ```

5. **Verify port availability increased**
   ```bash
   python scripts/port_status.py --all
   ```

**Why this workflow:**
- Maintains clean workspace
- Releases ports for new worktrees
- Ensures registry stays consistent

---

### Workflow 4: Emergency Hotfix

**Goal:** Quickly create worktree from production tag, fix bug, and cleanup.

**Steps:**

1. **Create hotfix worktree from production tag**
   ```bash
   python scripts/worktree_create.py --purpose hotfix --identifier CVE-2024-001 --branch v2.1.3 --ports
   ```

2. **Navigate and apply fix**
   ```bash
   cd worktrees/hotfix-CVE-2024-001
   # Make necessary changes
   git checkout -b hotfix/CVE-2024-001
   git commit -m "Fix security vulnerability CVE-2024-001"
   ```

3. **Test the fix**
   ```bash
   npm run test
   npm run dev -- --port 8001  # Use allocated port
   # Manually verify fix
   ```

4. **Push hotfix branch**
   ```bash
   git push origin hotfix/CVE-2024-001
   # Create PR for review
   ```

5. **After merge, cleanup**
   ```bash
   python scripts/worktree_remove.py hotfix-CVE-2024-001 --force
   ```

**Why this workflow:**
- Isolates hotfix from ongoing development
- Starts from exact production version
- Fast cleanup after merge

---

### Workflow 5: Experiment Without Risk

**Goal:** Test architectural changes without affecting main codebase.

**Steps:**

1. **Create experiment worktree**
   ```bash
   python scripts/worktree_create.py --purpose experiment --identifier async-rewrite --branch experiment/async-refactor
   ```

2. **Make experimental changes freely**
   ```bash
   cd worktrees/experiment-async-rewrite
   # Rewrite components
   # No pressure to commit or maintain quality
   ```

3. **If experiment succeeds, extract useful changes**
   ```bash
   # Cherry-pick good commits to feature branch
   git checkout -b feature/async-improvements
   git cherry-pick <useful-commit-sha>
   ```

4. **If experiment fails, remove without ceremony**
   ```bash
   python scripts/worktree_remove.py experiment-async-rewrite --force
   ```

**Why this workflow:**
- Freedom to experiment without polluting main history
- Easy to abandon failed experiments
- Can extract successful parts

---

### Workflow 6: Validate and Fix Registry After Manual Operations

**Goal:** Ensure registry is consistent after manual git operations or filesystem changes.

**Steps:**

1. **Run validation to detect issues**
   ```bash
   python scripts/registry_validate.py --verbose
   ```

2. **Review reported issues**
   - Orphaned entries (registry entry but no directory)
   - Missing entries (directory but no registry entry)
   - Port conflicts

3. **Create backup before fixing**
   ```bash
   cp .claude/worktree-registry.json .claude/worktree-registry.json.manual-backup
   ```

4. **Apply automatic fixes**
   ```bash
   python scripts/registry_validate.py --fix --verbose
   ```

5. **Verify fixes were successful**
   ```bash
   python scripts/worktree_list.py --validate
   ```

6. **Check port allocations are correct**
   ```bash
   python scripts/port_status.py --all
   ```

**Why this workflow:**
- Catches inconsistencies from manual operations
- Prevents registry corruption
- Maintains reliable automation

---

**End of Part 4: Common Workflows**

**Next:** [Part 5: Troubleshooting](scripts-guide-part5-troubleshooting.md) - Problem resolution and best practices
