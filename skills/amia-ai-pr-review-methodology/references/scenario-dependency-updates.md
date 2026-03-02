# Scenario Protocol: Dependency Update PRs

## Table of Contents

- S-DEP.1 When to use this scenario protocol
- S-DEP.2 Justification requirements for new or updated dependencies
- S-DEP.3 Security vulnerability scanning
- S-DEP.4 License compatibility checking
- S-DEP.5 Bundle size and performance impact assessment
- S-DEP.6 Checking for alternatives using existing dependencies
- S-DEP.7 Example: Reviewing a PR that adds a new npm package

---

## S-DEP.1 When to use this scenario protocol

Use this protocol when the PR adds a new dependency, updates an existing dependency to a new version, or replaces one dependency with another. Dependency changes are identified by modifications to:

- Python: `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, `poetry.lock`
- JavaScript/TypeScript: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- Rust: `Cargo.toml`, `Cargo.lock`
- Go: `go.mod`, `go.sum`
- Java/Kotlin: `pom.xml`, `build.gradle`, `build.gradle.kts`
- .NET: `.csproj`, `packages.config`, `Directory.Packages.props`

Dependency changes are high-impact because they affect the entire build, can introduce security vulnerabilities, and may create license conflicts.

---

## S-DEP.2 Justification requirements for new or updated dependencies

**For new dependencies, require answers to:**

1. **What problem does this dependency solve?** The author must explain what functionality the dependency provides and why it is needed.
2. **Why can this not be solved with existing code or existing dependencies?** Adding a dependency for something that can be done with 20 lines of code is usually unjustified.
3. **How mature and maintained is the dependency?** Check the repository for: last commit date, number of contributors, open issue count, release frequency.
4. **What is the dependency's own dependency tree?** A single dependency can transitively pull in dozens of sub-dependencies. Each sub-dependency is a potential vulnerability.

**For updated dependencies, require answers to:**

1. **Why is the update needed?** Is it a security fix, a bug fix, a feature needed by the project, or a routine version bump?
2. **What changed in the new version?** The author should reference the changelog or release notes.
3. **Are there breaking changes?** Check the dependency's changelog for breaking changes between the old and new versions.
4. **Has the update been tested?** All existing tests must pass with the new version.

**What to ask the author:**

"Can you explain why this dependency is needed and what it provides that we cannot achieve with existing code or dependencies? Please link to the dependency's repository and changelog."

---

## S-DEP.3 Security vulnerability scanning

Every dependency added or updated must be checked for known security vulnerabilities.

**How to check for vulnerabilities:**

| Ecosystem | Tool | Command |
|-----------|------|---------|
| Python | pip-audit | `pip-audit -r requirements.txt` |
| Python | safety | `safety check -r requirements.txt` |
| JavaScript | npm audit | `npm audit` |
| JavaScript | snyk | `snyk test` |
| Rust | cargo-audit | `cargo audit` |
| Go | govulncheck | `govulncheck ./...` |
| General | Snyk, Dependabot, OSV Scanner | Varies |

**What to check:**

- [ ] No known vulnerabilities (CVEs) in the dependency at the specified version
- [ ] No known vulnerabilities in the dependency's transitive dependencies
- [ ] The dependency has a security policy (reports and fixes vulnerabilities promptly)
- [ ] The dependency has not been flagged in security advisories (npm advisories, PyPI advisories, GitHub Security Advisories)

**What to ask the author:**

"Can you run a vulnerability scan on the updated dependencies and share the output? For Python, use `pip-audit`; for JavaScript, use `npm audit`."

---

## S-DEP.4 License compatibility checking

Every dependency has a license. The dependency's license must be compatible with the project's license and with any distribution requirements.

**Common license compatibility issues:**

| Project License | Dependency License | Compatible? | Notes |
|----------------|-------------------|-------------|-------|
| MIT | MIT | Yes | No restrictions |
| MIT | Apache 2.0 | Yes | Must include Apache notice |
| MIT | GPL-3.0 | PROBLEMATIC | GPL requires the entire project to be GPL if distributed |
| Apache 2.0 | MIT | Yes | No restrictions |
| Apache 2.0 | GPL-3.0 | PROBLEMATIC | Same GPL issue |
| GPL-3.0 | MIT | Yes | MIT is permissive |
| Proprietary | AGPL-3.0 | NO | AGPL requires source disclosure |

**How to check licenses:**

```bash
# Python
pip-licenses --from=mixed

# JavaScript
npx license-checker --summary

