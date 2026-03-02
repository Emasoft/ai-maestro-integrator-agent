---
name: conventional-commits-validation
description: "Conventional Commits format specification, validation regex, and commit-msg hook implementation for enforcing structured commit messages."
---

# Conventional Commits Validation

## Table of Contents

- 1. Understanding the Conventional Commits format before implementing validation
  - 1.1. What Conventional Commits are and why they matter
  - 1.2. The exact format specification: type, scope, breaking change indicator, description
  - 1.3. All 11 commit type definitions with usage examples
- 2. Implementing commit message validation with a regex pattern
  - 2.1. The complete validation regex with explanation of each component
  - 2.2. Special passthrough rules for merge commits and revert commits
  - 2.3. First-line length limit enforcement
- 3. Writing a portable commit-msg hook script
  - 3.1. Complete commit-msg hook implementation (POSIX sh compatible)
  - 3.2. How git passes the commit message file to the hook
  - 3.3. Producing clear error messages that teach the developer the correct format
- 4. Valid and invalid commit message examples for testing
  - 4.1. Valid messages: all types, with and without scope, with breaking change indicator
  - 4.2. Invalid messages: common mistakes and why they fail
  - 4.3. Edge cases: merge commits, revert commits, multi-line bodies

---

## 1. Understanding the Conventional Commits format before implementing validation

### 1.1. What Conventional Commits are and why they matter

Conventional Commits is a specification for writing structured, machine-readable commit messages. The specification defines a format that:

- Makes commit history scannable by humans (type prefix tells you what kind of change)
- Enables automated changelog generation (group commits by type)
- Enables automated semantic versioning (feat = minor bump, fix = patch bump, breaking = major bump)
- Enforces consistency across a team (everyone uses the same vocabulary)

The specification is documented at https://www.conventionalcommits.org/

### 1.2. The exact format specification: type, scope, breaking change indicator, description

The first line of a Conventional Commit message follows this structure:

```
type(optional-scope)!?: description
```

Breaking this down:

- **type** (required): One of the 11 defined types listed below. Always lowercase.
- **scope** (optional): A parenthesized string identifying what part of the codebase is affected. For example, `feat(auth):` or `fix(parser):`. The scope can contain letters, numbers, hyphens, underscores, slashes, and dots.
- **breaking change indicator** (optional): An exclamation mark `!` placed immediately before the colon. Indicates that this commit introduces a breaking change. For example, `feat!:` or `feat(api)!:`.
- **colon and space** (required): The literal characters `: ` (colon followed by a space) separating the type/scope from the description.
- **description** (required): A short summary of the change. Starts with a lowercase letter (conventionally). Must be between 1 and 100 characters.

After the first line, the commit message body is freeform and is NOT validated by the regex.

### 1.3. All 11 commit type definitions with usage examples

| Type | Definition | Example |
|------|-----------|---------|
| `feat` | A new feature visible to users or other systems | `feat(auth): add OAuth2 login flow` |
| `fix` | A bug fix that corrects incorrect behavior | `fix(parser): handle empty input without crashing` |
| `docs` | Changes to documentation only (no code changes) | `docs: update API reference for v2 endpoints` |
| `style` | Code style changes that do not affect logic (formatting, whitespace, semicolons, naming) | `style: apply consistent indentation to config files` |
| `refactor` | Code changes that neither fix a bug nor add a feature (restructuring, renaming internals) | `refactor(db): extract connection pooling into separate module` |
| `perf` | Performance improvements (same behavior, faster execution) | `perf: cache parsed templates to avoid repeated disk reads` |
| `test` | Adding new tests or updating existing tests (no production code changes) | `test(auth): add integration tests for token refresh` |
| `build` | Changes to build system, compilation, or external dependencies | `build: upgrade typescript to 5.4 and update tsconfig` |
| `ci` | Changes to CI/CD configuration files and scripts | `ci: add parallel test execution to pipeline` |
| `chore` | Maintenance tasks that do not fit other categories (dependency bumps, tooling config) | `chore: update .gitignore for new build artifacts` |
| `revert` | Reverting a previous commit | `revert: undo feat(auth) OAuth2 changes from abc1234` |

---

## 2. Implementing commit message validation with a regex pattern

