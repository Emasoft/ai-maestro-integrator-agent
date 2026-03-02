---
name: op-configure-pre-push-hook
description: "Step-by-step procedure for installing and configuring a pre-push git hook with language-specific check examples."
---

# Operation: Configure a Pre-Push Git Hook

## Table of Contents

- 1. Understanding git hook basics before creating a pre-push hook
  - 1.1. Where git hooks live and how git discovers them
  - 1.2. How the pre-push hook receives push information via stdin
  - 1.3. How exit codes control whether the push proceeds or is blocked
- 2. Creating a pre-push hook from scratch
  - 2.1. Writing the hook shell script skeleton
  - 2.2. Making the hook executable
  - 2.3. Testing the hook locally before relying on it
- 3. Choosing which checks to include and in what order
  - 3.1. Ordering principle: fast checks first, slow checks last
  - 3.2. Fail-fast: stop on first failure to save time
- 4. Language-specific pre-push hook examples
  - 4.1. Python project pre-push hook (ruff, mypy, pytest, bandit)
  - 4.2. JavaScript and TypeScript project pre-push hook (eslint, prettier, tsc, vitest, npm audit)
  - 4.3. Rust project pre-push hook (clippy, cargo fmt, cargo test, cargo audit)
  - 4.4. Go project pre-push hook (golangci-lint, go vet, go test, govulncheck)
- 5. Making hooks team-wide and reproducible
  - 5.1. Storing hook scripts in the repository
  - 5.2. Using a Makefile target to install hooks
  - 5.3. Documenting the bypass procedure for emergencies
- 6. Performance optimization techniques
  - 6.1. Running independent checks in parallel
  - 6.2. Running checks only on changed files
  - 6.3. Caching results across runs

---

## 1. Understanding git hook basics before creating a pre-push hook

### 1.1. Where git hooks live and how git discovers them

Git hooks are executable scripts stored in the `.git/hooks/` directory of a repository. When git performs certain actions (commit, push, merge, rebase), it checks for a hook script with a specific name in that directory. If the script exists and is executable, git runs it.

The pre-push hook must be named exactly `pre-push` (no file extension) and must be located at `.git/hooks/pre-push`.

You can also configure a custom hooks directory with:

```sh
git config core.hooksPath ./hooks
```

This tells git to look for hooks in `./hooks/` instead of `.git/hooks/`. This is useful for storing hooks in version control (since `.git/` is not tracked).

### 1.2. How the pre-push hook receives push information via stdin

When git invokes the pre-push hook, it passes:

- **Argument 1**: The name of the remote (for example, `origin`)
- **Argument 2**: The URL of the remote

Additionally, git sends information about each ref being pushed via **standard input**, one line per ref, in this format:

```
<local_ref> <local_sha> <remote_ref> <remote_sha>
```

For example:

```
refs/heads/feature-branch abc1234def5678 refs/heads/feature-branch 0000000000000000
```

A remote SHA of all zeros indicates a new branch (no existing remote ref).

### 1.3. How exit codes control whether the push proceeds or is blocked

- **Exit code 0**: All checks passed. Git proceeds with the push.
- **Any non-zero exit code**: Checks failed. Git aborts the push and displays the hook's stderr/stdout output to the developer.

---

## 2. Creating a pre-push hook from scratch

### 2.1. Writing the hook shell script skeleton

Create the file `.git/hooks/pre-push` with the following content:

```sh
#!/bin/sh
#
# Pre-push hook: runs quality checks before allowing a push.
# Exit 0 to allow the push, exit non-zero to block it.
#
# Arguments:
#   $1 = remote name (e.g., "origin")
#   $2 = remote URL
#
# Stdin: lines of "<local_ref> <local_sha> <remote_ref> <remote_sha>"

remote="$1"
url="$2"

# Safety: unset environment variables that can misdirect git operations
unset GIT_DIR
unset GIT_WORK_TREE

echo "=== Pre-push quality checks ==="
echo "Remote: $remote ($url)"
echo ""

# Track overall pass/fail status
exit_code=0

# --- Check 1: Lint ---
echo "[1/5] Running lint checks..."
# Replace with your lint command
if ! your_lint_command; then
  echo "FAILED: Lint checks did not pass."
  exit_code=1
fi

# Fail fast: stop if previous check failed
if [ "$exit_code" -ne 0 ]; then
  echo ""
  echo "Pre-push checks FAILED. Push blocked."
  exit "$exit_code"
fi

# --- Check 2: Format ---
echo "[2/5] Running format checks..."
# Replace with your format check command
if ! your_format_check_command; then
  echo "FAILED: Format checks did not pass."
  exit_code=1
fi

if [ "$exit_code" -ne 0 ]; then
  echo ""
  echo "Pre-push checks FAILED. Push blocked."
  exit "$exit_code"
fi

# Continue pattern for remaining checks...

echo ""
echo "All pre-push checks PASSED. Proceeding with push."
exit 0
```

