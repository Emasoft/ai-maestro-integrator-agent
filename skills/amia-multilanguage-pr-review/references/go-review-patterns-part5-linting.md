# Go Linting Tools Reference

## 5.5 Linting with golint, go vet, and staticcheck

### go vet (Built-in)

go vet finds suspicious constructs that might be bugs.

```bash
# Run on all packages
go vet ./...

# Run specific analyzers
go vet -printf ./...
```

### staticcheck (Recommended)

staticcheck is the most comprehensive Go linter.

```bash
# Install
go install honnef.co/go/tools/cmd/staticcheck@latest

# Run
staticcheck ./...
```

### Common staticcheck Checks

| Check | Description |
|-------|-------------|
| SA1000 | Invalid regex pattern |
| SA4006 | Value assigned but not used |
| SA4017 | Pure function discarded |
| SA5007 | Infinite recursive call |
| ST1000 | Package should have comment |
| ST1003 | Naming convention violation |
| ST1005 | Error strings should not be capitalized |

### golangci-lint (All-in-One)

golangci-lint runs multiple linters in parallel.

```yaml
# .golangci.yml
linters:
  enable:
    - errcheck
    - govet
    - staticcheck
    - gosimple
    - ineffassign
    - unused
    - gofmt
    - goimports
    - misspell
    - unconvert
    - gocritic
    - revive

linters-settings:
  errcheck:
    check-type-assertions: true
  govet:
    check-shadowing: true
  revive:
    rules:
      - name: exported
        severity: warning

issues:
  exclude-use-default: false
  max-issues-per-linter: 0
  max-same-issues: 0
```

```bash
# Install
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Run
golangci-lint run ./...

# Run with fix
golangci-lint run --fix ./...
```

### Linting Checklist

- [ ] go vet passes with no errors
- [ ] staticcheck passes with no errors
- [ ] golangci-lint passes with configured linters
- [ ] No nolint without explanation comment
- [ ] Error strings are lowercase without punctuation
- [ ] All exported symbols have doc comments
- [ ] Code is formatted with gofmt/goimports
