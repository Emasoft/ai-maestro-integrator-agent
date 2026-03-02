# Rust Clippy Lints Reference

## 4.4 Clippy Lints and Configuration

Clippy is Rust's official linter with hundreds of lints.

### Clippy Configuration

```toml
# Cargo.toml
[lints.clippy]
# Deny these (errors)
unwrap_used = "deny"
expect_used = "deny"
panic = "deny"
todo = "deny"
unimplemented = "deny"

# Warn on these
clone_on_ref_ptr = "warn"
missing_docs_in_private_items = "warn"
missing_errors_doc = "warn"
missing_panics_doc = "warn"
doc_markdown = "warn"
```

### Running Clippy

```bash
# Basic run
cargo clippy

# With all targets
cargo clippy --all-targets --all-features

# Strict mode (deny warnings)
cargo clippy -- -D warnings

# Fix automatically
cargo clippy --fix

# Specific lint groups
cargo clippy -- -W clippy::pedantic
cargo clippy -- -W clippy::nursery
```

### Important Clippy Lints

| Lint | Category | Description |
|------|----------|-------------|
| `unwrap_used` | restriction | Disallow .unwrap() |
| `expect_used` | restriction | Disallow .expect() |
| `clone_on_ref_ptr` | pedantic | Clone on Rc/Arc |
| `missing_errors_doc` | pedantic | Missing error documentation |
| `needless_pass_by_value` | pedantic | Should be reference |
| `redundant_clone` | correctness | Unnecessary clone |
| `useless_conversion` | complexity | Into self |
| `map_unwrap_or` | pedantic | Use map_or instead |
| `single_match` | style | Use if let |
| `match_bool` | pedantic | Use if/else |

### Clippy Attributes

```rust
// Allow specific lint for item
#[allow(clippy::too_many_arguments)]
fn complex_function(a: i32, b: i32, c: i32, d: i32, e: i32, f: i32, g: i32) {}

// Allow for module
#![allow(clippy::missing_docs_in_private_items)]

// Expect lint (warning if lint doesn't fire)
#[expect(clippy::unwrap_used, reason = "test code")]
fn test_function() {
    Some(42).unwrap();
}
```

### Clippy Review Checklist

- [ ] cargo clippy passes with no warnings
- [ ] No #[allow(clippy::...)] without comment explaining why
- [ ] Pedantic lints reviewed and addressed
- [ ] No unwrap/expect in library code
- [ ] No todo!/unimplemented! in production code