### 2.2. Making the hook executable

On Unix-like systems (Linux, macOS):

```sh
chmod +x .git/hooks/pre-push
```

On Windows, if using Git Bash (MSYS2), the same command works. If using PowerShell, the executable bit is not relevant -- git for Windows handles this automatically.

### 2.3. Testing the hook locally before relying on it

Test the hook without actually pushing by running it directly:

```sh
echo "refs/heads/main abc123 refs/heads/main 000000" | .git/hooks/pre-push origin https://github.com/user/repo.git
```

Check the exit code:

```sh
echo $?
```

If the exit code is 0, the hook would allow the push. If non-zero, it would block it.

---

## 3. Choosing which checks to include and in what order

### 3.1. Ordering principle: fast checks first, slow checks last

Run checks in this order to minimize wasted time:

| Order | Check | Typical Duration | Why This Order |
|-------|-------|-----------------|----------------|
| 1 | Lint | 2-10 seconds | Catches most issues fastest |
| 2 | Format verification | 1-5 seconds | Nearly instant, catches style issues |
| 3 | Type checking | 5-30 seconds | Catches type errors before running tests |
| 4 | Test suite | 10-300 seconds | Most thorough but slowest |
| 5 | Security/dependency audit | 5-60 seconds | Important but not blocking for most pushes |

### 3.2. Fail-fast: stop on first failure to save time

If lint fails, there is no point running the test suite. Each check should exit immediately if a previous check failed. This is implemented in the skeleton above with the repeated `if [ "$exit_code" -ne 0 ]` blocks.

---

## 4. Language-specific pre-push hook examples

### 4.1. Python project pre-push hook (ruff, mypy, pytest, bandit)

```sh
#!/bin/sh
unset GIT_DIR
unset GIT_WORK_TREE

echo "=== Python pre-push checks ==="

# Detect virtual environment
if [ -f ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
  PYTHON=".venv/Scripts/python.exe"
else
  PYTHON="python3"
fi

run_check() {
  step_number="$1"
  total_steps="$2"
  label="$3"
  shift 3
  echo "[$step_number/$total_steps] $label"
  if ! "$@"; then
    echo "FAILED: $label"
    exit 1
  fi
}

run_check 1 5 "Linting with ruff..."       $PYTHON -m ruff check src/ tests/
run_check 2 5 "Checking formatting..."      $PYTHON -m ruff format --check src/ tests/
run_check 3 5 "Type checking with mypy..."  $PYTHON -m mypy src/
run_check 4 5 "Running test suite..."       $PYTHON -m pytest tests/ -q --tb=short
run_check 5 5 "Security scan with bandit..." $PYTHON -m bandit -r src/ -q

echo ""
echo "All checks PASSED."
exit 0
```

### 4.2. JavaScript and TypeScript project pre-push hook (eslint, prettier, tsc, vitest, npm audit)

```sh
#!/bin/sh
unset GIT_DIR
unset GIT_WORK_TREE

echo "=== JavaScript/TypeScript pre-push checks ==="

# Detect package manager
if command -v bun >/dev/null 2>&1 && [ -f "bun.lockb" ]; then
  RUNNER="bun run"
elif command -v pnpm >/dev/null 2>&1 && [ -f "pnpm-lock.yaml" ]; then
  RUNNER="pnpm exec"
else
  RUNNER="npx"
fi

run_check() {
  step_number="$1"
  total_steps="$2"
  label="$3"
  shift 3
  echo "[$step_number/$total_steps] $label"
  if ! "$@"; then
    echo "FAILED: $label"
    exit 1
  fi
}

run_check 1 5 "Linting with eslint..."         $RUNNER eslint src/
run_check 2 5 "Checking formatting..."          $RUNNER prettier --check "src/**/*.{ts,tsx,js,jsx}"
run_check 3 5 "Type checking with tsc..."       $RUNNER tsc --noEmit
run_check 4 5 "Running test suite..."           $RUNNER vitest run --reporter=verbose
run_check 5 5 "Auditing dependencies..."        npm audit --audit-level=high

echo ""
echo "All checks PASSED."
exit 0
```

### 4.3. Rust project pre-push hook (clippy, cargo fmt, cargo test, cargo audit)

