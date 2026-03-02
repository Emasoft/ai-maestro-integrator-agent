---
name: cross-platform-hook-patterns
description: "Patterns for writing git hooks that work correctly on Linux, macOS, and Windows (Git Bash)."
---

# Cross-Platform Hook Patterns

## Table of Contents

- 1. Detecting and using virtual environments across platforms
  - 1.1. Unix virtual environment paths versus Windows virtual environment paths
  - 1.2. Writing a portable Python detection function
  - 1.3. Fallback to system Python when no virtual environment exists
- 2. Running linters and formatters only on staged files
  - 2.1. Extracting staged file paths filtered by extension
  - 2.2. Running a linter on only the staged files
  - 2.3. Re-staging files after an auto-formatter modifies them
- 3. Enforcing UTF-8 encoding in source files
  - 3.1. Why encoding enforcement matters for cross-platform teams
  - 3.2. Common Python encoding pitfalls and detection patterns
  - 3.3. Grep pattern to find files missing explicit encoding parameters
  - 3.4. Enforcing encoding in other languages
- 4. Line ending normalization across operating systems
  - 4.1. Configuring gitattributes for automatic line ending handling
  - 4.2. Detecting and fixing mixed line endings in a hook
  - 4.3. Python-based line ending normalization
- 5. Path handling that works on all platforms
  - 5.1. Never hardcode path separators
  - 5.2. Using POSIX paths in shell hooks
  - 5.3. Using pathlib in Python hook scripts
- 6. Shell portability: writing hooks that work in sh, bash, and Git Bash
  - 6.1. Using sh instead of bash for maximum compatibility
  - 6.2. Common bash-isms to avoid and their POSIX alternatives
  - 6.3. How Git Bash on Windows affects hook execution
- 7. Graceful dependency detection and tool availability checks
  - 7.1. Checking if a tool exists before running it
  - 7.2. Skipping checks when tools are missing without blocking the operation
  - 7.3. Providing installation instructions in skip messages

---

## 1. Detecting and using virtual environments across platforms

### 1.1. Unix virtual environment paths versus Windows virtual environment paths

Python virtual environments have different directory structures depending on the operating system:

| Component | Unix (Linux, macOS) | Windows |
|-----------|-------------------|---------|
| Python executable | `.venv/bin/python` | `.venv/Scripts/python.exe` |
| Pip executable | `.venv/bin/pip` | `.venv/Scripts/pip.exe` |
| Activate script | `.venv/bin/activate` | `.venv/Scripts/activate` |
| Site packages | `.venv/lib/python3.X/site-packages/` | `.venv/Lib/site-packages/` |

Note: On Windows with Git Bash (MSYS2), the Unix-style paths work because Git Bash translates them. However, hooks that call Python directly need the correct path.

### 1.2. Writing a portable Python detection function

```sh
# detect_python: find the best Python executable for this environment.
# Priority: virtual environment > uv-managed > system python3 > system python
detect_python() {
  # Check for Unix virtual environment
  if [ -x ".venv/bin/python" ]; then
    echo ".venv/bin/python"
    return 0
  fi

  # Check for Windows virtual environment (Git Bash on Windows)
  if [ -x ".venv/Scripts/python.exe" ]; then
    echo ".venv/Scripts/python.exe"
    return 0
  fi

  # Check for uv-managed Python
  if command -v uv >/dev/null 2>&1; then
    echo "uv run python"
    return 0
  fi

  # Fallback: system Python
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return 0
  fi

  if command -v python >/dev/null 2>&1; then
    echo "python"
    return 0
  fi

  echo ""
  return 1
}

# Usage in a hook:
PYTHON=$(detect_python)
if [ -z "$PYTHON" ]; then
  echo "WARNING: No Python interpreter found. Skipping Python checks."
  exit 0
fi

$PYTHON -m ruff check src/
```

### 1.3. Fallback to system Python when no virtual environment exists

When no virtual environment is detected, the hook should:

1. Use system Python if available
2. Warn the developer that checks may use different dependency versions
3. Never fail just because a virtual environment is missing

```sh
PYTHON=$(detect_python)
if echo "$PYTHON" | grep -q "venv"; then
  echo "Using virtual environment Python"
else
  echo "WARNING: No virtual environment found. Using system Python."
  echo "Results may differ from CI. Consider running: uv venv && uv sync"
fi
```

---

## 2. Running linters and formatters only on staged files

### 2.1. Extracting staged file paths filtered by extension

The `git diff --cached` command shows changes in the staging area (index). Use it to get only the files that will be committed:

