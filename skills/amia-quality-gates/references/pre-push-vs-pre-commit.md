---
name: pre-push-vs-pre-commit
description: "Why pre-push hooks are preferred over pre-commit hooks for development workflow efficiency."
---

# Pre-Push vs Pre-Commit Hook Strategy

## Table of Contents

- 1. When to choose pre-push hooks over pre-commit hooks for quality gates
  - 1.1. The core philosophy: commits are local, pushes are social
  - 1.2. Comparison table: pre-commit versus pre-push trade-offs
  - 1.3. Impact on developer flow state and productivity
- 2. When pre-commit hooks ARE the right choice
  - 2.1. Critical security checks that must run on every commit
  - 2.2. File encoding enforcement to prevent cross-platform corruption
  - 2.3. Credential and secret scanning before any local history is created
- 3. Recommended hybrid strategy: minimal pre-commit plus comprehensive pre-push
  - 3.1. What belongs in pre-commit (fast, critical, non-negotiable)
  - 3.2. What belongs in pre-push (thorough, batch-processed, quality-focused)
  - 3.3. How pre-push integrates with CI as defense-in-depth
- 4. Common objections and counterarguments
  - 4.1. Addressing the "but broken commits pollute history" concern
  - 4.2. Addressing the "developers will forget to push" concern
  - 4.3. Addressing the "CI catches everything anyway" concern

---

## 1. When to choose pre-push hooks over pre-commit hooks for quality gates

### 1.1. The core philosophy: commits are local, pushes are social

A commit is a local checkpoint. It is cheap, private, and reversible. Developers should commit frequently -- every time they reach a stable micro-state, every time they want to checkpoint before a risky change, every time they context-switch. Frequent commits enable:

- Safe experimentation (revert to last commit if things go wrong)
- Fine-grained history for debugging with `git bisect`
- Work-in-progress saves that prevent data loss
- Rapid context switching between branches

A push is a social act. It shares code with the team, triggers CI pipelines, and updates remote branches. The quality bar for pushing should be higher than for committing, because a push has consequences beyond the individual developer.

Pre-commit hooks that run linters, formatters, type checkers, or test suites impose the quality bar of sharing onto the act of saving. This is like requiring a full manuscript review every time an author saves a paragraph. It destroys flow state and encourages bad habits (large, infrequent commits, or liberal use of `--no-verify`).

Pre-push hooks impose the quality bar at the right moment: when the developer has decided their work is ready to share.

### 1.2. Comparison table: pre-commit versus pre-push trade-offs

| Aspect | Pre-commit | Pre-push |
|--------|-----------|----------|
| When it runs | Every single commit | Only before push |
| Developer friction | High -- blocks frequent saves | Low -- blocks only when sharing |
| Feedback timing | Immediate but causes frequent interruptions | Batched at push time |
| Partial/WIP work | Blocked -- cannot commit incomplete code | Allowed -- commit freely, validate before sharing |
| Squash workflow compatibility | Problematic -- every intermediate commit must pass all checks | Natural -- only the final squashed state matters |
| CI minutes consumed | None (runs locally) | None (runs locally) |
| Risk of --no-verify bypass | High -- developers bypass frequently to avoid friction | Lower -- developers are about to share, so motivation to pass is higher |
| Time cost per day (typical) | 30-120 seconds per commit multiplied by 20-50 commits = 10-100 minutes | 30-120 seconds per push multiplied by 3-8 pushes = 1.5-16 minutes |
| Suitability for monorepos | Poor -- even small commits trigger full checks | Better -- checks run less frequently, can be more thorough |
| Interactive rebase compatibility | Painful -- every replayed commit triggers hooks | No impact -- rebase is local, push validates final result |

### 1.3. Impact on developer flow state and productivity

Research on developer productivity consistently shows that interruptions are the primary destroyer of flow state. A pre-commit hook that takes even 10 seconds creates a context switch: the developer stops thinking about the next change and starts waiting for validation. If the hook fails, they must fix the issue before they can save their checkpoint, which means they lose the mental model of what they were about to do next.

Pre-push hooks consolidate this interruption into a single batch at the natural boundary of "I am done with this unit of work." The developer expects to wait at push time. The cost is amortized, and the interruption is planned rather than unexpected.

---

## 2. When pre-commit hooks ARE the right choice

### 2.1. Critical security checks that must run on every commit

Credential scanning (detecting accidentally committed API keys, passwords, private keys, or tokens) should run on every commit because:

- Even a local commit with credentials creates risk if the repository is later shared, cloned, or backed up
- `git log` and `git reflog` retain committed secrets even after they are removed in subsequent commits
- The cost of scanning for credential patterns is typically under 1 second, so friction is negligible

Example pre-commit credential check:

