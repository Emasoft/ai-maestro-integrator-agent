# Worktree Operations Reference

This document serves as an index to the worktree operations reference, which has been split into 7 parts for easier navigation and consumption.

## Table of Contents

- [Quick Reference: Which Part to Read](#quick-reference-which-part-to-read)
- [Part 1: Listing and Switching Worktrees](#part-1-listing-and-switching-worktrees)
- [Part 2: Updating Worktrees](#part-2-updating-worktrees)
- [Part 3: Locking and Moving Worktrees](#part-3-locking-and-moving-worktrees)
- [Part 4: Checking Worktree Status](#part-4-checking-worktree-status)
- [Part 5: Syncing with Main Branch](#part-5-syncing-with-main-branch)
- [Part 6: Best Practices](#part-6-best-practices)
- [Part 7: Troubleshooting](#part-7-troubleshooting)
- [Essential Commands Quick Reference](#essential-commands-quick-reference)

---

## Quick Reference: Which Part to Read

| If you need to... | Read this part |
|-------------------|----------------|
| See all active worktrees | [Part 1: Listing](#part-1-listing-and-switching-worktrees) |
| Work in a different worktree | [Part 1: Switching](#part-1-listing-and-switching-worktrees) |
| Get latest changes from remote | [Part 2: Updating](#part-2-updating-worktrees) |
| Handle rebase conflicts | [Part 2: Conflicts](#part-2-updating-worktrees) |
| Protect worktree from deletion | [Part 3: Locking](#part-3-locking-and-moving-worktrees) |
| Relocate a worktree | [Part 3: Moving](#part-3-locking-and-moving-worktrees) |
| Check worktree state | [Part 4: Status](#part-4-checking-worktree-status) |
| Incorporate main branch changes | [Part 5: Syncing](#part-5-syncing-with-main-branch) |
| Learn worktree management guidelines | [Part 6: Best Practices](#part-6-best-practices) |
| Fix worktree operation problems | [Part 7: Troubleshooting](#part-7-troubleshooting) |

---

## Part 1: Listing and Switching Worktrees

**File**: [worktree-operations-part1-listing-switching.md](worktree-operations-part1-listing-switching.md)

### Table of Contents
1. **Listing Worktrees** - When you need to see all active worktrees
   - 1.1 Basic Listing (`git worktree list`)
   - 1.2 Machine-Readable Listing (`git worktree list --porcelain`)
   - 1.3 Field Definitions (worktree, HEAD, branch, locked, prunable)
   - 1.4 When to Use Porcelain Format

2. **Switching Between Worktrees** - If you need to work in a different worktree
   - 2.1 How Switching Works
   - 2.2 Method 1: Using cd (Change Directory)
   - 2.3 Method 2: Using Absolute Paths
   - 2.4 Method 3: Creating Shell Aliases for Quick Switching
   - 2.5 Method 4: Using CDPATH Environment Variable
   - 2.6 Important Notes (independence, terminal sessions, isolation)

---

## Part 2: Updating Worktrees

**File**: [worktree-operations-part2-updating.md](worktree-operations-part2-updating.md)

### Table of Contents
1. **Phase 1: Pulling Latest Changes from Remote**
   - 1.1 What Pulling Does
   - 1.2 Command and Example
   - 1.3 Understanding Fast-forward

2. **Phase 2: Rebasing on Main Branch**
   - 2.1 What Rebasing Does
   - 2.2 Why Rebase Instead of Merge
   - 2.3 Step-by-Step Example

3. **Phase 3: Handling Rebase Conflicts**
   - 3.1 When Conflicts Occur
   - 3.2 Conflict Resolution Steps (5 steps)
   - 3.3 Alternative: Aborting the Rebase

4. **Phase 4: Pushing Updated Branch**
   - 4.1 Why `--force-with-lease` Instead of `--force`
   - 4.2 Example and Output

---

## Part 3: Locking and Moving Worktrees

**File**: [worktree-operations-part3-locking-moving.md](worktree-operations-part3-locking-moving.md)

### Table of Contents
1. **Locking and Unlocking Worktrees** - If you need to protect a worktree from deletion
   - 1.1 What Locking Does (and Does NOT Do)
   - 1.2 Locking a Worktree (basic and with reason)
   - 1.3 Unlocking a Worktree
   - 1.4 Checking Lock Status (two methods)
   - 1.5 Common Use Cases (active work, removable drive, shared team)

2. **Moving Worktrees** - When you need to relocate a worktree
   - 2.1 What Moving Does (and Does NOT Do)
   - 2.2 Basic Move Command
   - 2.3 Moving Locked Worktrees (unlock first)
   - 2.4 Common Move Scenarios (reorganizing, faster drive, renaming)
   - 2.5 Verifying Successful Move

---

## Part 4: Checking Worktree Status

**File**: [worktree-operations-part4-status.md](worktree-operations-part4-status.md)

### Table of Contents
1. **Phase 1: Basic Status Check**
   - 1.1 Command: `git status`
   - 1.2 Output When Clean
   - 1.3 Output With Changes
   - 1.4 Interpreting the Output

2. **Phase 2: Checking Modified Files in Detail**
   - 2.1 Command: `git diff`
   - 2.2 Reading the Diff
   - 2.3 Command: `git diff --staged`

3. **Phase 3: Checking Commit Status**
   - 3.1 Command: `git log --oneline -5`
   - 3.2 Reading the Output
   - 3.3 Command: `git show <hash>`

4. **Phase 4: Checking Upstream Tracking**
   - 4.1 Command: `git branch -vv`
   - 4.2 Reading the Output (ahead, behind, in sync)

5. **Phase 5: Checking If Pull Needed**
   - 5.1 Commands: `git fetch` + `git status`
   - 5.2 Output If Behind Remote
   - 5.3 Output If Diverged

6. **Summary Commands Table**
   - Quick reference table for all status commands

---

## Part 5: Syncing with Main Branch

**File**: [worktree-operations-part5-syncing.md](worktree-operations-part5-syncing.md)

### Table of Contents
1. **Why Sync Regularly**
   - 1.1 Benefits of Regular Syncing
   - 1.2 Recommended Frequency

2. **Phase 1: Fetch Latest Main**
   - 2.1 What Fetching Does
   - 2.2 Command and Output
   - 2.3 Understanding the Output

3. **Phase 2: Verify Current State**
   - 3.1 Check for Uncommitted Changes
   - 3.2 Option A: Commit Them
   - 3.3 Option B: Stash Them

4. **Phase 3: Rebase on Origin/Main**
   - 4.1 Command and Example
   - 4.2 What Happened (4 steps)

5. **Phase 4: Handling Rebase Conflicts (If They Occur)**
   - 5.1 Conflict Detection Output
   - 5.2 Step 1: Identify Conflicted Files
   - 5.3 Step 2: Open and Resolve Conflicts
   - 5.4 Step 3: Mark as Resolved
   - 5.5 Step 4: Continue Rebase
   - 5.6 Step 5: Repeat if More Conflicts

6. **Phase 5: Force Push Updated Branch**
   - 6.1 Why Force Push is Needed
   - 6.2 Safe Force Push Command
   - 6.3 Why `--force-with-lease`

7. **Phase 6: If You Stashed Changes Earlier**
   - 7.1 Restore Stashed Changes
   - 7.2 If Stash Conflicts with Rebased Code

8. **Complete Sync Workflow Example**
   - Full step-by-step script

---

## Part 6: Best Practices

**File**: [worktree-operations-part6-best-practices.md](worktree-operations-part6-best-practices.md)

### Table of Contents
1. **Practice 1: Keep Worktrees Updated**
   - Why and How
   - Automation script

2. **Practice 2: Clean Working Tree Before Switching**
   - Why and How (commit or stash)

3. **Practice 3: Use Meaningful Worktree Names**
   - Bad Names vs Good Names
   - Naming Convention Recommendation

4. **Practice 4: Lock Worktrees When In Active Use**
   - Why and When to Lock
   - How to Lock/Unlock

5. **Practice 5: Remove Completed Worktrees Promptly**
   - Why, When, and How

6. **Practice 6: Prune Stale Worktrees Regularly**
   - Why and How

7. **Practice 7: Document Worktree Purpose**
   - Method 1: Lock Reason
   - Method 2: README in Worktree
   - Method 3: Branch Naming

---

## Part 7: Troubleshooting

**File**: [worktree-operations-part7-troubleshooting.md](worktree-operations-part7-troubleshooting.md)

### Table of Contents
1. **Problem 1: Cannot Remove Worktree (Locked)**
   - Error and Solution

2. **Problem 2: Worktree Path Already Exists**
   - Error and Two Solutions

3. **Problem 3: Cannot Rebase (Uncommitted Changes)**
   - Error and Two Solutions

4. **Problem 4: Force Push Rejected (--force-with-lease)**
   - Error, What Happened, and Solution (4 steps)

5. **Problem 5: Worktree List Shows Deleted Directory**
   - Symptom, What Happened, and Solution

6. **Problem 6: Cannot Move Worktree (Path Does Not Exist)**
   - Error and Solution

7. **Problem 7: Rebase Conflicts Too Complex**
   - Symptom and Two Solutions

8. **Problem 8: Forgot Which Worktree Contains Which Work**
   - Solution: Search All Worktrees script

9. **Problem 9: Disk Space Running Low**
   - Solutions: Find Large Worktrees, Remove Old Worktrees

10. **Problem 10: Branch Not Tracking Remote**
    - Symptom, Solution, and Verification

---

## Essential Commands Quick Reference

| Operation | Command |
|-----------|---------|
| List worktrees | `git worktree list` |
| List worktrees (machine format) | `git worktree list --porcelain` |
| Create worktree | `git worktree add <path> <branch>` |
| Remove worktree | `git worktree remove <path>` |
| Lock worktree | `git worktree lock <path> --reason "reason"` |
| Unlock worktree | `git worktree unlock <path>` |
| Move worktree | `git worktree move <old-path> <new-path>` |
| Prune stale worktrees | `git worktree prune` |
| Check status | `git status` |
| Fetch updates | `git fetch origin` |
| Rebase on main | `git rebase origin/main` |
| Force push safely | `git push --force-with-lease origin <branch>` |

---

## End of Index

Navigate to the specific part files for detailed instructions and examples.
