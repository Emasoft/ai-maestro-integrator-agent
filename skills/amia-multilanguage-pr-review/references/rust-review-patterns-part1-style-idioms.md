# Rust Code Style and Idioms Reference

## Table of Contents

- [4.1 Rust Code Style and Idioms Checklist](#41-rust-code-style-and-idioms-checklist)
  - [Essential Style Rules](#essential-style-rules)
  - [rustfmt Configuration](#rustfmt-configuration)
  - [Idiomatic Rust Patterns](#idiomatic-rust-patterns)
  - [Style Checklist](#style-checklist)

## 4.1 Rust Code Style and Idioms Checklist

Rust has strong conventions enforced by rustfmt and clippy.

### Essential Style Rules

| Rule | Good | Bad |
|------|------|-----|
| Indentation | 4 spaces | Tabs or 2 spaces |
| Line length | Max 100 characters | Lines over 100 |
| Naming: variables | `snake_case` | `camelCase`, `PascalCase` |
| Naming: types | `PascalCase` | `snake_case` |
| Naming: constants | `SCREAMING_SNAKE_CASE` | `lowercase` |
| Naming: lifetimes | Short, lowercase (`'a`, `'b`) | Long names (`'lifetime`) |
| Naming: modules | `snake_case` | `PascalCase` |
| Trailing commas | Yes, in multiline | No trailing commas |

### rustfmt Configuration

```toml
# rustfmt.toml
max_width = 100
hard_tabs = false
tab_spaces = 4
newline_style = "Unix"
use_small_heuristics = "Default"
reorder_imports = true
reorder_modules = true
remove_nested_parens = true
edition = "2021"
merge_derives = true
use_try_shorthand = true
use_field_init_shorthand = true
force_explicit_abi = true
```

### Idiomatic Rust Patterns

```rust
// Use iterators instead of manual loops
// Good
let sum: i32 = numbers.iter().sum();
let doubled: Vec<i32> = numbers.iter().map(|n| n * 2).collect();

// Bad
let mut sum = 0;
for n in &numbers {
    sum += n;
}

// Use if let for single pattern matching
// Good
if let Some(value) = optional {
    process(value);
}

// Bad (when only one pattern matters)
match optional {
    Some(value) => process(value),
    None => {}
}

// Use ? operator for error propagation
// Good
fn read_file(path: &str) -> Result<String, io::Error> {
    let content = fs::read_to_string(path)?;
    Ok(content.trim().to_string())
}

// Bad
fn read_file(path: &str) -> Result<String, io::Error> {
    match fs::read_to_string(path) {
        Ok(content) => Ok(content.trim().to_string()),
        Err(e) => Err(e),
    }
}

// Use derive macros
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct User {
    id: u64,
    name: String,
}

// Use Default trait
#[derive(Default)]
struct Config {
    timeout: u64,
    retries: u32,
    verbose: bool,
}

let config = Config {
    timeout: 30,
    ..Default::default()
};
```

### Style Checklist

- [ ] Code formatted with rustfmt
- [ ] No warnings from cargo build
- [ ] Uses idiomatic patterns (iterators, ? operator)
- [ ] Appropriate derives on structs
- [ ] Consistent naming conventions
- [ ] No unnecessary mut
- [ ] No unnecessary clone()
- [ ] Uses &str instead of &String for parameters
