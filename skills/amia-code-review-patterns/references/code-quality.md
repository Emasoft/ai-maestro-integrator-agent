# Code Quality Review

## Table of Contents
- When checking if code is readable → Verification Checklist: Readability
- If you need to verify naming conventions → Verification Checklist: Naming Conventions
- When assessing code complexity → Verification Checklist: Code Complexity
- If you're reviewing comments and documentation → Verification Checklist: Comments and Documentation
- When evaluating code organization → Verification Checklist: Code Organization
- If you need to assess error handling → Verification Checklist: Error Handling
- When detecting code quality issues → Verification Checklist: Code Smells
- If you suspect quality problems → Common Issues to Look For

## Purpose
Assess code readability, maintainability, style consistency, and adherence to coding standards to ensure long-term codebase health.

## Verification Checklist

### Readability
- [ ] Code is easy to understand
- [ ] Variable names are descriptive and meaningful
- [ ] Function names clearly indicate purpose
- [ ] Class names follow naming conventions
- [ ] Constants are appropriately named
- [ ] Abbreviations are avoided or explained
- [ ] Code structure is logical and clear
- [ ] Indentation is consistent

### Naming Conventions
- [ ] Consistent case style (camelCase, snake_case, PascalCase)
- [ ] Names reveal intent
- [ ] Boolean names are affirmative (is_valid, has_permission)
- [ ] Functions use verb phrases (get_user, calculate_total)
- [ ] Classes use noun phrases (UserManager, PaymentProcessor)
- [ ] Constants use UPPER_CASE
- [ ] Private members use appropriate prefix/suffix
- [ ] No single-letter names (except loop counters)

### Code Complexity
- [ ] Functions are focused and concise (<50 lines)
- [ ] Cyclomatic complexity is manageable (<10)
- [ ] Nesting depth is reasonable (<4 levels)
- [ ] Number of parameters is limited (<5)
- [ ] No long parameter lists
- [ ] Complex logic is broken into smaller functions
- [ ] Cognitive complexity is low

### Comments and Documentation
- [ ] Code is self-documenting where possible
- [ ] Comments explain "why", not "what"
- [ ] Complex algorithms are explained
- [ ] Public APIs have docstrings
- [ ] Non-obvious code has clarifying comments
- [ ] TODO/FIXME comments have issue numbers
- [ ] No commented-out code
- [ ] No misleading comments

### Code Organization
- [ ] Imports are organized and sorted
- [ ] Related code is grouped together
- [ ] Functions are ordered logically
- [ ] File length is reasonable (<500 lines)
- [ ] One class per file (when appropriate)
- [ ] Utility functions are properly grouped
- [ ] Constants are defined at module level

### Error Handling
- [ ] Errors are handled explicitly
- [ ] Error messages are clear and actionable
- [ ] Exceptions are appropriate types
- [ ] No bare except clauses
- [ ] Resources are cleaned up properly
- [ ] Error handling doesn't hide bugs
- [ ] Errors are logged appropriately

### Code Smells
- [ ] No duplicated code
- [ ] No magic numbers or strings
- [ ] No deeply nested conditionals
- [ ] No long methods
- [ ] No large classes
- [ ] No dead code
- [ ] No commented-out code
- [ ] No unnecessary complexity

## Common Issues to Look For

### Poor Naming

**Unclear variable names**
```python
# WRONG: Unclear abbreviations
def calc(a, b, c):
    t = a * b
    r = t - c
    return r

# CORRECT: Descriptive names
def calculate_net_price(unit_price, quantity, discount):
    subtotal = unit_price * quantity
    net_price = subtotal - discount
    return net_price
```

**Non-descriptive function names**
```python
# WRONG: Doesn't describe what it does
def process(data):
    return [x * 2 for x in data]

# CORRECT: Clear purpose
def double_values(numbers):
    return [number * 2 for number in numbers]
```

**Misleading names**
```python
# WRONG: Name doesn't match behavior
def get_user(user_id):
    user = database.fetch(user_id)
    user.last_accessed = datetime.now()
    database.save(user)  # Unexpected side effect
    return user

# CORRECT: Name reveals side effect
def get_and_update_user_access_time(user_id):
    user = database.fetch(user_id)
    user.last_accessed = datetime.now()
    database.save(user)
    return user
```

### Excessive Complexity

**Too many parameters**
```python
# WRONG: Too many parameters
def create_user(name, email, age, address, city, state, zip, phone, role, department, manager):
    pass

# CORRECT: Use object/dataclass
@dataclass
class UserData:
    name: str
    email: str
    age: int
    address: Address
    contact: ContactInfo
    employment: EmploymentInfo

def create_user(user_data: UserData):
    pass
```

**Deep nesting**
```python
# WRONG: Deep nesting
def process_order(order):
    if order:
        if order.is_valid():
            if order.has_items():
                if order.customer:
                    if order.customer.is_active():
                        return process(order)
    return None

# CORRECT: Early returns
def process_order(order):
    if not order:
        return None
    if not order.is_valid():
        return None
    if not order.has_items():
        return None
    if not order.customer or not order.customer.is_active():
        return None
    return process(order)
```

**Long functions**
```python
# WRONG: Function does too much
def handle_request(request):
    # 100+ lines of code
    # Parse request
    # Validate input
    # Process business logic
    # Format response
    # Log activity
    # Send notifications
    # Update analytics

# CORRECT: Split into focused functions
def handle_request(request):
    data = parse_request(request)
    validate_input(data)
    result = process_business_logic(data)
    response = format_response(result)
    log_and_notify(request, result)
    return response
```

