# Creating Worktrees: Purpose-Specific Patterns

## Overview

Different types of worktrees have specific creation patterns optimized for their use case. This document covers the four main worktree types.

## Table of Contents

1. [Review Worktrees](#review-worktrees) - For reviewing Pull Requests
2. [Feature Worktrees](#feature-worktrees) - For developing new features
3. [Bugfix Worktrees](#bugfix-worktrees) - For fixing bugs linked to GitHub issues
4. [Testing Worktrees](#testing-worktrees) - For extensive tests and experiments

---

## Review Worktrees

**Purpose**: Review Pull Requests in isolation without affecting your main development environment.

**Naming**: `review-GH-{number}` where `{number}` is the GitHub PR number.

**Creation flow**:
```bash
# 1. Fetch latest from remote
git fetch origin

# 2. Create worktree from PR branch
git worktree add ../review-GH-42 origin/feature/new-auth

# 3. Navigate to worktree
cd ../review-GH-42

# 4. Install dependencies
npm install  # or: pip install -r requirements.txt, bundle install, etc.

# 5. Run tests
npm test

# 6. Start dev server with allocated ports
PORT=3002 npm start
```

**When to use review worktrees**:
- Yes: Reviewing PRs that require running the code
- Yes: Testing PRs for bugs or regressions
- Yes: Verifying PR functionality before merge
- No: Simple typo fixes or documentation PRs (just review on GitHub)

**Best practices**:
- Always create from the PR's remote branch, not a local copy
- Test thoroughly before approving PR
- Clean up review worktree after PR is merged/closed
- Document review findings in GitHub PR comments

---

## Feature Worktrees

**Purpose**: Develop new features in isolation from main development.

**Naming**: `feature-{name}` where `{name}` is a short, descriptive feature name using kebab-case.

**Creation flow**:
```bash
# 1. Create worktree with new branch
git worktree add ../feature-user-profiles -b feature/user-profiles

# 2. Navigate to worktree
cd ../feature-user-profiles

# 3. Setup environment
cp ../main-repo/.env.example .env
npm install

# 4. Allocate ports and update .env
echo "PORT=3002" >> .env
echo "API_PORT=3003" >> .env

# 5. Create feature branch on remote (optional, for backup)
git push -u origin feature/user-profiles
```

**When to use feature worktrees**:
- Yes: Large features that take multiple days/weeks
- Yes: Features that need to run alongside main dev environment
- Yes: Experimental features you want to keep separate
- No: Small, quick features (just use main repo)

**Best practices**:
- Create feature worktrees for significant work only
- Keep feature branch updated with main regularly
- Run full test suite before merging
- Clean up worktree after feature is merged

---

## Bugfix Worktrees

**Purpose**: Fix bugs in isolation, especially when linked to GitHub issues.

**Naming**: `bugfix-GH-{number}-{desc}` where:
- `{number}`: GitHub issue number
- `{desc}`: Short bug description (1-2 words, kebab-case)

**Creation flow**:
```bash
# 1. Identify base branch (usually main or a release branch)
git fetch origin

# 2. Create worktree from base branch
git worktree add ../bugfix-GH-55-crash -b bugfix/crash-on-login origin/main

# 3. Navigate to worktree
cd ../bugfix-GH-55-crash

# 4. Setup environment
npm install

# 5. Reproduce bug first
npm test -- test/login.test.js  # Run specific test that shows bug

# 6. Fix bug, verify fix
# ... make changes ...
npm test  # Verify fix
```

**When to use bugfix worktrees**:
- Yes: Bugs that require running the application
- Yes: Bugs that might take multiple sessions to fix
- Yes: Bugs that need testing against production-like data
- No: Trivial bugs (typos, simple logic errors) - fix in main repo

**Best practices**:
- Always reproduce the bug first before fixing
- Write regression test before fixing
- Verify fix with tests
- Link commits to GitHub issue

---

## Testing Worktrees

**Purpose**: Run extensive tests, experiments, or performance benchmarks without affecting main environment.

**Naming**: `test-{type}-{target}` where:
- `{type}`: Type of testing (integration, e2e, performance, load, etc.)
- `{target}`: What's being tested

**Creation flow**:
```bash
# 1. Create worktree from appropriate branch
git worktree add ../test-integration-api -b test/integration-api

# 2. Navigate to worktree
cd ../test-integration-api

# 3. Setup test environment
npm install
npm install --save-dev additional-test-tools  # if needed

# 4. Configure test database/services
cp .env.example .env.test
echo "DATABASE_URL=postgresql://localhost:5433/test_db" >> .env.test
echo "PORT=3004" >> .env.test

# 5. Run tests
npm run test:integration
```

**When to use testing worktrees**:
- Yes: Long-running test suites
- Yes: Performance/load testing
- Yes: Testing that requires specific environment setup
- Yes: Destructive tests (database migrations, etc.)
- No: Quick unit tests (run in main repo)

**Best practices**:
- Use separate test databases
- Allocate different ports
- Document test results in GitHub issue or PR
- Clean up test data after completion

---

## Summary Table

| Type | Naming Pattern | Primary Use Case |
|------|----------------|------------------|
| Review | `review-GH-{number}` | Testing PRs before merge |
| Feature | `feature-{name}` | Long-running feature development |
| Bugfix | `bugfix-GH-{number}-{desc}` | Bug fixes linked to issues |
| Testing | `test-{type}-{target}` | Integration, e2e, performance tests |

---

## Related Documentation

- [Standard Creation Flow](./creating-worktrees-part1-standard-flow.md)
- [Port Allocation Strategy](./creating-worktrees-part3-port-allocation.md)
- [Environment Setup](./creating-worktrees-part4-environment-setup.md)
- [Commands Reference and Checklist](./creating-worktrees-part5-commands-checklist.md)
- [Troubleshooting](./creating-worktrees-part6-troubleshooting.md)
