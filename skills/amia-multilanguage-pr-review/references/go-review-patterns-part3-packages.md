# Go Package Organization and Naming Reference

## Table of Contents

- [5.3 Package Organization and Naming](#53-package-organization-and-naming)
  - [Package Structure](#package-structure)
  - [Package Naming Rules](#package-naming-rules)
  - [Import Organization](#import-organization)
  - [Avoiding Circular Dependencies](#avoiding-circular-dependencies)
  - [Package Organization Checklist](#package-organization-checklist)

## 5.3 Package Organization and Naming

Go packages should be small, focused, and well-organized.

### Package Structure

```
myproject/
├── cmd/
│   ├── myapp/
│   │   └── main.go         # Application entry point
│   └── mycli/
│       └── main.go         # CLI tool entry point
├── internal/               # Private packages
│   ├── auth/
│   │   ├── auth.go
│   │   └── auth_test.go
│   └── database/
│       ├── database.go
│       └── database_test.go
├── pkg/                    # Public packages (optional)
│   └── api/
│       └── api.go
├── go.mod
├── go.sum
└── README.md
```

### Package Naming Rules

```go
// Good package names
package http      // Short, clear
package user      // Noun describing content
package config    // Noun describing content

// Bad package names
package httputil  // OK but less preferred
package utils     // Too generic
package common    // Too generic
package base      // Too generic
package helpers   // Too generic
```

### Import Organization

```go
import (
    // Standard library (blank line separation)
    "context"
    "fmt"
    "net/http"

    // Third-party packages
    "github.com/gorilla/mux"
    "go.uber.org/zap"

    // Internal packages
    "myproject/internal/auth"
    "myproject/internal/database"
)
```

### Avoiding Circular Dependencies

```go
// Problem: Circular dependency
// package a imports package b
// package b imports package a

// Solution 1: Extract shared code to new package
// package shared (no imports from a or b)
// package a imports shared
// package b imports shared

// Solution 2: Use interfaces
// package a defines interface
// package b implements interface
// package a depends on interface, not b

// Example
// In package a:
type UserStore interface {
    GetUser(id int) (*User, error)
}

// In package b:
type PostgresUserStore struct{}

func (s *PostgresUserStore) GetUser(id int) (*User, error) {
    // Implementation
}

// In main:
var store a.UserStore = &b.PostgresUserStore{}
```

### Package Organization Checklist

- [ ] Each package has a single, clear purpose
- [ ] Package names are short and descriptive
- [ ] Internal packages are in internal/ directory
- [ ] No circular dependencies
- [ ] Main packages are in cmd/ directory
- [ ] Imports are grouped and sorted
- [ ] No "util", "common", "misc" packages
