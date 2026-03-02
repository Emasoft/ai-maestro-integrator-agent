# Worktree Coordination

## Table of Contents

- 4.1 When to use worktrees
- 4.2 Worktree assignment to subagents
- 4.3 Isolation enforcement rules
- 4.4 Cleanup coordination
- 4.5 Conflict handling procedures

---

## 4.1 When to use worktrees

**Definition**: A git worktree is an additional working directory linked to the same repository, allowing multiple branches to be checked out simultaneously.

### Use worktrees when

| Scenario | Why Worktree Needed |
|----------|---------------------|
| Parallel PR work | Two subagents need different branches simultaneously |
| Long-running task + urgent task | Don't want to interrupt long task to handle urgent PR |
| Multiple PRs from same repo | Each PR needs its own isolated environment |
| Testing branch vs main | Need to compare behavior across branches |

### Do NOT use worktrees when

| Scenario | Why Not |
|----------|---------|
| Single PR work | Main worktree sufficient |
| Sequential tasks | Can switch branches between tasks |
| Non-code tasks | Worktrees only help with code isolation |
| Limited disk space | Worktrees duplicate working files |

### Worktree benefits

1. **True isolation**: Each worktree has its own working directory
2. **No branch switching**: Eliminates checkout conflicts
3. **Parallel execution**: Multiple subagents can work simultaneously
4. **Clean state**: Each worktree starts fresh

### Worktree costs

1. **Disk space**: Each worktree duplicates working files
2. **Complexity**: More state to track
3. **Cleanup burden**: Must remove worktrees when done
4. **Path confusion**: Subagents must use correct paths

---

## 4.2 Worktree assignment to subagents

### Creating worktrees for subagents

**Naming convention**: `worktree-pr-{number}` or `worktree-{task-name}`

**Creation command**:
```bash
# From main repository
git worktree add ../worktree-pr-123 pr-123-branch
```

**Directory structure**:
```
/path/to/
├── main-repo/           # Main worktree
├── worktree-pr-123/     # PR 123 worktree
├── worktree-pr-456/     # PR 456 worktree
└── worktree-hotfix/     # Hotfix worktree
```

### Assignment in subagent prompts

**Always include in prompt**:
```
Working directory: /path/to/worktree-pr-123
IMPORTANT: All file operations must use this path, not the main repository path.
```

**Example delegation with worktree**:
```
You are an implementation subagent. Your single task is:
Fix the bug described in PR #123 review comment.

Context:
- Repository: owner/repo
- PR number: 123
- Branch: feature/new-widget
- Working directory: /path/to/worktree-pr-123

CRITICAL: Work ONLY in /path/to/worktree-pr-123
Do NOT access /path/to/main-repo

Success criteria:
- Bug fixed in worktree-pr-123
- Tests pass in worktree-pr-123
- Changes committed to feature/new-widget branch
```

### Worktree state tracking

Maintain a worktree registry in `docs_dev/worktrees.md`:

```markdown
# Active Worktrees

| Worktree Path | Branch | PR | Assigned To | Created | Status |
|---------------|--------|-----|-------------|---------|--------|
| /path/to/worktree-pr-123 | feature/widget | 123 | impl-subagent-1 | 2024-01-15 | active |
| /path/to/worktree-pr-456 | bugfix/login | 456 | impl-subagent-2 | 2024-01-15 | active |
```

---

## 4.3 Isolation enforcement rules

### Rule 1: One branch per worktree

**Never switch branches within a worktree assigned to a subagent.**

Wrong:
```bash
cd /path/to/worktree-pr-123
git checkout different-branch  # VIOLATION
```

Correct:
```bash
# Create new worktree for different branch
git worktree add ../worktree-different different-branch
```

### Rule 2: One subagent per worktree

**Never assign the same worktree to multiple subagents.**

Why: Concurrent modifications cause conflicts and corruption.

Enforcement:
1. Track assignments in worktrees.md
2. Check assignment before delegating
3. Queue if worktree busy

### Rule 3: Subagent stays in assigned worktree

**Subagent must not access files outside its assigned worktree.**

Include in every prompt:
```
CONSTRAINT: You may ONLY access files within /path/to/worktree-pr-123
Accessing files in other directories is forbidden.
```

### Rule 4: Git operations only from worktree

**All git commands must run from within the worktree.**

Wrong:
```bash
cd /path/to/main-repo
git -C ../worktree-pr-123 commit -m "message"
```

