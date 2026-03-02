---
name: op-generate-changelog
description: "Generate changelog from commit history since last release"
procedure: support-skill
workflow-instruction: support
---

# Operation: Generate Changelog


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Identify version range](#step-1-identify-version-range)
  - [Step 2: Fetch commits in range](#step-2-fetch-commits-in-range)
  - [Step 3: Categorize commits](#step-3-categorize-commits)
  - [Step 4: Format changelog](#step-4-format-changelog)
  - [Step 5: Save changelog](#step-5-save-changelog)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Changelog Format](#changelog-format)
- [[1.2.4] - 2025-02-05](#124-2025-02-05)
  - [Breaking Changes](#breaking-changes)
  - [Features](#features)
  - [Bug Fixes](#bug-fixes)
  - [Documentation](#documentation)
  - [Maintenance](#maintenance)
- [Category Detection Rules](#category-detection-rules)
- [Error Handling](#error-handling)
  - [No commits in range](#no-commits-in-range)
  - [Invalid tag](#invalid-tag)
  - [No commit convention](#no-commit-convention)
- [Complete Changelog Script](#complete-changelog-script)
- [Verification](#verification)

## Purpose

Compile a categorized changelog from commit history between two versions, formatted for release notes.

## When to Use

- Before creating release notes
- When preparing a release
- When auditing changes between versions

## Prerequisites

1. Git access to repository
2. Consistent commit message convention used
3. Previous release tag exists (or first release)

## Procedure

### Step 1: Identify version range

```bash
# Get the previous tag
FROM_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
TO_REF="HEAD"

if [ -z "$FROM_TAG" ]; then
  echo "No previous tag found - including all commits"
  FROM_TAG=""
fi

echo "Generating changelog from $FROM_TAG to $TO_REF"
```

### Step 2: Fetch commits in range

```bash
if [ -n "$FROM_TAG" ]; then
  COMMITS=$(git log "$FROM_TAG".."$TO_REF" --pretty=format:"%H|%s|%an|%ad" --date=short)
else
  COMMITS=$(git log --pretty=format:"%H|%s|%an|%ad" --date=short)
fi
```

### Step 3: Categorize commits

```bash
# Initialize categories
BREAKING=""
FEATURES=""
FIXES=""
DOCS=""
REFACTOR=""
TESTS=""
CHORE=""
OTHER=""

# Process each commit
while IFS='|' read -r hash subject author date; do
  # Determine category from commit message
  LOWER_SUBJECT=$(echo "$subject" | tr '[:upper:]' '[:lower:]')

  if echo "$LOWER_SUBJECT" | grep -q "breaking"; then
    BREAKING="$BREAKING\n- $subject"
  elif echo "$LOWER_SUBJECT" | grep -qE "^feat|^feature|^add"; then
    FEATURES="$FEATURES\n- $subject"
  elif echo "$LOWER_SUBJECT" | grep -qE "^fix|^bug|^patch|^hotfix"; then
    FIXES="$FIXES\n- $subject"
  elif echo "$LOWER_SUBJECT" | grep -qE "^doc|^docs"; then
    DOCS="$DOCS\n- $subject"
  elif echo "$LOWER_SUBJECT" | grep -qE "^refactor|^refact"; then
    REFACTOR="$REFACTOR\n- $subject"
  elif echo "$LOWER_SUBJECT" | grep -qE "^test|^tests"; then
    TESTS="$TESTS\n- $subject"
  elif echo "$LOWER_SUBJECT" | grep -qE "^chore|^build|^ci"; then
    CHORE="$CHORE\n- $subject"
  else
    OTHER="$OTHER\n- $subject"
  fi
done <<< "$COMMITS"
```

### Step 4: Format changelog

```bash
VERSION="1.2.4"
DATE=$(date +%Y-%m-%d)

CHANGELOG="## [$VERSION] - $DATE

"

# Add sections in order of importance
if [ -n "$BREAKING" ]; then
  CHANGELOG="$CHANGELOG### Breaking Changes
$(echo -e "$BREAKING")

"
fi

if [ -n "$FEATURES" ]; then
  CHANGELOG="$CHANGELOG### Features
$(echo -e "$FEATURES")

"
fi

if [ -n "$FIXES" ]; then
  CHANGELOG="$CHANGELOG### Bug Fixes
$(echo -e "$FIXES")

"
fi

if [ -n "$DOCS" ]; then
  CHANGELOG="$CHANGELOG### Documentation
$(echo -e "$DOCS")

"
fi

if [ -n "$REFACTOR" ]; then
  CHANGELOG="$CHANGELOG### Refactoring
$(echo -e "$REFACTOR")

"
fi

if [ -n "$TESTS" ]; then
  CHANGELOG="$CHANGELOG### Tests
$(echo -e "$TESTS")

"
fi

if [ -n "$CHORE" ]; then
  CHANGELOG="$CHANGELOG### Maintenance
$(echo -e "$CHORE")

"
fi

if [ -n "$OTHER" ]; then
  CHANGELOG="$CHANGELOG### Other Changes
$(echo -e "$OTHER")

"
fi

echo "$CHANGELOG"
```

### Step 5: Save changelog

```bash
# Append to CHANGELOG.md (prepend to existing content)
if [ -f "CHANGELOG.md" ]; then
  # Read existing content
  EXISTING=$(cat CHANGELOG.md)

  # Write new changelog at top
  echo -e "$CHANGELOG\n$EXISTING" > CHANGELOG.md
else
  # Create new file
  echo -e "# Changelog\n\n$CHANGELOG" > CHANGELOG.md
fi

echo "Changelog updated"
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| from_tag | string | no | Start tag (auto-detected if not provided) |
| to_ref | string | no | End reference (default: HEAD) |
| version | string | yes | Version number for changelog header |
| include_authors | boolean | no | Whether to include author names |
| include_hashes | boolean | no | Whether to include commit hashes |

## Output

| Field | Type | Description |
|-------|------|-------------|
| changelog | string | Formatted changelog markdown |
| commit_count | number | Total commits processed |
| categories | object | Count per category |
| saved_to | string | Path where changelog was saved |

## Example Output

```json
{
  "changelog": "## [1.2.4] - 2025-02-05\n\n### Features\n- Add SSO support\n...",
  "commit_count": 15,
  "categories": {
    "breaking": 0,
    "features": 3,
    "fixes": 8,
    "docs": 2,
    "other": 2
  },
  "saved_to": "CHANGELOG.md"
}
```

## Changelog Format

```markdown
## [1.2.4] - 2025-02-05

### Breaking Changes
- Remove deprecated API endpoints

### Features
- Add SSO authentication support
- Implement user preferences panel

### Bug Fixes
- Fix login redirect loop
- Resolve session timeout issue

### Documentation
- Update API documentation
- Add deployment guide

### Maintenance
- Update dependencies
- Improve CI pipeline
```

## Category Detection Rules

| Category | Commit Prefixes |
|----------|-----------------|
| Breaking | BREAKING, breaking change |
| Features | feat, feature, add |
| Bug Fixes | fix, bug, patch, hotfix |
| Documentation | doc, docs |
| Refactoring | refactor, refact |
| Tests | test, tests |
| Maintenance | chore, build, ci |

## Error Handling

### No commits in range

**Cause**: No commits between tags.

**Solution**: Verify tag range, or use different range.

### Invalid tag

**Cause**: Tag doesn't exist.

**Solution**: List available tags with `git tag -l`.

### No commit convention

**Cause**: Commits don't follow convention.

**Solution**: All non-matching commits go to "Other Changes".

## Complete Changelog Script

```bash
#!/bin/bash
# generate_changelog.sh

VERSION="$1"
FROM_TAG="${2:-$(git describe --tags --abbrev=0 2>/dev/null)}"
TO_REF="${3:-HEAD}"

echo "=== Generating Changelog ==="
echo "Version: $VERSION"
echo "Range: $FROM_TAG..$TO_REF"

# Categories
declare -a BREAKING FEATURES FIXES DOCS OTHER

# Get commits
if [ -n "$FROM_TAG" ]; then
  RANGE="$FROM_TAG..$TO_REF"
else
  RANGE=""
fi

while IFS= read -r line; do
  LOWER=$(echo "$line" | tr '[:upper:]' '[:lower:]')
  if [[ "$LOWER" == *"breaking"* ]]; then
    BREAKING+=("$line")
  elif [[ "$LOWER" == feat* ]] || [[ "$LOWER" == add* ]]; then
    FEATURES+=("$line")
  elif [[ "$LOWER" == fix* ]] || [[ "$LOWER" == bug* ]]; then
    FIXES+=("$line")
  elif [[ "$LOWER" == doc* ]]; then
    DOCS+=("$line")
  else
    OTHER+=("$line")
  fi
done < <(git log $RANGE --pretty=format:"%s")

# Generate markdown
echo "## [$VERSION] - $(date +%Y-%m-%d)"
echo ""

if [ ${#BREAKING[@]} -gt 0 ]; then
  echo "### Breaking Changes"
  for c in "${BREAKING[@]}"; do echo "- $c"; done
  echo ""
fi

if [ ${#FEATURES[@]} -gt 0 ]; then
  echo "### Features"
  for c in "${FEATURES[@]}"; do echo "- $c"; done
  echo ""
fi

if [ ${#FIXES[@]} -gt 0 ]; then
  echo "### Bug Fixes"
  for c in "${FIXES[@]}"; do echo "- $c"; done
  echo ""
fi

if [ ${#DOCS[@]} -gt 0 ]; then
  echo "### Documentation"
  for c in "${DOCS[@]}"; do echo "- $c"; done
  echo ""
fi

if [ ${#OTHER[@]} -gt 0 ]; then
  echo "### Other"
  for c in "${OTHER[@]}"; do echo "- $c"; done
fi
```

## Verification

After generating:

```bash
# Preview changelog
head -50 CHANGELOG.md

# Verify format
if grep -q "## \[$VERSION\]" CHANGELOG.md; then
  echo "Changelog entry for $VERSION found"
else
  echo "ERROR: Version entry not found"
fi
```
