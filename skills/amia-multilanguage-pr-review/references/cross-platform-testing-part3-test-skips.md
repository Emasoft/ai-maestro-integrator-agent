# Cross-Platform Testing: Part 3 - Platform-Specific Test Skips and Annotations

## Table of Contents

- 7.3.1 Python (pytest) platform skips and custom markers
- 7.3.2 JavaScript (Jest/Vitest) conditional tests
- 7.3.3 Rust conditional compilation for tests
- 7.3.4 Go build tags and runtime skips

---

## 7.3 Platform-Specific Test Skips and Annotations

Sometimes tests must be skipped on certain platforms.

### Python (pytest)

```python
import pytest
import sys

# Skip on specific platform
@pytest.mark.skipif(sys.platform == 'win32', reason="Not supported on Windows")
def test_unix_permissions():
    import os
    os.chmod('file.txt', 0o755)

# Skip unless on specific platform
@pytest.mark.skipif(sys.platform != 'darwin', reason="macOS-specific test")
def test_macos_keychain():
    # Test macOS Keychain integration
    pass

# Custom markers
@pytest.mark.windows
def test_windows_registry():
    pass

@pytest.mark.unix
def test_unix_signals():
    pass

# In conftest.py
def pytest_configure(config):
    config.addinivalue_line("markers", "windows: mark test as Windows-only")
    config.addinivalue_line("markers", "unix: mark test as Unix-only")

def pytest_collection_modifyitems(config, items):
    if sys.platform == 'win32':
        skip_unix = pytest.mark.skip(reason="Unix-only test")
        for item in items:
            if "unix" in item.keywords:
                item.add_marker(skip_unix)
    else:
        skip_windows = pytest.mark.skip(reason="Windows-only test")
        for item in items:
            if "windows" in item.keywords:
                item.add_marker(skip_windows)
```

### JavaScript (Jest/Vitest)

```typescript
// Jest
describe('Unix-specific tests', () => {
  const itUnix = process.platform !== 'win32' ? it : it.skip;

  itUnix('should handle Unix permissions', () => {
    // Test
  });
});

// Vitest
import { describe, it, test } from 'vitest';

describe.skipIf(process.platform === 'win32')('Unix tests', () => {
  it('handles Unix permissions', () => {
    // Test
  });
});

// Conditional test
test.runIf(process.platform === 'darwin')('macOS Keychain', () => {
  // Test
});
```

### Rust

```rust
#[cfg(target_os = "linux")]
#[test]
fn test_linux_specific() {
    // Only compiled and run on Linux
}

#[cfg(target_os = "macos")]
#[test]
fn test_macos_specific() {
    // Only compiled and run on macOS
}

#[cfg(target_os = "windows")]
#[test]
fn test_windows_specific() {
    // Only compiled and run on Windows
}

#[cfg(unix)]
#[test]
fn test_unix() {
    // Runs on all Unix-like systems
}

// Or use ignore with conditional compilation
#[test]
#[cfg_attr(windows, ignore = "Not supported on Windows")]
fn test_posix_only() {
    // Test
}
```

### Go

```go
// file_unix_test.go - only built on Unix
//go:build unix

package mypackage

func TestUnixSpecific(t *testing.T) {
    // Test
}

// file_windows_test.go - only built on Windows
//go:build windows

package mypackage

func TestWindowsSpecific(t *testing.T) {
    // Test
}

// In regular test file, skip at runtime
func TestFeature(t *testing.T) {
    if runtime.GOOS == "windows" {
        t.Skip("Not supported on Windows")
    }
    // Test
}
```

---

**Previous**: [Part 2 - CI Matrix Configuration](cross-platform-testing-part2-ci-matrix.md)

**Next**: [Part 4 - Docker for Reproducible Builds](cross-platform-testing-part4-docker.md)
