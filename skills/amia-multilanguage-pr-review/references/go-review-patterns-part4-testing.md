# Go Test Patterns Reference

## Table of Contents

- [5.4 Test Patterns with go test](#54-test-patterns-with-go-test)
  - [Test File Organization](#test-file-organization)
  - [Basic Test Patterns](#basic-test-patterns)
  - [Test Helpers and Setup](#test-helpers-and-setup)
  - [Running Tests](#running-tests)
  - [Test Checklist](#test-checklist)

## 5.4 Test Patterns with go test

Go has built-in testing support with the testing package.

### Test File Organization

```
mypackage/
├── user.go
├── user_test.go           # Tests for user.go
├── user_internal_test.go  # Internal tests (same package)
└── export_test.go         # Test helpers exported for tests
```

### Basic Test Patterns

```go
// user_test.go
package user_test  // External test package (black-box testing)

import (
    "testing"

    "myproject/internal/user"
)

func TestCreateUser(t *testing.T) {
    u, err := user.Create("Alice", "alice@example.com")
    if err != nil {
        t.Fatalf("Create() error = %v", err)
    }
    if u.Name != "Alice" {
        t.Errorf("Create() Name = %v, want %v", u.Name, "Alice")
    }
}

// Table-driven tests
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name    string
        email   string
        wantErr bool
    }{
        {"valid email", "user@example.com", false},
        {"valid subdomain", "user@sub.example.com", false},
        {"missing @", "userexample.com", true},
        {"missing domain", "user@", true},
        {"empty string", "", true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := user.ValidateEmail(tt.email)
            if (err != nil) != tt.wantErr {
                t.Errorf("ValidateEmail(%q) error = %v, wantErr %v",
                    tt.email, err, tt.wantErr)
            }
        })
    }
}
```

### Test Helpers and Setup

```go
// testdata/ directory for test fixtures
// Files in testdata/ are ignored by go build

func TestParseConfig(t *testing.T) {
    // Read test fixture
    data, err := os.ReadFile("testdata/valid_config.json")
    if err != nil {
        t.Fatal(err)
    }

    config, err := ParseConfig(data)
    if err != nil {
        t.Fatalf("ParseConfig() error = %v", err)
    }
    // ...
}

// Test helper functions
func newTestServer(t *testing.T) *Server {
    t.Helper()  // Marks this as helper (better error locations)

    srv, err := NewServer(":0")  // Random port
    if err != nil {
        t.Fatalf("NewServer() error = %v", err)
    }

    t.Cleanup(func() {
        srv.Close()
    })

    return srv
}
```

### Running Tests

```bash
# Run all tests
go test ./...

# Run with verbose output
go test -v ./...

# Run specific tests
go test -run TestValidateEmail ./internal/user

# Run with coverage
go test -cover ./...
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Run benchmarks
go test -bench=. ./...

# Run with race detector
go test -race ./...
```

### Test Checklist

- [ ] All packages have corresponding _test.go files
- [ ] Uses table-driven tests where appropriate
- [ ] Uses t.Helper() for helper functions
- [ ] Uses t.Cleanup() for cleanup
- [ ] Tests are independent (no order dependency)
- [ ] Uses testdata/ for test fixtures
- [ ] Race detector passes (go test -race)
- [ ] Coverage is adequate for critical paths
