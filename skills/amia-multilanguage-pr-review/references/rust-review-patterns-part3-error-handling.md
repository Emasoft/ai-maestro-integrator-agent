# Rust Error Handling Reference

## Table of Contents

- [4.3 Error Handling with Result and Option](#43-error-handling-with-result-and-option)
  - [Result Patterns](#result-patterns)
  - [Option Patterns](#option-patterns)
  - [Error Handling Checklist](#error-handling-checklist)

## 4.3 Error Handling with Result and Option

Rust uses `Result<T, E>` for recoverable errors and `Option<T>` for optional values.

### Result Patterns

```rust
use std::fs;
use std::io;

// Returning Result
fn read_config(path: &str) -> Result<Config, ConfigError> {
    let content = fs::read_to_string(path)
        .map_err(|e| ConfigError::IoError(e))?;

    let config: Config = toml::from_str(&content)
        .map_err(|e| ConfigError::ParseError(e))?;

    Ok(config)
}

// Custom error types
#[derive(Debug)]
enum ConfigError {
    IoError(io::Error),
    ParseError(toml::de::Error),
    ValidationError(String),
}

impl std::error::Error for ConfigError {}

impl std::fmt::Display for ConfigError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::IoError(e) => write!(f, "IO error: {}", e),
            Self::ParseError(e) => write!(f, "Parse error: {}", e),
            Self::ValidationError(msg) => write!(f, "Validation error: {}", msg),
        }
    }
}

// Using thiserror crate (recommended)
use thiserror::Error;

#[derive(Error, Debug)]
enum ConfigError {
    #[error("IO error: {0}")]
    Io(#[from] io::Error),

    #[error("Parse error: {0}")]
    Parse(#[from] toml::de::Error),

    #[error("Validation error: {0}")]
    Validation(String),
}
```

### Option Patterns

```rust
// Creating Options
let some_value: Option<i32> = Some(42);
let no_value: Option<i32> = None;

// Unwrapping safely
let value = some_value.unwrap_or(0);          // Default value
let value = some_value.unwrap_or_default();   // T::default()
let value = some_value.unwrap_or_else(|| compute_default());

// Transforming Options
let doubled = some_value.map(|v| v * 2);      // Option<i32>
let result = some_value.ok_or("error");       // Result<i32, &str>

// Chaining Options
fn get_user_city(user_id: u64) -> Option<String> {
    get_user(user_id)
        .and_then(|user| user.address)
        .and_then(|addr| addr.city)
}

// Using ? with Option (in functions returning Option)
fn get_user_city(user_id: u64) -> Option<String> {
    let user = get_user(user_id)?;
    let address = user.address?;
    let city = address.city?;
    Some(city)
}
```

### Error Handling Checklist

- [ ] Functions return Result for operations that can fail
- [ ] Custom error types implement std::error::Error
- [ ] Uses thiserror for error type definitions
- [ ] Uses anyhow for application-level error handling
- [ ] No unwrap() except in tests or truly unreachable code
- [ ] expect() has meaningful message
- [ ] Errors are propagated with ?, not matched and re-raised
- [ ] Option used for optional values, not Result
