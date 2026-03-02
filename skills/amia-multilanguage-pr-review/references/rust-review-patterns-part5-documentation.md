# Rust Documentation Standards Reference

## Table of Contents

- [4.5 Documentation Standards with rustdoc](#45-documentation-standards-with-rustdoc)
  - [Documentation Comments](#documentation-comments)
  - [Documentation Sections](#documentation-sections)
  - [Doc Tests](#doc-tests)
  - [Documentation Checklist](#documentation-checklist)

## 4.5 Documentation Standards with rustdoc

Rust has built-in documentation support with rustdoc.

### Documentation Comments

```rust
//! Crate-level documentation
//!
//! This crate provides utilities for working with configuration files.
//!
//! # Features
//!
//! - TOML parsing
//! - JSON parsing
//! - Environment variable overrides
//!
//! # Example
//!
//! ```
//! use my_crate::Config;
//!
//! let config = Config::from_file("config.toml")?;
//! println!("Port: {}", config.port);
//! # Ok::<(), my_crate::ConfigError>(())
//! ```

/// A configuration object loaded from file.
///
/// This struct represents the application configuration.
/// It can be loaded from TOML, JSON, or environment variables.
///
/// # Examples
///
/// Loading from a file:
///
/// ```
/// use my_crate::Config;
///
/// let config = Config::from_file("config.toml")?;
/// # Ok::<(), my_crate::ConfigError>(())
/// ```
///
/// Using the builder:
///
/// ```
/// use my_crate::Config;
///
/// let config = Config::builder()
///     .port(8080)
///     .host("localhost")
///     .build()?;
/// # Ok::<(), my_crate::ConfigError>(())
/// ```
#[derive(Debug, Clone)]
pub struct Config {
    /// The port to listen on.
    pub port: u16,
    /// The host address to bind to.
    pub host: String,
    /// Optional TLS configuration.
    pub tls: Option<TlsConfig>,
}

impl Config {
    /// Creates a new configuration from a file path.
    ///
    /// # Arguments
    ///
    /// * `path` - Path to the configuration file (TOML or JSON)
    ///
    /// # Errors
    ///
    /// Returns an error if:
    /// - The file cannot be read
    /// - The file format is invalid
    /// - Required fields are missing
    ///
    /// # Examples
    ///
    /// ```
    /// use my_crate::Config;
    ///
    /// let config = Config::from_file("config.toml")?;
    /// assert!(config.port > 0);
    /// # Ok::<(), my_crate::ConfigError>(())
    /// ```
    pub fn from_file(path: &str) -> Result<Self, ConfigError> {
        // Implementation
    }

    /// Returns `true` if TLS is configured.
    ///
    /// # Examples
    ///
    /// ```
    /// use my_crate::Config;
    ///
    /// let config = Config::default();
    /// assert!(!config.has_tls());
    /// ```
    #[must_use]
    pub fn has_tls(&self) -> bool {
        self.tls.is_some()
    }
}
```

### Documentation Sections

| Section | Purpose |
|---------|---------|
| `# Examples` | Code examples (tested by cargo test) |
| `# Errors` | Conditions that cause errors |
| `# Panics` | Conditions that cause panics |
| `# Safety` | Safety requirements for unsafe code |
| `# Arguments` | Parameter descriptions |
| `# Returns` | Return value description |
| `# See Also` | Links to related items |

### Doc Tests

```rust
/// Parses a string into a number.
///
/// # Examples
///
/// ```
/// use my_crate::parse_number;
///
/// assert_eq!(parse_number("42"), Ok(42));
/// assert!(parse_number("not a number").is_err());
/// ```
///
/// ```should_panic
/// use my_crate::parse_number;
///
/// parse_number("will panic").unwrap();
/// ```
///
/// ```no_run
/// use my_crate::expensive_operation;
///
/// // This compiles but doesn't run in tests
/// expensive_operation();
/// ```
///
/// ```ignore
/// // This is completely ignored
/// broken_code();
/// ```
pub fn parse_number(s: &str) -> Result<i32, ParseError> {
    s.parse().map_err(ParseError::from)
}
```

### Documentation Checklist

- [ ] All public items have doc comments
- [ ] Doc comments include examples
- [ ] Examples compile and pass tests
- [ ] Errors section documents all error conditions
- [ ] Panics section documents panic conditions
- [ ] Safety section for unsafe functions
- [ ] Links to related items use intra-doc links
- [ ] `#[must_use]` on functions where return value matters
