# Step-by-Step Procedures

## Table of Contents

- [Phase 1: Understanding Prerequisites](#phase-1-understanding-worktree-prerequisites) - Before creating worktrees
- [Phase 2: Create a Worktree](#phase-2-create-a-worktree) - Creating new worktrees
- [Phase 3: Manage Multiple Worktrees](#phase-3-manage-multiple-worktrees) - Working with multiple worktrees
- [Phase 4: Service Port Management](#phase-4-service-port-management) - Allocating and managing ports
- [Phase 5: Remove Worktrees](#phase-5-remove-worktrees) - Safe worktree removal
- [Phase 6: Maintain Registry](#phase-6-maintain-registry) - Registry maintenance procedures

---

## Phase 1: Understanding Worktree Prerequisites

Before creating worktrees, verify the following requirements are met.

### Step 1.1: Verify Git Repository Exists

Check that your repository is properly initialized:

```bash
# Verify repository exists
git rev-parse --git-dir

# Check for at least one commit
git log --oneline -1
```

**Requirements:**

- The main repository exists at the target path
- You have write permissions to the repository
- The repository has at least one commit (initial commit)

### Step 1.2: Verify Registry Directory

Ensure the AMIA configuration directory is accessible:

```bash
# Check if directory exists
ls -la ~/design/

# If not, create it
mkdir -p ~/design/

# Verify write permissions
touch ~/design/.write-test && rm ~/design/.write-test
```

**Requirements:**

- The `~/design/` directory exists or can be created
- You have write permissions to `~/design/`
- The directory will store the `worktree-registry.json` file

### Step 1.3: Plan Port Allocation

Document your port requirements before creating worktrees:

| Worktree Name | Purpose | Port | Services |
|--------------|---------|------|----------|
| feature-auth | User authentication | 8101 | Web server |
| bugfix-api | API fixes | 8102 | API server |
| test-integration | Integration tests | 8110 | Test runner |

**Guidelines:**

- Identify which ports will be needed (8100-8199 range)
- Document the port usage in advance
- Avoid conflicts with existing services

---

## Phase 2: Create a Worktree

Follow these steps to create a new worktree with registry tracking.

### Step 2.1: Create Worktree Entry in Registry

The creation script handles this automatically:

```bash
python scripts/worktree_create.py \
  --name my-feature \
  --branch feature/my-feature \
  --port 8101
```

**Internal Process:**

1. Calculate available port from registry
2. Add worktree metadata to registry
3. Record: worktree name, path, branch, port, creation timestamp

### Step 2.2: Create Physical Worktree

The script executes the Git command:

```bash
# Underlying Git command
git worktree add ../my-feature feature/my-feature
```

**What Happens:**

- Git creates worktree directory at specified path
- Links to specific branch (creates if doesn't exist)
- Shares Git object database with main repository

### Step 2.3: Validate Worktree Creation

Verify the worktree was created correctly:

```bash
# Confirm worktree directory exists
ls -la ../my-feature/

# Verify .git file points to main repository
cat ../my-feature/.git

# Check branch is correctly checked out
cd ../my-feature && git branch --show-current
```

**Expected Results:**

- Directory exists with full working copy
- `.git` file contains path to main repo's `.git` directory
- Correct branch is active

---

## Phase 3: Manage Multiple Worktrees

### Step 3.1: List Worktrees

Display all worktrees from registry:

```bash
python scripts/worktree_list.py
```

**Output Format:**

```
Name              Branch                  Port   Status   Path
----------------  ----------------------  -----  -------  ------------------
main              main                    8100   active   /path/to/main
feature-auth      feature/user-auth       8101   active   /path/to/feature-auth
bugfix-login      bugfix/login-issue      8102   active   /path/to/bugfix-login
```

### Step 3.2: Switch to Worktree Context

Navigate to and activate a worktree:

```bash
# Change to worktree directory
cd ../feature-auth

# Activate any necessary environment
source .venv/bin/activate  # Python
# or
nvm use                    # Node.js

# Verify correct branch is active
git branch --show-current
```

### Step 3.3: Work in Worktree

Work independently in the worktree:

```bash
# Make changes
vim src/auth.py

# Commit changes
git add -A
git commit -m "Add user authentication"

# Push when ready
git push -u origin feature/user-auth
```

**Key Points:**

- Changes in one worktree don't affect others
- Each worktree has independent staging area
- Push commits independently

---

## Phase 4: Service Port Management

### Step 4.1: Allocate Port to Worktree Service

Query registry for next available port:

```bash
python scripts/port_allocate.py --worktree my-feature --port 8101
```

**Process:**

1. Check port not already allocated
2. Reserve port in registry with service name
3. Update registry file atomically

### Step 4.2: Start Service in Worktree

Launch service on allocated port:

```bash
# Navigate to worktree
cd ../my-feature

# Start service on allocated port
npm start --port 8101
# or
python manage.py runserver 0.0.0.0:8101
# or
flask run --port 8101
```

**Verification:**

```bash
curl http://localhost:8101/health
```

### Step 4.3: Document Port Usage

The registry tracks port metadata:

```json
{
  "worktrees": {
    "my-feature": {
      "port": 8101,
      "service_type": "web",
      "allocated_at": "2025-01-08T10:00:00Z"
    }
  }
}
```

---

## Phase 5: Remove Worktrees

### Step 5.1: Prepare for Removal

Before removing, verify worktree is clean:

```bash
cd ../my-feature

# Check for uncommitted changes
git status

# Push any unpushed commits
git log origin/feature-name..HEAD

# Stop any running services
pkill -f "port 8101"
```

**Checklist:**

- [ ] No uncommitted changes
- [ ] All commits pushed if needed
- [ ] No services running in worktree

### Step 5.2: Remove Worktree from Registry

Use the removal script:

```bash
python scripts/worktree_remove.py --name my-feature
```

**Process:**

1. Find worktree entry in registry
2. Remove from active worktrees list
3. Mark port as available
4. Delete physical worktree directory

### Step 5.3: Delete Physical Worktree

The script executes:

```bash
# Underlying Git command
git worktree remove ../my-feature
```

**Verification:**

```bash
# Confirm directory deleted
ls ../my-feature  # Should fail

# Verify registry updated
python scripts/worktree_list.py
```

---

## Phase 6: Maintain Registry

### Step 6.1: Verify Registry Integrity

Run validation to check health:

```bash
python scripts/registry_validate.py
```

**Checks Performed:**

- Registry file is valid JSON
- All registered worktrees physically exist
- No duplicate port allocations
- All required fields present

### Step 6.2: Clean Up Orphaned Entries

If validation finds orphans:

```bash
python scripts/registry_validate.py --fix-orphans
```

**Process:**

1. Remove registry entries for deleted worktrees
2. Free up ports for reuse
3. Update registry file atomically

### Step 6.3: Export Registry Information

Generate reports:

```bash
# JSON export
python scripts/worktree_list.py --format json > worktrees.json

# Summary report
python scripts/port_status.py
```

**Report Contents:**

- All active worktrees
- Port allocations
- Status information
- Creation timestamps
