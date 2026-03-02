# Language-Specific CI Failure Patterns

## Table of Contents

- 6.1 Python CI Patterns
  - 6.1.1 Virtual environment issues
  - 6.1.2 pip installation failures
  - 6.1.3 pytest configuration issues
- 6.2 JavaScript/TypeScript CI Patterns
  - 6.2.1 node_modules caching issues
  - 6.2.2 npm vs yarn vs pnpm differences
  - 6.2.3 ESM vs CommonJS issues
- 6.3 Rust CI Patterns
  - 6.3.1 cargo build failures
  - 6.3.2 Target directory management
  - 6.3.3 Cross-compilation issues
- 6.4 Go CI Patterns
  - 6.4.1 Module resolution issues
  - 6.4.2 Go version mismatches
  - 6.4.3 CGO dependencies

---

## 6.1 Python CI Patterns

### 6.1.1 Virtual Environment Issues

**Common CI Failure**: Wrong Python or package version used.

**Symptom**: Tests pass locally but fail in CI with import errors.

**Root Cause**: System Python used instead of virtual environment.

**Solution**: Always use setup-python and virtual environments

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

**Using venv explicitly**:
```yaml
- name: Create and activate venv
  run: |
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate   # Windows
    pip install -r requirements.txt
```

**Using uv (faster)**:
```yaml
- name: Install with uv
  run: |
    pip install uv
    uv venv
    uv pip install -r requirements.txt
```

### 6.1.2 pip Installation Failures

**Common CI Failure**: Package fails to build from source.

**Error Message**:
```
error: Microsoft Visual C++ 14.0 or greater is required
```
or
```
error: command 'gcc' failed with exit code 1
```

**Root Cause**: Package requires compilation but build tools missing.

**Solution for Linux**:
```yaml
- name: Install build dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y build-essential python3-dev
```

**Solution for Windows**:
```yaml
- name: Install Visual Studio Build Tools
  run: |
    choco install visualstudio2019buildtools
```

**Better Solution**: Use pre-built wheels
```yaml
- name: Install with pre-built wheels
  run: |
    pip install --only-binary :all: numpy pandas
```

**Common CI Failure**: Hash mismatch.

**Error Message**:
```
HASH MISMATCH: Expected sha256:xxx got sha256:yyy
```

**Solution**: Clear pip cache
```yaml
- name: Clear pip cache and retry
  run: |
    pip cache purge
    pip install -r requirements.txt
```

### 6.1.3 pytest Configuration Issues

**Common CI Failure**: No tests collected.

**Error Message**:
```
collected 0 items
```

**Root Causes and Fixes**:

1. **Test discovery not finding files**:
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
```

2. **Missing `__init__.py` in test directories**:
```bash
touch tests/__init__.py
```

3. **PYTHONPATH not set**:
```yaml
- name: Run tests
  run: pytest
  env:
    PYTHONPATH: ${{ github.workspace }}/src
```

**Common CI Failure**: Tests timeout.

**Solution**: Set explicit timeout
```yaml
- name: Run tests with timeout
  run: pytest --timeout=300  # 5 minutes per test
  timeout-minutes: 30  # GitHub Actions job timeout
```

**Common CI Failure**: Fixture not found.

**Solution**: Ensure conftest.py is in correct location
```
tests/
├── conftest.py      # Fixtures available to all tests
├── unit/
│   ├── conftest.py  # Fixtures for unit tests only
│   └── test_*.py
└── integration/
    └── test_*.py    # Uses root conftest.py fixtures
```

---

## 6.2 JavaScript/TypeScript CI Patterns

### 6.2.1 node_modules Caching Issues

**Common CI Failure**: Cache hit but packages missing or wrong version.

**Root Cause**: Cache key doesn't include all relevant files.

**Better: Use setup-node caching**:
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'

- run: npm ci
```

**Common CI Failure**: "EINTEGRITY" error - clear cache with `npm cache clean --force`.

### 6.2.2 npm vs yarn vs pnpm Differences

**Package Manager Comparison**:

| Feature | npm | yarn | pnpm |
|---------|-----|------|------|
| Lock file | `package-lock.json` | `yarn.lock` | `pnpm-lock.yaml` |
| CI install | `npm ci` | `yarn install --frozen-lockfile` | `pnpm install --frozen-lockfile` |
| Workspaces | `npm workspaces` | `yarn workspaces` | `pnpm workspaces` |

**Common CI Failure**: Wrong package manager used.

**pnpm Setup**:
```yaml
- uses: pnpm/action-setup@v4
  with:
    version: 8

- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'pnpm'

- run: pnpm install --frozen-lockfile
```

### 6.2.3 ESM vs CommonJS Issues

**Common CI Failure**: "require is not defined in ES module scope".

**Error Message**:
```
ReferenceError: require is not defined in ES module scope
```

**Root Cause**: Mixing ESM and CommonJS.

**Detection**:
```json
// package.json
{
  "type": "module"  // All .js files are ESM
}
```

**Solutions**:

1. **Use `.cjs` extension for CommonJS**:
```javascript
// config.cjs (CommonJS in ESM project)
module.exports = { ... };
```

2. **Use `.mjs` extension for ESM**:
```javascript
// config.mjs (ESM in CommonJS project)
export default { ... };
```

3. **Configure Jest for ESM**:
```json
// package.json
{
  "jest": {
    "transform": {}
  }
}
```

4. **Use tsx for TypeScript**:
```yaml
- name: Run TypeScript with ESM
  run: npx tsx ./src/index.ts
```

