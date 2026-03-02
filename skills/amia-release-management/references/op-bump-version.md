---
name: op-bump-version
description: "Update version number in all required files"
procedure: support-skill
workflow-instruction: support
---

# Operation: Bump Version


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify version files](#step-1-identify-version-files)
  - [Step 2: Get current version](#step-2-get-current-version)
  - [Step 3: Update each file](#step-3-update-each-file)
  - [Step 4: Update lock files (if applicable)](#step-4-update-lock-files-if-applicable)
  - [Step 5: Verify updates](#step-5-verify-updates)
  - [Step 6: Generate report](#step-6-generate-report)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Supported File Types](#supported-file-types)
- [Error Handling](#error-handling)
  - [File not writable](#file-not-writable)
  - [Version mismatch after update](#version-mismatch-after-update)
  - [Lock file update fails](#lock-file-update-fails)
- [Complete Bump Script](#complete-bump-script)
- [Verification](#verification)

## Purpose

Update the version number consistently across all project files that contain version information.

## When to Use

- After determining the new version number
- As part of the release process
- Before creating the release tag

## Prerequisites

1. New version number determined
2. Write access to version files
3. Knowledge of which files contain version

## Procedure

### Step 1: Identify version files

```bash
# Common version file locations
VERSION_FILES=(
  "package.json"
  "pyproject.toml"
  "setup.py"
  "setup.cfg"
  "VERSION"
  "version.txt"
  "src/__version__.py"
  "lib/version.rb"
  "Cargo.toml"
  "pom.xml"
)

# Find which ones exist
EXISTING_FILES=()
for file in "${VERSION_FILES[@]}"; do
  if [ -f "$file" ]; then
    EXISTING_FILES+=("$file")
  fi
done

echo "Version files found: ${EXISTING_FILES[*]}"
```

### Step 2: Get current version

```bash
NEW_VERSION="1.2.4"

# Detect current version from first available file
for file in "${EXISTING_FILES[@]}"; do
  case "$file" in
    package.json)
      CURRENT=$(jq -r '.version' "$file")
      ;;
    pyproject.toml)
      CURRENT=$(grep -oP '(?<=version = ").*(?=")' "$file")
      ;;
    VERSION|version.txt)
      CURRENT=$(cat "$file" | tr -d '[:space:]')
      ;;
  esac
  if [ -n "$CURRENT" ]; then
    break
  fi
done

echo "Current version: $CURRENT"
echo "New version: $NEW_VERSION"
```

### Step 3: Update each file

```bash
UPDATED_FILES=()

for file in "${EXISTING_FILES[@]}"; do
  echo "Updating $file..."

  case "$file" in
    package.json)
      # Use jq to update version
      jq ".version = \"$NEW_VERSION\"" "$file" > "$file.tmp" && mv "$file.tmp" "$file"
      ;;

    pyproject.toml)
      # Update version in pyproject.toml
      sed -i '' "s/version = \"$CURRENT\"/version = \"$NEW_VERSION\"/" "$file"
      ;;

    setup.py)
      # Update version in setup.py
      sed -i '' "s/version=['\"]$CURRENT['\"]/version='$NEW_VERSION'/" "$file"
      ;;

    VERSION|version.txt)
      # Simple file with just version
      echo "$NEW_VERSION" > "$file"
      ;;

    src/__version__.py|*/__version__.py)
      # Python version module
      echo "__version__ = \"$NEW_VERSION\"" > "$file"
      ;;

    Cargo.toml)
      # Rust package
      sed -i '' "s/^version = \"$CURRENT\"/version = \"$NEW_VERSION\"/" "$file"
      ;;
  esac

  UPDATED_FILES+=("$file")
done
```

### Step 4: Update lock files (if applicable)

```bash
# Update package-lock.json
if [ -f "package-lock.json" ]; then
  npm install --package-lock-only
  UPDATED_FILES+=("package-lock.json")
fi

# Update poetry.lock
if [ -f "poetry.lock" ]; then
  poetry lock --no-update
  UPDATED_FILES+=("poetry.lock")
fi
```

### Step 5: Verify updates

```bash
echo "Verifying version updates..."

for file in "${UPDATED_FILES[@]}"; do
  case "$file" in
    package.json)
      VERIFY=$(jq -r '.version' "$file")
      ;;
    pyproject.toml)
      VERIFY=$(grep -oP '(?<=version = ").*(?=")' "$file")
      ;;
    VERSION|version.txt)
      VERIFY=$(cat "$file" | tr -d '[:space:]')
      ;;
  esac

  if [ "$VERIFY" = "$NEW_VERSION" ]; then
    echo "  $file: OK ($VERIFY)"
  else
    echo "  $file: MISMATCH (expected $NEW_VERSION, got $VERIFY)"
  fi
done
```

### Step 6: Generate report

```json
{
  "old_version": "1.2.3",
  "new_version": "1.2.4",
  "files_modified": [
    "package.json",
    "package-lock.json",
    "pyproject.toml"
  ],
  "verification": "all_match"
}
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| new_version | string | yes | Version to set |
| files | string[] | no | Specific files to update (auto-detect if not provided) |
| dry_run | boolean | no | Preview changes without writing |

## Output

| Field | Type | Description |
|-------|------|-------------|
| old_version | string | Previous version |
| new_version | string | New version set |
| files_modified | string[] | List of files updated |
| verification | string | all_match or list of mismatches |

## Example Output

```json
{
  "old_version": "1.2.3",
  "new_version": "1.2.4",
  "files_modified": [
    "package.json",
    "package-lock.json"
  ],
  "verification": "all_match"
}
```

## Supported File Types

| File | Format | Update Method |
|------|--------|---------------|
| package.json | JSON | jq |
| pyproject.toml | TOML | sed |
| setup.py | Python | sed |
| VERSION | Plain text | echo |
| Cargo.toml | TOML | sed |
| __version__.py | Python | echo |

## Error Handling

### File not writable

**Cause**: Permission denied.

**Solution**: Check file permissions.

### Version mismatch after update

**Cause**: Sed pattern didn't match.

**Solution**: Check file format, update pattern.

### Lock file update fails

**Cause**: Package manager error.

**Solution**: Run package manager manually.

## Complete Bump Script

```bash
#!/bin/bash
# bump_version.sh

NEW_VERSION="$1"
DRY_RUN="${2:-false}"

if [ -z "$NEW_VERSION" ]; then
  echo "Usage: bump_version.sh <new_version> [dry_run]"
  exit 1
fi

echo "=== Version Bump ==="
echo "New version: $NEW_VERSION"
echo "Dry run: $DRY_RUN"

UPDATED=()

# package.json
if [ -f "package.json" ]; then
  OLD=$(jq -r '.version' package.json)
  if [ "$DRY_RUN" = "false" ]; then
    jq ".version = \"$NEW_VERSION\"" package.json > package.json.tmp
    mv package.json.tmp package.json
  fi
  echo "package.json: $OLD -> $NEW_VERSION"
  UPDATED+=("package.json")
fi

# pyproject.toml
if [ -f "pyproject.toml" ]; then
  OLD=$(grep -oP '(?<=version = ").*(?=")' pyproject.toml | head -1)
  if [ "$DRY_RUN" = "false" ]; then
    sed -i '' "s/version = \"$OLD\"/version = \"$NEW_VERSION\"/" pyproject.toml
  fi
  echo "pyproject.toml: $OLD -> $NEW_VERSION"
  UPDATED+=("pyproject.toml")
fi

# VERSION file
if [ -f "VERSION" ]; then
  OLD=$(cat VERSION)
  if [ "$DRY_RUN" = "false" ]; then
    echo "$NEW_VERSION" > VERSION
  fi
  echo "VERSION: $OLD -> $NEW_VERSION"
  UPDATED+=("VERSION")
fi

echo ""
echo "Files updated: ${UPDATED[*]}"

# Verify
if [ "$DRY_RUN" = "false" ]; then
  echo ""
  echo "Verification:"
  for f in "${UPDATED[@]}"; do
    case "$f" in
      package.json) V=$(jq -r '.version' "$f") ;;
      pyproject.toml) V=$(grep -oP '(?<=version = ").*(?=")' "$f" | head -1) ;;
      VERSION) V=$(cat "$f") ;;
    esac
    if [ "$V" = "$NEW_VERSION" ]; then
      echo "  $f: OK"
    else
      echo "  $f: MISMATCH"
    fi
  done
fi
```

## Verification

After bumping:

```bash
# Verify all version files match
./bump_version.sh "$NEW_VERSION" true  # dry run to see current

# Git diff to see changes
git diff --name-only

# Check specific file
jq '.version' package.json
```
