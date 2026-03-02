---
name: op-determine-version
description: "Determine the next version number based on change scope and semantic versioning"
procedure: support-skill
workflow-instruction: support
---

# Operation: Determine Version


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Get current version](#step-1-get-current-version)
  - [Step 2: Parse version components](#step-2-parse-version-components)
  - [Step 3: Analyze changes since last release](#step-3-analyze-changes-since-last-release)
  - [Step 4: Determine version increment](#step-4-determine-version-increment)
  - [Step 5: Handle pre-release versions](#step-5-handle-pre-release-versions)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Semantic Versioning Rules](#semantic-versioning-rules)
- [Commit Convention Keywords](#commit-convention-keywords)
- [Error Handling](#error-handling)
  - [No version found](#no-version-found)
  - [Invalid version format](#invalid-version-format)
  - [No commits since last release](#no-commits-since-last-release)
- [Complete Version Script](#complete-version-script)
- [Verification](#verification)

## Purpose

Calculate the correct next version number based on the type of changes being released, following semantic versioning rules.

## When to Use

- At the start of any release process
- When evaluating what version a release should be
- When changes span multiple categories and need version guidance

## Prerequisites

1. Current version number is known
2. Understanding of changes being released (breaking, features, fixes)
3. Git access to analyze commits since last release

## Procedure

### Step 1: Get current version

```bash
# From git tag
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//')

# Or from package.json
CURRENT_VERSION=$(jq -r '.version' package.json)

# Or from pyproject.toml
CURRENT_VERSION=$(grep -oP '(?<=version = ").*(?=")' pyproject.toml)

echo "Current version: $CURRENT_VERSION"
```

### Step 2: Parse version components

```bash
# Split version into components
MAJOR=$(echo "$CURRENT_VERSION" | cut -d. -f1)
MINOR=$(echo "$CURRENT_VERSION" | cut -d. -f2)
PATCH=$(echo "$CURRENT_VERSION" | cut -d. -f3 | cut -d- -f1)  # Handle pre-release suffix

echo "Major: $MAJOR, Minor: $MINOR, Patch: $PATCH"
```

### Step 3: Analyze changes since last release

```bash
# Get commits since last tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [ -n "$LAST_TAG" ]; then
  COMMITS=$(git log "$LAST_TAG"..HEAD --oneline)
else
  COMMITS=$(git log --oneline)
fi

# Categorize changes
BREAKING=$(echo "$COMMITS" | grep -ci "BREAKING\|breaking change" || echo "0")
FEATURES=$(echo "$COMMITS" | grep -ci "feat\|feature\|add" || echo "0")
FIXES=$(echo "$COMMITS" | grep -ci "fix\|bug\|patch" || echo "0")

echo "Breaking: $BREAKING, Features: $FEATURES, Fixes: $FIXES"
```

### Step 4: Determine version increment

```bash
if [ "$BREAKING" -gt 0 ]; then
  # Breaking changes = MAJOR
  INCREMENT="major"
  NEW_MAJOR=$((MAJOR + 1))
  NEW_VERSION="$NEW_MAJOR.0.0"
elif [ "$FEATURES" -gt 0 ]; then
  # New features = MINOR
  INCREMENT="minor"
  NEW_MINOR=$((MINOR + 1))
  NEW_VERSION="$MAJOR.$NEW_MINOR.0"
else
  # Bug fixes only = PATCH
  INCREMENT="patch"
  NEW_PATCH=$((PATCH + 1))
  NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
fi

echo "Increment type: $INCREMENT"
echo "New version: $NEW_VERSION"
```

### Step 5: Handle pre-release versions

```bash
# For alpha/beta/rc versions
PRERELEASE_TYPE="${1:-}"  # alpha, beta, rc

if [ -n "$PRERELEASE_TYPE" ]; then
  # Find existing pre-release number
  EXISTING=$(git tag -l "v$NEW_VERSION-$PRERELEASE_TYPE.*" | sort -V | tail -1)

  if [ -n "$EXISTING" ]; then
    PRE_NUM=$(echo "$EXISTING" | grep -oP "(?<=$PRERELEASE_TYPE\.)\d+")
    PRE_NUM=$((PRE_NUM + 1))
  else
    PRE_NUM=1
  fi

  NEW_VERSION="$NEW_VERSION-$PRERELEASE_TYPE.$PRE_NUM"
  echo "Pre-release version: $NEW_VERSION"
fi
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| current_version | string | no | Current version (auto-detected if not provided) |
| release_type | string | no | Force type: major, minor, patch |
| prerelease | string | no | Pre-release type: alpha, beta, rc |
| analyze_commits | boolean | no | Whether to analyze commits for type (default: true) |

## Output

| Field | Type | Description |
|-------|------|-------------|
| current_version | string | Current version |
| new_version | string | Recommended next version |
| increment_type | string | major, minor, or patch |
| changes | object | Breakdown of changes |
| rationale | string | Why this version was chosen |

## Example Output

```json
{
  "current_version": "1.2.3",
  "new_version": "1.3.0",
  "increment_type": "minor",
  "changes": {
    "breaking": 0,
    "features": 3,
    "fixes": 5
  },
  "rationale": "New features added (3 feat commits), no breaking changes"
}
```

## Semantic Versioning Rules

| Change Type | Version Part | Example |
|-------------|--------------|---------|
| Breaking API change | MAJOR | 1.2.3 -> 2.0.0 |
| New backward-compatible feature | MINOR | 1.2.3 -> 1.3.0 |
| Bug fix (no API change) | PATCH | 1.2.3 -> 1.2.4 |
| Alpha release | PRERELEASE | 1.2.4-alpha.1 |
| Beta release | PRERELEASE | 1.2.4-beta.1 |
| Release candidate | PRERELEASE | 1.2.4-rc.1 |

## Commit Convention Keywords

| Keyword | Category | Version Impact |
|---------|----------|----------------|
| BREAKING CHANGE | Breaking | MAJOR |
| feat, feature, add | Feature | MINOR |
| fix, bug, patch | Fix | PATCH |
| docs, documentation | Docs | PATCH |
| refactor | Refactor | PATCH |
| test | Test | PATCH |
| chore | Chore | PATCH |

## Error Handling

### No version found

**Cause**: Cannot determine current version.

**Solution**: Specify version manually or check version source files.

### Invalid version format

**Cause**: Version doesn't follow semver.

**Solution**: Fix version format to X.Y.Z pattern.

### No commits since last release

**Cause**: No changes to release.

**Solution**: Verify there are changes, or don't create release.

## Complete Version Script

```bash
#!/bin/bash
# determine_version.sh

RELEASE_TYPE="${1:-auto}"  # auto, major, minor, patch
PRERELEASE="${2:-}"        # alpha, beta, rc, or empty

# Get current version
CURRENT=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || echo "0.0.0")
MAJOR=$(echo "$CURRENT" | cut -d. -f1)
MINOR=$(echo "$CURRENT" | cut -d. -f2)
PATCH=$(echo "$CURRENT" | cut -d. -f3 | cut -d- -f1)

if [ "$RELEASE_TYPE" = "auto" ]; then
  # Analyze commits
  LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
  if [ -n "$LAST_TAG" ]; then
    COMMITS=$(git log "$LAST_TAG"..HEAD --oneline)
  else
    COMMITS=$(git log --oneline)
  fi

  if echo "$COMMITS" | grep -qi "BREAKING\|breaking change"; then
    RELEASE_TYPE="major"
  elif echo "$COMMITS" | grep -qi "feat\|feature\|add"; then
    RELEASE_TYPE="minor"
  else
    RELEASE_TYPE="patch"
  fi
fi

# Calculate new version
case "$RELEASE_TYPE" in
  major)
    NEW_VERSION="$((MAJOR + 1)).0.0"
    ;;
  minor)
    NEW_VERSION="$MAJOR.$((MINOR + 1)).0"
    ;;
  patch)
    NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"
    ;;
esac

# Add prerelease suffix
if [ -n "$PRERELEASE" ]; then
  EXISTING=$(git tag -l "v$NEW_VERSION-$PRERELEASE.*" | sort -V | tail -1)
  if [ -n "$EXISTING" ]; then
    PRE_NUM=$(echo "$EXISTING" | grep -oP "(?<=$PRERELEASE\.)\d+")
    PRE_NUM=$((PRE_NUM + 1))
  else
    PRE_NUM=1
  fi
  NEW_VERSION="$NEW_VERSION-$PRERELEASE.$PRE_NUM"
fi

echo "Current: $CURRENT"
echo "New: $NEW_VERSION"
echo "Type: $RELEASE_TYPE"
```

## Verification

After determining version:

```bash
# Verify version is valid semver
if [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+\.[0-9]+)?$ ]]; then
  echo "Valid semver: $NEW_VERSION"
else
  echo "Invalid version format"
fi

# Check tag doesn't already exist
if git rev-parse "v$NEW_VERSION" >/dev/null 2>&1; then
  echo "ERROR: Tag v$NEW_VERSION already exists"
else
  echo "Tag v$NEW_VERSION is available"
fi
```
