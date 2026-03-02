# Architecture and Design Review

## Table of Contents
- When evaluating SOLID principles adherence → Verification Checklist: Architectural Principles
- If you're concerned about code organization → Verification Checklist: Code Organization
- When verifying design patterns are appropriate → Verification Checklist: Design Patterns
- If you need to review API design → Verification Checklist: API Design
- When assessing data structure choices → Verification Checklist: Data Structures
- If you're checking dependencies → Verification Checklist: Dependencies
- If you suspect architecture issues → Common Issues to Look For
- When prioritizing fixes → Scoring Criteria
- If you're unsure about the design → Review Questions
- If you see warning signs → Red Flags
- When identifying design problems → Architecture Smells

## Purpose
Evaluate the structural design, architectural patterns, and design decisions to ensure the code is maintainable, scalable, and follows established patterns.

## Verification Checklist

### Architectural Principles
- [ ] Single Responsibility Principle (SRP) is followed
- [ ] Open/Closed Principle (OCP) is respected
- [ ] Liskov Substitution Principle (LSP) is maintained
- [ ] Interface Segregation Principle (ISP) is applied
- [ ] Dependency Inversion Principle (DIP) is used
- [ ] Don't Repeat Yourself (DRY) is enforced
- [ ] You Aren't Gonna Need It (YAGNI) is considered
- [ ] Keep It Simple, Stupid (KISS) is applied

### Code Organization
- [ ] Code is organized into logical modules/packages
- [ ] Related functionality is grouped together
- [ ] Clear separation of concerns
- [ ] Appropriate abstraction levels
- [ ] Minimal coupling between modules
- [ ] High cohesion within modules
- [ ] Clear dependency direction
- [ ] No circular dependencies

### Design Patterns
- [ ] Appropriate patterns are used
- [ ] Patterns are implemented correctly
- [ ] Patterns solve actual problems (not over-engineered)
- [ ] Pattern choice is justified
- [ ] No anti-patterns present
- [ ] Patterns are used consistently
- [ ] Custom patterns are documented

### API Design
- [ ] APIs are intuitive and easy to use
- [ ] Function signatures are clear
- [ ] Parameter order is logical
- [ ] Return types are appropriate
- [ ] Error handling is consistent
- [ ] API versioning is considered
- [ ] Breaking changes are avoided
- [ ] Backward compatibility is maintained

### Data Structures
- [ ] Appropriate data structures chosen
- [ ] Time complexity is acceptable
- [ ] Space complexity is reasonable
- [ ] Data structure choice is justified
- [ ] Collections are used correctly
- [ ] Immutability is used where appropriate
- [ ] Data encapsulation is proper

### Dependencies
- [ ] Dependencies are minimal and justified
- [ ] Dependency versions are specified
- [ ] No unnecessary dependencies
- [ ] Dependencies are up-to-date
- [ ] License compatibility is verified
- [ ] Transitive dependencies are reviewed
- [ ] Vendor lock-in is avoided

## Common Issues to Look For

### Violation of SOLID Principles

**Single Responsibility Principle violation**
```python
# WRONG: Class does too many things
class UserManager:
    def authenticate(self, credentials):
        pass
    def send_email(self, user, message):
        pass
    def log_activity(self, action):
        pass
    def generate_report(self):
        pass

# CORRECT: Each class has one responsibility
class Authenticator:
    def authenticate(self, credentials):
        pass

class EmailService:
    def send_email(self, user, message):
        pass

class ActivityLogger:
    def log(self, action):
        pass

class ReportGenerator:
    def generate(self):
        pass
```

**Dependency Inversion violation**
```python
# WRONG: High-level module depends on low-level
class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Concrete dependency

# CORRECT: Depend on abstraction
class UserService:
    def __init__(self, database: DatabaseInterface):
        self.db = database  # Abstract dependency
```

### Poor Abstraction

**Leaky abstraction**
```python
# WRONG: Implementation details leak through
class DataStore:
    def get_user(self, user_id):
        cursor = self.connection.cursor()  # SQL details exposed
        cursor.execute("SELECT * FROM users WHERE id = ?", user_id)
        return cursor.fetchone()

# CORRECT: Hide implementation details
class DataStore:
    def get_user(self, user_id) -> User:
        return self._fetch_user_by_id(user_id)
```

**Wrong abstraction level**
```python
# WRONG: Too low-level for the abstraction
class PaymentProcessor:
    def process(self, payment):
        bytes_data = payment.encode('utf-8')  # Too low-level
        socket.send(bytes_data)

# CORRECT: Appropriate abstraction level
class PaymentProcessor:
    def process(self, payment: Payment):
        self.gateway.submit(payment)
```

### Tight Coupling

**Direct dependencies**
```python
# WRONG: Classes tightly coupled
class OrderProcessor:
    def __init__(self):
        self.email = EmailSender()
        self.inventory = InventorySystem()
        self.payment = PaymentGateway()

# CORRECT: Dependency injection
class OrderProcessor:
    def __init__(self, email_service, inventory_service, payment_service):
        self.email = email_service
        self.inventory = inventory_service
        self.payment = payment_service
```

