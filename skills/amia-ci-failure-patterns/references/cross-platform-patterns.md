# Cross-Platform CI Failure Patterns

## Table of Contents

- 1.1 Temporary Path Differences
  - 1.1.1 Windows temp path handling ($env:TEMP)
  - 1.1.2 Linux/macOS temp path handling (/tmp, $TMPDIR)
  - 1.1.3 Language-specific solutions (Python, JavaScript, Bash, PowerShell)
- 1.2 Path Separator Differences
  - 1.2.1 Forward slash vs backslash behavior
  - 1.2.2 Path normalization techniques
  - 1.2.3 Platform-agnostic path construction
- 1.3 Line Ending Differences
  - 1.3.1 CRLF vs LF detection
  - 1.3.2 Git autocrlf configuration
  - 1.3.3 Fixing line ending issues in CI
- 1.4 Case Sensitivity Differences
  - 1.4.1 Filesystem case sensitivity by platform
  - 1.4.2 Common case-related CI failures
  - 1.4.3 Enforcing consistent casing

---

## 1.1 Temporary Path Differences

Temporary file paths are a major source of cross-platform CI failures. Each operating system uses different conventions and environment variables for temporary directories.

### 1.1.1 Windows Temp Path Handling

Windows uses multiple environment variables for temp paths:

| Variable | Typical Value | Notes |
|----------|---------------|-------|
| `$env:TEMP` | `C:\Users\runner\AppData\Local\Temp` | User temp directory |
| `$env:TMP` | Same as TEMP | Alternative variable |
| `$env:RUNNER_TEMP` | `D:\a\_temp` | GitHub Actions specific |

**Common CI Failure**: Hardcoding `/tmp` in code that runs on Windows.

**Error Message Example**:
```
FileNotFoundError: [WinError 3] The system cannot find the path specified: '/tmp/myfile.txt'
```

**PowerShell Solution**:
```powershell
# Get system temp directory
$tempDir = [System.IO.Path]::GetTempPath()
$tempFile = Join-Path $tempDir "myfile.txt"

# Alternative using environment variable
$tempDir = $env:TEMP
```

### 1.1.2 Linux/macOS Temp Path Handling

Linux and macOS use POSIX-style temp paths:

| Platform | Default Temp Path | Environment Variable |
|----------|-------------------|---------------------|
| Linux | `/tmp` | `$TMPDIR` (often unset) |
| macOS | `/var/folders/...` | `$TMPDIR` |
| GitHub Actions Linux | `/tmp` | `$RUNNER_TEMP` |
| GitHub Actions macOS | `/tmp` | `$RUNNER_TEMP` |

**Common CI Failure**: Assuming `$TMPDIR` is always set.

**Bash Solution**:
```bash
# Use TMPDIR if set, otherwise fall back to /tmp
TEMP_DIR="${TMPDIR:-/tmp}"
TEMP_FILE="$TEMP_DIR/myfile.txt"
```

### 1.1.3 Language-Specific Solutions

#### Python

```python
import tempfile
import os

# CORRECT: Platform-agnostic temp directory
temp_dir = tempfile.gettempdir()
temp_file = os.path.join(temp_dir, "myfile.txt")

# CORRECT: Create temp file automatically
with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
    temp_path = f.name
    f.write(b"content")

# WRONG: Hardcoded path
temp_file = "/tmp/myfile.txt"  # Fails on Windows
```

#### JavaScript (Node.js)

```javascript
const os = require('os');
const path = require('path');

// CORRECT: Platform-agnostic temp directory
const tempDir = os.tmpdir();
const tempFile = path.join(tempDir, 'myfile.txt');

// WRONG: Hardcoded path
const tempFile = '/tmp/myfile.txt';  // Fails on Windows
```

#### Bash

```bash
# CORRECT: Use mktemp for portable temp files
TEMP_FILE=$(mktemp)
TEMP_DIR=$(mktemp -d)

# CORRECT: Fallback pattern
TEMP_DIR="${TMPDIR:-${TMP:-/tmp}}"

# WRONG: Hardcoded path without fallback
TEMP_FILE="/tmp/myfile.txt"  # May fail if /tmp doesn't exist
```

