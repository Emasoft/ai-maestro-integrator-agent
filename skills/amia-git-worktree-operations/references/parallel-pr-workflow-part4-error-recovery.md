# Parallel PR Workflow - Part 4: Error Recovery

This document covers:

- Error recovery when isolation is violated
- Summary of parallel PR workflow requirements

## Table of Contents

- [2.7 Error Recovery When Isolation is Violated](#27-error-recovery-when-isolation-is-violated)
  - [Detecting Violations](#detecting-violations)
  - [Recovery Procedure for Main Repo Contamination](#recovery-procedure-for-main-repo-contamination)
  - [Recovery Procedure for Cross-Worktree Contamination](#recovery-procedure-for-cross-worktree-contamination)
  - [Preventing Future Violations](#preventing-future-violations)
- [Summary](#summary)

---

## 2.7 Error Recovery When Isolation is Violated

### Detecting Violations

Run the isolation verification script:

```bash
# All paths MUST be inside the agent folder: $AGENT_DIR = ~/agents/<persona-name>
python scripts/amia_verify_worktree_isolation.py \
    --worktree-path "$AGENT_DIR/worktrees/pr-123" \
    --main-repo "$AGENT_DIR/repos/<repo-name>" \
    --check-git-status
```

### Recovery Procedure for Main Repo Contamination

If files were accidentally written to the main repo:

**Step 1: Identify contaminated files**

```bash
# Use git -C to target the specific repo inside the agent folder
git -C "$AGENT_DIR/repos/<repo-name>" status
# Shows unexpected changes
```

**Step 2: Determine if changes should be kept**

```bash
git -C "$AGENT_DIR/repos/<repo-name>" diff <file>
# Review the changes
```

**Step 3a: Discard contaminating changes**

```bash
git -C "$AGENT_DIR/repos/<repo-name>" checkout -- <file>
# Or for all changes:
git -C "$AGENT_DIR/repos/<repo-name>" checkout -- .
```

**Step 3b: Move changes to correct worktree**

```bash
# Save the diff — NEVER write to /tmp, use $AGENT_DIR/tmp/ instead
git -C "$AGENT_DIR/repos/<repo-name>" diff <file> > "$AGENT_DIR/tmp/changes.patch"

# Discard in main repo
git -C "$AGENT_DIR/repos/<repo-name>" checkout -- <file>

# Apply in correct worktree
git -C "$AGENT_DIR/worktrees/pr-123" apply "$AGENT_DIR/tmp/changes.patch"
```

### Recovery Procedure for Cross-Worktree Contamination

If Agent A accidentally modified Agent B's worktree:

**Step 1: Identify which worktree was contaminated**

```bash
# Check each worktree — all worktrees are inside $AGENT_DIR/worktrees/
for wt in "$AGENT_DIR"/worktrees/pr-*/; do
    echo "=== $wt ==="
    git -C "$wt" status
done
```

**Step 2: Determine ownership of changes**

- Which agent should have made this change?
- Is the change correct but misplaced?

**Step 3: Reset contaminated worktree**

```bash
# Target the contaminated worktree inside agent folder
git -C "$AGENT_DIR/worktrees/pr-456" status
git -C "$AGENT_DIR/worktrees/pr-456" checkout -- <accidentally_modified_files>
```

**Step 4: Re-apply changes in correct worktree**
Have the correct agent redo their work in the proper worktree.

### Preventing Future Violations

After recovering from a violation:

1. **Review agent instructions:** Were isolation rules clear?
2. **Add path validation:** Implement automated checks
3. **Update prompts:** Make worktree constraints more explicit
4. **Consider file watchers:** Monitor for out-of-worktree writes

---

## Summary

Parallel PR workflow with worktrees requires:

1. **Proper setup:** Create worktrees with consistent naming
2. **Strict isolation:** All operations within assigned worktree
3. **Clear delegation:** Agents know their boundaries
4. **Serialized git ops:** One git operation at a time
5. **Violation recovery:** Procedures for when things go wrong

---

**Previous:** [Part 3 - Concurrent Operations and Example Workflow](parallel-pr-workflow-part3-concurrency-and-example.md)

**Continue to:** [worktree-cleanup.md](worktree-cleanup.md) for safe worktree removal procedures.
