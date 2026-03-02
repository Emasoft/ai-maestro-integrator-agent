# Cross-Platform Testing: Part 1 - Testing on Multiple Operating Systems

## Table of Contents

- 7.1.1 Platform categories and key differences
- 7.1.2 Common platform issues (file paths, line endings, permissions, case sensitivity)
- 7.1.3 Testing matrix dimensions
- 7.1.4 Platform detection in tests (Python and TypeScript)

---

## 7.1 Testing on Multiple Operating Systems

Applications targeting multiple platforms need comprehensive testing strategies.

### Platform Categories

| Category | Examples | Key Differences |
|----------|----------|-----------------|
| Desktop OS | Windows, macOS, Linux | File paths, line endings, permissions |
| Linux Distros | Ubuntu, Debian, Fedora, Alpine | Package managers, default tools |
| Architecture | x86_64, ARM64, i386 | Binary compatibility, performance |
| Runtime | Node.js version, Python version | API availability, behavior |

### Common Platform Issues

#### File Paths

```python
# Bad: Hardcoded separator
path = "data/files/config.json"

# Good: Use pathlib (Python) or path.join (Node.js)
from pathlib import Path
path = Path("data") / "files" / "config.json"

# JavaScript/TypeScript
import path from 'path';
const configPath = path.join('data', 'files', 'config.json');
```

#### Line Endings

```python
# Bad: Assumes Unix line endings
content = file.read()
lines = content.split('\n')

# Good: Universal newlines
with open(file, 'r', newline='') as f:
    lines = f.readlines()
```

#### File Permissions

```python
# File permissions work differently on Windows
import os
import stat

if os.name != 'nt':  # Not Windows
    os.chmod(script_path, stat.S_IRWXU)
```

#### Case Sensitivity

```python
# macOS and Windows: case-insensitive by default
# Linux: case-sensitive

# Problem: Two files with same name, different case
# Config.json and config.json

# Solution: Be consistent with case
```

### Testing Matrix Dimensions

When testing across platforms, consider these dimensions:

1. **Operating System**: Windows, macOS, Linux
2. **OS Version**: Latest, LTS, older supported
3. **Architecture**: x86_64, ARM64
4. **Runtime Version**: Multiple versions of Python, Node.js, etc.
5. **Dependencies**: With/without optional dependencies

### Platform Detection in Tests

```python
# Python
import sys
import platform

def is_windows():
    return sys.platform == 'win32'

def is_macos():
    return sys.platform == 'darwin'

def is_linux():
    return sys.platform.startswith('linux')

def get_arch():
    return platform.machine()  # 'x86_64', 'arm64', etc.
```

```typescript
// TypeScript/JavaScript
function isWindows(): boolean {
  return process.platform === 'win32';
}

function isMacOS(): boolean {
  return process.platform === 'darwin';
}

function isLinux(): boolean {
  return process.platform === 'linux';
}
```

---

**Next**: [Part 2 - CI Matrix Configuration](cross-platform-testing-part2-ci-matrix.md)
