---
name: "Code Review Evaluation Criteria"
description: "Comprehensive criteria for evaluating code quality, style, security, and performance in code reviews"
---

# Code Review Evaluation Criteria

## Table of Contents

- [1. Code Quality](#1-code-quality)
  - [1.1 Readability](#11-readability)
  - [1.2 Maintainability](#12-maintainability)
  - [1.3 Correctness](#13-correctness)
- [2. Code Style](#2-code-style)
  - [2.1 Language Conventions](#21-language-conventions)
  - [2.2 Project Standards](#22-project-standards)
  - [2.3 Documentation Style](#23-documentation-style)
- [3. Security](#3-security)
  - [3.1 Input Validation](#31-input-validation)
  - [3.2 Authentication & Authorization](#32-authentication--authorization)
  - [3.3 Data Protection](#33-data-protection)
  - [3.4 Common Vulnerabilities](#34-common-vulnerabilities)
- [4. Performance](#4-performance)
  - [4.1 Algorithmic Efficiency](#41-algorithmic-efficiency)
  - [4.2 Resource Management](#42-resource-management)
  - [4.3 Scalability](#43-scalability)
  - [4.4 Optimization Level](#44-optimization-level)
- [5. Testing](#5-testing)
  - [5.1 Test Coverage](#51-test-coverage)
  - [5.2 Test Quality](#52-test-quality)
  - [5.3 Test Maintainability](#53-test-maintainability)
- [6. Architecture & Design](#6-architecture--design)
  - [6.1 Design Patterns](#61-design-patterns)
  - [6.2 Dependencies](#62-dependencies)
  - [6.3 API Design](#63-api-design)
- [7. Evaluation Scoring](#7-evaluation-scoring)
  - [Priority Levels](#priority-levels)
  - [Review Decision Matrix](#review-decision-matrix)
- [8. Review Checklist](#8-review-checklist)

This document defines the key criteria for evaluating code during reviews. Each criterion includes specific checkpoints and examples.

## 1. Code Quality

### 1.1 Readability
- **Clear naming**: Variables, functions, and classes have descriptive, unambiguous names
- **Consistent style**: Follows project's style guide (indentation, naming conventions, formatting)
- **Appropriate comments**: Complex logic is explained; self-documenting code is preferred over excessive comments
- **Modular structure**: Functions/methods have single responsibilities and reasonable length (<50 lines preferred)

**Example - Good:**
```python
def calculate_total_price(items: list[Item], discount_rate: float) -> Decimal:
    """Calculate total price after applying discount."""
    subtotal = sum(item.price * item.quantity for item in items)
    return subtotal * (1 - discount_rate)
```

**Example - Bad:**
```python
def calc(x, y):  # Unclear what x and y represent
    t = 0
    for i in x:
        t += i.p * i.q
    return t * (1 - y)  # Magic number without explanation
```

### 1.2 Maintainability
- **DRY principle**: No unnecessary code duplication
- **Clear abstractions**: Appropriate use of functions, classes, and modules
- **Low coupling**: Components are loosely coupled
- **High cohesion**: Related functionality is grouped together
- **Testability**: Code is structured to be easily testable

### 1.3 Correctness
- **Logic verification**: Implementation matches requirements and specifications
- **Edge cases**: Handles boundary conditions, empty inputs, null values
- **Error conditions**: Appropriate error handling for expected failures
- **Type safety**: Proper type annotations and type checking (for typed languages)

## 2. Code Style

### 2.1 Language Conventions
- Follows language-specific best practices (PEP 8 for Python, ESLint for JavaScript, etc.)
- Uses language features appropriately (list comprehensions, async/await, etc.)
- Avoids anti-patterns and code smells

### 2.2 Project Standards
- Matches existing codebase patterns and conventions
- Uses project's preferred libraries and frameworks
- Follows established architectural patterns
- Adheres to team coding guidelines

### 2.3 Documentation Style
- Clear docstrings/comments for public APIs
- Consistent documentation format
- Up-to-date README and inline documentation
- Examples for complex functionality

## 3. Security

### 3.1 Input Validation
- **Sanitization**: All user inputs are validated and sanitized
- **Type checking**: Input types are verified before use
- **Range validation**: Numeric inputs are checked for valid ranges
- **Injection prevention**: SQL/command injection vulnerabilities are prevented

**Example - Secure:**
```python
def get_user(user_id: int) -> User:
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid user_id")
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,))  # Parameterized query
```

**Example - Insecure:**
```python
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection risk
    return db.execute(query)
```

### 3.2 Authentication & Authorization
- Proper authentication checks are in place
- Authorization is verified before sensitive operations
- Session management is secure
- Password handling follows best practices (hashing, salting)

### 3.3 Data Protection
- Sensitive data is encrypted at rest and in transit
- No hardcoded secrets or credentials
- Secure random number generation where needed
- Proper access controls on resources

### 3.4 Common Vulnerabilities
- No XSS (Cross-Site Scripting) vulnerabilities
- No CSRF (Cross-Site Request Forgery) vulnerabilities
- No path traversal vulnerabilities
- No information leakage in error messages
- Dependencies are up-to-date and security-patched

## 4. Performance

### 4.1 Algorithmic Efficiency
- **Time complexity**: Algorithm uses appropriate time complexity for the problem
- **Space complexity**: Memory usage is reasonable for the use case
- **Data structures**: Appropriate data structures are chosen (hash maps vs lists, etc.)

**Example - Efficient:**
```python
def find_duplicates(items: list[str]) -> set[str]:
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return duplicates  # O(n) time complexity
```

**Example - Inefficient:**
```python
def find_duplicates(items: list[str]) -> list[str]:
    duplicates = []
    for i, item in enumerate(items):
        if item in items[i+1:]:  # O(n²) due to repeated slicing
            duplicates.append(item)
    return duplicates
```

### 4.2 Resource Management
- **Database queries**: N+1 queries avoided; appropriate indexing considered
- **Network calls**: Batch requests where possible; caching implemented
- **File I/O**: Files are properly closed; streaming used for large files
- **Memory leaks**: No circular references or unclosed resources

### 4.3 Scalability
- Code handles increasing load gracefully
- No hardcoded limits that would prevent scaling
- Asynchronous operations used where appropriate
- Rate limiting and throttling considered

### 4.4 Optimization Level
- **Premature optimization avoided**: Code is clear first, optimized only when needed
- **Profiling-driven**: Optimizations are based on actual bottlenecks
- **Trade-offs documented**: Performance vs readability trade-offs are explained

## 5. Testing

### 5.1 Test Coverage
- Critical paths have test coverage
- Edge cases are tested
- Error conditions are tested
- Unit tests exist for individual components

### 5.2 Test Quality
- Tests are deterministic (no flaky tests)
- Tests are independent (can run in any order)
- Tests are fast (no unnecessary delays)
- Test names clearly describe what is being tested

### 5.3 Test Maintainability
- Tests use appropriate fixtures and mocking
- Tests avoid duplication through helper functions
- Tests are updated when code changes
- Integration tests verify component interactions

## 6. Architecture & Design

### 6.1 Design Patterns
- Appropriate design patterns are used
- Patterns are applied correctly, not forced
- SOLID principles are followed

### 6.2 Dependencies
- Dependencies are necessary and well-justified
- No circular dependencies
- Dependency versions are pinned or constrained
- License compatibility is verified

### 6.3 API Design
- APIs are intuitive and consistent
- Breaking changes are avoided or documented
- Backward compatibility is maintained where required
- API contracts are clear and documented

## 7. Evaluation Scoring

### Priority Levels

**P0 - Critical (Must Fix)**
- Security vulnerabilities
- Data loss or corruption risks
- Breaking changes without migration path
- Correctness issues affecting core functionality

**P1 - High (Should Fix)**
- Performance issues affecting user experience
- Maintainability issues that block future development
- Missing critical test coverage
- Significant violations of project standards

**P2 - Medium (Nice to Have)**
- Code style inconsistencies
- Minor performance optimizations
- Documentation improvements
- Refactoring opportunities

**P3 - Low (Optional)**
- Naming improvements
- Comment clarity
- Code organization preferences

### Review Decision Matrix

| Criteria Met | Decision | Action |
|--------------|----------|--------|
| All P0, most P1 | **Approve** | Minor feedback for P2/P3 |
| All P0, some P1 | **Approve with Comments** | Request P1 fixes in follow-up |
| P0 issues exist | **Request Changes** | Must fix all P0 before merge |
| Multiple P1 issues | **Request Changes** | Must address P1 concerns |

## 8. Review Checklist

Quick checklist for reviewers:

- [ ] Code compiles/runs without errors
- [ ] Tests pass locally
- [ ] No obvious security vulnerabilities
- [ ] Code follows project style guide
- [ ] Complex logic is explained
- [ ] Edge cases are handled
- [ ] No hardcoded secrets or sensitive data
- [ ] Performance is acceptable for use case
- [ ] Changes are backward compatible (or migration documented)
- [ ] Documentation is updated
- [ ] Tests cover new functionality
- [ ] No unnecessary dependencies added