```sh
# Get staged Python files (Added, Copied, or Modified -- not Deleted)
staged_py_files=$(git diff --cached --name-only --diff-filter=ACM -- '*.py')

# Get staged JavaScript/TypeScript files
staged_js_files=$(git diff --cached --name-only --diff-filter=ACM -- '*.js' '*.ts' '*.jsx' '*.tsx')

# Get staged Rust files
staged_rs_files=$(git diff --cached --name-only --diff-filter=ACM -- '*.rs')

# Get staged Go files
staged_go_files=$(git diff --cached --name-only --diff-filter=ACM -- '*.go')
```

The `--diff-filter=ACM` flag includes only:

- **A** = Added (new files)
- **C** = Copied
- **M** = Modified

It excludes:

- **D** = Deleted (cannot lint a deleted file)
- **R** = Renamed (the new name is shown as Added)

### 2.2. Running a linter on only the staged files

```sh
staged_py_files=$(git diff --cached --name-only --diff-filter=ACM -- '*.py')

if [ -z "$staged_py_files" ]; then
  echo "No staged Python files. Skipping Python lint."
else
  echo "Linting staged Python files..."
  # Pass the file list to the linter
  # Note: use printf to handle filenames with spaces correctly
  echo "$staged_py_files" | tr '\n' '\0' | xargs -0 ruff check
  if [ $? -ne 0 ]; then
    echo "FAILED: Python lint errors found in staged files."
    exit 1
  fi
fi
```

### 2.3. Re-staging files after an auto-formatter modifies them

If your pre-commit hook runs an auto-formatter (like `ruff format` or `prettier --write`), the formatted files are modified in the working directory but the staged versions are still the unformatted originals. You must re-add the formatted files to the staging area:

```sh
staged_py_files=$(git diff --cached --name-only --diff-filter=ACM -- '*.py')

if [ -n "$staged_py_files" ]; then
  echo "Formatting staged Python files..."
  echo "$staged_py_files" | tr '\n' '\0' | xargs -0 ruff format

  # Re-stage the formatted files so the commit includes the formatted versions
  echo "$staged_py_files" | tr '\n' '\0' | xargs -0 git add

  echo "Formatted files have been re-staged."
fi
```

**Important**: This pattern is only appropriate for pre-commit hooks, not pre-push hooks. Pre-push hooks should use `--check` mode (verify formatting without modifying files).

---

## 3. Enforcing UTF-8 encoding in source files

### 3.1. Why encoding enforcement matters for cross-platform teams

Python on Windows defaults to the system locale encoding, which is typically `cp1252` (Windows-1252) in Western locales. Python on Linux and macOS defaults to `utf-8`. This means:

- A Python script that calls `open("file.txt")` without specifying `encoding` will use `utf-8` on Linux/macOS but `cp1252` on Windows
- Files containing non-ASCII characters (accented letters, symbols, CJK characters) will be read differently on different platforms
- This causes `UnicodeDecodeError` at runtime, but only on one platform, making bugs difficult to reproduce

### 3.2. Common Python encoding pitfalls and detection patterns

| Pitfall | Code Pattern | Problem |
|---------|-------------|---------|
| `open()` without encoding | `open("file.txt", "r")` | Uses platform default encoding |
| `Path.read_text()` without encoding | `Path("file.txt").read_text()` | Uses platform default encoding |
| `subprocess.run()` output decoding | `subprocess.run(cmd, capture_output=True)` | stdout/stderr decoded with platform default |
| `json.load()` from file | `json.load(open("data.json"))` | Inherits open() encoding problem |
| `csv.reader()` from file | `csv.reader(open("data.csv"))` | Inherits open() encoding problem |

The correct patterns:

```python
# Correct: explicit encoding
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Correct: Path with encoding
content = Path("file.txt").read_text(encoding="utf-8")

# Correct: subprocess with encoding
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
```

### 3.3. Grep pattern to find files missing explicit encoding parameters

Use this pattern in a hook to detect `open()` calls without `encoding=`:

```sh
# Find Python files with open() calls that lack an encoding parameter
# This grep pattern matches: open( followed by anything that does NOT contain "encoding="
# before the closing parenthesis

staged_py_files=$(git diff --cached --name-only --diff-filter=ACM -- '*.py')

if [ -n "$staged_py_files" ]; then
  # Search for open() without encoding= on the same line
  # This is a heuristic -- multi-line open() calls may be missed
  violations=$(echo "$staged_py_files" | tr '\n' '\0' | \
    xargs -0 grep -nE 'open\([^)]*\)' | \
    grep -v 'encoding=' | \
    grep -v '#.*open' | \
    grep -v '^\s*#')

  if [ -n "$violations" ]; then
    echo "WARNING: Found open() calls without explicit encoding parameter:"
    echo "$violations"
    echo ""
    echo "Add encoding=\"utf-8\" to prevent cross-platform encoding issues."
    # Warn but do not block (this is a heuristic with possible false positives)
  fi
fi
```

### 3.4. Enforcing encoding in other languages

