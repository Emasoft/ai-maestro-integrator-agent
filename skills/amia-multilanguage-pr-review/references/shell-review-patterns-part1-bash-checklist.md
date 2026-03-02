# Shell Review Patterns - Part 1: Bash/Shell Script Review Checklist

## Table of Contents

- 6.1 Bash/Shell script review checklist
  - 6.1.1 Essential script header with shebang and set options
  - 6.1.2 Set options explained (set -e, -u, -o pipefail, -x)
  - 6.1.3 Variable best practices (quoting, braces, defaults, readonly, local)
  - 6.1.4 Command substitution ($() vs backticks)
  - 6.1.5 Conditionals ([[ ]] vs [ ], string/regex/arithmetic)
  - 6.1.6 Array usage (declare, iterate, length, indices)
  - 6.1.7 Style checklist for Bash scripts

---

## 6.1 Bash/Shell Script Review Checklist

Shell scripts are critical for automation but prone to subtle bugs.

### 6.1.1 Essential Script Header

```bash
#!/usr/bin/env bash
# Description: Brief description of what this script does
# Usage: script.sh [options] <arguments>
# Author: Name <email>
# Date: YYYY-MM-DD

set -euo pipefail

# Script body here
```

### 6.1.2 Set Options Explained

| Option | Effect | Recommendation |
|--------|--------|----------------|
| `set -e` | Exit on error | Always use |
| `set -u` | Error on undefined variable | Always use |
| `set -o pipefail` | Pipe fails if any command fails | Always use |
| `set -x` | Print commands (debug) | Only for debugging |

### 6.1.3 Variable Best Practices

```bash
# Always quote variables
name="$1"
path="$HOME/documents"

# Use braces for clarity
echo "${name}_suffix"
echo "${array[0]}"

# Default values
name="${1:-default}"      # Use default if unset or empty
name="${1-default}"       # Use default only if unset
name="${1:?Error message}" # Exit with error if unset or empty

# Readonly constants
readonly CONFIG_DIR="/etc/myapp"
readonly VERSION="1.0.0"

# Local variables in functions
my_function() {
    local result
    result=$(some_command)
    echo "$result"
}
```

### 6.1.4 Command Substitution

```bash
# Preferred: $() syntax
files=$(ls -la)
count=$(wc -l < "$file")

# Avoid: backticks (harder to nest, read)
# files=`ls -la`
```

### 6.1.5 Conditionals

```bash
# Use [[ ]] instead of [ ] for bash
if [[ -f "$file" ]]; then
    echo "File exists"
fi

# String comparison
if [[ "$name" == "expected" ]]; then
    echo "Match"
fi

# Regex matching
if [[ "$input" =~ ^[0-9]+$ ]]; then
    echo "Is a number"
fi

# Arithmetic
if (( count > 10 )); then
    echo "Greater than 10"
fi

# Multiple conditions
if [[ -f "$file" && -r "$file" ]]; then
    echo "File exists and is readable"
fi
```

### 6.1.6 Array Usage

```bash
# Declare array
files=()
files=("file1.txt" "file2.txt" "file 3.txt")

# Add to array
files+=("file4.txt")

# Iterate (preserving spaces in elements)
for file in "${files[@]}"; do
    echo "Processing: $file"
done

# Array length
echo "Count: ${#files[@]}"

# Array indices
for i in "${!files[@]}"; do
    echo "Index $i: ${files[i]}"
done
```

### 6.1.7 Style Checklist

- [ ] Script has shebang line
- [ ] Uses `set -euo pipefail`
- [ ] All variables are quoted
- [ ] Uses `[[ ]]` instead of `[ ]`
- [ ] Uses `$(...)` instead of backticks
- [ ] Functions use `local` for variables
- [ ] Constants are `readonly`
- [ ] Uses meaningful variable names
- [ ] Has usage/help documentation

---

## Navigation

- **Previous**: [shell-review-patterns.md](shell-review-patterns.md) (Index)
- **Next**: [Part 2: POSIX Compatibility](shell-review-patterns-part2-posix-compat.md)
