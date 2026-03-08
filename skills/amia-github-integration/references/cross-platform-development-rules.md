---
name: cross-platform-development-rules
description: "Cross-platform development rules for quality gate enforcement covering encoding, paths, line endings, and platform testing."
---

# Cross-Platform Development Rules

## Table of Contents

- 1. When to Apply These Rules
  - 1.1 Projects that require cross-platform support
  - 1.2 How the integrator agent enforces these rules during review
- 1. UTF-8 Encoding Rules
  - 2.1 Why encoding must be specified explicitly
  - 2.2 Python pitfall: JSON file operations without encoding
  - 2.3 Python pitfall: Path.read_text() without encoding
  - 2.4 Python pitfall: subprocess output decoding
  - 2.5 Node.js and other languages
- 1. Path Handling Rules
  - 3.1 Why hardcoded path separators break cross-platform code
  - 3.2 Correct path construction in Python
  - 3.3 Correct path construction in JavaScript and TypeScript
  - 3.4 Correct path construction in Go and Rust
- 1. Line Ending Rules
  - 4.1 CRLF versus LF and why it matters
  - 4.2 Configuring .gitattributes for consistent line endings
  - 4.3 Normalizing line endings in application code
- 1. Shell Command Rules
  - 5.1 Why shell commands should be avoided in cross-platform code
  - 5.2 Python alternatives to common shell commands
  - 5.3 Platform detection patterns
- 1. Common Windows-Specific Issues
  - 6.1 File locking and context managers
  - 6.2 Maximum path length (260 characters)
  - 6.3 Case-insensitive filesystem behavior
  - 6.4 Reserved filenames on Windows
- 1. Platform-Specific Test Patterns
  - 7.1 Skipping tests by platform
  - 7.2 Parameterizing tests for platform differences
- 1. AMIA Review Checklist for Cross-Platform Code
  - 8.1 What to check in every pull request
  - 8.2 Red flags that indicate platform-specific bugs

---

## 1. When to Apply These Rules

### 1.1 Projects that require cross-platform support

These rules apply to any project that runs on more than one operating system. This includes:

- CLI tools distributed to Windows, macOS, and Linux users
- Libraries published to package registries (PyPI, npm, crates.io) where consumers run any OS
- Desktop applications targeting multiple platforms
- CI pipelines that run on multiple OS runners

### 1.2 How the integrator agent enforces these rules during review

During pull request review, the integrator agent checks for violations of these rules. Each rule has a specific code pattern to search for (documented in section 8). When a violation is found, the integrator requests changes with a reference to the specific rule and a corrected code example.

---

## 2. UTF-8 Encoding Rules

### 2.1 Why encoding must be specified explicitly

On Windows, Python's `open()` function defaults to the system encoding, which is typically `cp1252` (Windows-1252), not UTF-8. On macOS and Linux, the default is usually UTF-8. This means code that works on macOS or Linux can silently corrupt data on Windows if encoding is not specified.

The rule: ALWAYS specify `encoding="utf-8"` for ALL text file operations, without exception.

### 2.2 Python pitfall: JSON file operations without encoding

Wrong:

```python
# This uses cp1252 on Windows, corrupting non-ASCII characters
with open("config.json") as f:
    config = json.load(f)

with open("output.json", "w") as f:
    json.dump(data, f)
```

Correct:

```python
# Explicit UTF-8 encoding works identically on all platforms
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
```

Note the `ensure_ascii=False` in `json.dump()`. Without it, Python escapes all non-ASCII characters to `\uXXXX` sequences, which is safe but produces less readable output.

### 2.3 Python pitfall: Path.read_text() without encoding

Wrong:

```python
from pathlib import Path

# Path.read_text() also uses system default encoding
content = Path("README.md").read_text()
```

Correct:

```python
from pathlib import Path

# Always pass encoding parameter
content = Path("README.md").read_text(encoding="utf-8")
Path("output.txt").write_text(content, encoding="utf-8")
```

### 2.4 Python pitfall: subprocess output decoding

Wrong:

```python
import subprocess

# subprocess output is bytes; .stdout with text=True uses system encoding
result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True)
print(result.stdout)
```

Correct:

```python
import subprocess

# Specify encoding for subprocess text mode
result = subprocess.run(
    ["git", "log", "--oneline"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)
print(result.stdout)
```

### 2.5 Node.js and other languages

In Node.js, `fs.readFileSync` defaults to returning a Buffer. When specifying encoding, use `"utf8"` (no hyphen):

