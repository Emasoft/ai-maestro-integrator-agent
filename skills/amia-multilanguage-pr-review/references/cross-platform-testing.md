# Cross-Platform Testing Reference

This reference covers comprehensive strategies for testing applications across multiple operating systems, architectures, and runtime environments.

---

## Table of Contents

### Part 1: Testing on Multiple Operating Systems
**File**: [cross-platform-testing-part1-multi-os.md](cross-platform-testing-part1-multi-os.md)

- 7.1.1 Platform categories and key differences
- 7.1.2 Common platform issues (file paths, line endings, permissions, case sensitivity)
- 7.1.3 Testing matrix dimensions
- 7.1.4 Platform detection in tests (Python and TypeScript)

### Part 2: CI Matrix Configuration for GitHub Actions
**File**: [cross-platform-testing-part2-ci-matrix.md](cross-platform-testing-part2-ci-matrix.md)

- 7.2.1 Basic matrix configuration (os, python-version)
- 7.2.2 Extended matrix with include/exclude
- 7.2.3 Node.js matrix example
- 7.2.4 Rust matrix example
- 7.2.5 Conditional steps based on matrix

### Part 3: Platform-Specific Test Skips and Annotations
**File**: [cross-platform-testing-part3-test-skips.md](cross-platform-testing-part3-test-skips.md)

- 7.3.1 Python (pytest) platform skips and custom markers
- 7.3.2 JavaScript (Jest/Vitest) conditional tests
- 7.3.3 Rust conditional compilation for tests
- 7.3.4 Go build tags and runtime skips

### Part 4: Using Docker for Reproducible Builds
**File**: [cross-platform-testing-part4-docker.md](cross-platform-testing-part4-docker.md)

- 7.4.1 Multi-platform Docker build with multi-stage
- 7.4.2 GitHub Actions with Docker services
- 7.4.3 Multi-architecture builds (amd64, arm64)
- 7.4.4 Docker Compose for testing
- 7.4.5 Development containers (devcontainer)
- 7.4.6 Docker testing checklist

---

## Quick Reference

### When to Read Each Part

| If you need to... | Read |
|-------------------|------|
| Handle file paths, permissions, line endings across OS | Part 1 |
| Set up GitHub Actions matrix for multi-OS testing | Part 2 |
| Skip tests on specific platforms in pytest/Jest/Rust/Go | Part 3 |
| Use Docker for consistent build/test environments | Part 4 |

### Platform Detection Quick Reference

**Python**:
```python
import sys
sys.platform == 'win32'   # Windows
sys.platform == 'darwin'  # macOS
sys.platform.startswith('linux')  # Linux
```

**TypeScript/JavaScript**:
```typescript
process.platform === 'win32'   // Windows
process.platform === 'darwin'  // macOS
process.platform === 'linux'   // Linux
```

**GitHub Actions**:
```yaml
if: runner.os == 'Windows'
if: runner.os == 'macOS'
if: runner.os == 'Linux'
```

---

## Key Principles

1. **Use path libraries**: Never hardcode path separators
2. **Handle line endings**: Use universal newline mode
3. **Test on all targets**: Use CI matrix builds
4. **Skip gracefully**: Use platform-specific test annotations
5. **Containerize**: Docker ensures reproducibility