Correct:
```bash
cd /path/to/worktree-pr-123
git commit -m "message"
```

### Rule 5: No worktree deletion while assigned

**Never delete a worktree while a subagent is using it.**

Deletion is only safe when:
1. Assigned subagent has completed
2. All changes committed and pushed
3. No uncommitted files

---

## 4.4 Cleanup coordination

### When to clean up

| Trigger | Action |
|---------|--------|
| PR merged | Delete worktree |
| PR closed | Delete worktree |
| Subagent completed with no pending work | Consider deletion |
| Disk space low | Delete oldest inactive worktrees |

### Cleanup procedure

1. **Verify no uncommitted changes**:
   ```bash
   cd /path/to/worktree-pr-123
   git status --porcelain
   ```

   If output is non-empty, changes exist. Do not delete.

2. **Verify no unpushed commits**:
   ```bash
   git log origin/branch-name..HEAD
   ```

   If output is non-empty, commits need pushing. Push first.

3. **Remove the worktree**:
   ```bash
   cd /path/to/main-repo
   git worktree remove ../worktree-pr-123
   ```

4. **Update registry**:
   Remove entry from `docs_dev/worktrees.md`

### Automated cleanup script

Create and run periodically:
```bash
#!/bin/bash
# cleanup-worktrees.sh

# List all worktrees
git worktree list --porcelain | while read -r line; do
    if [[ $line == worktree* ]]; then
        worktree_path="${line#worktree }"
        # Check if PR is merged/closed
        # If so, verify clean and remove
    fi
done
```

### Cleanup before orchestrator session ends

Before ending a session, the orchestrator should:
1. List all worktrees created during session
2. Verify all subagents completed
3. Clean up unused worktrees
4. Report remaining worktrees to user

---

## 4.5 Conflict handling procedures

### Type 1: Branch divergence

**Symptom**: Worktree branch has diverged from remote.

**Detection**:
```bash
git fetch origin
git status  # Shows "Your branch has diverged"
```

**Resolution**:
1. If local changes are correct: Push with appropriate strategy
2. If remote changes are correct: Reset or rebase
3. If both have valid changes: Merge and resolve conflicts

**Delegate to**: Implementation subagent with clear instructions

### Type 2: File modification conflicts

**Symptom**: Multiple worktrees modified the same file, PR merge shows conflicts.

**Detection**: GitHub PR shows merge conflicts.

**Resolution**:
1. Identify which worktree has the authoritative changes
2. In that worktree, merge the base branch and resolve
3. Push resolved changes

**Example conflict resolution delegation**:
```
You are a conflict resolution subagent. Your single task is:
Resolve merge conflicts in PR #123.

Context:
- Working directory: /path/to/worktree-pr-123
- Base branch: main
- PR branch: feature/widget

Steps:
1. Fetch latest: git fetch origin
2. Merge base: git merge origin/main
3. Resolve conflicts (prefer PR changes unless obviously wrong)
4. Commit resolution
5. Push

Return: [DONE/FAILED] conflict-resolution - brief result
```

### Type 3: Worktree corruption

**Symptom**: Git commands fail with errors about corrupt objects or broken refs.

**Detection**:
```bash
git fsck --full
```

**Resolution**:
1. Do NOT try to fix. Data may be lost.
2. Create new worktree from remote
3. Delete corrupted worktree
4. Re-delegate work to subagent in new worktree

### Type 4: Lock file conflicts

**Symptom**: "Another git process seems to be running" error.

**Detection**: `.git/index.lock` or similar lock files exist.

**Resolution**:
1. Verify no git process is running
2. Remove lock file: `rm .git/index.lock`
3. Retry operation

**Prevention**: Ensure only one subagent per worktree.

---

## Worktree Checklist

### Before creating worktree

- [ ] Confirmed worktree needed (parallel work required)
- [ ] Disk space available
- [ ] Unique worktree name chosen
- [ ] Target branch exists

### When assigning worktree to subagent

- [ ] Worktree path included in prompt
- [ ] Isolation constraints included in prompt
- [ ] Assignment recorded in worktrees.md
- [ ] Verified worktree not already assigned

### Before deleting worktree

- [ ] All changes committed
- [ ] All commits pushed
- [ ] No subagent currently assigned
- [ ] PR merged/closed or user approved deletion
- [ ] Registry updated
