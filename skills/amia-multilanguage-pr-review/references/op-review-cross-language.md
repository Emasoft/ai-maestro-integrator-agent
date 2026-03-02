---
name: op-review-cross-language
description: Review cross-language interfaces and dependencies in a PR
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Review Cross-Language Interfaces


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Cross-Language Interface Types](#cross-language-interface-types)
  - [1. API Contracts](#1-api-contracts)
  - [2. Data Serialization](#2-data-serialization)
  - [3. FFI Boundaries](#3-ffi-boundaries)
  - [4. Shared Configuration](#4-shared-configuration)
- [Procedure](#procedure)
- [Example: Backend/Frontend API Change](#example-backendfrontend-api-change)
- [Example: FFI Boundary (Rust + Python)](#example-ffi-boundary-rust-python)
- [Common Compatibility Issues](#common-compatibility-issues)
- [Review Checklist](#review-checklist)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Identify and review interfaces between different programming languages in a multilanguage PR. This includes API contracts, FFI boundaries, shared configuration, and data serialization.

## When to Use

- When a PR touches code in multiple languages
- When backend and frontend code are both modified
- When changes affect API contracts or data schemas
- When FFI (Foreign Function Interface) code is involved

## Prerequisites

- Languages detected in PR
- Understanding of the system architecture
- Access to API schemas or interface definitions

## Input

| Parameter | Type | Description |
|-----------|------|-------------|
| PR diff | Text | The changes being made |
| Languages | List | Languages detected in the PR |
| Architecture docs | Optional | System architecture documentation |

## Output

| Field | Type | Description |
|-------|------|-------------|
| `interfaces_affected` | List | Cross-language interfaces touched |
| `compatibility_issues` | List | Potential compatibility problems |
| `recommendations` | List | Suggested reviews or checks |

## Cross-Language Interface Types

### 1. API Contracts

When backend and frontend communicate:

| Check | Description |
|-------|-------------|
| Endpoint changes | URL paths, HTTP methods |
| Request format | Field names, types, required fields |
| Response format | Structure, field types, status codes |
| Error handling | Error codes, messages |

### 2. Data Serialization

When data crosses language boundaries:

| Check | Description |
|-------|-------------|
| JSON schema | Field names match both sides |
| Type mapping | int64 vs number, datetime formats |
| Null handling | Optional vs required fields |
| Encoding | UTF-8 consistency |

### 3. FFI Boundaries

When languages call each other directly:

| Check | Description |
|-------|-------------|
| Function signatures | Parameter types match |
| Memory management | Who allocates/frees |
| Error propagation | How errors cross boundary |
| Thread safety | Concurrent access handling |

### 4. Shared Configuration

When multiple languages read same config:

| Check | Description |
|-------|-------------|
| Config format | YAML/JSON/TOML consistency |
| Key names | Same keys in all consumers |
| Value types | String vs int vs bool |
| Defaults | Same defaults everywhere |

## Procedure

1. **Identify cross-language interfaces**
   - Look for API endpoint changes
   - Check for schema/type definition changes
   - Find FFI or binding code
   - Locate shared configuration files

2. **For each interface found:**
   - Compare changes on both sides of the interface
   - Verify types are compatible
   - Check for breaking changes
   - Verify tests cover the interface

3. **Document findings**
   - List all affected interfaces
   - Note compatibility concerns
   - Recommend additional reviews

## Example: Backend/Frontend API Change

```python
# Python backend change (before)
@app.get("/api/users/{user_id}")
def get_user(user_id: int) -> User:
    return User(id=user_id, name="Test", email="test@example.com")

# Python backend change (after)
@app.get("/api/users/{user_id}")
def get_user(user_id: int) -> User:
    return User(id=user_id, name="Test", email="test@example.com", role="user")
    # Added new field: role
```

```typescript
// TypeScript frontend (must be updated to match)
interface User {
  id: number;
  name: string;
  email: string;
  role?: string;  // Must add this field
}
```

**Review check**: Verify TypeScript interface was updated to match Python model.

## Example: FFI Boundary (Rust + Python)

```rust
// Rust library
#[no_mangle]
pub extern "C" fn process_data(data: *const u8, len: usize) -> i32 {
    // Changed return type from bool to i32
}
```

```python
# Python bindings (must match)
lib = ctypes.CDLL("./libprocessor.so")
lib.process_data.restype = ctypes.c_int32  # Must update from c_bool
lib.process_data.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
```

**Review check**: Verify Python ctypes definition matches Rust signature.

## Common Compatibility Issues

| Issue | Description | Solution |
|-------|-------------|----------|
| Field name mismatch | `user_id` vs `userId` | Agree on naming convention |
| Type mismatch | Python `int` vs JS `number` precision | Use string for large numbers |
| Null vs undefined | Python `None` vs JS `undefined` | Explicit null handling |
| Date format | ISO string vs timestamp | Standardize on ISO 8601 |
| Error codes | Different error representations | Shared error schema |

## Review Checklist

- [ ] Identify all cross-language interfaces affected
- [ ] Verify API contracts match on both sides
- [ ] Check type mappings are compatible
- [ ] Verify shared configuration is consistent
- [ ] Ensure FFI signatures match
- [ ] Check for breaking changes
- [ ] Verify integration tests exist

## Error Handling

| Scenario | Action |
|----------|--------|
| Interface mismatch found | Request changes to align both sides |
| No tests for interface | Request integration tests |
| Breaking change detected | Flag for review, may need migration plan |

## Related Operations

- [op-detect-pr-languages.md](op-detect-pr-languages.md) - Know which languages are involved
- [op-run-multilang-linters.md](op-run-multilang-linters.md) - Linters may catch type issues
- [op-compile-multilang-review.md](op-compile-multilang-review.md) - Include in final review