```sh
#!/bin/sh
unset GIT_DIR
unset GIT_WORK_TREE

echo "=== Rust pre-push checks ==="

run_check() {
  step_number="$1"
  total_steps="$2"
  label="$3"
  shift 3
  echo "[$step_number/$total_steps] $label"
  if ! "$@"; then
    echo "FAILED: $label"
    exit 1
  fi
}

run_check 1 4 "Linting with clippy..."     cargo clippy -- -D warnings
run_check 2 4 "Checking formatting..."      cargo fmt --check
run_check 3 4 "Running test suite..."       cargo test --quiet
run_check 4 4 "Auditing dependencies..."    cargo audit

echo ""
echo "All checks PASSED."
exit 0
```

### 4.4. Go project pre-push hook (golangci-lint, go vet, go test, govulncheck)

```sh
#!/bin/sh
unset GIT_DIR
unset GIT_WORK_TREE

echo "=== Go pre-push checks ==="

run_check() {
  step_number="$1"
  total_steps="$2"
  label="$3"
  shift 3
  echo "[$step_number/$total_steps] $label"
  if ! "$@"; then
    echo "FAILED: $label"
    exit 1
  fi
}

run_check 1 4 "Linting with golangci-lint..."  golangci-lint run ./...
run_check 2 4 "Running go vet..."              go vet ./...
run_check 3 4 "Running test suite..."          go test ./... -count=1
run_check 4 4 "Vulnerability check..."         govulncheck ./...

echo ""
echo "All checks PASSED."
exit 0
```

---

## 5. Making hooks team-wide and reproducible

### 5.1. Storing hook scripts in the repository

Store hook scripts in a tracked directory, for example `hooks/` or `scripts/git-hooks/`:

```
project-root/
  hooks/
    pre-push
    commit-msg
    pre-commit
  Makefile
```

### 5.2. Using a Makefile target to install hooks

```makefile
.PHONY: install-hooks
install-hooks:
	@echo "Installing git hooks..."
	@cp hooks/* .git/hooks/
	@chmod +x .git/hooks/*
	@echo "Git hooks installed."
```

Developers run `make install-hooks` after cloning. Alternatively, use `core.hooksPath`:

```makefile
.PHONY: install-hooks
install-hooks:
	git config core.hooksPath ./hooks
	@echo "Git hooks path set to ./hooks/"
```

### 5.3. Documenting the bypass procedure for emergencies

Include in your project README or CONTRIBUTING guide:

```
To bypass pre-push hooks in an emergency:
  git push --no-verify

This should ONLY be used when:
- CI is the authoritative check and you need to push a hotfix immediately
- The hook itself is broken and you have verified the code manually
- You are pushing to a draft/WIP branch that will not be merged

Document the reason for bypass in the commit message or PR description.
```

---

## 6. Performance optimization techniques

### 6.1. Running independent checks in parallel

If your shell supports background processes, run independent checks concurrently:

```sh
#!/bin/sh
unset GIT_DIR
unset GIT_WORK_TREE

echo "=== Running checks in parallel ==="

# Start independent checks in background
ruff check src/ tests/ > /tmp/prepush-lint.log 2>&1 &
pid_lint=$!

ruff format --check src/ tests/ > /tmp/prepush-fmt.log 2>&1 &
pid_fmt=$!

# Wait for both and check results
wait $pid_lint
lint_result=$?

wait $pid_fmt
fmt_result=$?

# Report results
if [ "$lint_result" -ne 0 ]; then
  echo "FAILED: Lint"
  cat /tmp/prepush-lint.log
fi

if [ "$fmt_result" -ne 0 ]; then
  echo "FAILED: Format"
  cat /tmp/prepush-fmt.log
fi

if [ "$lint_result" -ne 0 ] || [ "$fmt_result" -ne 0 ]; then
  exit 1
fi

# Sequential checks that depend on the above passing
echo "Running tests..."
pytest tests/ -q --tb=short || exit 1

echo "All checks PASSED."
exit 0
```

### 6.2. Running checks only on changed files

Determine which files changed between the local branch and the remote tracking branch:

```sh
# Files changed compared to the remote branch
changed_files=$(git diff --name-only "origin/$(git branch --show-current)" HEAD -- '*.py' 2>/dev/null)

if [ -z "$changed_files" ]; then
  echo "No Python files changed. Skipping Python checks."
  exit 0
fi

echo "Checking changed files:"
echo "$changed_files"

# Run lint only on changed files
echo "$changed_files" | xargs ruff check
```

### 6.3. Caching results across runs

Some tools support incremental or cached runs:

- **mypy**: Uses `.mypy_cache/` automatically for incremental checking
- **ruff**: Fast enough that caching is rarely needed
- **pytest**: Use `pytest-cache` plugin with `--last-failed` to rerun only failed tests
- **cargo**: Uses `target/` directory for incremental compilation

Do not clear these cache directories in your hook scripts. Let the tools manage their own caches.
