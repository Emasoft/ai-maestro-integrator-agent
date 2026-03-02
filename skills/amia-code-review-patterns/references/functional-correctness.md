# Functional Correctness Review

## Table of Contents
- When you need to verify core functionality → Verification Checklist: Core Functionality
- If you need to check logic correctness → Verification Checklist: Logic Correctness
- When reviewing data flow → Verification Checklist: Data Flow
- If you're concerned about input validation → Verification Checklist: Input Validation
- When verifying output → Verification Checklist: Output Verification
- If you suspect logic errors → Common Issues to Look For

## Purpose
Verify that code implements the intended functionality correctly, handles edge cases appropriately, and produces expected outputs for given inputs.

## Verification Checklist

### Core Functionality
- [ ] Code implements all requirements from the specification or issue
- [ ] All documented features are present and working
- [ ] Function signatures match their documented behavior
- [ ] Return values match expected types and formats
- [ ] Error conditions are handled appropriately
- [ ] Edge cases are addressed (null, empty, boundary values)
- [ ] Default values are sensible and documented
- [ ] Optional parameters work as expected

### Logic Correctness
- [ ] Conditional logic is correct (no inverted conditions)
- [ ] Loop boundaries are correct (no off-by-one errors)
- [ ] Recursion has proper base cases and termination
- [ ] Mathematical operations are accurate
- [ ] String operations handle encoding correctly
- [ ] Date/time calculations account for timezones and DST
- [ ] Floating point comparisons use appropriate epsilon
- [ ] Integer overflow/underflow is prevented

### Data Flow
- [ ] Variables are initialized before use
- [ ] Data transformations preserve correctness
- [ ] Type conversions are safe and intentional
- [ ] State transitions are valid
- [ ] Invariants are maintained throughout execution
- [ ] Side effects are intentional and documented
- [ ] Data races are prevented in concurrent code

### Input Validation
- [ ] All inputs are validated before use
- [ ] Input ranges are enforced
- [ ] Input formats are verified
- [ ] Malformed input is rejected gracefully
- [ ] User input is sanitized appropriately
- [ ] File paths are validated and sanitized
- [ ] Database queries are parameterized

### Output Verification
- [ ] Output format matches specification
- [ ] Output encoding is correct
- [ ] Output is complete (no truncation)
- [ ] Output handles special characters correctly
- [ ] Error messages are clear and actionable
- [ ] Logging provides adequate context
- [ ] Return codes/status are meaningful

## Common Issues to Look For

### Logic Errors
**Off-by-one errors**
```python
# WRONG: Misses last element
for i in range(len(items) - 1):
    process(items[i])

# CORRECT: Processes all elements
for i in range(len(items)):
    process(items[i])
```

**Inverted conditions**
```python
# WRONG: Logic is backwards
if user.is_authenticated():
    return "Access denied"

# CORRECT: Proper logic flow
if not user.is_authenticated():
    return "Access denied"
```

**Incorrect boolean logic**
```python
# WRONG: Should be OR, not AND
if status == "active" and status == "pending":
    process()

# CORRECT: Proper boolean operator
if status == "active" or status == "pending":
    process()
```

### Edge Case Failures
**Null/None handling**
```python
# WRONG: No null check
def get_name(user):
    return user.name.upper()

# CORRECT: Handles None
def get_name(user):
    if user is None or user.name is None:
        return ""
    return user.name.upper()
```

**Empty collection handling**
```python
# WRONG: Assumes non-empty
def get_first(items):
    return items[0]

# CORRECT: Checks for empty
def get_first(items):
    if not items:
        return None
    return items[0]
```

**Boundary value errors**
```python
# WRONG: Doesn't handle min/max
def validate_age(age):
    return age > 0

# CORRECT: Proper range check
def validate_age(age):
    return 0 <= age <= 150
```

### Type Errors
**Unsafe type conversions**
```python
# WRONG: Can raise ValueError
age = int(user_input)

# CORRECT: Handles conversion errors
try:
    age = int(user_input)
except ValueError:
    return "Invalid age format"
```

**Type mismatches**
```python
# WRONG: Mixing types
result = "Count: " + count

# CORRECT: Explicit conversion
result = "Count: " + str(count)
```

### State Management
**Uninitialized variables**
```python
# WRONG: total might be undefined
if condition:
    total = calculate()
return total

# CORRECT: Initialize first
total = 0
if condition:
    total = calculate()
return total
```

**Invalid state transitions**
```python
# WRONG: Allows invalid state change
def cancel_order(order):
    order.status = "cancelled"

# CORRECT: Validates state transition
def cancel_order(order):
    if order.status not in ["pending", "confirmed"]:
        raise InvalidStateError("Cannot cancel shipped order")
    order.status = "cancelled"
```

## Scoring Criteria

### Critical (Must Fix)
- Logic errors that produce incorrect results
- Missing validation that allows invalid data
- Edge cases that cause crashes or data corruption
- Type errors that cause runtime failures
- Race conditions in concurrent code
- Security vulnerabilities from logic flaws

### High Priority (Should Fix)
- Missing edge case handling
- Incomplete error handling
- Unsafe type conversions
- Missing input validation
- Inadequate output verification
- State management issues

### Medium Priority (Consider Fixing)
- Missing null checks in non-critical paths
- Redundant validations
- Overly permissive validations
- Missing boundary checks
- Inconsistent error handling

### Low Priority (Nice to Have)
- Additional defensive checks
- More detailed error messages
- Enhanced logging
- Additional edge case coverage

## Review Questions

1. Does the code do what it claims to do?
2. Have all edge cases been identified and handled?
3. Are all inputs validated appropriately?
4. Are outputs correct and complete?
5. Does error handling cover all failure modes?
6. Are type conversions safe and correct?
7. Is the logic flow clear and correct?
8. Are state transitions valid?
9. Have boundary conditions been tested?
10. Does concurrent code avoid race conditions?

## Red Flags

- Functions that are too complex to verify correctness
- Missing validation on user input
- Unchecked type conversions
- No error handling for external calls
- Assumptions about data that aren't validated
- Magic numbers without explanation
- Complex boolean logic without tests
- State changes without validation
- Resource leaks (unclosed files, connections)
- Floating point equality comparisons

## Best Practices

- Write tests that verify correctness for normal, edge, and error cases
- Use assertions to document and verify invariants
- Validate inputs at system boundaries
- Handle errors explicitly, don't ignore them
- Use type hints/annotations to catch type errors early
- Document assumptions and preconditions
- Prefer simple, obvious logic over clever code
- Use meaningful variable names that clarify intent
- Break complex logic into smaller, testable functions
- Review mathematical operations for correctness
