# Encoding Compliance Checker

## Contents

- When to run the encoding compliance checker
- How to run amia_check_encoding.py on specific files
- How to run amia_check_encoding.py on an entire directory
- What the checker verifies (5 checks)
- How to fix each type of encoding violation
- Integrating with pre-push hooks

---

## When to Run the Encoding Compliance Checker

Run `amia_check_encoding.py` in these situations:

1. **Before committing Python code** — as part of pre-commit or pre-push hooks
2. **During PR review** — to verify all file operations specify UTF-8 encoding
3. **After porting scripts from external sources** — to catch missing encoding parameters
4. **When CI reports encoding errors on Windows** — Windows defaults to cp1252, not UTF-8

---

## How to Run on Specific Files

```bash
uv run python scripts/amia_check_encoding.py path/to/file1.py path/to/file2.py --verbose
```

The `--verbose` flag shows a success message when all files pass.

---

## How to Run on an Entire Directory

```bash
uv run python scripts/amia_check_encoding.py --directory src/
```

This recursively finds all `.py` files in the directory and checks them all.

---

## What the Checker Verifies (5 Checks)

| # | Check | Pattern Detected | Fix |
|---|-------|-----------------|-----|
| 1 | `open()` without encoding | `open(path, "r")` | Add `encoding="utf-8"` |
| 2 | `.read_text()` without encoding | `path.read_text()` | Add `encoding="utf-8"` |
| 3 | `.write_text()` without encoding | `path.write_text(content)` | Add `encoding="utf-8"` |
| 4 | `json.load(open())` without encoding | `json.load(open(path))` | Add `encoding="utf-8"` to `open()` |
| 5 | `json.dump(open())` without encoding | `json.dump(data, open(path))` | Add `encoding="utf-8"` to `open()` |

The checker skips:

- Binary mode opens (`"rb"`, `"wb"`, etc.)
- Calls that already have `encoding=`
- Method calls on `self`/`cls` (custom methods, not Path)

---

## How to Fix Each Violation

### Fix 1: open() without encoding

```python
# WRONG
with open(path) as f:

# CORRECT
with open(path, encoding="utf-8") as f:
```

### Fix 2: .read_text() without encoding

```python
# WRONG
content = path.read_text()

# CORRECT
content = path.read_text(encoding="utf-8")
```

### Fix 3: .write_text() without encoding

```python
# WRONG
path.write_text(content)

# CORRECT
path.write_text(content, encoding="utf-8")
```

### Fix 4-5: json.load/dump with open()

```python
# WRONG
data = json.load(open(path))

# CORRECT
with open(path, encoding="utf-8") as f:
    data = json.load(f)
```

---

## Integrating with Pre-Push Hooks

Add to the plugin's pre-push hook script:

```python
# Run encoding compliance check on all staged .py files
import subprocess
result = subprocess.run(
    ["uv", "run", "python", "scripts/amia_check_encoding.py", "--directory", "scripts/"],
    capture_output=True,
    text=True
)
if result.returncode != 0:
    print(result.stdout)
    print("Encoding compliance check failed. Fix issues before pushing.")
    sys.exit(1)
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All files pass encoding checks |
| 1 | One or more encoding issues found |
