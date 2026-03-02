# Dependency CI Failure Patterns

## Table of Contents

- 4.1 Module Import Path Issues
  - 4.1.1 Relative path calculation
  - 4.1.2 Language-specific import resolution
  - 4.1.3 Working directory assumptions
- 4.2 Missing Dependencies in CI
  - 4.2.1 Lock file synchronization
  - 4.2.2 Optional dependencies
  - 4.2.3 Development vs production dependencies
- 4.3 Version Mismatches
  - 4.3.1 Pinned version conflicts
  - 4.3.2 Transitive dependency issues
  - 4.3.3 CI-specific version requirements

---

## 4.1 Module Import Path Issues

Module import failures are among the most common CI problems, especially when tests pass locally but fail in CI.

### 4.1.1 Relative Path Calculation

Relative imports depend on the current working directory and module structure.

**Python Relative Imports**:

```python
# Directory structure:
# project/
# ├── src/
# │   ├── __init__.py
# │   ├── main.py
# │   └── utils/
# │       ├── __init__.py
# │       └── helpers.py
# └── tests/
#     └── test_main.py

# In src/main.py - import from sibling package
from utils.helpers import my_function  # Works if src/ is in PYTHONPATH

# In tests/test_main.py - import from parent package
from src.main import main_function  # Requires src/ in PYTHONPATH
```

**Common CI Failure**: Import works locally (IDE adds paths) but fails in CI.

**Error Message**:
```
ModuleNotFoundError: No module named 'src'
```

**Fix 1**: Install package in development mode
```yaml
- name: Install package
  run: pip install -e .
```

**Fix 2**: Set PYTHONPATH explicitly
```yaml
- name: Run tests
  run: pytest
  env:
    PYTHONPATH: ${{ github.workspace }}/src
```

**Fix 3**: Use absolute imports with proper package structure
```python
# In pyproject.toml or setup.py, define package
# Then use: from mypackage.utils.helpers import my_function
```

### 4.1.2 Language-Specific Import Resolution

Each language resolves imports differently:

**Python Import Resolution Order**:
1. Built-in modules
2. Modules in `sys.path[0]` (script directory)
3. Installed packages (site-packages)
4. Paths in `PYTHONPATH` environment variable

**JavaScript/Node.js Resolution Order**:
1. Core modules (fs, path, etc.)
2. File path (if starts with `./`, `../`, or `/`)
3. `node_modules` folders (traversing up directory tree)

**Common CI Failure**: Module found locally but not in CI due to different directory structure.

**JavaScript Example**:
```javascript
// WRONG: Relies on specific directory structure
const config = require('../../../config');

// BETTER: Use path from project root
const path = require('path');
const config = require(path.join(process.cwd(), 'config'));

// BEST: Use package.json paths or tsconfig paths
```

**Go Import Resolution**:
```go
// Go uses module paths from go.mod
import "github.com/user/project/pkg/utils"

// Local imports (same module) use relative paths from module root
import "./internal/helpers"  // WRONG in modules
import "mymodule/internal/helpers"  // CORRECT
```

**Rust Import Resolution**:
```rust
// Crate-relative paths
use crate::utils::helpers;

// Module-relative paths
use super::sibling_module;
use self::child_module;
```

### 4.1.3 Working Directory Assumptions

Scripts often assume they run from a specific directory.

**Common CI Failure**: Script assumes it's run from project root.

**WRONG**:
```bash
# Assumes current directory is project root
python src/main.py
```

**CORRECT**:
```bash
# Use script's directory as reference
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python "$SCRIPT_DIR/../src/main.py"

# Or cd to known location first
cd "$GITHUB_WORKSPACE"
python src/main.py
```

**GitHub Actions Behavior**:
- `$GITHUB_WORKSPACE` is the repository root
- Each `run:` step starts in `$GITHUB_WORKSPACE` by default
- Use `working-directory:` to change

```yaml
- name: Run from subdirectory
  working-directory: ./src
  run: python main.py
```

---

## 4.2 Missing Dependencies in CI

### 4.2.1 Lock File Synchronization

Lock files ensure reproducible builds but cause CI failures when out of sync.

**Package Manager Lock Files**:

| Language | Lock File | Command to Sync |
|----------|-----------|-----------------|
| Python (pip) | `requirements.txt` | `pip freeze > requirements.txt` |
| Python (poetry) | `poetry.lock` | `poetry lock` |
| JavaScript | `package-lock.json` | `npm install` (regenerates) |
| JavaScript | `yarn.lock` | `yarn install` (regenerates) |
| JavaScript | `pnpm-lock.yaml` | `pnpm install` (regenerates) |
| Rust | `Cargo.lock` | `cargo update` |
| Go | `go.sum` | `go mod tidy` |

**Common CI Failure**: Lock file doesn't match package manifest.

**npm Error**:
```
npm ERR! `npm ci` can only install packages with an existing package-lock.json
```