### 2.1. The complete validation regex with explanation of each component

The full regex pattern for validating the first line of a Conventional Commit message:

```
^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_/.-]+\))?!?: .{1,100}$
```

Breaking down each component:

| Component | Pattern | Meaning |
|-----------|---------|---------|
| Start of line | `^` | Anchors the match to the beginning of the string |
| Type | `(feat\|fix\|docs\|style\|refactor\|perf\|test\|build\|ci\|chore\|revert)` | Exactly one of the 11 allowed types |
| Optional scope | `(\([a-zA-Z0-9_/.-]+\))?` | Parenthesized scope with allowed characters; the entire group is optional |
| Breaking change | `!?` | Optional exclamation mark indicating a breaking change |
| Separator | `: ` | Colon followed by a space (literal characters, required) |
| Description | `.{1,100}` | The description text, between 1 and 100 characters, any character allowed |
| End of line | `$` | Anchors the match to the end of the string |

Allowed characters in scope: uppercase and lowercase letters (`a-zA-Z`), digits (`0-9`), underscore (`_`), forward slash (`/`), dot (`.`), hyphen (`-`).

### 2.2. Special passthrough rules for merge commits and revert commits

Some commit messages are generated automatically by git and should bypass validation:

- **Merge commits**: Messages starting with `Merge ` (for example, `Merge branch 'feature' into main`). These are generated by `git merge` and should not be reformatted.
- **Revert commits**: Messages starting with `Revert "` (for example, `Revert "feat(auth): add OAuth2 login flow"`). These are generated by `git revert` and include the original commit message in quotes.

The passthrough regex:

```
^(Merge |Revert ")
```

If the first line matches this pattern, skip Conventional Commits validation entirely.

### 2.3. First-line length limit enforcement

The description portion of the first line must be at most 100 characters. The total first line (including type, scope, colon, and space) can be longer, but the description itself is capped.

In the regex above, `.{1,100}` enforces this on the description portion. If you want to enforce a total first-line length (for example, 120 characters including type prefix), add a separate length check:

```sh
first_line_length=$(echo "$first_line" | wc -c)
if [ "$first_line_length" -gt 120 ]; then
  echo "ERROR: First line is $first_line_length characters. Maximum is 120."
  exit 1
fi
```

---

## 3. Writing a portable commit-msg hook script

### 3.1. Complete commit-msg hook implementation (POSIX sh compatible)

Create this file at `.git/hooks/commit-msg` (or in your tracked hooks directory):

```sh
#!/bin/sh
#
# commit-msg hook: validates that the commit message follows Conventional Commits format.
# Exit 0 to allow the commit, exit non-zero to block it.
#
# Argument $1: path to the temporary file containing the commit message.

# Safety: unset environment variables that can misdirect git operations
unset GIT_DIR
unset GIT_WORK_TREE

commit_msg_file="$1"

# Read the first line of the commit message (ignore comment lines starting with #)
first_line=$(grep -v '^#' "$commit_msg_file" | head -n 1)

# Allow empty first line (git will abort the commit anyway)
if [ -z "$first_line" ]; then
  exit 0
fi

# Passthrough: merge commits and auto-generated revert commits
if echo "$first_line" | grep -qE '^(Merge |Revert ")'; then
  exit 0
fi

# Validate against Conventional Commits format
if echo "$first_line" | grep -qE '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_/.-]+\))?!?: .{1,100}$'; then
  exit 0
fi

# Validation failed: produce a helpful error message
echo ""
echo "================================================================"
echo "ERROR: Invalid commit message format."
echo "================================================================"
echo ""
echo "Your message:"
echo "  $first_line"
echo ""
echo "Expected format:"
echo "  type(optional-scope): description"
echo ""
echo "Valid types:"
echo "  feat      - A new feature"
echo "  fix       - A bug fix"
echo "  docs      - Documentation changes only"
echo "  style     - Code style (formatting, whitespace)"
echo "  refactor  - Code restructuring (no feature/fix)"
echo "  perf      - Performance improvement"
echo "  test      - Adding or updating tests"
echo "  build     - Build system or dependencies"
echo "  ci        - CI/CD configuration"
echo "  chore     - Maintenance tasks"
echo "  revert    - Reverting a previous commit"
echo ""
echo "Examples of valid messages:"
echo "  feat(auth): add password reset flow"
echo "  fix: resolve null pointer in config parser"
echo "  docs(api): update endpoint reference for v3"
echo "  feat!: redesign public API (breaking change)"
echo "  refactor(db): extract connection pool module"
echo ""
echo "To bypass this check (not recommended):"
echo "  git commit --no-verify"
echo ""
exit 1
```