```javascript
// Correct
const content = fs.readFileSync("config.json", "utf8");

// Also correct
const content = fs.readFileSync("config.json", { encoding: "utf8" });
```

In Go, strings are UTF-8 by default. In Rust, `String` is guaranteed UTF-8. These languages require less explicit encoding management, but be cautious when interfacing with Windows APIs that use UTF-16.

---

## 3. Path Handling Rules

### 3.1 Why hardcoded path separators break cross-platform code

Windows uses backslash (`\`) as the path separator. macOS and Linux use forward slash (`/`). Hardcoding either separator creates code that fails on the other platform.

### 3.2 Correct path construction in Python

Wrong:

```python
# Hardcoded forward slash -- fails on Windows in some contexts
config_path = home_dir + "/.config/myapp/settings.json"

# Hardcoded backslash -- fails on macOS and Linux
log_path = "C:\\Users\\name\\logs\\app.log"

# String concatenation with os.sep -- fragile and verbose
full_path = base + os.sep + "subdir" + os.sep + "file.txt"
```

Correct:

```python
from pathlib import Path

# pathlib handles separators automatically on all platforms
config_path = Path.home() / ".config" / "myapp" / "settings.json"

# os.path.join also works correctly
import os
config_path = os.path.join(os.path.expanduser("~"), ".config", "myapp", "settings.json")
```

### 3.3 Correct path construction in JavaScript and TypeScript

Wrong:

```javascript
const configPath = homeDir + "/.config/myapp/settings.json";
```

Correct:

```javascript
const path = require("path");
const os = require("os");

const configPath = path.join(os.homedir(), ".config", "myapp", "settings.json");
```

### 3.4 Correct path construction in Go and Rust

Go:

```go
import "path/filepath"

configPath := filepath.Join(homeDir, ".config", "myapp", "settings.json")
```

Rust:

```rust
use std::path::PathBuf;

let config_path: PathBuf = [home_dir, ".config", "myapp", "settings.json"]
    .iter()
    .collect();
```

---

## 4. Line Ending Rules

### 4.1 CRLF versus LF and why it matters

Windows uses CRLF (`\r\n`) for line endings. macOS and Linux use LF (`\n`). Mixed line endings in a repository cause noisy diffs, merge conflicts, and can break tools that expect consistent endings (such as shell scripts that must use LF).

### 4.2 Configuring .gitattributes for consistent line endings

Create a `.gitattributes` file in the repository root:

```
# Normalize all text files to LF in the repository, convert to OS-native on checkout
* text=auto

# Force LF for files that must have Unix-style endings
*.py text eol=lf
*.sh text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
*.json text eol=lf
*.md text eol=lf
*.toml text eol=lf

# Force CRLF for Windows-specific files
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf

# Binary files -- never normalize
*.png binary
*.jpg binary
*.gif binary
*.ico binary
*.zip binary
*.tar.gz binary
*.woff binary
*.woff2 binary
```

### 4.3 Normalizing line endings in application code

When reading text from external sources (user input, network, files from other systems), normalize line endings:

Python:

```python
# Normalize any line ending style to LF
normalized = "\n".join(content.splitlines())
```

JavaScript:

```javascript
// Normalize any line ending style to LF
const normalized = content.replace(/\r\n/g, "\n");
```

---

## 5. Shell Command Rules

### 5.1 Why shell commands should be avoided in cross-platform code

Shell commands like `cp`, `rm`, `mv`, `ls`, `grep`, and `cat` do not exist on Windows (unless a Unix compatibility layer is installed). Even when Windows equivalents exist (`copy`, `del`, `move`, `dir`), their syntax and behavior differ.

The rule: Use language-native libraries for file operations instead of spawning shell commands.

### 5.2 Python alternatives to common shell commands

| Shell Command | Python Alternative |
|--------------|-------------------|
| `cp file1 file2` | `shutil.copy2("file1", "file2")` |
| `cp -r dir1 dir2` | `shutil.copytree("dir1", "dir2")` |
| `rm file` | `os.remove("file")` or `Path("file").unlink()` |
| `rm -rf dir` | `shutil.rmtree("dir")` |
| `mv file1 file2` | `shutil.move("file1", "file2")` |
| `mkdir -p dir` | `os.makedirs("dir", exist_ok=True)` or `Path("dir").mkdir(parents=True, exist_ok=True)` |
| `ls dir` | `os.listdir("dir")` or `list(Path("dir").iterdir())` |
| `cat file` | `Path("file").read_text(encoding="utf-8")` |
| `which program` | `shutil.which("program")` |

### 5.3 Platform detection patterns

When platform-specific code is unavoidable:

```python
import sys

if sys.platform == "win32":
    # Windows-specific code
    config_dir = Path(os.environ["APPDATA"]) / "myapp"
elif sys.platform == "darwin":
    # macOS-specific code
    config_dir = Path.home() / "Library" / "Application Support" / "myapp"
else:
    # Linux and other Unix-like systems
    config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "myapp"
```

---

## 6. Common Windows-Specific Issues

### 6.1 File locking and context managers

Windows locks files that are open by a process. Other processes cannot delete, rename, or write to a locked file. This is different from Unix systems where files can be deleted while open.

Always use context managers to ensure files are closed promptly:

```python
# Correct: file is closed when the with-block exits
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)
# File is now closed and can be deleted or renamed