**Solution**: Ensure lock files are committed and up to date
```yaml
- name: Verify lock file is in sync
  run: |
    npm ci
    git diff --exit-code package-lock.json
```

### 4.2.2 Optional Dependencies

Optional dependencies work locally but may be missing in CI.

**Python Optional Dependencies**:
```toml
# pyproject.toml
[project.optional-dependencies]
dev = ["pytest", "black"]
docs = ["sphinx"]
```

**CI Installation**:
```yaml
- name: Install with dev dependencies
  run: pip install -e ".[dev]"
```

**Common CI Failure**: Test dependency not installed.

**Error Message**:
```
ModuleNotFoundError: No module named 'pytest'
```

**JavaScript Optional Dependencies**:
```json
{
  "dependencies": {},
  "devDependencies": {
    "jest": "^29.0.0"
  },
  "optionalDependencies": {
    "fsevents": "^2.0.0"
  }
}
```

**CI Note**: `npm ci --omit=optional` skips optional dependencies.

### 4.2.3 Development vs Production Dependencies

**Common CI Failure**: Running tests without dev dependencies.

**Python Pattern**:
```yaml
# WRONG: Production dependencies only
- run: pip install .

# CORRECT: Include dev dependencies
- run: pip install -e ".[dev]"

# Or with requirements files
- run: |
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
```

**JavaScript Pattern**:
```yaml
# WRONG: Production only
- run: npm ci --omit=dev

# CORRECT: Include dev dependencies
- run: npm ci
```

**Rust Pattern**:
```yaml
# WRONG: Release mode might not include test deps
- run: cargo build --release

# CORRECT: Test with dev dependencies
- run: cargo test
```

---

## 4.3 Version Mismatches

### 4.3.1 Pinned Version Conflicts

Pinning versions prevents "works on my machine" but causes CI failures when pins conflict.

**Common CI Failure**: Dependency version conflict.

**pip Error**:
```
ERROR: Cannot install package-a and package-b because these package versions have conflicting dependencies.
```

**Resolution Strategies**:

1. **Find compatible versions**:
```bash
pip install package-a package-b --dry-run
```

2. **Use a constraint file**:
```
# constraints.txt
shared-dependency>=1.0,<2.0
```
```yaml
- run: pip install -c constraints.txt -r requirements.txt
```

3. **Loosen version pins**:
```
# WRONG: Too strict
numpy==1.21.0

# BETTER: Allow compatible versions
numpy>=1.21.0,<2.0.0
```

### 4.3.2 Transitive Dependency Issues

Transitive (indirect) dependencies can cause subtle CI failures.

**Problem**: Direct dependency updates, pulling incompatible transitive version.

**Detection**:
```bash
# Python: Show dependency tree
pip install pipdeptree
pipdeptree

# JavaScript: Show why package is installed
npm explain <package-name>

# Rust: Show dependency tree
cargo tree
```

**CI Fix**: Pin transitive dependencies explicitly
```yaml
- name: Install with pinned transitive deps
  run: |
    pip install -r requirements.txt
    # Add problematic transitive dep explicitly
    pip install problematic-package==1.2.3
```

### 4.3.3 CI-Specific Version Requirements

Some dependencies have CI-specific requirements.

**Platform-Specific Dependencies**:

```python
# setup.py or pyproject.toml
install_requires=[
    "pywin32; sys_platform == 'win32'",
    "fcntl; sys_platform != 'win32'",  # This would fail - fcntl is built-in
]
```

**CI Environment Matrix**:
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.9', '3.10', '3.11']

steps:
  - name: Install OS-specific deps
    if: matrix.os == 'ubuntu-latest'
    run: sudo apt-get install -y libfoo-dev
```

**Version Compatibility Matrix**:
```yaml
# Test against multiple versions
strategy:
  matrix:
    node: ['16', '18', '20']

steps:
  - uses: actions/setup-node@v4
    with:
      node-version: ${{ matrix.node }}
```

---

## Quick Reference: Dependency Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError` | Missing PYTHONPATH | Add `pip install -e .` or set PYTHONPATH |
| `Cannot find module` (JS) | node_modules not installed | Run `npm ci` |
| Lock file out of sync | Dependencies changed | Regenerate and commit lock file |
| Version conflict | Incompatible pins | Loosen version constraints |
| Works locally, fails CI | Dev deps missing | Install with dev dependencies |

---

## Summary: Dependency Checklist

Before committing CI workflows:

- [ ] Package installed in development mode (`pip install -e .`)
- [ ] Lock files committed and up to date
- [ ] Dev dependencies installed for tests
- [ ] Import paths work from repository root
- [ ] PYTHONPATH/NODE_PATH set if needed
- [ ] Platform-specific dependencies handled
- [ ] Version constraints allow CI environments
- [ ] Working directory assumptions documented