### 3.2. How git passes the commit message file to the hook

When a developer runs `git commit`, git:

1. Opens the configured editor (or accepts `-m "message"`) to compose the commit message
2. Writes the message to a temporary file at `.git/COMMIT_EDITMSG`
3. Passes the path to that file as the first argument (`$1`) to the `commit-msg` hook
4. If the hook exits with code 0, the commit proceeds
5. If the hook exits with a non-zero code, the commit is aborted and the message file is preserved so the developer can fix it

The hook reads from the file, not from stdin. This is different from the pre-push hook which reads ref data from stdin.

### 3.3. Producing clear error messages that teach the developer the correct format

A good error message from a commit-msg hook must include:

1. **What went wrong**: Show the invalid message the developer wrote
2. **What was expected**: Show the expected format pattern
3. **All valid options**: List all valid types with brief descriptions
4. **Concrete examples**: Show 3-5 examples of correctly formatted messages
5. **How to bypass**: Document `--no-verify` for emergencies (and discourage its use)

Never produce a cryptic "commit message validation failed" with no guidance. The error message IS the documentation. Most developers will read it once and remember the format.

---

## 4. Valid and invalid commit message examples for testing

### 4.1. Valid messages: all types, with and without scope, with breaking change indicator

All of the following messages pass validation:

```
feat: add user authentication module
feat(auth): implement JWT token refresh
fix: resolve crash when input is empty
fix(parser): handle malformed JSON gracefully
docs: update installation guide for Linux
docs(api): add examples to endpoint reference
style: apply consistent indentation across codebase
style(css): normalize spacing in layout files
refactor: extract database connection to separate module
refactor(auth/oauth): simplify token validation logic
perf: cache compiled regex patterns
perf(query): add index hint for slow join
test: add unit tests for validation module
test(e2e): cover login flow with integration tests
build: upgrade dependency versions for Q4 release
build(webpack): enable tree-shaking for production builds
ci: add code coverage reporting to pipeline
ci(github-actions): parallelize test matrix
chore: update gitignore for new tooling artifacts
chore(deps): bump minor versions across all packages
revert: undo refactor of connection pool
feat!: redesign public API response format
feat(api)!: remove deprecated v1 endpoints
fix(auth)!: change token format from opaque to JWT
```

### 4.2. Invalid messages: common mistakes and why they fail

| Invalid Message | Why It Fails |
|----------------|--------------|
| `added new feature` | Missing type prefix |
| `Feat: add login` | Type must be lowercase (`feat`, not `Feat`) |
| `feat:add login` | Missing space after colon |
| `feat : add login` | Space before colon is not allowed |
| `feature: add login` | `feature` is not a valid type (use `feat`) |
| `feat(auth: add login` | Missing closing parenthesis in scope |
| `feat(): add login` | Empty scope (scope must have at least one character) |
| `feat(auth/module with spaces): add login` | Space in scope is not allowed |
| `fix` | Missing colon separator and description |
| `fix:` | Missing space after colon and missing description |
| `fix: ` | Description is empty (just a trailing space) |

### 4.3. Edge cases: merge commits, revert commits, multi-line bodies

**Merge commits** (passthrough, not validated):

```
Merge branch 'feature/oauth' into main
Merge pull request #42 from user/feature-branch
```

**Revert commits** (passthrough, not validated):

```
Revert "feat(auth): add OAuth2 login flow"
```

**Multi-line commit messages** (only the first line is validated):

```
feat(auth): add password reset via email

This implements the complete password reset flow:
- User requests reset via email
- System sends a time-limited token
- User sets new password using the token

Closes #123
```

The lines after the first blank line are the commit body and are not subject to Conventional Commits validation. Teams may add additional validation for the body (for example, requiring issue references) but that is outside the scope of this document.