```sh
#!/bin/sh
# Scan staged files for common credential patterns
staged_files=$(git diff --cached --name-only --diff-filter=ACM)
if [ -z "$staged_files" ]; then
  exit 0
fi

# Pattern matches common secret formats
echo "$staged_files" | xargs grep -lnE \
  '(AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----|sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|password\s*=\s*["\x27][^"\x27]{8,})' \
  2>/dev/null

if [ $? -eq 0 ]; then
  echo ""
  echo "ERROR: Potential credentials detected in staged files."
  echo "Review the matches above and remove secrets before committing."
  echo "If these are false positives, use: git commit --no-verify"
  exit 1
fi

exit 0
```

### 2.2. File encoding enforcement to prevent cross-platform corruption

Encoding checks are appropriate for pre-commit because:

- A file saved with wrong encoding (for example, cp1252 instead of utf-8) causes immediate problems for any team member on a different platform
- The check is instantaneous (read first few bytes of each file)
- Fixing encoding later requires rewriting history or accepting corrupted files in the log

### 2.3. Credential and secret scanning before any local history is created

Tools like `gitleaks`, `detect-secrets`, or `trufflehog` should be configured as pre-commit hooks. Their execution time is typically under 2 seconds for staged files only, which is within the acceptable friction threshold.

---

## 3. Recommended hybrid strategy: minimal pre-commit plus comprehensive pre-push

### 3.1. What belongs in pre-commit (fast, critical, non-negotiable)

Pre-commit hooks should complete in under 3 seconds total. Include only:

1. **Credential/secret scanning** -- Pattern-based detection of API keys, tokens, passwords
2. **File encoding verification** -- Ensure all text files are valid UTF-8
3. **Large file prevention** -- Block files over a size threshold (for example, 5MB) from being committed
4. **Merge conflict marker detection** -- Ensure no `<<<<<<<`, `=======`, `>>>>>>>` markers remain

Nothing else. No linters, no formatters, no type checkers, no tests.

### 3.2. What belongs in pre-push (thorough, batch-processed, quality-focused)

Pre-push hooks can take 30-120 seconds. Include:

1. **Linting** -- Static analysis for code quality and style violations
2. **Formatting verification** -- Check that code matches the project formatter output
3. **Type checking** -- Static type analysis for typed languages
4. **Test suite** -- Run the full or targeted test suite
5. **Security audit** -- Dependency vulnerability scanning
6. **Build verification** -- Ensure the project compiles/builds without errors

The pre-push hook should run these checks in dependency order: fast checks first (lint, format) so that slow checks (tests, security audit) are skipped if fast checks fail.

### 3.3. How pre-push integrates with CI as defense-in-depth

Pre-push hooks and CI pipelines serve different roles:

| Layer | Purpose | Authority |
|-------|---------|-----------|
| Pre-push hook | Catch obvious issues locally before consuming CI resources | Advisory -- developer can bypass with `--no-verify` |
| CI pipeline | Authoritative quality gate that cannot be bypassed | Authoritative -- merge is blocked if CI fails |

Pre-push is defense-in-depth. It reduces CI failures by catching 80-90% of issues locally, saving CI minutes and reducing the feedback loop from "push, wait 5-15 minutes for CI, fix, push again" to "push blocked locally, fix in 30 seconds, push successfully."

Pre-push does NOT replace CI. CI runs in a clean environment, tests against multiple platforms, and cannot be bypassed. Pre-push is a convenience layer that makes the development cycle faster.

---

## 4. Common objections and counterarguments

### 4.1. Addressing the "but broken commits pollute history" concern

Broken intermediate commits are not visible after squash-merge or interactive rebase. Most modern workflows use squash-merge for pull requests, which means the individual commit history is collapsed into a single commit. The intermediate commits only exist in the feature branch, which is deleted after merge.

For projects that use linear history (no squash), the pre-push hook ensures that the pushed state is clean. Developers can use `git rebase -i` locally to clean up intermediate commits before pushing.

### 4.2. Addressing the "developers will forget to push" concern

This is not a hooks problem. Developers who forget to push will forget regardless of hook strategy. The solution is process (daily standups, PR review cadence) not tooling.

### 4.3. Addressing the "CI catches everything anyway" concern

CI catches everything, but slowly. A failed CI run means:

1. Developer pushes code (time zero)
2. CI queues the job (1-5 minutes)
3. CI runs checks (5-30 minutes)
4. Developer sees failure notification (variable -- could be hours if they context-switched)
5. Developer context-switches back to fix the issue
6. Developer pushes again, repeating the cycle

Pre-push catches the same issue at step 1, with a 30-120 second delay. The developer is still in context and fixes the issue immediately. Total time saved per failure: 15-60 minutes.
