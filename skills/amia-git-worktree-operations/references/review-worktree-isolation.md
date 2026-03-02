# Review Worktree Isolation

## Table of Contents

1. [When you need to understand worktree isolation for reviews → Purpose](#purpose)
2. [If you need the fundamental isolation rule → Core Rule](#core-rule)
3. [When you need to set up a review worktree → Worktree Setup for Review](#worktree-setup-for-review)
   - [If you're creating the review worktree → Step 1: Create Review Worktree](#step-1-create-review-worktree)
   - [When you need to ensure clean state → Step 2: Verify Clean State](#step-2-verify-clean-state)
   - [If you need to run tests in isolation → Step 3: Run Tests in Isolation](#step-3-run-tests-in-isolation)
   - [When you're reviewing the code → Step 4: Review Code](#step-4-review-code)
   - [If you need to document findings → Step 5: Document Review](#step-5-document-review)
   - [When you're done reviewing → Step 6: Cleanup](#step-6-cleanup)
4. [If you need to understand why isolation is important → Why Isolation Matters](#why-isolation-matters)
5. [When you need to name review worktrees → Worktree Naming Convention](#worktree-naming-convention)
6. [If you're managing multiple reviews → Multiple Concurrent Reviews](#multiple-concurrent-reviews)
7. [When you need to understand the review lifecycle → Review Worktree Lifecycle](#review-worktree-lifecycle)
8. [If you need to integrate with review protocols → Integration with Review Protocol](#integration-with-review-protocol)

## Purpose

All code reviews MUST happen in isolated git worktrees to prevent review contamination and ensure clean testing environments.

## Core Rule

**NEVER review code in the main working directory.**

Every review gets its own worktree.

## Worktree Setup for Review

### Step 1: Create Review Worktree

```bash
# Create worktree for PR review
git worktree add ../review-GH-42 origin/feature/GH-42-auth

# Navigate to review worktree
cd ../review-GH-42
```

### Step 2: Verify Clean State

```bash
# Ensure no local modifications
git status
# Should show: "nothing to commit, working tree clean"

# Verify correct branch
git branch --show-current
# Should show: feature/GH-42-auth
```

### Step 3: Run Tests in Isolation

```bash
# Install dependencies fresh
uv pip install -e ".[dev]" --system

# Run full test suite
pytest --tb=short

# Run linting
ruff check src/ tests/

# Run type checking
mypy src/
```

### Step 4: Review Code

Perform code review in this isolated environment:
- Read changed files
- Verify functionality
- Check edge cases
- Test manually if needed

### Step 5: Document Review

```bash
# Write review notes
cat > review-notes.md << 'EOF'
## Review: GH-42 - User Authentication

### Tests
- All 45 tests pass
- Coverage: 87%

### Issues Found
1. Missing input validation in login endpoint
2. JWT expiry not configurable

### Verdict: CHANGES REQUESTED
EOF
```

### Step 6: Cleanup

After review complete:

```bash
# Return to main directory
cd ../main-project

# Remove review worktree
git worktree remove ../review-GH-42
```

## Why Isolation Matters

| Problem | Caused By | Prevented By |
|---------|-----------|--------------|
| Stale dependencies | Main dir has old packages | Fresh install in worktree |
| Uncommitted changes | Mixed with reviewed code | Clean worktree |
| Wrong branch | Forgot to switch | Dedicated worktree per PR |
| Test pollution | Cached test artifacts | Fresh environment |

## Worktree Naming Convention

```
../review-{ISSUE_NUMBER}
```

Examples:
- `../review-GH-42`
- `../review-GH-123`
- `../review-hotfix-auth`

## Multiple Concurrent Reviews

```bash
# Review multiple PRs simultaneously
git worktree add ../review-GH-42 origin/feature/GH-42-auth
git worktree add ../review-GH-45 origin/feature/GH-45-api
git worktree add ../review-GH-48 origin/bugfix/GH-48-crash

# List active review worktrees
git worktree list
```

## Review Worktree Lifecycle

```
PR Created → Create Worktree → Run Tests → Review Code →
Document Findings → Remove Worktree (if rejected) OR
Keep Until Merge → Remove After Merge
```

## Integration with Review Protocol

1. Reviewer receives PR notification
2. Reviewer creates review worktree
3. Reviewer runs all checks in worktree
4. Reviewer writes review in worktree
5. Reviewer submits review via GitHub
6. IF changes requested: keep worktree for re-review
7. IF approved and merged: remove worktree
