# Review Worktree Workflow

## Table of Contents

1. [When understanding review worktrees](#overview)
2. [When creating a review worktree](#setup)
3. [When reviewing PRs in isolated environment](#review-process)
4. [When removing review worktrees](#cleanup)
5. [When worktree workflow integrates with status changes](#integration-with-status-flow)
6. [When following worktree best practices](#best-practices)
7. [If worktree issues occur](#troubleshooting)
8. [When referencing related worktree documentation](#related-files)

## Overview

A review worktree is an isolated git workspace for reviewing PRs without disrupting your main development environment. The orchestrator uses worktrees to test PR changes in complete isolation before approving.

### When to Use Worktrees for Review

- **ALWAYS** when reviewing PRs that modify build configurations
- **ALWAYS** when reviewing PRs that change dependencies
- **ALWAYS** when PR requires running tests locally
- **RECOMMENDED** for any non-trivial PR review
- **OPTIONAL** for documentation-only changes

### Benefits

1. **Isolation**: Review code without affecting current work
2. **Clean state**: Fresh environment for accurate testing
3. **Parallel reviews**: Multiple worktrees for multiple PRs
4. **Easy cleanup**: Remove worktree after review, no trace left

## Setup

### Creating Review Worktree

```bash
# Navigate to repository root
cd /path/to/repo

# Create worktree for specific PR branch
git worktree add ../repo-review-pr-42 pr-branch-name

# OR create worktree and fetch PR branch in one step
git fetch origin pull/42/head:pr-42-review
git worktree add ../repo-review-pr-42 pr-42-review
```

### Directory Convention

```
projects/
├── my-repo/                  # Main working directory
├── my-repo-review-pr-42/     # Review worktree for PR #42
├── my-repo-review-pr-57/     # Review worktree for PR #57
└── my-repo-review-pr-63/     # Review worktree for PR #63
```

### Installing Dependencies in Worktree

```bash
cd ../repo-review-pr-42

# Python projects
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"

# Node.js projects
pnpm install

# Go projects
go mod download
```

## Review Process

### Step 1: Prepare Worktree

```bash
# Create worktree
git worktree add ../repo-review-pr-42 feature/new-auth

# Navigate to worktree
cd ../repo-review-pr-42

# Install dependencies
# (use appropriate commands for project type)
```

### Step 2: Run Tests in Isolation

```bash
# Run full test suite
pytest -v --cov=src

# Run specific tests related to PR changes
pytest tests/test_auth.py -v

# Run linting
ruff check src/ tests/
mypy src/
```

### Step 3: Manual Verification

- [ ] Application starts without errors
- [ ] Changed functionality works as expected
- [ ] No regressions in related features
- [ ] Performance is acceptable
- [ ] Security considerations addressed

### Step 4: Record Review Results

Document findings in PR review:

```markdown
## Review in Isolated Worktree

**Environment**: macOS 14.2 / Python 3.12.1
**Tests**: 47 passed, 0 failed, 2 skipped
**Coverage**: 87%

### Verification
- [x] All tests pass
- [x] Linting passes
- [x] Manual testing successful
- [x] No regressions found

### Notes
[Any observations or minor suggestions]
```

## Cleanup

### After Review Approval

```bash
# Remove worktree
git worktree remove ../repo-review-pr-42

# If worktree has uncommitted changes (shouldn't happen in review)
git worktree remove --force ../repo-review-pr-42

# Clean up tracking branch if created
git branch -D pr-42-review
```

### After Changes Requested

If review requested changes:

1. **Keep worktree** for re-review (optional)
2. **Or remove and recreate** when changes are pushed:

```bash
git worktree remove ../repo-review-pr-42
# Later, when changes pushed:
git worktree add ../repo-review-pr-42 feature/new-auth
```

### Worktree Management Commands

```bash
# List all worktrees
git worktree list

# Prune stale worktree references
git worktree prune

# Repair broken worktree links
git worktree repair
```

## Integration with Status Flow

### When Status Changes to "AI Review"

1. Orchestrator receives notification that PR is ready
2. Create review worktree:
   ```bash
   git worktree add ../repo-review-pr-{number} {branch}
   ```
3. Install dependencies in worktree
4. Run automated tests
5. Perform manual verification
6. Record results

### When Review Completes

#### If Approved (100% criteria pass)

1. Update status to "Done"
2. Remove review worktree:
   ```bash
   git worktree remove ../repo-review-pr-{number}
   ```
3. Merge PR

#### If Changes Requested

1. Update status back to "In Progress"
2. Either:
   - Keep worktree for quick re-review, OR
   - Remove worktree, recreate when changes ready
3. Add review feedback to PR
4. Wait for changes

### Multiple Concurrent Reviews

The orchestrator can review multiple PRs in parallel using separate worktrees:

```
repo-review-pr-42/  → Reviewing authentication changes
repo-review-pr-57/  → Reviewing API refactor
repo-review-pr-63/  → Reviewing database migrations
```

Each worktree is completely independent.

## Best Practices

### DO

- Use descriptive worktree directory names
- Clean up worktrees after reviews complete
- Run full test suite, not just changed tests
- Document worktree environment in review comments
- Keep worktrees for complex reviews (re-review likely)

### DON'T

- Make commits in review worktrees (read-only review)
- Leave worktrees indefinitely (cleanup after 7 days max)
- Share worktrees between reviewers
- Skip dependency installation (may miss build issues)

## Troubleshooting

### "fatal: is already checked out"

Branch is checked out in another worktree:
```bash
# Find which worktree has the branch
git worktree list

# Remove that worktree first, or use different branch name
git fetch origin pull/42/head:pr-42-review-v2
git worktree add ../repo-review-v2 pr-42-review-v2
```

### Worktree shows stale files

```bash
# Reset worktree to branch HEAD
cd ../repo-review-pr-42
git reset --hard HEAD
git clean -fd
```

### Dependencies fail to install

Review worktree should have same environment as CI:
```bash
# Check Python version matches CI
python --version

# Check Node version matches CI
node --version

# Ensure clean install
rm -rf node_modules .venv
# Reinstall
```

## Related Files

- `status-management.md` - Status transitions that trigger worktree operations
- `iteration-cycle-rules.md` - 100% approval requirement for reviews
- `../worktree-management/SKILL.md` - Full worktree management skill