# General
# Check the dependency's repository for a LICENSE file
```

**What to ask the author:**

"What is the license of this dependency? Is it compatible with our project's license? If the dependency uses GPL or AGPL, we need to carefully evaluate whether it can be included."

---

## S-DEP.5 Bundle size and performance impact assessment

Dependencies affect the size and startup time of the application. Large dependencies may be inappropriate for projects where size matters (browser bundles, serverless functions, CLI tools, mobile apps).

**What to check:**

- [ ] The dependency's installed size (disk space)
- [ ] The dependency's impact on bundle size (for JavaScript/TypeScript projects)
- [ ] The dependency's startup time impact (does it do heavy initialization?)
- [ ] The number of transitive dependencies (more dependencies means more to download, audit, and maintain)

**How to check bundle size (JavaScript):**

```bash
# Check the dependency's size before adding
npx bundle-phobia <package-name>

# Or use the online tool: https://bundlephobia.com/<package-name>
```

**How to check installed size (Python):**

```bash
# Check what pip installs
pip install --dry-run <package-name>

# After installation, check size
du -sh $(python -c "import <module>; print(<module>.__path__[0])")
```

**What to ask the author:**

"What is the installed size of this dependency, including its transitive dependencies? Does it affect startup time or bundle size? For context, our current bundle is X MB and our startup time is Y seconds."

---

## S-DEP.6 Checking for alternatives using existing dependencies

Before accepting a new dependency, verify that the required functionality cannot be achieved using:

1. **Standard library functions.** Many languages have built-in functionality that makes external dependencies unnecessary (for example, Python's `json` module instead of a third-party JSON library).
2. **Existing project dependencies.** A dependency already in the project may provide the needed functionality (for example, if the project already uses `requests`, there is no need to add `httpx` for HTTP calls).
3. **A small amount of custom code.** If the dependency provides a single function, it may be simpler to implement that function directly instead of adding an external dependency.

**How to check:**

1. Read the dependency's documentation to understand what it provides.
2. Check if the standard library has equivalent functionality.
3. Search the project's existing dependencies for similar functionality.
4. Estimate how much custom code would be needed to replace the dependency.

**Decision framework:**

| Scenario | Decision |
|----------|----------|
| Standard library covers the use case | Do not add the dependency |
| Existing dependency covers the use case | Do not add the dependency |
| Custom code would be < 50 lines with no edge cases | Consider not adding the dependency |
| Custom code would be > 100 lines or has complex edge cases | The dependency is justified |

**What to ask the author:**

"Before we add this dependency, can you check whether the standard library or our existing dependency `X` provides this functionality? Specifically, does `X.some_method()` cover the use case described in this PR?"

---

## S-DEP.7 Example: Reviewing a PR that adds a new npm package

**PR title:** "Add `date-fns` for date formatting"

**PR diff (package.json):**

```json
 "dependencies": {
     "express": "^4.18.0",
     "lodash": "^4.17.21",
+    "date-fns": "^3.0.0"
 }
```

**PR code change:**

```javascript
// Before
const formatted = new Date(timestamp).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric'
});

// After
import { format } from 'date-fns';
const formatted = format(new Date(timestamp), 'MMMM d, yyyy');
```

**Review using this protocol:**

**S-DEP.2 (Justification):**

Question: The native `Date.toLocaleDateString()` already formats dates. What does `date-fns` provide that the native API does not?

The PR shows that the before and after code produce the same output format. There is no justification for the dependency.

**S-DEP.3 (Security):**

Check: `npm audit` shows no vulnerabilities for `date-fns@3.0.0`. PASS.

**S-DEP.4 (License):**

Check: `date-fns` uses MIT license. Project uses MIT. Compatible. PASS.

**S-DEP.5 (Bundle size):**

Check: `date-fns` adds approximately 75KB to the bundle (tree-shaken). The project's current bundle is 200KB. This is a 37.5% increase.

CONCERN -- A 37.5% bundle size increase for date formatting that the native API already supports.

**S-DEP.6 (Alternatives):**

The native `Date.toLocaleDateString()` and `Intl.DateTimeFormat` provide the same formatting capability without any dependency. The existing code already works.

FAIL -- The native API covers this use case.

**Review response:**

"This PR adds `date-fns` (75KB bundle impact) to format dates, but the existing code already formats dates correctly using the native `Date.toLocaleDateString()` API. The before and after code produce the same output.

Unless there is a specific date formatting need that the native API cannot handle (such as relative time formatting, timezone conversion, or locale-specific calendar support), I recommend keeping the native implementation.

Can you explain what specific functionality from `date-fns` is needed that `Date.toLocaleDateString()` or `Intl.DateTimeFormat` does not provide?"
