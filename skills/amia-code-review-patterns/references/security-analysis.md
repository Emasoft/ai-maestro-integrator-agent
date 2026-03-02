# Security Analysis Review

## Table of Contents
- When validating input handling → Verification Checklist: Input Validation
- If you're reviewing authentication and authorization → Verification Checklist: Authentication & Authorization
- When checking sensitive data protection → Verification Checklist: Data Protection
- If you're concerned about SQL injection → Verification Checklist: SQL Injection Prevention
- When verifying XSS protection → Verification Checklist: XSS Prevention
- If you need to check CSRF protection → Verification Checklist: CSRF Protection
- When reviewing cryptography usage → Verification Checklist: Cryptography
- If you're assessing dependency security → Verification Checklist: Dependency Security
- When identifying security vulnerabilities → Common Issues to Look For

## Purpose
Identify security vulnerabilities, assess risk exposure, and ensure code follows security best practices to protect against common attacks.

## Verification Checklist

### Input Validation
- [ ] All user input is validated
- [ ] Input length limits enforced
- [ ] Input type checking performed
- [ ] Whitelist validation used over blacklist
- [ ] Special characters handled properly
- [ ] File uploads validated (type, size, content)
- [ ] Path traversal prevented
- [ ] Command injection prevented

### Authentication & Authorization
- [ ] Authentication required for protected resources
- [ ] Password strength requirements enforced
- [ ] Password hashing uses modern algorithms (bcrypt, Argon2)
- [ ] No hardcoded credentials
- [ ] Session management secure
- [ ] Authorization checks on all operations
- [ ] Principle of least privilege followed
- [ ] Multi-factor authentication supported

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] Sensitive data encrypted in transit (TLS)
- [ ] No sensitive data in logs
- [ ] No sensitive data in error messages
- [ ] Database credentials secured
- [ ] API keys not hardcoded
- [ ] Secrets management system used
- [ ] PII handling complies with regulations

### SQL Injection Prevention
- [ ] Parameterized queries used
- [ ] ORM used correctly
- [ ] No string concatenation for queries
- [ ] Input sanitized before queries
- [ ] Stored procedures parameterized
- [ ] Error messages don't reveal schema
- [ ] Database user has minimal privileges

### XSS Prevention
- [ ] Output encoding applied
- [ ] User input escaped in HTML
- [ ] Content Security Policy implemented
- [ ] No dangerous innerHTML usage
- [ ] Template engines auto-escape by default
- [ ] Sanitization libraries used
- [ ] No eval() with user input

### CSRF Protection
- [ ] CSRF tokens implemented
- [ ] Same-site cookie attribute set
- [ ] State-changing operations require POST
- [ ] Origin header validated
- [ ] Double-submit cookie pattern used
- [ ] Referer header checked
- [ ] Synchronizer token pattern implemented

### Cryptography
- [ ] Strong algorithms used (AES-256, RSA-2048+)
- [ ] No deprecated algorithms (MD5, SHA1 for security)
- [ ] Proper key management
- [ ] Secure random number generation
- [ ] Initialization vectors properly used
- [ ] TLS 1.2+ only
- [ ] Certificate validation enabled

### Dependency Security
- [ ] Dependencies up to date
- [ ] Known vulnerabilities checked
- [ ] Dependency scanning automated
- [ ] Supply chain attacks considered
- [ ] License compliance verified
- [ ] Minimal dependencies used
- [ ] Dependency pinning implemented

## Common Issues to Look For

### SQL Injection

**Vulnerable string concatenation**
```python
# WRONG: SQL injection vulnerability
user_id = request.get('user_id')
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)

# Attacker input: "1 OR 1=1"
# Results in: SELECT * FROM users WHERE id = 1 OR 1=1

# CORRECT: Parameterized query
user_id = request.get('user_id')
query = "SELECT * FROM users WHERE id = ?"
db.execute(query, (user_id,))
```

**ORM misuse**
```python
# WRONG: Using raw queries with user input
search = request.get('search')
User.objects.raw(f"SELECT * FROM users WHERE name LIKE '%{search}%'")

# CORRECT: Use ORM properly
search = request.get('search')
User.objects.filter(name__contains=search)
```