| Language | Issue | Solution |
|----------|-------|----------|
| Java | Source file encoding | Use `-encoding UTF-8` compiler flag; specify `StandardCharsets.UTF_8` for I/O |
| Go | Strings are UTF-8 by default | No action needed (Go strings are always valid UTF-8) |
| Rust | Strings are UTF-8 by default | No action needed (`String` type guarantees UTF-8) |
| JavaScript/Node.js | `fs.readFile` defaults to buffer | Use `fs.readFile(path, 'utf-8')` or `fs.readFile(path, { encoding: 'utf-8' })` |
| C/C++ | No standard string encoding | Use ICU or platform-specific APIs; document encoding expectations |

---

## 4. Line ending normalization across operating systems

### 4.1. Configuring gitattributes for automatic line ending handling

Create a `.gitattributes` file at the repository root:

```
# Default: auto-detect text files and normalize line endings
* text=auto

# Force LF for all source code files
*.py text eol=lf
*.js text eol=lf
*.ts text eol=lf
*.jsx text eol=lf
*.tsx text eol=lf
*.rs text eol=lf
*.go text eol=lf
*.java text eol=lf
*.c text eol=lf
*.h text eol=lf
*.cpp text eol=lf
*.hpp text eol=lf
*.sh text eol=lf
*.json text eol=lf
*.yaml text eol=lf
*.yml text eol=lf
*.toml text eol=lf
*.md text eol=lf
*.html text eol=lf
*.css text eol=lf

# Force CRLF for Windows-specific files
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf

# Binary files: do not normalize
*.png binary
*.jpg binary
*.gif binary
*.ico binary
*.woff binary
*.woff2 binary
*.ttf binary
*.eot binary
*.pdf binary
*.zip binary
*.tar.gz binary
```

The `text=auto` setting tells git to auto-detect text files. The `eol=lf` setting forces LF line endings in the repository (git converts to platform-native on checkout for Windows users if `core.autocrlf` is set).

### 4.2. Detecting and fixing mixed line endings in a hook

```sh
# Detect files with mixed line endings (both LF and CRLF in the same file)
staged_files=$(git diff --cached --name-only --diff-filter=ACM)

for file in $staged_files; do
  if [ -f "$file" ]; then
    # Count lines with CR (\r) -- if file has both CR and non-CR lines, it is mixed
    cr_lines=$(tr -cd '\r' < "$file" | wc -c | tr -d ' ')
    total_lines=$(wc -l < "$file" | tr -d ' ')

    if [ "$cr_lines" -gt 0 ] && [ "$cr_lines" -lt "$total_lines" ]; then
      echo "WARNING: Mixed line endings detected in: $file"
      echo "  CR lines: $cr_lines, Total lines: $total_lines"
    fi
  fi
done
```

### 4.3. Python-based line ending normalization

For hooks written in Python:

```python
import sys
from pathlib import Path

def normalize_line_endings(file_path: str) -> bool:
    """Normalize line endings to LF. Returns True if file was modified."""
    path = Path(file_path)
    content_bytes = path.read_bytes()

    # Replace CRLF with LF, then replace any remaining CR with LF
    normalized = content_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

    if normalized != content_bytes:
        path.write_bytes(normalized)
        return True
    return False
```

---

## 5. Path handling that works on all platforms

### 5.1. Never hardcode path separators

```sh
# WRONG: hardcoded forward slash
config_path="src/config/settings.py"

# CORRECT for shell hooks: forward slash works on all platforms in sh/bash/Git Bash
# Git Bash on Windows translates forward slashes automatically
config_path="src/config/settings.py"
# This is actually fine in shell scripts because Git Bash handles translation
```

In Python hook scripts:

```python
from pathlib import Path

# WRONG: hardcoded separator
config_path = "src/config/settings.py"

# CORRECT: use pathlib
config_path = Path("src") / "config" / "settings.py"
```

### 5.2. Using POSIX paths in shell hooks

Shell hooks run in `sh` or `bash` on Unix, and in Git Bash (MSYS2) on Windows. Git Bash translates POSIX-style paths (`/c/Users/...`) to Windows paths automatically. Therefore:

- Use forward slashes in all shell hook paths
- Use `$(pwd)` or `$PWD` for the current directory
- Use `$(dirname "$0")` to find the hook script's own directory

```sh
# Get the directory containing this hook script
hook_dir=$(dirname "$0")

# Construct path relative to hook directory
config_file="$hook_dir/../config/quality-rules.json"
```

### 5.3. Using pathlib in Python hook scripts

```python
from pathlib import Path

# Current directory (where git runs the hook)
project_root = Path.cwd()

# Construct paths portably
src_dir = project_root / "src"
test_dir = project_root / "tests"
config_file = project_root / ".config" / "rules.json"

# Check existence
if not src_dir.is_dir():
    print(f"WARNING: Source directory not found: {src_dir}")
```

