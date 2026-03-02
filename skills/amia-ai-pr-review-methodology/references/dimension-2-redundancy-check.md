# Dimension 2: Redundancy and Duplication Check

## Table of Contents

- D2.1 When to apply redundancy checking
- D2.2 Searching for similar patterns in the codebase
- D2.3 Identifying when existing code already handles the case
- D2.4 List and array addition analysis: priority order and placement justification
- D2.5 Configuration changes vs code changes
- D2.6 Red flags for redundancy
- D2.7 Example: Detecting a redundant path addition

---

## D2.1 When to apply redundancy checking

Apply redundancy checking to every PR that adds new code, new configuration entries, new paths, new options, or new data to a list. This dimension answers the question: "Does this change duplicate something that already exists in the codebase?"

Redundancy is one of the most common issues in PRs because authors often write new code to solve a problem without first checking whether existing code already handles it. Redundant code increases maintenance burden, creates confusion about which code path is authoritative, and may cause subtle bugs when one copy is updated but the other is not.

---

## D2.2 Searching for similar patterns in the codebase

Before evaluating the PR's approach, search the codebase for code that serves a similar purpose.

**Search strategy:**

1. **Search by function name:** If the PR adds a function called `validate_input()`, search for "validate" and "input" to find existing validation functions.

2. **Search by error message:** If the PR handles a specific error, search for that error message to find existing error handlers.

3. **Search by pattern:** If the PR adds a path to a list, search for all path lists in the codebase to find existing lists that might already include this path.

4. **Search by purpose:** If the PR adds email validation, search for "email" across the codebase to find existing email handling code.

**Example search commands:**

```bash
# Search for similar function names
grep -rn "validate.*input" src/

# Search for existing path lists
grep -rn "search_paths\|binary_paths\|install_paths" src/

# Search for error handling of the same error type
grep -rn "FileNotFoundError\|No such file" src/
```

**Checklist:**

- [ ] Searched for similar function/method names
- [ ] Searched for the same error message or exception type
- [ ] Searched for similar data patterns (paths, URLs, configuration keys)
- [ ] Checked utility modules and helper files for existing solutions

---

## D2.3 Identifying when existing code already handles the case

After searching (section D2.2), evaluate whether any existing code already covers the PR's use case.

**Questions to ask:**

1. Does an existing function perform the same or similar operation?
   - If yes: Can the existing function be reused, extended, or parameterized instead of adding a new one?

2. Does an existing configuration option already control this behavior?
   - If yes: Can the configuration be adjusted instead of adding new code?

3. Does an existing list, array, or set already contain an entry that covers this case?
   - If yes: Why is a new entry needed? Does the author know the existing entry exists?

**What to ask the author if existing code covers the case:**

"I found that `utils/validators.py:validate_format()` (line 87) already performs this validation. Can you explain why a new function is needed instead of using the existing one? If the existing function is insufficient, what specific limitation does it have?"

---

## D2.4 List and array addition analysis: priority order and placement justification

When a PR adds an item to a list, array, or ordered collection, special attention is needed. The position of the item matters because:

- Items searched in order (like path lists) have priority implications: an item placed first will be found first and may override better alternatives.
- Items in configuration lists may be processed sequentially, where order affects behavior.

**Checklist for list additions:**

- [ ] The priority order of the new item is justified (why is it placed at this position, not another?)
- [ ] The placement does not override a better alternative (for example, placing a less-reliable path before a standard one)
- [ ] All items in the list after the addition are still necessary (the new item does not make an existing item redundant)
- [ ] The new item serves a purpose distinct from all existing items

**Example of unjustified placement:**

```python
# Before
search_paths = [
    "/usr/local/bin/mytool",    # Standard Homebrew (Intel Mac)
    "/usr/bin/mytool",          # System package manager
]

# PR adds a new path at the TOP
search_paths = [
    "/opt/custom/bin/mytool",   # Added by PR -- no justification for priority
    "/usr/local/bin/mytool",    # Standard Homebrew (Intel Mac)
    "/usr/bin/mytool",          # System package manager
]
```

**Review question:** "Why is `/opt/custom/bin/mytool` placed before the standard paths? If both paths exist on a system, this would cause the custom installation to take priority over the system package manager installation. Is this intentional? What evidence shows this path is more commonly used than the standard paths?"

---

## D2.5 Configuration changes vs code changes

Sometimes the right solution is not adding code but changing configuration. Before accepting a code change, check whether a configuration adjustment would achieve the same result with less complexity.

**Examples of configuration-over-code solutions:**

| Code Change Proposed | Configuration Alternative |
|---------------------|--------------------------|
| Adding a new search path to a hardcoded list in source code | Adding the path to a configuration file or environment variable that the code already reads |
| Adding a new retry loop around a network call | Adjusting the existing timeout or retry configuration |
| Adding a feature flag check in the code | Using an existing feature flag system to enable/disable the feature |

**What to ask the author:**

"Could this be solved by changing the configuration instead of modifying the source code? For example, if the search path list is already configurable via environment variables, the new path could be added to the configuration without a code change."

---

## D2.6 Red flags for redundancy

These patterns strongly suggest the PR introduces redundant code:

| Red Flag | Why It Matters |
|----------|---------------|
| Adding a new item to a list without explaining its priority relative to existing items | The author may not be aware of existing items that already cover the case |
| Duplicating logic that exists elsewhere in the codebase | Creates maintenance burden and risk of divergence |
| Hardcoding a value that could be configured dynamically | Reduces flexibility and makes the code harder to adapt to different environments |
| Adding a special case instead of a general solution | Special cases accumulate and make the code harder to reason about |
| Adding a new utility function when an existing one covers the same purpose | Suggests the author did not search the codebase before writing new code |

---

## D2.7 Example: Detecting a redundant path addition

**Scenario:** A PR adds a new path to a binary search list used to find a CLI tool.

**PR diff:**

```python
# detection.py
 TOOL_SEARCH_PATHS = [
+    "/home/user/.local/share/tools/mytool",  # User-local installation
     "/usr/local/bin/mytool",                  # Homebrew / manual install
     "/usr/bin/mytool",                        # System package manager
     "/snap/bin/mytool",                       # Snap package
 ]
```

**Context gathering (Phase 1) reveals:**

The reviewer reads the complete `detection.py` file and discovers that 20 lines below the path list, there is already a function that expands `~/.local/bin/` dynamically:

```python
def find_tool():
    # Also check user-local bin directory
    user_local = os.path.expanduser("~/.local/bin/mytool")
    if os.path.exists(user_local):
        return user_local

    for path in TOOL_SEARCH_PATHS:
        if os.path.exists(path):
            return path
    return None
```

**Redundancy finding:** The existing `find_tool()` function already checks `~/.local/bin/mytool`, which is the standard user-local installation path. The PR adds `/home/user/.local/share/tools/mytool`, which is a non-standard path that:

1. Hardcodes `/home/user/` instead of using `~` or `os.path.expanduser()`, so it would only work for a user named "user".
2. Uses `.local/share/tools/` which is not a standard binary location (FreeDesktop XDG spec puts binaries in `~/.local/bin/`, not `~/.local/share/`).
3. Duplicates the intent of the existing `user_local` check.

**Review response:** "The existing `find_tool()` function already checks `~/.local/bin/mytool` (the standard user-local binary location). The new path `/home/user/.local/share/tools/mytool` has two issues: (1) it hardcodes the username 'user' instead of using home directory expansion, and (2) `~/.local/share/tools/` is not a standard binary installation path. Can you explain what installation method places the binary at this non-standard path? If this path is needed, it should use `os.path.expanduser()` instead of a hardcoded home directory."
