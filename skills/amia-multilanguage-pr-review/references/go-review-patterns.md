# Go Review Patterns Reference

This document serves as an index to Go code review patterns and best practices. Each section is detailed in a separate reference file for efficient progressive disclosure.

---

## Table of Contents

- [5.1 Go Code Style and Idioms](#51-go-code-style-and-idioms)
- [5.2 Error Handling Patterns](#52-error-handling-patterns)
- [5.3 Package Organization and Naming](#53-package-organization-and-naming)
- [5.4 Test Patterns with go test](#54-test-patterns-with-go-test)
- [5.5 Linting with golint, go vet, and staticcheck](#55-linting-with-golint-go-vet-and-staticcheck)

---

## 5.1 Go Code Style and Idioms

**When to read**: When reviewing Go code for style compliance, naming conventions, or idiomatic patterns.

**Full reference**: [go-review-patterns-part1-style.md](go-review-patterns-part1-style.md)

### Contents

- Essential Style Rules (table of Good vs Bad patterns)
- Idiomatic Go Patterns
  - Short variable names for short scopes
  - Receiver naming conventions
  - Accept interfaces, return concrete types
  - Zero values usage
  - defer for cleanup
- Style Checklist

### Quick Reference

| Rule | Good | Bad |
|------|------|-----|
| Naming: exported | `PascalCase` | `camelCase` |
| Naming: unexported | `camelCase` | `snake_case` |
| Naming: interfaces | `Reader`, `Writer` | `IReader` |
| Naming: packages | Short, lowercase | `myPackage` |

---

## 5.2 Error Handling Patterns

**When to read**: When reviewing error handling, error wrapping, or custom error types in Go code.

**Full reference**: [go-review-patterns-part2-errors.md](go-review-patterns-part2-errors.md)

### Contents

- Basic Error Handling
  - Always check errors
  - Using errors.Is and errors.As
- Error Wrapping
  - Wrapping with context using %w
  - Preserving error chains
- Custom Error Types
  - Sentinel errors
  - Custom error types with data
- Error Handling Best Practices
  - Panic vs return error
  - Handle errors at the right level
- Error Handling Checklist

### Quick Reference

```go
// Wrap errors with context
return fmt.Errorf("loading config: %w", err)

// Check specific errors
if errors.Is(err, os.ErrNotExist) { ... }

// Extract error types
var valErr *ValidationError
if errors.As(err, &valErr) { ... }
```

---

## 5.3 Package Organization and Naming

**When to read**: When reviewing project structure, package naming, import organization, or circular dependencies.

**Full reference**: [go-review-patterns-part3-packages.md](go-review-patterns-part3-packages.md)

### Contents

- Package Structure
  - cmd/, internal/, pkg/ directories
  - Standard Go project layout
- Package Naming Rules
  - Good vs bad package names
- Import Organization
  - Grouping and sorting imports
- Avoiding Circular Dependencies
  - Extract shared code
  - Use interfaces
- Package Organization Checklist

### Quick Reference

```
myproject/
├── cmd/           # Application entry points
├── internal/      # Private packages
├── pkg/           # Public packages (optional)
├── go.mod
└── go.sum
```

---

## 5.4 Test Patterns with go test

**When to read**: When reviewing test code, test organization, or test coverage.

**Full reference**: [go-review-patterns-part4-testing.md](go-review-patterns-part4-testing.md)

### Contents

- Test File Organization
  - Naming conventions (_test.go)
  - External vs internal tests
- Basic Test Patterns
  - Table-driven tests
  - t.Run for subtests
- Test Helpers and Setup
  - t.Helper() for better error locations
  - t.Cleanup() for cleanup
  - testdata/ directory
- Running Tests
  - go test commands
  - Coverage and race detection
- Test Checklist

### Quick Reference

```bash
go test ./...                    # Run all tests
go test -v ./...                 # Verbose output
go test -cover ./...             # With coverage
go test -race ./...              # Race detection
```

---

## 5.5 Linting with golint, go vet, and staticcheck

**When to read**: When setting up or reviewing linting configuration, or understanding linter warnings.

**Full reference**: [go-review-patterns-part5-linting.md](go-review-patterns-part5-linting.md)

### Contents

- go vet (Built-in)
  - Finding suspicious constructs
- staticcheck (Recommended)
  - Common staticcheck checks table
- golangci-lint (All-in-One)
  - Configuration (.golangci.yml)
  - Running with fix
- Linting Checklist

### Quick Reference

```bash
go vet ./...                     # Built-in checks
staticcheck ./...                # Comprehensive linting
golangci-lint run ./...          # All-in-one linter
golangci-lint run --fix ./...    # Auto-fix issues
```

---

## Master Checklist for Go Code Review

Use this combined checklist for comprehensive Go code reviews:

### Style
- [ ] Code formatted with gofmt/goimports
- [ ] Naming conventions followed
- [ ] No stuttering (package.PackageThing)

### Errors
- [ ] All errors checked
- [ ] Errors wrapped with context (%w)
- [ ] No panic for recoverable errors

### Packages
- [ ] Clear package purposes
- [ ] No circular dependencies
- [ ] Imports grouped and sorted

### Tests
- [ ] Table-driven tests used
- [ ] t.Helper() in helpers
- [ ] Race detector passes

### Linting
- [ ] go vet passes
- [ ] staticcheck passes
- [ ] Doc comments on exports