**Global state**
```python
# WRONG: Global state creates coupling
config = GlobalConfig()

class Service:
    def process(self):
        value = config.get('setting')

# CORRECT: Pass configuration explicitly
class Service:
    def __init__(self, config):
        self.config = config

    def process(self):
        value = self.config.get('setting')
```

### Poor Code Organization

**Mixed concerns**
```python
# WRONG: UI, business logic, and data access mixed
def handle_submit():
    username = request.form['username']  # UI layer
    if len(username) < 3:  # Business logic
        return "Error"
    db.execute("INSERT INTO users...")  # Data layer

# CORRECT: Separated concerns
def handle_submit():
    username = extract_username(request)
    user = create_user(username)
    save_user(user)
```

**God object**
```python
# WRONG: One class does everything
class Application:
    def setup_database(self):
        pass
    def handle_requests(self):
        pass
    def send_emails(self):
        pass
    def generate_reports(self):
        pass
    def manage_cache(self):
        pass

# CORRECT: Distributed responsibilities
class Application:
    def __init__(self, db, router, email, reports, cache):
        self.db = db
        self.router = router
        self.email = email
        self.reports = reports
        self.cache = cache
```

### Anti-Patterns

**Spaghetti code**
```python
# WRONG: Complex, tangled control flow
def process():
    if x:
        if y:
            if z:
                for i in range(n):
                    if condition:
                        while True:
                            if break_condition:
                                break

# CORRECT: Simplified, clear flow
def process():
    if not should_process():
        return

    items = get_items()
    for item in items:
        process_item(item)
```

**Magic numbers/strings**
```python
# WRONG: Unexplained literals
if status == 42:
    process()
if type == "ACTV":
    activate()

# CORRECT: Named constants
STATUS_APPROVED = 42
TYPE_ACTIVE = "ACTV"

if status == STATUS_APPROVED:
    process()
if type == TYPE_ACTIVE:
    activate()
```

## Scoring Criteria

### Critical (Must Fix)
- Violations of core architectural principles
- Circular dependencies
- Tight coupling that prevents testing
- Leaky abstractions that expose internals
- God objects that do everything
- Spaghetti code with tangled control flow
- Missing separation of concerns

### High Priority (Should Fix)
- Poor abstraction choices
- Unnecessary dependencies
- Code duplication across modules
- Inconsistent design patterns
- Poor API design
- Inadequate encapsulation
- Wrong data structure choice

### Medium Priority (Consider Fixing)
- Minor SOLID principle violations
- Suboptimal design patterns
- Slightly tight coupling
- Room for better abstractions
- Opportunities for refactoring
- Inconsistent naming conventions
- Missing design documentation

### Low Priority (Nice to Have)
- Potential future scalability improvements
- Alternative design pattern suggestions
- Code organization improvements
- Additional abstraction opportunities
- Optimization of dependency graph

## Review Questions

1. Does the architecture support the requirements?
2. Are SOLID principles followed appropriately?
3. Is the code organized logically?
4. Are abstractions at the right level?
5. Is coupling minimized between modules?
6. Is cohesion high within modules?
7. Are design patterns used correctly?
8. Is the API design intuitive?
9. Are dependencies justified and minimal?
10. Can the design scale with requirements?

## Red Flags

- Classes with too many responsibilities
- Functions with too many parameters (>5)
- Deep inheritance hierarchies (>3 levels)
- Circular dependencies between modules
- Global state used extensively
- Hard-coded configuration values
- Mixed abstraction levels in same function
- Tight coupling to specific implementations
- Large switch/if-else chains for type checking
- Duplicated logic across multiple modules

## Architecture Smells

### Structural Smells
- **Cyclic Dependency**: Modules depend on each other cyclically
- **Unstable Dependency**: Depending on less stable modules
- **God Class**: One class doing too much
- **Feature Envy**: Method using more features of another class
- **Inappropriate Intimacy**: Classes too tightly coupled

### Design Smells
- **Refused Bequest**: Subclass doesn't use inherited methods
- **Lazy Class**: Class doing too little to justify existence
- **Speculative Generality**: Over-engineering for future needs
- **Primitive Obsession**: Using primitives instead of objects
- **Data Class**: Class with only data, no behavior

### Implementation Smells
- **Long Method**: Method too long (>20 lines)
- **Long Parameter List**: Too many parameters (>5)
- **Large Class**: Class too large (>300 lines)
- **Duplicated Code**: Same code in multiple places
- **Dead Code**: Unused code still present

## Best Practices

- Follow established architectural patterns consistently
- Keep classes focused on single responsibility
- Prefer composition over inheritance
- Design for interfaces, not implementations
- Minimize dependencies between modules
- Use dependency injection for flexibility
- Keep abstraction levels consistent
- Encapsulate what varies
- Program to interfaces, not implementations
- Apply patterns when they solve actual problems
- Document architectural decisions
- Review dependency graph regularly
- Refactor when complexity grows
- Keep modules loosely coupled
- Maintain high cohesion within modules