#### PowerShell

```powershell
# CORRECT: Use .NET method
$tempDir = [System.IO.Path]::GetTempPath()
$tempFile = [System.IO.Path]::GetTempFileName()

# CORRECT: Join paths properly
$tempFile = Join-Path $tempDir "myfile.txt"

# WRONG: Unix-style path
$tempFile = "/tmp/myfile.txt"  # Fails on Windows
```

---

## 1.2 Path Separator Differences

Path separators cause subtle bugs that only appear on specific platforms.

### 1.2.1 Forward Slash vs Backslash Behavior

| Platform | Native Separator | Accepts Forward Slash |
|----------|------------------|----------------------|
| Windows | `\` | Yes (in most contexts) |
| Linux | `/` | Yes |
| macOS | `/` | Yes |

**Key Insight**: Windows often accepts forward slashes, but not always. Some Windows APIs and tools require backslashes.

**Common CI Failure**: Building a path with backslashes that fails on Linux.

**Error Message Example**:
```
Error: ENOENT: no such file or directory, open 'src\config\settings.json'
```

### 1.2.2 Path Normalization Techniques

#### Python

```python
import os
from pathlib import Path

# CORRECT: os.path.join handles separators
config_path = os.path.join("src", "config", "settings.json")

# CORRECT: pathlib is even better
config_path = Path("src") / "config" / "settings.json"

# CORRECT: Normalize mixed separators
normalized = os.path.normpath("src\\config/settings.json")

# WRONG: Hardcoded separator
config_path = "src\\config\\settings.json"  # Fails on Linux
config_path = "src/config/settings.json"    # Usually works but inconsistent
```

#### JavaScript (Node.js)

```javascript
const path = require('path');

// CORRECT: path.join handles separators
const configPath = path.join('src', 'config', 'settings.json');

// CORRECT: Normalize mixed separators
const normalized = path.normalize('src\\config/settings.json');

// WRONG: Hardcoded separator
const configPath = 'src\\config\\settings.json';  // Fails on Linux
```

#### Bash

```bash
# Bash always uses forward slashes, safe for Linux/macOS
config_path="src/config/settings.json"

# For Windows Git Bash, convert paths
windows_path=$(cygpath -w "$config_path")
```

### 1.2.3 Platform-Agnostic Path Construction

**Best Practice**: Always use language-provided path joining functions.

| Language | Function | Example |
|----------|----------|---------|
| Python | `os.path.join()` | `os.path.join("a", "b")` |
| Python | `pathlib.Path` | `Path("a") / "b"` |
| JavaScript | `path.join()` | `path.join("a", "b")` |
| Go | `filepath.Join()` | `filepath.Join("a", "b")` |
| Rust | `Path::new().join()` | `Path::new("a").join("b")` |

---

## 1.3 Line Ending Differences

Line endings cause CI failures when files are modified during checkout or when string comparisons fail.

### 1.3.1 CRLF vs LF Detection

| Platform | Default Line Ending | Bytes |
|----------|---------------------|-------|
| Windows | CRLF | `\r\n` (0x0D 0x0A) |
| Linux | LF | `\n` (0x0A) |
| macOS | LF | `\n` (0x0A) |

**Common CI Failure**: Git converts line endings on checkout, causing file hash mismatches or test failures.

**Error Message Example**:
```
AssertionError: 'expected content\n' != 'expected content\r\n'
```

**Detection Commands**:
```bash
# Check line endings in a file
file myfile.txt
# Output: "myfile.txt: ASCII text, with CRLF line terminators"

