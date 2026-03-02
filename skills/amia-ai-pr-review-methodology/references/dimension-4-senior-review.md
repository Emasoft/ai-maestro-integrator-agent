# Dimension 4: Senior Developer Review

## Table of Contents

- D4.1 When to apply senior developer review criteria
- D4.2 Architectural layer assessment
- D4.3 Technical debt and maintainability evaluation
- D4.4 Performance and resource implications
- D4.5 Security implications analysis
- D4.6 Backwards compatibility assessment
- D4.7 Red flags for architectural concerns
- D4.8 Example: Evaluating a quick fix for long-term impact

---

## D4.1 When to apply senior developer review criteria

Apply senior developer review criteria to every PR, but allocate more attention to PRs that:

- Change core logic or business rules
- Modify public APIs or interfaces
- Introduce new dependencies
- Change authentication, authorization, or data handling
- Alter the build, deployment, or configuration pipeline
- Touch code that many other modules depend on

This dimension answers the question: "Is this the right solution for the long term, not just the short term?"

---

## D4.2 Architectural layer assessment

Every codebase has an implicit or explicit architecture with layers (for example: presentation, business logic, data access). Changes should respect these layers.

**Checklist:**

- [ ] The change is placed in the appropriate module or component
- [ ] The change does not bypass abstraction layers (for example, a UI component directly querying the database)
- [ ] The change follows existing architectural patterns (if the codebase uses repositories for data access, new data access code should also use repositories)
- [ ] If the change introduces a new pattern, there is a justification for why the existing pattern is insufficient

**How to assess:**

1. Identify which architectural layer the changed code belongs to.
2. Check whether the change reaches into a layer it should not access directly.
3. Check whether similar changes elsewhere in the codebase follow the same pattern.

**Example of a layer violation:**

```python
# Bad: Controller directly accessing the database
class UserController:
    def get_user(self, user_id):
        # Bypasses the service and repository layers
        conn = sqlite3.connect("users.db")
        cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

# Good: Controller uses the service layer
class UserController:
    def get_user(self, user_id):
        return self.user_service.get_by_id(user_id)
```

---

## D4.3 Technical debt and maintainability evaluation

Code is read far more often than it is written. Every change should make the codebase easier to understand and maintain, not harder.

**Checklist:**

- [ ] The code is self-documenting or has clear comments explaining non-obvious logic
- [ ] A future developer unfamiliar with this PR would understand why the code exists and what it does
- [ ] The change is easy to debug if something breaks (clear error messages, logging, traceable execution)
- [ ] The change does not increase complexity unnecessarily (for example, adding an abstraction layer for a single use case)
- [ ] The change does not leave dead code, commented-out code, or TODO comments without linked issues

**Questions to consider:**

1. If you removed all context about this PR and read only the resulting code, would it make sense?
2. Would a new team member understand this code without asking the author?
3. If this code breaks in production at 3 AM, can the on-call engineer diagnose the issue quickly?

---

## D4.4 Performance and resource implications

Every change has potential performance implications, even if the change is not primarily about performance.

**Checklist:**

- [ ] No unnecessary I/O operations (disk reads/writes, network calls)
- [ ] No unnecessary memory allocations (loading entire files into memory when streaming would suffice)
- [ ] Efficient for the common case (the typical execution path is optimized, edge cases can be slower)
- [ ] No performance regressions compared to the previous version
- [ ] Database queries are efficient (no N+1 queries, appropriate use of indexes)

**Common performance issues in PRs:**

| Issue | Example | Impact |
|-------|---------|--------|
| Unnecessary file I/O | Reading a config file on every request instead of caching it | Disk I/O latency on every request |
| N+1 queries | Fetching a list of users, then fetching profile for each user individually | Database load scales linearly with result count |
| Unbounded memory | Loading an entire log file into memory to search for one line | Out-of-memory crash for large files |
| Synchronous blocking | Making a network call in the main thread without timeout | Application hangs if the remote service is down |

---

## D4.5 Security implications analysis

Every change that handles user input, authentication, authorization, file operations, or network communication has security implications.

**Checklist:**

