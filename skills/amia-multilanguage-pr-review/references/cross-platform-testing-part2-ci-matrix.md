# Cross-Platform Testing: Part 2 - CI Matrix Configuration for GitHub Actions

## Table of Contents

- 7.2.1 Basic matrix configuration (os, python-version)
- 7.2.2 Extended matrix with include/exclude
- 7.2.3 Node.js matrix example
- 7.2.4 Rust matrix example
- 7.2.5 Conditional steps based on matrix

---

## 7.2 CI Matrix Configuration for GitHub Actions

GitHub Actions supports matrix builds for cross-platform testing.

### Basic Matrix Configuration

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    strategy:
      fail-fast: false  # Continue other jobs if one fails
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run tests
        run: pytest
```

### Extended Matrix with Include/Exclude

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12']

        # Exclude specific combinations
        exclude:
          - os: macos-latest
            python-version: '3.10'

        # Include additional specific combinations
        include:
          # Test on Ubuntu 22.04 for specific version
          - os: ubuntu-22.04
            python-version: '3.12'
            extra-args: '--slow-tests'

          # ARM64 runner for macOS
          - os: macos-14  # M1 runner
            python-version: '3.12'
            arch: arm64

    runs-on: ${{ matrix.os }}
```

### Node.js Matrix Example

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node-version: ['18.x', '20.x', '21.x']

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test
```

### Rust Matrix Example

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        rust: [stable, beta, nightly]
        include:
          - os: ubuntu-latest
            rust: stable
            coverage: true

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-action@stable
        with:
          toolchain: ${{ matrix.rust }}
          components: clippy, rustfmt

      - name: Build
        run: cargo build --verbose

      - name: Run tests
        run: cargo test --verbose

      - name: Run clippy
        run: cargo clippy -- -D warnings
```

### Conditional Steps Based on Matrix

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      # Linux-only step
      - name: Install Linux dependencies
        if: runner.os == 'Linux'
        run: sudo apt-get install -y libsqlite3-dev

      # macOS-only step
      - name: Install macOS dependencies
        if: runner.os == 'macOS'
        run: brew install sqlite3

      # Windows-only step
      - name: Install Windows dependencies
        if: runner.os == 'Windows'
        run: choco install sqlite
```

---

**Previous**: [Part 1 - Testing on Multiple Operating Systems](cross-platform-testing-part1-multi-os.md)

**Next**: [Part 3 - Platform-Specific Test Skips](cross-platform-testing-part3-test-skips.md)