# Wrong: file remains open until garbage collection
f = open("data.json", encoding="utf-8")
data = json.load(f)
# File is still locked on Windows
```

### 6.2 Maximum path length (260 characters)

Windows has a default maximum path length of 260 characters (`MAX_PATH`). Deeply nested directories or long filenames can exceed this limit.

Mitigations:

- Keep directory nesting shallow
- Use short but descriptive names
- On Windows 10+, the limit can be raised via a registry setting or by using the `\\?\` path prefix, but do not rely on this for distributed software

### 6.3 Case-insensitive filesystem behavior

Windows and macOS (by default) treat `File.txt` and `file.txt` as the same file. Linux treats them as different files. This can cause:

- Tests that pass on Linux but fail on Windows/macOS (or vice versa)
- Git tracking two files that differ only in case, causing checkout errors on Windows

Rule: Never create two files that differ only in case within the same directory.

### 6.4 Reserved filenames on Windows

Windows reserves certain filenames regardless of extension: `CON`, `PRN`, `AUX`, `NUL`, `COM1`-`COM9`, `LPT1`-`LPT9`.

These cannot be used as file or directory names:

```
CON.txt       <-- invalid on Windows
aux.json      <-- invalid on Windows
NUL           <-- invalid on Windows
```

---

## 7. Platform-Specific Test Patterns

### 7.1 Skipping tests by platform

Python (pytest):

```python
import sys
import pytest

@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
def test_windows_registry_access():
    """Verify registry key can be read on Windows."""
    import winreg
    # test implementation

@pytest.mark.skipif(sys.platform == "win32", reason="Unix-only test")
def test_unix_file_permissions():
    """Verify file permission bits are set correctly on Unix."""
    import stat
    # test implementation
```

### 7.2 Parameterizing tests for platform differences

```python
import pytest
import sys

@pytest.mark.parametrize("path_input,expected", [
    pytest.param("a/b/c", "a/b/c", marks=pytest.mark.skipif(sys.platform == "win32", reason="Unix path")),
    pytest.param("a\\b\\c", "a\\b\\c", marks=pytest.mark.skipif(sys.platform != "win32", reason="Windows path")),
])
def test_path_normalization(path_input, expected):
    """Verify path normalization produces platform-correct separators."""
    from pathlib import Path
    assert str(Path(path_input)) == expected
```

---

## 8. AMIA Review Checklist for Cross-Platform Code

### 8.1 What to check in every pull request

When reviewing code that may run on multiple platforms, check for:

| Check | What to Look For | Grep Pattern |
|-------|-----------------|--------------|
| Encoding in open() | Missing `encoding=` parameter | `open(` without `encoding` |
| Encoding in read_text() | Missing encoding parameter | `.read_text()` without arguments |
| Encoding in subprocess | Missing encoding in text mode | `text=True` without `encoding` |
| Path separators | Hardcoded `/` or `\\` in path construction | String concatenation with `/` for paths |
| Shell commands | `os.system()` or `subprocess` running shell commands | `os.system(`, `subprocess.run(["rm"` |
| Platform-specific imports | Unconditional import of platform-specific modules | `import winreg`, `import fcntl` |

### 8.2 Red flags that indicate platform-specific bugs

- Any use of `os.system()` -- this spawns a shell and is inherently platform-specific
- Paths constructed with string formatting or f-strings containing `/`
- `subprocess.run()` with `shell=True` -- shell syntax differs between platforms
- `os.chmod()` with Unix-specific permission bits (no effect on Windows)
- Hardcoded paths like `/tmp/`, `/usr/local/`, or `C:\\`
- Use of `os.symlink()` without handling Windows permission requirements