- [ ] No new attack vectors introduced (injection, path traversal, privilege escalation)
- [ ] User inputs are sanitized and validated before use
- [ ] No sensitive data exposure (secrets, tokens, passwords in logs or error messages)
- [ ] No execution of untrusted code (eval, exec, shell commands with user input)
- [ ] File operations do not follow symlinks to unintended locations
- [ ] Network communications use appropriate encryption (TLS/HTTPS)

**Common security issues in PRs:**

| Issue | Example | Risk |
|-------|---------|------|
| Command injection | `os.system("ping " + user_input)` | Attacker executes arbitrary commands |
| Path traversal | `open("/data/" + user_input)` with input `../etc/passwd` | Attacker reads arbitrary files |
| Secret exposure | `logger.error(f"Auth failed with token {token}")` | Secrets in log files |
| Insecure deserialization | `pickle.loads(user_data)` | Remote code execution |

**What to ask the author if security concerns exist:**

"This change passes user input directly to a shell command. Can you add input validation to prevent command injection? Specifically, the input should be validated against an allowlist of permitted characters, or the command should use parameterized execution (subprocess with a list of arguments, not a shell string)."

---

## D4.6 Backwards compatibility assessment

Changes that affect the behavior observable by users, consumers of an API, or other modules in the system must be evaluated for backwards compatibility.

**Checklist:**

- [ ] The change does not break existing installations or configurations
- [ ] If the behavior changes, a migration path is provided (for example, a deprecation warning before removing a feature)
- [ ] Default values are preserved unless there is a documented reason to change them
- [ ] API contracts (function signatures, return types, error types) are preserved or versioned
- [ ] Configuration file formats remain compatible with previous versions

**Example of a backwards compatibility issue:**

```python
# Before (existing API)
def parse_config(path: str) -> dict:
    """Returns a dictionary of configuration values."""
    ...

# After (PR changes the return type)
def parse_config(path: str) -> Config:
    """Returns a Config object."""
    ...
```

This change breaks all callers that expect a dictionary. The reviewer should ask: "All existing callers of `parse_config()` expect a dictionary. This change to return a `Config` object will break them. Can you add a deprecation period where both are supported, or provide a migration guide?"

---

## D4.7 Red flags for architectural concerns

These patterns strongly suggest the PR has architectural issues:

| Red Flag | Why It Matters |
|----------|---------------|
| Quick fix without considering long-term impact | Short-term patches accumulate into unmaintainable code |
| Code requires deep knowledge to understand | Only the author can maintain it; high bus factor risk |
| Bypasses existing patterns without explanation | Inconsistency makes the codebase harder to navigate |
| Security implications not addressed | Vulnerabilities may go unnoticed until exploited |
| Breaking changes without migration path | Users of the affected API will be broken without warning |
| Adding complexity to solve a simple problem | Over-engineering creates maintenance burden disproportionate to the benefit |

---

## D4.8 Example: Evaluating a quick fix for long-term impact

**Scenario:** A PR fixes a timeout issue by increasing the timeout value from 5 seconds to 60 seconds.

**PR diff:**

```python
# api_client.py
- TIMEOUT = 5  # seconds
+ TIMEOUT = 60  # seconds -- increased to fix timeout errors
```

**Senior developer analysis:**

1. **Root cause not addressed:** The timeout is occurring because the API endpoint has degraded performance. Increasing the timeout masks the problem. The real fix should be to investigate why the endpoint is slow.

2. **Performance implication:** A 60-second timeout means that if the endpoint is down, users will wait 60 seconds before seeing an error. The previous 5-second timeout provided a faster failure.

3. **Architectural concern:** The timeout is hardcoded. It should be configurable so that different environments (development, staging, production) can use different values.

4. **Technical debt:** This is a "quick fix" that will likely remain forever because it makes the symptom disappear. Nobody will investigate the slow endpoint.

**Review response:**

"Increasing the timeout from 5 to 60 seconds will mask the underlying performance issue. Can you investigate why the endpoint is timing out at 5 seconds? Some questions:

1. What is the p95 latency of the endpoint under normal conditions?
2. Has something changed recently that could cause increased latency?
3. Could the timeout be made configurable (via environment variable or configuration file) so different environments can use appropriate values?

If the timeout increase is truly necessary as a short-term mitigation, I recommend also filing a separate issue to investigate the root cause of the endpoint's slow response time."