### Poor Comments

**Obvious comments**
```python
# WRONG: States the obvious
# Increment counter
counter = counter + 1

# Loop through users
for user in users:
    # Print user name
    print(user.name)

# CORRECT: Self-documenting code
counter += 1
for user in users:
    print(user.name)
```

**Misleading comments**
```python
# WRONG: Comment doesn't match code
# Calculate average
total = sum(values)

# CORRECT: Comment matches code
# Calculate sum (average calculated later)
total = sum(values)
```

**Commented-out code**
```python
# WRONG: Dead code left in
def process(data):
    # old_method(data)
    # result = legacy_process(data)
    # if result:
    #     return result
    return new_method(data)

# CORRECT: Remove dead code
def process(data):
    return new_method(data)
```

### Magic Numbers

**Unexplained constants**
```python
# WRONG: Magic numbers
if status == 3:
    send_notification()
if retry_count > 5:
    fail()
sleep(86400)

# CORRECT: Named constants
STATUS_APPROVED = 3
MAX_RETRIES = 5
SECONDS_PER_DAY = 86400

if status == STATUS_APPROVED:
    send_notification()
if retry_count > MAX_RETRIES:
    fail()
sleep(SECONDS_PER_DAY)
```

### Code Duplication

**Repeated logic**
```python
# WRONG: Duplicated code
def process_admin_user(user):
    user.validate()
    user.normalize_email()
    user.set_defaults()
    user.role = "admin"
    user.save()

def process_regular_user(user):
    user.validate()
    user.normalize_email()
    user.set_defaults()
    user.role = "user"
    user.save()

# CORRECT: Extract common logic
def prepare_user(user):
    user.validate()
    user.normalize_email()
    user.set_defaults()

def process_admin_user(user):
    prepare_user(user)
    user.role = "admin"
    user.save()

def process_regular_user(user):
    prepare_user(user)
    user.role = "user"
    user.save()
```

### Poor Error Handling

**Silent failures**
```python
# WRONG: Swallows all exceptions
try:
    process_payment()
except:
    pass

# CORRECT: Explicit error handling
try:
    process_payment()
except PaymentError as e:
    logger.error(f"Payment failed: {e}")
    notify_admin(e)
    raise
```

**Vague error messages**
```python
# WRONG: Unhelpful message
raise ValueError("Invalid input")

# CORRECT: Specific message
raise ValueError(f"Email '{email}' is invalid: must contain @ symbol")
```

## Scoring Criteria

### Critical (Must Fix)
- Misleading names
- Silently swallowed exceptions
- Security-sensitive magic values
- Extremely long functions (>100 lines)
- Very deep nesting (>5 levels)
- Critical duplicated logic
- Completely missing error handling

### High Priority (Should Fix)
- Unclear variable/function names
- Magic numbers in business logic
- Code duplication
- Functions with too many parameters
- Deep nesting (4-5 levels)
- Long functions (50-100 lines)
- Missing comments on complex code
- Bare except clauses

### Medium Priority (Consider Fixing)
- Minor naming improvements
- Moderate complexity (cyclomatic > 10)
- Long parameter lists (5-7 parameters)
- File length issues (>500 lines)
- Inconsistent formatting
- Missing docstrings
- Commented-out code

### Low Priority (Nice to Have)
- Additional self-documentation
- Improved code organization
- More descriptive names
- Better comment placement
- Formatting consistency
- Minor refactoring opportunities

## Review Questions

1. Can you understand the code without extensive comments?
2. Are names self-explanatory?
3. Is the code complexity manageable?
4. Are functions focused on single tasks?
5. Is error handling explicit and clear?
6. Are there any code smells present?
7. Is the code DRY (Don't Repeat Yourself)?
8. Are magic numbers explained?
9. Is the code formatted consistently?
10. Would a new developer understand this code?

## Red Flags

- Functions longer than 50 lines
- Nesting deeper than 4 levels
- More than 5 function parameters
- Single-letter variable names (except i, j, k in loops)
- Bare except clauses
- Commented-out code
- Magic numbers in logic
- Duplicated code blocks
- Functions doing multiple things
- Classes longer than 300 lines
- Files longer than 500 lines
- Cryptic abbreviations
- Misleading function names
- No error handling
- Silent failures

## Code Quality Metrics

### Complexity Metrics
- **Cyclomatic Complexity**: Number of independent paths (<10 preferred)
- **Cognitive Complexity**: Effort to understand code (<15 preferred)
- **Nesting Depth**: Maximum indentation levels (<4 preferred)
- **Function Length**: Lines of code per function (<50 preferred)
- **Class Length**: Lines of code per class (<300 preferred)
- **File Length**: Lines of code per file (<500 preferred)

### Maintainability Metrics
- **Code Duplication**: Percentage of duplicated code (<3% target)
- **Comment Density**: Comments per code lines (10-20% range)
- **Test Coverage**: Percentage of code tested (>80% target)
- **Documentation Coverage**: Percentage of public APIs documented (100% target)

## Best Practices

- Use meaningful, descriptive names that reveal intent
- Keep functions small and focused (single responsibility)
- Limit function parameters to 3-5 maximum
- Avoid deep nesting; use early returns
- Extract complex conditions into named functions
- Use constants instead of magic numbers
- Write self-documenting code; add comments for "why"
- Handle errors explicitly; never ignore exceptions
- Follow language-specific style guides consistently
- Remove commented-out code; use version control
- Break up large files and classes
- Organize imports and dependencies
- Keep cognitive complexity low
- Refactor when complexity grows
- Use linters and formatters automatically
