# Syntax CI Failure Patterns

## Table of Contents

- 3.1 Here-String and Heredoc Terminator Issues
  - 3.1.1 PowerShell here-string requirements ("@ at column 0)
  - 3.1.2 Bash heredoc requirements (EOF at column 0)
  - 3.1.3 YAML multiline string indentation
- 3.2 Shell Quoting Differences
  - 3.2.1 Bash quoting rules
  - 3.2.2 POSIX sh quoting rules
  - 3.2.3 Zsh quoting differences
  - 3.2.4 PowerShell quoting rules
- 3.3 Command Substitution Syntax
  - 3.3.1 Backticks vs $() differences
  - 3.3.2 Nested command substitution

---

## 3.1 Here-String and Heredoc Terminator Issues

Here-documents (heredocs) and here-strings have strict formatting requirements that cause cryptic CI failures.

### 3.1.1 PowerShell Here-String Requirements

PowerShell here-strings have strict rules:

1. Opening `@"` or `@'` must be at end of line (nothing after)
2. Closing `"@` or `'@` must be at column 0 (start of line)
3. No characters allowed after the closing delimiter

**Common CI Failure**: Indented closing delimiter.

**Error Message**:
```
Unrecognized token in source text.
At line:5 char:1
```

**WRONG** (indented closing delimiter):
```powershell
$content = @"
    This is content
    on multiple lines
    "@ # WRONG: "@ is indented
```

**CORRECT** (closing at column 0):
```powershell
$content = @"
    This is content
    on multiple lines
"@
```

**WRONG** (text after opening):
```powershell
$content = @" some text
more text
"@
```

**CORRECT**:
```powershell
$content = @"
some text
more text
"@
```

**GitHub Actions YAML Gotcha**: YAML indentation conflicts with here-string requirements.

**WRONG**:
```yaml
- name: Create file
  shell: pwsh
  run: |
    $content = @"
    Line 1
    Line 2
    "@ # YAML indentation pushes "@ to column 4
```

**CORRECT** (use YAML literal block with proper structure):
```yaml
- name: Create file
  shell: pwsh
  run: |
    $content = @"
    Line 1
    Line 2
"@
    Set-Content -Path "file.txt" -Value $content
```

### 3.1.2 Bash Heredoc Requirements

Bash heredocs have similar requirements:

1. Delimiter must be consistent (case-sensitive)
2. Default: closing delimiter at column 0, no trailing spaces
3. With `<<-`: closing delimiter can be preceded by tabs (not spaces)

**Common CI Failure**: Trailing whitespace after delimiter.

**Error Message**:
```
./script.sh: line 10: warning: here-document at line 3 delimited by end-of-file (wanted 'EOF')
```

**WRONG** (space after EOF):
```bash
cat <<EOF
Line 1
Line 2
EOF   # WRONG: trailing space
```

**CORRECT**:
```bash
cat <<EOF
Line 1
Line 2
EOF
```

**WRONG** (indented closing delimiter without `-`):
```bash
cat <<EOF
    Line 1
    Line 2
    EOF  # WRONG: EOF is indented
```

**CORRECT with indentation** (use `<<-` and tabs):
```bash
cat <<-EOF
	Line 1
	Line 2
	EOF
```
Note: The indentation above must be TAB characters, not spaces.

**GitHub Actions YAML Pattern**:
```yaml
- name: Create heredoc
  run: |
    cat > output.txt <<'EOF'
    This is line 1
    This is line 2
    EOF
```

**Single vs Double Quote Delimiter**:
```bash
# Variables expanded (unquoted or double-quoted)
cat <<EOF
Hello $USER
EOF

# Variables NOT expanded (single-quoted)
cat <<'EOF'
Hello $USER
EOF
# Output: Hello $USER (literal)
```

### 3.1.3 YAML Multiline String Indentation

YAML has multiple multiline syntaxes, each with different rules.

**Literal Block Scalar (`|`)**: Preserves newlines
```yaml
script: |
  Line 1
  Line 2
  Line 3
# Result: "Line 1\nLine 2\nLine 3\n"
```

**Folded Block Scalar (`>`)**: Folds newlines to spaces
```yaml
script: >
  This is a
  single line
  of text
# Result: "This is a single line of text\n"
```

**Block Chomping Indicators**:
```yaml
# Keep trailing newline (default)
script: |
  content

# Strip trailing newline
script: |-
  content

# Keep all trailing newlines
script: |+
  content


```

**Common CI Failure**: Inconsistent indentation in YAML blocks.

**Error Message**:
```
yaml: line 5: did not find expected key
```

**WRONG** (inconsistent indentation):
```yaml
- name: Run script
  run: |
    echo "line 1"
   echo "line 2"  # WRONG: 3 spaces instead of 4
```

**CORRECT**:
```yaml
- name: Run script
  run: |
    echo "line 1"
    echo "line 2"
```

---

## 3.2 Shell Quoting Differences

Different shells have different quoting rules, causing CI failures when scripts run on unexpected shells.

### 3.2.1 Bash Quoting Rules

**Single Quotes (`'`)**: Literal strings, no expansion
```bash
echo 'Hello $USER'  # Output: Hello $USER
echo 'It'\''s fine' # Escape single quote by ending, adding \', starting again
```

**Double Quotes (`"`)**: Variable expansion, escape sequences
```bash
echo "Hello $USER"  # Output: Hello username
echo "Tab\there"    # Output: Tab	here (tab character)
echo "Quote: \""    # Output: Quote: "
```

**No Quotes**: Word splitting and glob expansion
```bash
files="file1.txt file2.txt"
cat $files   # Expands to: cat file1.txt file2.txt

pattern="*.txt"
echo $pattern  # Expands to actual filenames
```

**$'...' (ANSI-C Quoting)**: Escape sequences in single quotes
```bash
echo $'Tab\there'  # Output: Tab	here
echo $'Line1\nLine2'  # Output with actual newline
```

### 3.2.2 POSIX sh Quoting Rules

POSIX sh is more limited than Bash:

**NOT available in POSIX sh**:
- `$'...'` ANSI-C quoting
- `[[` double bracket conditionals
- Arrays
- `+=` append operator

**Common CI Failure**: Using Bash syntax with `shell: sh`

**WRONG** (Bash syntax in sh):
```yaml
- name: Run script
  shell: sh
  run: |
    # FAILS: $'...' not available in sh
    echo $'Line1\nLine2'
```

**CORRECT** (POSIX-compatible):
```yaml
- name: Run script
  shell: sh
  run: |
    # Use printf for escape sequences
    printf 'Line1\nLine2\n'
```

### 3.2.3 Zsh Quoting Differences

Zsh (default on macOS) has subtle differences:

**Word Splitting**: Zsh does NOT split unquoted variables by default
```bash
# In Bash
files="file1 file2"
cat $files  # Passes two arguments

# In Zsh (by default)
files="file1 file2"
cat $files  # Passes ONE argument: "file1 file2"
```

**Fix**: Use explicit word splitting
```zsh
# Zsh: Force word splitting
cat ${=files}

# Or set option
setopt SH_WORD_SPLIT
```

**Glob Expansion**: Zsh errors on no match by default
```bash
# In Bash (no match = literal pattern)
echo *.xyz  # Output: *.xyz (if no .xyz files)

# In Zsh (no match = error)
echo *.xyz  # Error: no matches found: *.xyz
```

### 3.2.4 PowerShell Quoting Rules

PowerShell quoting is different from POSIX shells:

**Single Quotes (`'`)**: Literal string, no expansion
```powershell
Write-Host 'Hello $env:USER'  # Output: Hello $env:USER
Write-Host 'It''s fine'       # Double single-quote to escape
```

**Double Quotes (`"`)**: Variable expansion
```powershell
Write-Host "Hello $env:USER"  # Output: Hello username
Write-Host "Quote: `""        # Backtick escapes in double quotes
```

**Escape Character**: Backtick (\`) not backslash (\)
```powershell
Write-Host "Line1`nLine2"     # Newline
Write-Host "Tab`there"        # Tab
Write-Host "`$variable"       # Literal dollar sign
```

**Common CI Failure**: Using backslash escapes in PowerShell
```powershell
# WRONG: Backslash is not escape character
Write-Host "Line1\nLine2"  # Output: Line1\nLine2

# CORRECT: Use backtick
Write-Host "Line1`nLine2"  # Output with newline
```

---

## 3.3 Command Substitution Syntax

### 3.3.1 Backticks vs $() Differences

Two syntaxes for command substitution:

| Syntax | Nesting | Escaping | Recommended |
|--------|---------|----------|-------------|
| \`cmd\` | Difficult | Complex | No |
| $(cmd) | Easy | Simple | Yes |

**Backtick Issues**:
```bash
# Escaping is confusing
echo `echo \`pwd\``  # Nested backticks need escaping

# Backslash behavior is inconsistent
echo `echo "\$HOME"`  # May not work as expected
```

**$() is Better**:
```bash
# Clear nesting
echo $(echo $(pwd))  # No escaping needed

# Consistent backslash handling
echo $(echo "\$HOME")
```

**Common CI Failure**: Nested backticks without proper escaping

**WRONG**:
```bash
# Fails: unbalanced backticks
result=`echo `date``
```

**CORRECT**:
```bash
result=$(echo $(date))
```

### 3.3.2 Nested Command Substitution

**Pattern**: Building complex commands
```bash
# Get directory of a symlink target
dir=$(dirname $(readlink -f "$0"))

# Multiple levels
result=$(command1 $(command2 $(command3)))
```

**In YAML** (watch quote escaping):
```yaml
- name: Get script directory
  run: |
    SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
    echo "Script is in: $SCRIPT_DIR"
```

**PowerShell Equivalent**:
```powershell
# Use $() inside strings
$result = "Today is $(Get-Date -Format 'yyyy-MM-dd')"

# Or for commands returning objects
$dir = (Get-Item $PSScriptRoot).FullName
```

---

## Summary: Syntax Checklist

Before committing CI workflows:

- [ ] Here-string closing delimiters at column 0
- [ ] Heredoc delimiters have no trailing whitespace
- [ ] YAML multiline blocks have consistent indentation
- [ ] Shell script uses correct shell (bash vs sh vs zsh)
- [ ] Escape sequences use correct syntax for target shell
- [ ] Command substitution uses `$()` not backticks
- [ ] PowerShell uses backtick (\`) for escaping
- [ ] Quotes are appropriate for expansion needs
- [ ] POSIX sh scripts avoid Bash-only features