### XSS (Cross-Site Scripting)

**Unescaped output**
```python
# WRONG: Direct output of user input
@app.route('/hello')
def hello():
    name = request.args.get('name')
    return f"<h1>Hello {name}</h1>"

# Attacker input: <script>alert('XSS')</script>

# CORRECT: Escape output
from html import escape

@app.route('/hello')
def hello():
    name = request.args.get('name')
    return f"<h1>Hello {escape(name)}</h1>"
```

**Dangerous innerHTML**
```javascript
// WRONG: XSS vulnerability
const comment = userInput;
element.innerHTML = comment;

// CORRECT: Use textContent or sanitize
element.textContent = comment;
// OR
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(comment);
```

### Authentication Issues

**Weak password hashing**
```python
# WRONG: Weak hashing
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# CORRECT: Strong modern hashing
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

**Hardcoded credentials**
```python
# WRONG: Hardcoded secrets
API_KEY = "sk_live_1234567890abcdef"
DATABASE_URL = "postgresql://admin:password123@localhost/db"

# CORRECT: Environment variables
import os
API_KEY = os.environ.get('API_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')
```

**Missing authentication**
```python
# WRONG: No authentication check
@app.route('/admin/delete-user/<user_id>')
def delete_user(user_id):
    User.delete(user_id)
    return "Deleted"

# CORRECT: Require authentication and authorization
@app.route('/admin/delete-user/<user_id>')
@require_auth
@require_role('admin')
def delete_user(user_id):
    User.delete(user_id)
    return "Deleted"
```

### Authorization Issues

**Missing authorization checks**
```python
# WRONG: No ownership verification
@app.route('/document/<doc_id>')
def get_document(doc_id):
    doc = Document.get(doc_id)
    return doc.content

# CORRECT: Verify user owns document
@app.route('/document/<doc_id>')
@login_required
def get_document(doc_id):
    doc = Document.get(doc_id)
    if doc.owner_id != current_user.id:
        abort(403)
    return doc.content
```

**Insecure Direct Object Reference**
```python
# WRONG: Predictable IDs expose data
@app.route('/api/order/<order_id>')
def get_order(order_id):
    return Order.get(order_id).to_json()

# User can guess other order IDs

# CORRECT: Use UUIDs and verify ownership
@app.route('/api/order/<order_uuid>')
@login_required
def get_order(order_uuid):
    order = Order.get_by_uuid(order_uuid)
    if order.user_id != current_user.id:
        abort(403)
    return order.to_json()
```

### Path Traversal

**Unvalidated file paths**
```python
# WRONG: Path traversal vulnerability
@app.route('/download/<filename>')
def download(filename):
    return send_file(f'/uploads/{filename}')

# Attacker input: ../../etc/passwd

# CORRECT: Validate and sanitize path
from werkzeug.utils import secure_filename
import os

@app.route('/download/<filename>')
def download(filename):
    safe_name = secure_filename(filename)
    file_path = os.path.join('/uploads', safe_name)
    if not file_path.startswith('/uploads/'):
        abort(400)
    return send_file(file_path)
```

### Command Injection

**Unsanitized shell commands**
```python
# WRONG: Command injection vulnerability
import os
filename = request.get('filename')
os.system(f'cat {filename}')

# Attacker input: "file.txt; rm -rf /"

# CORRECT: Use safe APIs
import subprocess
filename = request.get('filename')
# Validate filename first
subprocess.run(['cat', filename], check=True)
```

### Information Disclosure

**Verbose error messages**
```python
# WRONG: Exposes internal details
try:
    db.execute(query)
except Exception as e:
    return str(e)  # Reveals database structure

# CORRECT: Generic error message
try:
    db.execute(query)
except Exception as e:
    logger.error(f"Database error: {e}")
    return "An error occurred", 500
```

**Sensitive data in logs**
```python
# WRONG: Logs sensitive data
logger.info(f"User {user.email} logged in with password {password}")

