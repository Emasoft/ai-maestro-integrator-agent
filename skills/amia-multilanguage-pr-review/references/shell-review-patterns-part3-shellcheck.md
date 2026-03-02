# Shell Review Patterns - Part 3: ShellCheck Lints and Fixes

## Table of Contents

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

---

## 6.3 ShellCheck Lints and Fixes

ShellCheck is the definitive shell script linter.

### 6.3.1 Running ShellCheck

```bash
# Basic usage
shellcheck script.sh

# Specify shell
shellcheck -s bash script.sh
shellcheck -s sh script.sh    # POSIX

# Output formats
shellcheck -f json script.sh
shellcheck -f gcc script.sh   # Compiler-like output

# Check all scripts
find . -name "*.sh" -exec shellcheck {} +

# Exclude specific checks
shellcheck -e SC2086 script.sh

# Severity levels
shellcheck --severity=warning script.sh
```

### 6.3.2 Common ShellCheck Warnings

#### SC2086: Double quote to prevent globbing and word splitting

```bash
# Bad
rm $file

# Good
rm "$file"
```

#### SC2046: Quote to prevent word splitting

```bash
# Bad
for f in $(ls); do echo "$f"; done

# Good
for f in *; do echo "$f"; done
```

#### SC2006: Use $(...) instead of backticks

```bash
# Bad
result=`command`

# Good
result=$(command)
```

#### SC2004: $/$[..] is unnecessary on arithmetic variables

```bash
# Bad
result=$((${a} + ${b}))

# Good
result=$((a + b))
```

#### SC2034: Variable appears unused

```bash
# Either use the variable or export it
readonly VERSION="1.0.0"
export VERSION

# Or disable check with directive
# shellcheck disable=SC2034
unused_var="value"
```

#### SC2164: Use 'cd ... || exit' in case cd fails

```bash
# Bad
cd /some/directory
rm -rf *

# Good
cd /some/directory || exit 1
rm -rf *

# Or use subshell
(
    cd /some/directory || exit 1
    rm -rf *
)
```

#### SC2155: Declare and assign separately to avoid masking return values

```bash
# Bad
local result=$(command)

# Good
local result
result=$(command)
```

### 6.3.3 ShellCheck Directives

```bash
# Disable for next line
# shellcheck disable=SC2086
rm $file

# Disable for entire file (at top)
# shellcheck disable=SC2086,SC2046

# Disable for block
# shellcheck disable=SC2086
{
    rm $file1
    rm $file2
}

# Source directive (for sourced files)
# shellcheck source=./lib.sh
source "$SCRIPT_DIR/lib.sh"
```

### 6.3.4 ShellCheck Configuration

```yaml
# .shellcheckrc
shell=bash
enable=all
disable=SC2059,SC2086

# Per-directory configuration
# Create .shellcheckrc in directory
```

### 6.3.5 ShellCheck Checklist

- [ ] ShellCheck passes with no errors
- [ ] All warnings addressed or explicitly disabled
- [ ] Disabled checks have comment explaining why
- [ ] Source directives added for sourced files
- [ ] Correct shell specified (-s bash or -s sh)

---

## Navigation

- **Previous**: [Part 2: POSIX Compatibility](shell-review-patterns-part2-posix-compat.md)
- **Next**: [Part 4: Cross-Platform](shell-review-patterns-part4-crossplatform.md)
- **Index**: [shell-review-patterns.md](shell-review-patterns.md)
