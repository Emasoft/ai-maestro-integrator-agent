# Shell Review Patterns - Part 2: POSIX Compatibility Requirements

## Table of Contents

- 6.2 POSIX compatibility requirements
  - 6.2.1 POSIX shell features safe to use
  - 6.2.2 Bash-only features that are NOT POSIX
  - 6.2.3 POSIX alternatives for Bash features table
  - 6.2.4 Testing POSIX compatibility (dash, checkbashisms, shellcheck)
  - 6.2.5 POSIX compatibility checklist

---

## 6.2 POSIX Compatibility Requirements

POSIX compatibility matters for scripts that must run on different systems.

### 6.2.1 POSIX Shell Features (Safe to Use)

```sh
#!/bin/sh
# POSIX-compatible script

# Variables
name="value"

# Basic conditionals
if [ -f "$file" ]; then
    echo "Exists"
fi

# Loops
for item in one two three; do
    echo "$item"
done

while [ "$count" -lt 10 ]; do
    count=$((count + 1))
done

# Functions (two syntaxes)
my_func() {
    echo "Function body"
}
```

### 6.2.2 Bash-Only Features (Not POSIX)

```bash
# These are NOT POSIX-compatible:

# [[ ]] test construct
[[ "$var" == "value" ]]

# (( )) arithmetic
(( x++ ))

# Arrays
arr=(one two three)

# $'...' quoting
echo $'tab\there'

# Process substitution
diff <(cmd1) <(cmd2)

# Brace expansion
echo {1..10}

# Here strings
grep pattern <<< "$string"

# local keyword
local var=value
```

### 6.2.3 POSIX Alternatives for Bash Features

| Bash Feature | POSIX Alternative |
|--------------|-------------------|
| `[[ $a == $b ]]` | `[ "$a" = "$b" ]` |
| `(( x++ ))` | `x=$((x + 1))` |
| `${var,,}` (lowercase) | `echo "$var" \| tr '[:upper:]' '[:lower:]'` |
| `${var^^}` (uppercase) | `echo "$var" \| tr '[:lower:]' '[:upper:]'` |
| `[[ $a =~ regex ]]` | `echo "$a" \| grep -qE "regex"` |
| `local var` | `var=value` (function-scoped anyway in some shells) |
| `source file` | `. file` |
| `echo -e` | `printf` |

### 6.2.4 Testing POSIX Compatibility

```bash
# Run script with dash (Debian/Ubuntu POSIX shell)
dash ./script.sh

# Use checkbashisms (Debian devscripts)
checkbashisms ./script.sh

# ShellCheck with POSIX mode
shellcheck -s sh ./script.sh
```

### 6.2.5 POSIX Checklist

- [ ] Shebang is `#!/bin/sh` (not bash)
- [ ] No `[[` or `((` constructs
- [ ] No arrays
- [ ] No `local` keyword (or verify shell supports it)
- [ ] Uses `=` not `==` in tests
- [ ] No process substitution
- [ ] No brace expansion
- [ ] Tested with dash or other POSIX shell

---

## Navigation

- **Previous**: [Part 1: Bash Checklist](shell-review-patterns-part1-bash-checklist.md)
- **Next**: [Part 3: ShellCheck](shell-review-patterns-part3-shellcheck.md)
- **Index**: [shell-review-patterns.md](shell-review-patterns.md)