**Common CI Failure**: "Cannot use import statement outside a module" - use `node --experimental-vm-modules`.

---

## 6.3 Rust CI Patterns

### 6.3.1 cargo build Failures

**Common CI Failure**: Out of disk space during compilation.

**Error Message**:
```
error: failed to write to `/target/...`: No space left on device
```

**Solution**: Use sccache and clean targets
```yaml
- name: Install sccache
  uses: mozilla-actions/sccache-action@v0.0.4

- name: Build with sccache
  env:
    SCCACHE_GHA_ENABLED: true
    RUSTC_WRAPPER: sccache
  run: cargo build --release
```

**Common CI Failure**: Linking error.

**Error Message**:
```
error: linking with `cc` failed: exit code: 1
```

**Solution for Linux**:
```yaml
- name: Install linker dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y build-essential pkg-config libssl-dev
```

**Solution for Windows** (use MSVC):
```yaml
- name: Setup MSVC
  uses: ilammy/msvc-dev-cmd@v1
```

### 6.3.2 Target Directory Management

**Common CI Failure**: Cache bloat from multiple targets.

**Solution**: Limit cached directories
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/bin/
      ~/.cargo/registry/index/
      ~/.cargo/registry/cache/
      ~/.cargo/git/db/
      target/
    key: cargo-${{ runner.os }}-${{ hashFiles('**/Cargo.lock') }}
```

**Common CI Failure**: Stale artifacts cause build issues.

**Solution**: Clean selectively
```yaml
- name: Clean old artifacts
  run: |
    cargo clean --release -p my-crate  # Clean only your crate
    # Or full clean if needed
    # cargo clean
```

### 6.3.3 Cross-Compilation Issues

**Common CI Failure**: Target not installed.

**Error Message**:
```
error: target `x86_64-unknown-linux-musl` not found in channel
```

**Solution**:
```yaml
- name: Add cross-compilation target
  run: rustup target add x86_64-unknown-linux-musl

- name: Build for musl
  run: cargo build --target x86_64-unknown-linux-musl --release
```

**Cross-compilation with cross tool**:
```yaml
- name: Install cross
  run: cargo install cross

- name: Build for ARM
  run: cross build --target aarch64-unknown-linux-gnu --release
```

---

## 6.4 Go CI Patterns

### 6.4.1 Module Resolution Issues

**Common CI Failure**: "go: module not found".

**Error Message**:
```
go: github.com/user/repo@v1.0.0: reading github.com/user/repo/go.mod at revision v1.0.0: unknown revision v1.0.0
```

**Root Causes and Fixes**:

1. **Private repository access**:
```yaml
- name: Configure Git for private repos
  run: git config --global url."https://${{ secrets.GH_TOKEN }}@github.com/".insteadOf "https://github.com/"
```

2. **Module not tagged**:
```bash
# Ensure tag exists
git tag v1.0.0
git push origin v1.0.0
```

3. **go.sum out of sync**:
```yaml
- name: Verify go.sum
  run: |
    go mod tidy
    git diff --exit-code go.sum
```

### 6.4.2 Go Version Mismatches

**Common CI Failure**: "module requires Go 1.21".

**Solution**: Match Go version to go.mod
```yaml
- name: Read Go version from go.mod
  id: go-version
  run: |
    GO_VERSION=$(grep '^go ' go.mod | cut -d ' ' -f 2)
    echo "version=$GO_VERSION" >> $GITHUB_OUTPUT

- uses: actions/setup-go@v5
  with:
    go-version: ${{ steps.go-version.outputs.version }}
```

**Or specify explicitly**:
```yaml
- uses: actions/setup-go@v5
  with:
    go-version: '1.21'
    check-latest: true
```

### 6.4.3 CGO Dependencies

**Common CI Failure**: CGO disabled but required.

**Error Message**:
```
# runtime/cgo
cgo: C compiler "gcc" not found: exec: "gcc": executable file not found in $PATH
```

**Solution 1**: Disable CGO if not needed
```yaml
- name: Build without CGO
  run: CGO_ENABLED=0 go build ./...
```

**Solution 2**: Install C compiler
```yaml
- name: Install GCC
  run: sudo apt-get install -y gcc

- name: Build with CGO
  run: CGO_ENABLED=1 go build ./...
```

**Solution 3**: Use pure-Go alternatives (e.g., `modernc.org/sqlite` instead of `mattn/go-sqlite3`).

---

## Quick Reference: Language-Specific Troubleshooting

| Language | Common Issue | Quick Fix |
|----------|--------------|-----------|
| Python | No tests collected | Check pytest testpaths config |
| Python | Build fails | Install build-essential |
| JavaScript | EINTEGRITY | Clear npm cache |
| JavaScript | require not defined | Check type: module |
| Rust | No space left | Use sccache, clean targets |
| Rust | Linking failed | Install build tools |
| Go | Module not found | Run go mod tidy |
| Go | CGO error | Set CGO_ENABLED=0 |

---

## Summary: Language-Specific Checklist

Before committing CI workflows:

**Python**:
- [ ] Python version specified
- [ ] Virtual environment used
- [ ] Build dependencies installed
- [ ] pytest configured correctly

**JavaScript**:
- [ ] Correct package manager used
- [ ] Lock file committed
- [ ] ESM/CJS properly configured
- [ ] Node.js version specified

**Rust**: sccache configured, targets installed, build dependencies available

**Go**:
- [ ] Go version matches go.mod
- [ ] go.sum committed
- [ ] CGO_ENABLED set appropriately