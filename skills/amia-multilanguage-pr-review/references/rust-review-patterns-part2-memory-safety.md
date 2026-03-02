# Rust Memory Safety Patterns Reference

## Table of Contents

- [4.2 Memory Safety Patterns and Ownership](#42-memory-safety-patterns-and-ownership)
  - [Ownership Rules](#ownership-rules)
  - [Borrowing Patterns](#borrowing-patterns)
  - [Lifetime Annotations](#lifetime-annotations)
  - [Common Patterns for Avoiding Borrow Checker Issues](#common-patterns-for-avoiding-borrow-checker-issues)
  - [Memory Safety Checklist](#memory-safety-checklist)

## 4.2 Memory Safety Patterns and Ownership

Rust's ownership system prevents memory errors at compile time.

### Ownership Rules

1. Each value has exactly one owner
2. When the owner goes out of scope, the value is dropped
3. Values can be borrowed (referenced) without transferring ownership

### Borrowing Patterns

```rust
// Immutable borrow (&T) - can have multiple
fn process(data: &Vec<i32>) {
    for item in data {
        println!("{}", item);
    }
}

// Mutable borrow (&mut T) - only one at a time
fn modify(data: &mut Vec<i32>) {
    data.push(42);
}

// Ownership transfer (T)
fn consume(data: Vec<i32>) {
    // data is dropped at end of function
}

// Returning owned values
fn create() -> Vec<i32> {
    vec![1, 2, 3]  // Ownership transferred to caller
}
```

### Lifetime Annotations

```rust
// Explicit lifetimes when references are returned
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// Struct with references needs lifetime
struct Parser<'a> {
    input: &'a str,
    position: usize,
}

impl<'a> Parser<'a> {
    fn new(input: &'a str) -> Self {
        Self { input, position: 0 }
    }
}

// 'static lifetime for data that lives forever
const GREETING: &'static str = "Hello, world!";
```

### Common Patterns for Avoiding Borrow Checker Issues

```rust
// Pattern 1: Clone when borrowing is complex
let data = expensive_data.clone();
modify(&mut expensive_data);
use_data(&data);

// Pattern 2: Use indices instead of references in collections
struct Graph {
    nodes: Vec<Node>,
    edges: Vec<(usize, usize)>,  // Indices instead of references
}

// Pattern 3: Use interior mutability (Cell, RefCell, Mutex)
use std::cell::RefCell;

struct Counter {
    count: RefCell<u32>,
}

impl Counter {
    fn increment(&self) {  // &self, not &mut self
        *self.count.borrow_mut() += 1;
    }
}

// Pattern 4: Split borrows
struct Data {
    field_a: String,
    field_b: Vec<i32>,
}

// Can borrow different fields mutably
fn process(data: &mut Data) {
    let a = &mut data.field_a;
    let b = &mut data.field_b;
    // Both can be used simultaneously
}
```

### Memory Safety Checklist

- [ ] No unnecessary clones
- [ ] Lifetimes are as short as possible
- [ ] Uses references instead of ownership when possible
- [ ] No RefCell in hot paths (runtime cost)
- [ ] Arc used for shared ownership across threads
- [ ] Mutex for mutable shared state across threads
- [ ] No unsafe blocks without safety comments