# Count line ending types
cat -A myfile.txt | head -5
# ^M$ indicates CRLF, $ alone indicates LF
```

### 1.3.2 Git Autocrlf Configuration

Git's `core.autocrlf` setting controls line ending conversion:

| Setting | On Checkout (Windows) | On Commit |
|---------|----------------------|-----------|
| `true` | LF → CRLF | CRLF → LF |
| `input` | No change | CRLF → LF |
| `false` | No change | No change |

**GitHub Actions Default**: `autocrlf=false` on Linux/macOS, `autocrlf=true` on Windows.

**CI Fix**: Add `.gitattributes` to control line endings explicitly:

```gitattributes
# Force LF for all text files
* text=auto eol=lf

# Force specific file types
*.sh text eol=lf
*.bat text eol=crlf
*.ps1 text eol=crlf

# Binary files (no conversion)
*.png binary
*.jpg binary
```

### 1.3.3 Fixing Line Ending Issues in CI

**Step 1**: Add `.gitattributes` to repository

**Step 2**: Normalize existing files:
```bash
# Re-normalize all files
git add --renormalize .
git commit -m "Normalize line endings"
```

**Step 3**: In CI workflow, ensure consistent checkout:
```yaml
- uses: actions/checkout@v4
  with:
    # Preserve line endings as committed
    persist-credentials: false
```

**Python Fix**: Handle both line endings in tests:
```python
# Read file with universal newlines
with open("file.txt", "r", newline=None) as f:
    content = f.read()  # \r\n converted to \n

# Or explicitly normalize
content = content.replace("\r\n", "\n")
```

---

## 1.4 Case Sensitivity Differences

Filesystem case sensitivity causes "works on my machine" bugs.

### 1.4.1 Filesystem Case Sensitivity by Platform

| Platform | Filesystem | Case Sensitive | Notes |
|----------|------------|----------------|-------|
| Linux | ext4, xfs | Yes | `File.txt` ≠ `file.txt` |
| macOS | APFS | No (default) | `File.txt` = `file.txt` |
| Windows | NTFS | No | `File.txt` = `file.txt` |
| GitHub Actions Linux | ext4 | Yes | Case matters |
| GitHub Actions macOS | APFS | No | Case preserved |
| GitHub Actions Windows | NTFS | No | Case preserved |

### 1.4.2 Common Case-Related CI Failures

**Scenario 1**: Import with wrong case works locally but fails in CI.

```python
# File is named: MyModule.py

# WRONG: Works on macOS/Windows, fails on Linux
import mymodule  # ModuleNotFoundError on Linux

# CORRECT: Match exact case
import MyModule
```

**Scenario 2**: Git doesn't detect case-only renames.

```bash
# This rename might not be detected
mv MyFile.txt myfile.txt
git status  # May show no changes on case-insensitive filesystem
```

**Fix**: Use `git mv` with intermediate step:
```bash
git mv MyFile.txt myfile_temp.txt
git mv myfile_temp.txt myfile.txt
git commit -m "Rename MyFile.txt to myfile.txt"
```

### 1.4.3 Enforcing Consistent Casing

**Git Configuration**:
```bash
# Make Git aware of case changes
git config core.ignorecase false
```

**CI Check**: Add a workflow step to detect case issues:
```yaml
- name: Check for case conflicts
  run: |
    # Find duplicate files that differ only by case
    find . -type f | sort -f | uniq -di
```

**Linting**: Use language-specific tools:

```python
# Python: pylint can detect import case mismatches
# Enable import-error check

# JavaScript: ESLint can enforce consistent casing
# Use eslint-plugin-import with case-sensitive option
```

**Best Practice**: Use lowercase for all filenames:
- `my_module.py` instead of `MyModule.py`
- `config.json` instead of `Config.json`
- `readme.md` instead of `README.md` (if not required by convention)

---

## Summary: Cross-Platform Checklist

Before committing code that runs in CI, verify:

- [ ] Temp paths use language-provided functions (not hardcoded `/tmp`)
- [ ] File paths use `path.join()` or equivalent (no hardcoded separators)
- [ ] `.gitattributes` defines line ending policy
- [ ] File/module names use consistent casing
- [ ] Imports match exact file casing
- [ ] No case-only file renames without proper git handling
