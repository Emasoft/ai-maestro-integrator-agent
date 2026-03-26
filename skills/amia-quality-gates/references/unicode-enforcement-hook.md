# Unicode Enforcement Hook

## Table of Contents

- When the Unicode enforcement hook runs
- What the hook checks (4 checks)
- How to fix each type of Unicode violation
- Running the standalone Unicode compliance checker
- Configuring the hook in pre-push scripts

---

## When the Unicode Enforcement Hook Runs

The Unicode compliance check runs automatically as part of the pre-push hook (step 4) in every Emasoft plugin. It checks all text files in `scripts/` and `skills/` directories before allowing a `git push`.

The hook blocks pushes when MAJOR issues are found (BOM detection). MINOR issues (CRLF line endings) generate warnings but do not block.

---

## What the Hook Checks (4 Checks)

| # | Check | Severity | Description |
|---|-------|----------|-------------|
| 1 | BOM detection | MAJOR | Files must NOT have a Byte Order Mark (UTF-8 BOM `EF BB BF` or UTF-16 BOM) |
| 2 | Line ending consistency | MINOR | Files should use Unix line endings (LF `\n`), not Windows (CRLF `\r\n`) |
| 3 | Encoding validity | Blocks | Files must be valid UTF-8 (checked by the standalone script) |
| 4 | Non-ASCII identifiers | Warning | Python identifiers should use ASCII-only characters (checked by standalone script) |

The pre-push hook performs checks 1 and 2 (lightweight byte-level checks). The standalone `amia_unicode_compliance.py` script performs all 4 checks for comprehensive auditing.

---

## How to Fix Each Violation

### Fix BOM (Byte Order Mark)

A BOM is an invisible marker at the start of a file. Some Windows editors add it automatically.

**Detection**: The file starts with bytes `EF BB BF` (UTF-8 BOM) or `FF FE` / `FE FF` (UTF-16 BOM).

**Fix options**:

Option 1 -- Using Python:

```python
path = "path/to/file.py"
with open(path, "rb") as f:
    content = f.read()
# Remove UTF-8 BOM
if content.startswith(b"\xef\xbb\xbf"):
    content = content[3:]
with open(path, "wb") as f:
    f.write(content)
```

Option 2 -- Using sed (macOS/Linux):

```bash
sed -i '1s/^\xEF\xBB\xBF//' path/to/file.py
```

Option 3 -- Configure your editor to save without BOM. In VS Code: set `"files.encoding": "utf8"` (not `"utf8bom"`).

### Fix CRLF Line Endings

**Detection**: File contains `\r\n` byte sequences instead of `\n`.

**Fix options**:

Option 1 -- Using git (recommended):

```bash
# Configure git to auto-convert
git config core.autocrlf input

# Re-checkout the file
git checkout -- path/to/file.py
```

Option 2 -- Using dos2unix:

```bash
dos2unix path/to/file.py
```

Option 3 -- Using Python:

```python
path = "path/to/file.py"
content = open(path, "rb").read()
content = content.replace(b"\r\n", b"\n")
open(path, "wb").write(content)
```

### Fix Non-ASCII Identifiers

**Detection**: Python variable, function, or class names contain characters with code points > 127.

**Fix**: Rename the identifier to use only ASCII characters (a-z, A-Z, 0-9, underscore).

```python
# WRONG
cafe_count = 42
naive_approach = True

# CORRECT
cafe_count = 42
naive_approach = True
```

### Fix Invalid UTF-8 Encoding

**Detection**: File cannot be decoded as UTF-8.

**Fix**: Convert the file to UTF-8:

```bash
# Using iconv
iconv -f WINDOWS-1252 -t UTF-8 file.py > file_utf8.py
mv file_utf8.py file.py
```

---

## Running the Standalone Unicode Compliance Checker

The full-featured checker is at `scripts/amia_unicode_compliance.py`:

```bash
# Check specific files
uv run python scripts/amia_unicode_compliance.py path/to/file1.py path/to/file2.md --verbose

# Check an entire directory recursively
uv run python scripts/amia_unicode_compliance.py --directory src/

# Check the plugin itself
uv run python scripts/amia_unicode_compliance.py --directory scripts/ --verbose
```

The standalone checker performs all 4 checks (BOM, line endings, encoding validity, non-ASCII identifiers) and provides detailed file:line reports.

---

## Configuring the Hook in Pre-Push Scripts

The Unicode compliance check is added as step 4 in each plugin's pre-push hook script. The check function scans `scripts/` and `skills/` directories for BOM markers and CRLF line endings.

```python
# In pre-push-hook.py main():

# 4. Unicode compliance check
print(f"{BLUE}Checking Unicode compliance...{NC}")
all_issues.extend(check_unicode_compliance(repo_root))
```

The `check_unicode_compliance()` function returns a list of `(severity, message)` tuples:

- `("MAJOR", "...")` -- BOM detected (blocks push)
- `("MINOR", "...")` -- CRLF line endings (warning only)
