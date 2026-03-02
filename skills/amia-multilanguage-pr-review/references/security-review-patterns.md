# Security Review Patterns

Security-focused code review patterns for identifying vulnerabilities and security issues across multiple languages.

---

## Table of Contents

- 1. Input Validation
  - 1.1 If reviewing user input handling
  - 1.2 If reviewing file path operations
  - 1.3 If reviewing SQL queries
- 2. Authentication and Authorization
  - 2.1 If reviewing authentication flows
  - 2.2 If reviewing authorization checks
  - 2.3 If reviewing session management
- 3. Secrets Management
  - 3.1 If secrets are hardcoded
  - 3.2 If environment variables are mishandled
  - 3.3 If secrets are logged
- 4. Language-Specific Security
  - 4.1 If reviewing Python code for security
  - 4.2 If reviewing JavaScript/TypeScript for security
  - 4.3 If reviewing shell scripts for security
  - 4.4 If reviewing Go code for security
  - 4.5 If reviewing Rust code for security

---

## 1. Input Validation

### 1.1 If reviewing user input handling

**Check for**:
- Input length limits
- Character allowlists/blocklists
- Type validation
- Encoding handling

**Red flags**:
```python
# WRONG - no validation
user_input = request.get("name")
db.execute(f"INSERT INTO users (name) VALUES ('{user_input}')")

# CORRECT - parameterized query
db.execute("INSERT INTO users (name) VALUES (?)", [user_input])
```

### 1.2 If reviewing file path operations

**Check for path traversal**:
```python
# WRONG - allows ../../../etc/passwd
file_path = os.path.join(BASE_DIR, user_input)

# CORRECT - validate path
safe_path = os.path.realpath(os.path.join(BASE_DIR, user_input))
if not safe_path.startswith(os.path.realpath(BASE_DIR)):
    raise SecurityError("Path traversal attempt")
```

### 1.3 If reviewing SQL queries

**Check for SQL injection**:
- Use parameterized queries ALWAYS
- Never string-concatenate user input
- Validate and sanitize even with ORMs

---

## 2. Authentication and Authorization

### 2.1 If reviewing authentication flows

**Check for**:
- Password hashing (bcrypt, argon2)
- Timing-safe comparisons
- Rate limiting
- Account lockout after failed attempts

### 2.2 If reviewing authorization checks

**Check for**:
- IDOR (Insecure Direct Object References)
- Missing authorization on endpoints
- Role/permission bypass opportunities

### 2.3 If reviewing session management

**Check for**:
- Secure session IDs (random, sufficient entropy)
- HTTPOnly and Secure cookie flags
- Session expiration
- Session invalidation on logout

---

## 3. Secrets Management

### 3.1 If secrets are hardcoded

**Red flags**:
```python
# WRONG
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgres://user:password@host/db"
```

**Correct approach**:
```python
# CORRECT - environment variables
API_KEY = os.environ.get("API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")
```

### 3.2 If environment variables are mishandled

**Check for**:
- Secrets printed to stdout/logs
- Secrets in error messages
- Secrets in stack traces

### 3.3 If secrets are logged

**Check logging code for**:
```python
# WRONG
logger.info(f"Connecting with API key: {api_key}")

# CORRECT
logger.info("Connecting to API (key configured)")
```

---

## 4. Language-Specific Security

### 4.1 If reviewing Python code for security

**Check for**:
- `eval()`, `exec()` with user input
- `pickle` with untrusted data
- `subprocess.shell=True` with user input
- `yaml.load()` without SafeLoader

### 4.2 If reviewing JavaScript/TypeScript for security

**Check for**:
- `eval()`, `Function()` with user input
- `innerHTML` with unsanitized content
- Missing CSRF tokens
- Prototype pollution

### 4.3 If reviewing shell scripts for security

**Check for**:
- Unquoted variables: `$var` vs `"$var"`
- Command injection: `eval "$user_input"`
- Unsafe temp file creation

**See also**: [shell-review-patterns.md](shell-review-patterns.md) for complete shell review checklist.

### 4.4 If reviewing Go code for security

**Check for**:
- SQL injection in raw queries
- Path traversal in file operations
- Missing TLS verification
- Race conditions with goroutines

### 4.5 If reviewing Rust code for security

**Check for**:
- Unsafe blocks without justification
- Unchecked `.unwrap()` on user input
- Memory safety issues in FFI code

---

## Security Review Checklist

- [ ] Input validation on all user-controlled data
- [ ] Parameterized queries for all database operations
- [ ] No hardcoded secrets in code
- [ ] Proper authentication and authorization checks
- [ ] Secure session management
- [ ] No sensitive data in logs
- [ ] Path traversal protection for file operations
- [ ] HTTPS/TLS for all external communications
- [ ] Rate limiting on authentication endpoints
- [ ] Error messages don't leak sensitive info

---

## See Also

- [shell-review-patterns.md](shell-review-patterns.md) - Shell script patterns
- [python-review-patterns.md](python-review-patterns.md) - Python patterns
- [javascript-review-patterns.md](javascript-review-patterns.md) - JavaScript patterns