# CORRECT: Don't log sensitive data
logger.info(f"User {user.email} logged in successfully")
```

### Cryptographic Issues

**Weak algorithms**
```python
# WRONG: Weak encryption
from Crypto.Cipher import DES
cipher = DES.new(key)

# CORRECT: Strong encryption
from Crypto.Cipher import AES
cipher = AES.new(key, AES.MODE_GCM)
```

**Predictable randomness**
```python
# WRONG: Predictable random
import random
token = random.randint(1000, 9999)

# CORRECT: Cryptographically secure random
import secrets
token = secrets.token_urlsafe(32)
```

## Scoring Criteria

### Critical (Must Fix)
- SQL injection vulnerabilities
- XSS vulnerabilities
- Authentication bypass
- Authorization bypass
- Hardcoded credentials
- Command injection
- Path traversal
- Remote code execution risks
- Insecure cryptography (MD5, DES, etc.)

### High Priority (Should Fix)
- Missing authentication on sensitive endpoints
- Missing authorization checks
- Weak password hashing
- Missing CSRF protection
- Information disclosure
- Insecure session management
- Missing input validation
- Known vulnerable dependencies
- Sensitive data in logs

### Medium Priority (Consider Fixing)
- Weak password requirements
- Missing security headers
- Incomplete input validation
- Missing rate limiting
- Outdated dependencies
- No security monitoring
- Missing audit logging
- Insufficient error handling

### Low Priority (Nice to Have)
- Additional security headers
- Enhanced logging
- More restrictive CSP
- Additional rate limiting
- Security documentation
- Penetration testing

## Review Questions

1. Is all user input validated and sanitized?
2. Are SQL queries parameterized?
3. Is output properly encoded/escaped?
4. Are credentials stored securely?
5. Is authentication required on protected resources?
6. Are authorization checks in place?
7. Is sensitive data encrypted?
8. Are dependencies up to date and vulnerability-free?
9. Are error messages non-revealing?
10. Is cryptography implemented correctly?

## Red Flags

- String concatenation in SQL queries
- eval() or exec() with user input
- Hardcoded passwords or API keys
- No input validation
- Missing authentication decorators
- No authorization checks
- Sensitive data in logs
- MD5 or SHA1 for password hashing
- No HTTPS enforcement
- Vulnerable dependencies
- Disabled SSL certificate validation
- Missing CSRF tokens
- No rate limiting on authentication
- Predictable session IDs
- Direct object references without checks

## Security Testing

### OWASP Top 10 Checks
1. **Injection**: SQL, command, LDAP, etc.
2. **Broken Authentication**: Session management, credential storage
3. **Sensitive Data Exposure**: Encryption, secure transmission
4. **XML External Entities (XXE)**: XML parsing vulnerabilities
5. **Broken Access Control**: Authorization bypasses
6. **Security Misconfiguration**: Default configs, unnecessary features
7. **XSS**: Reflected, stored, DOM-based
8. **Insecure Deserialization**: Object injection
9. **Using Components with Known Vulnerabilities**: Outdated dependencies
10. **Insufficient Logging & Monitoring**: Security events, incident response

### Security Tools
- **Static Analysis**: Bandit, Semgrep, SonarQube
- **Dependency Scanning**: Snyk, npm audit, Safety
- **SAST**: Static Application Security Testing
- **DAST**: Dynamic Application Security Testing
- **Penetration Testing**: Manual security testing

## Best Practices

- Validate and sanitize all user input
- Use parameterized queries for database access
- Escape output in HTML contexts
- Hash passwords with bcrypt or Argon2
- Store secrets in environment variables or secret managers
- Implement authentication and authorization consistently
- Encrypt sensitive data at rest and in transit
- Use HTTPS/TLS for all communications
- Keep dependencies updated and scan for vulnerabilities
- Implement CSRF protection on state-changing operations
- Use Content Security Policy headers
- Apply principle of least privilege
- Log security events but not sensitive data
- Implement rate limiting on authentication
- Use secure session management
- Conduct regular security reviews
- Follow OWASP guidelines
- Perform security testing in CI/CD pipeline
