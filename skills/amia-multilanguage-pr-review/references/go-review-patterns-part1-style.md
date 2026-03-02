# Go Code Style and Idioms Reference

## 5.1 Go Code Style and Idioms Checklist

Go has strong conventions enforced by gofmt and community standards.

### Essential Style Rules

| Rule | Good | Bad |
|------|------|-----|
| Indentation | Tabs | Spaces |
| Line length | No strict limit, but readable | Extremely long lines |
| Naming: exported | `PascalCase` | `camelCase` |
| Naming: unexported | `camelCase` | `snake_case`, `PascalCase` |
| Naming: acronyms | `HTTPServer`, `ID` | `HttpServer`, `Id` |
| Naming: interfaces | `Reader`, `Writer` (single method: -er) | `IReader`, `ReaderInterface` |
| Naming: packages | Short, lowercase, no underscores | `myPackage`, `my_package` |
| Braces | Same line | New line |
| Imports | Grouped, goimports sorted | Unsorted |

### Idiomatic Go Patterns

```go
// Use short variable names for short scopes
for i, v := range items {
    process(v)
}

// Use meaningful names for package-level and longer scopes
func ProcessUserRegistration(user *User) error {
    validationResult := validateUser(user)
    if validationResult != nil {
        return validationResult
    }
    return nil
}

// Use receiver names consistently (short, single letter)
type User struct {
    Name string
}

func (u *User) Validate() error {
    // Not 'user' or 'this' or 'self'
    return nil
}

// Accept interfaces, return concrete types
func ProcessReader(r io.Reader) ([]byte, error) {
    return io.ReadAll(r)
}

// Use zero values
var count int        // 0
var name string      // ""
var items []string   // nil (valid empty slice)
var enabled bool     // false

// Check zero values, not nil for strings/numbers
if name == "" {
    return errors.New("name required")
}

// Use make() for maps and channels
users := make(map[string]*User)
ch := make(chan int, 10)

// Use composite literals
user := &User{
    Name:  "Alice",
    Email: "alice@example.com",
}

// Use defer for cleanup
func ReadFile(path string) ([]byte, error) {
    f, err := os.Open(path)
    if err != nil {
        return nil, err
    }
    defer f.Close()  // Always close after function returns

    return io.ReadAll(f)
}
```

### Style Checklist

- [ ] Code formatted with gofmt/goimports
- [ ] No warnings from go vet
- [ ] Exported names are PascalCase
- [ ] Package names are short lowercase
- [ ] Receiver names are consistent
- [ ] No stuttering (user.UserName -> user.Name)
- [ ] Uses zero values appropriately
- [ ] defer used for resource cleanup