---

## 6. Shell portability: writing hooks that work in sh, bash, and Git Bash

### 6.1. Using sh instead of bash for maximum compatibility

Always use `#!/bin/sh` as the shebang line for git hooks unless you specifically need bash features. The POSIX `sh` shell is available on every Unix-like system and is what Git Bash emulates on Windows.

```sh
#!/bin/sh
# This hook runs on Linux sh, macOS zsh (as sh), and Windows Git Bash
```

### 6.2. Common bash-isms to avoid and their POSIX alternatives

| Bash-ism (avoid in hooks) | POSIX Alternative | Explanation |
|---------------------------|-------------------|-------------|
| `[[ "$var" == "value" ]]` | `[ "$var" = "value" ]` | Double bracket is bash-only; single bracket with single `=` is POSIX |
| `[[ "$var" =~ regex ]]` | `echo "$var" \| grep -qE 'regex'` | Regex matching in test is bash-only; use grep instead |
| `${var,,}` (lowercase) | `echo "$var" \| tr '[:upper:]' '[:lower:]'` | Case conversion is bash 4+; use tr for portability |
| `${var^^}` (uppercase) | `echo "$var" \| tr '[:lower:]' '[:upper:]'` | Case conversion is bash 4+; use tr for portability |
| `array=(a b c)` | Use files or IFS-split strings | Arrays are bash-only; POSIX sh has no array support |
| `<(process substitution)` | Use temp files or pipes | Process substitution is bash-only |
| `source file` | `. file` | `source` is a bash alias for the POSIX `.` (dot) command |
| `$'string'` (ANSI-C quoting) | Use printf | ANSI-C quoting is bash-only |
| `((arithmetic))` | Use `$((arithmetic))` or `expr` | Double parentheses for arithmetic are bash-only; `$((...))` is POSIX |
| `local var` in functions | `local` is common but technically not POSIX | Most shells support it, but strict POSIX compliance requires omitting it |

### 6.3. How Git Bash on Windows affects hook execution

On Windows, git hooks run inside Git Bash (MSYS2 environment). Key behaviors:

- `/bin/sh` is available (it is Git Bash's built-in shell)
- Forward-slash paths work and are translated automatically
- Most common Unix utilities are available: `grep`, `sed`, `awk`, `tr`, `wc`, `xargs`, `find`
- `command -v` works for checking tool availability
- Python must be found via Windows PATH (not Unix-style `/usr/bin/python`)
- Line endings in the hook script itself must be LF (CRLF will cause `/bin/sh^M: bad interpreter` error)

To prevent the bad interpreter error, ensure your `.gitattributes` includes:

```
# Git hooks must always have LF line endings, even on Windows
*.sh text eol=lf
```

And hooks stored in the `hooks/` directory:

```
hooks/* text eol=lf
```

---

## 7. Graceful dependency detection and tool availability checks

### 7.1. Checking if a tool exists before running it

```sh
# Check if a command is available on PATH
if command -v ruff >/dev/null 2>&1; then
  echo "ruff is available"
else
  echo "ruff is not available"
fi
```

The `command -v` built-in is POSIX-compliant and works in `sh`, `bash`, `zsh`, and Git Bash. Do NOT use `which` (not POSIX, behaves differently across systems) or `type` (output format varies).

### 7.2. Skipping checks when tools are missing without blocking the operation

```sh
# Pattern: require-or-skip
require_tool() {
  tool_name="$1"
  install_hint="$2"

  if ! command -v "$tool_name" >/dev/null 2>&1; then
    echo "SKIP: $tool_name not found. Install with: $install_hint"
    return 1
  fi
  return 0
}

# Usage:
if require_tool "ruff" "pip install ruff"; then
  ruff check src/
fi

if require_tool "mypy" "pip install mypy"; then
  mypy src/
fi

if require_tool "eslint" "npm install -g eslint"; then
  eslint src/
fi
```

This pattern lets the hook continue with available tools instead of failing completely when one tool is missing.

### 7.3. Providing installation instructions in skip messages

When a tool is missing, the skip message should tell the developer exactly how to install it:

```sh
if ! command -v ruff >/dev/null 2>&1; then
  echo "============================================"
  echo "SKIP: ruff not installed"
  echo ""
  echo "To install ruff, run one of:"
  echo "  pip install ruff          (via pip)"
  echo "  uv pip install ruff       (via uv)"
  echo "  brew install ruff         (via Homebrew on macOS)"
  echo "  cargo install ruff        (via cargo, from source)"
  echo ""
  echo "After installation, re-run your git operation."
  echo "============================================"
fi
```

This saves the developer from having to search for installation instructions and reduces the chance they will simply bypass the hook with `--no-verify`.
