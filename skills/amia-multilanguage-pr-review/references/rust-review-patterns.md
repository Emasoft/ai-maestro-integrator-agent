# Rust Review Patterns Reference

This document provides comprehensive Rust code review patterns covering style, memory safety, error handling, linting, and documentation.

---

## Table of Contents

### 4.1 Rust Code Style and Idioms
**File:** [rust-review-patterns-part1-style-idioms.md](rust-review-patterns-part1-style-idioms.md)

- Essential Style Rules (naming, indentation, line length)
- rustfmt Configuration (complete rustfmt.toml example)
- Idiomatic Rust Patterns (iterators, if let, ? operator, derives, Default trait)
- Style Checklist

**When to read:** When reviewing code formatting, naming conventions, or idiomatic Rust usage.

---

### 4.2 Memory Safety Patterns and Ownership
**File:** [rust-review-patterns-part2-memory-safety.md](rust-review-patterns-part2-memory-safety.md)

- Ownership Rules (the three fundamental rules)
- Borrowing Patterns (immutable, mutable, ownership transfer)
- Lifetime Annotations (explicit lifetimes, struct lifetimes, 'static)
- Common Patterns for Avoiding Borrow Checker Issues (clone, indices, interior mutability, split borrows)
- Memory Safety Checklist

**When to read:** When reviewing ownership, borrowing, lifetimes, or borrow checker errors.

---

### 4.3 Error Handling with Result and Option
**File:** [rust-review-patterns-part3-error-handling.md](rust-review-patterns-part3-error-handling.md)

- Result Patterns (returning Result, custom error types, thiserror crate)
- Option Patterns (creating, unwrapping safely, transforming, chaining)
- Error Handling Checklist

**When to read:** When reviewing error handling, Result/Option usage, or custom error types.

---

### 4.4 Clippy Lints and Configuration
**File:** [rust-review-patterns-part4-clippy.md](rust-review-patterns-part4-clippy.md)

- Clippy Configuration (Cargo.toml lints section)
- Running Clippy (basic, strict, fix, lint groups)
- Important Clippy Lints (table of key lints)
- Clippy Attributes (allow, expect)
- Clippy Review Checklist

**When to read:** When reviewing linting configuration or addressing Clippy warnings.

---

### 4.5 Documentation Standards with rustdoc
**File:** [rust-review-patterns-part5-documentation.md](rust-review-patterns-part5-documentation.md)

- Documentation Comments (crate-level, item-level, field-level)
- Documentation Sections (Examples, Errors, Panics, Safety, Arguments, Returns)
- Doc Tests (should_panic, no_run, ignore)
- Documentation Checklist

**When to read:** When reviewing documentation, doc comments, or doc tests.

---

## Quick Reference: Review Focus by File Type

| File Type | Primary Review Focus |
|-----------|---------------------|
| `lib.rs`, `main.rs` | Crate docs, module organization |
| `*.rs` (modules) | Style, ownership, error handling |
| `Cargo.toml` | Dependencies, clippy config |
| `rustfmt.toml` | Formatting settings |
| Tests | unwrap usage OK, doc test coverage |

## Quick Reference: Common Review Issues

| Issue | Reference |
|-------|-----------|
| Formatting inconsistent | Part 1: rustfmt configuration |
| Unnecessary clone | Part 2: Memory safety checklist |
| Using unwrap in library | Part 3: Error handling checklist |
| Missing documentation | Part 5: Documentation checklist |
| Clippy warnings ignored | Part 4: Clippy review checklist |
