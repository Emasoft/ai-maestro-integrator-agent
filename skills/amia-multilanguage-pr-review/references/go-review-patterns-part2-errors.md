# Go Error Handling Patterns Reference

## Table of Contents

- [5.2 Error Handling Patterns in Go](#52-error-handling-patterns-in-go)
  - [Basic Error Handling](#basic-error-handling)
  - [Error Wrapping](#error-wrapping)
  - [Custom Error Types](#custom-error-types)
  - [Error Handling Best Practices](#error-handling-best-practices)
  - [Error Handling Checklist](#error-handling-checklist)

## 5.2 Error Handling Patterns in Go

Go uses explicit error handling with the `error` type.

### Basic Error Handling

```go
// Always check errors
result, err := doSomething()
if err != nil {
    return err
}
// Use result

// Handle specific errors
if errors.Is(err, os.ErrNotExist) {
    // File doesn't exist
}

// Check error types
var pathErr *os.PathError
if errors.As(err, &pathErr) {
    fmt.Printf("Path error: %s on %s\n", pathErr.Op, pathErr.Path)
}
```

### Error Wrapping

```go
import "fmt"

// Wrap errors with context using %w
func LoadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("loading config from %s: %w", path, err)
    }

    var config Config
    if err := json.Unmarshal(data, &config); err != nil {
        return nil, fmt.Errorf("parsing config: %w", err)
    }

    return &config, nil
}

// Error chain is preserved
err := LoadConfig("missing.json")
if errors.Is(err, os.ErrNotExist) {
    // Still matches wrapped error
}
```

### Custom Error Types

```go
// Simple sentinel errors
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrValidation   = errors.New("validation failed")
)

// Custom error type with data
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error on field %s: %s", e.Field, e.Message)
}

// Usage
func ValidateUser(u *User) error {
    if u.Name == "" {
        return &ValidationError{
            Field:   "name",
            Message: "required field",
        }
    }
    return nil
}

// Checking custom errors
var valErr *ValidationError
if errors.As(err, &valErr) {
    fmt.Printf("Invalid field: %s\n", valErr.Field)
}
```

### Error Handling Best Practices

```go
// Don't use panic for normal error handling
// Good
func Divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Bad
func Divide(a, b int) int {
    if b == 0 {
        panic("division by zero")
    }
    return a / b
}

// Use panic only for programmer errors (assertions)
func MustCompile(pattern string) *regexp.Regexp {
    re, err := regexp.Compile(pattern)
    if err != nil {
        panic(fmt.Sprintf("invalid regex pattern: %s", pattern))
    }
    return re
}

// Handle errors at the right level
// Don't log and return - do one or the other
func ProcessData(data []byte) error {
    result, err := parse(data)
    if err != nil {
        // Bad: log.Printf("parse error: %v", err)
        return fmt.Errorf("processing data: %w", err)
    }
    return nil
}
```

### Error Handling Checklist

- [ ] All errors are checked
- [ ] Errors are wrapped with context using %w
- [ ] Errors can be compared with errors.Is
- [ ] Error types can be extracted with errors.As
- [ ] No panic for recoverable errors
- [ ] Errors are handled at appropriate level
- [ ] Error messages are lowercase (no punctuation at end)
- [ ] Sentinel errors use errors.New
