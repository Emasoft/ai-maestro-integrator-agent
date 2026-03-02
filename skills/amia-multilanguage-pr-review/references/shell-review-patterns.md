# Shell Script Review Patterns Reference

## Overview

This reference covers shell script code review patterns, including Bash best practices, POSIX compatibility, ShellCheck integration, and cross-platform considerations.

---

## Table of Contents

### Part 1: Bash/Shell Script Review Checklist
**File**: [shell-review-patterns-part1-bash-checklist.md](shell-review-patterns-part1-bash-checklist.md)

- 6.1 Bash/Shell script review checklist
  - 6.1.1 Essential script header with shebang and set options
  - 6.1.2 Set options explained (set -e, -u, -o pipefail, -x)
  - 6.1.3 Variable best practices (quoting, braces, defaults, readonly, local)
  - 6.1.4 Command substitution ($() vs backticks)
  - 6.1.5 Conditionals ([[ ]] vs [ ], string/regex/arithmetic)
  - 6.1.6 Array usage (declare, iterate, length, indices)
  - 6.1.7 Style checklist for Bash scripts

### Part 2: POSIX Compatibility Requirements
**File**: [shell-review-patterns-part2-posix-compat.md](shell-review-patterns-part2-posix-compat.md)

- 6.2 POSIX compatibility requirements
  - 6.2.1 POSIX shell features safe to use
  - 6.2.2 Bash-only features that are NOT POSIX
  - 6.2.3 POSIX alternatives for Bash features table
  - 6.2.4 Testing POSIX compatibility (dash, checkbashisms, shellcheck)
  - 6.2.5 POSIX compatibility checklist

### Part 3: ShellCheck Lints and Fixes
**File**: [shell-review-patterns-part3-shellcheck.md](shell-review-patterns-part3-shellcheck.md)

- 6.3 ShellCheck lints and fixes
  - 6.3.1 Running ShellCheck (basic usage, output formats, severity)
  - 6.3.2 Common ShellCheck warnings with fixes
    - SC2086: Double quote to prevent globbing
    - SC2046: Quote to prevent word splitting
    - SC2006: Use $(...) instead of backticks
    - SC2004: Unnecessary $ in arithmetic
    - SC2034: Variable appears unused
    - SC2164: Use 'cd ... || exit'
    - SC2155: Declare and assign separately
  - 6.3.3 ShellCheck directives (disable, source)
  - 6.3.4 ShellCheck configuration (.shellcheckrc)
  - 6.3.5 ShellCheck review checklist

### Part 4: Cross-Platform Considerations
**File**: [shell-review-patterns-part4-crossplatform.md](shell-review-patterns-part4-crossplatform.md)

- 6.4 Cross-platform considerations for macOS and Linux
  - 6.4.1 Key differences table (sed, date, stat, readlink, grep)
  - 6.4.2 Portable patterns for sed in-place editing
  - 6.4.3 Portable patterns for date formatting
  - 6.4.4 Portable patterns for readlink -f (canonical path)
  - 6.4.5 OS detection functions
  - 6.4.6 GNU Coreutils on macOS (brew install)
  - 6.4.7 Portable script template
  - 6.4.8 Cross-platform review checklist

---

## Quick Reference

| Topic | When to Read |
|-------|--------------|
| Part 1: Bash Checklist | Reviewing any Bash script for style and correctness |
| Part 2: POSIX Compat | Script must run on /bin/sh or multiple Unix variants |
| Part 3: ShellCheck | Setting up linting or understanding ShellCheck warnings |
| Part 4: Cross-Platform | Script must work on both macOS and Linux |

---

## Related References

- For security review patterns, see [security-review-patterns.md](security-review-patterns.md)
- For general code review methodology, see the main SKILL.md
