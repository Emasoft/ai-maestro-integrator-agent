---
name: op-create-release-tag
description: "Create an annotated git tag for the release"
procedure: support-skill
workflow-instruction: support
---

# Operation: Create Release Tag


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Verify working directory is clean](#step-1-verify-working-directory-is-clean)
  - [Step 2: Verify version bump is committed](#step-2-verify-version-bump-is-committed)
  - [Step 3: Check tag doesn't already exist](#step-3-check-tag-doesnt-already-exist)
  - [Step 4: Create tag annotation message](#step-4-create-tag-annotation-message)
  - [Step 5: Create annotated tag](#step-5-create-annotated-tag)
  - [Step 6: Verify tag](#step-6-verify-tag)
  - [Step 7: Push tag to remote](#step-7-push-tag-to-remote)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Tag Naming Convention](#tag-naming-convention)
- [Signed Tags](#signed-tags)
- [Error Handling](#error-handling)
  - [Tag already exists](#tag-already-exists)
  - [Working directory dirty](#working-directory-dirty)
  - [Push fails](#push-fails)
  - [GPG signing fails](#gpg-signing-fails)
- [Complete Tag Script](#complete-tag-script)
- [Verification](#verification)

## Purpose

Create an annotated git tag marking the release commit, with proper annotation message.

## When to Use

- After version bump is committed
- As part of the release process
- Before pushing release to remote

## Prerequisites

1. Version bump committed
2. All release changes committed
3. Clean working directory
4. Write access to repository

## Procedure

### Step 1: Verify working directory is clean

```bash
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: Working directory is not clean"
  git status --short
  exit 1
fi
echo "Working directory is clean"
```

### Step 2: Verify version bump is committed

```bash
VERSION="1.2.4"
TAG_NAME="v$VERSION"

# Check last commit includes version files
LAST_COMMIT_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)
if echo "$LAST_COMMIT_FILES" | grep -qE "package.json|pyproject.toml|VERSION"; then
  echo "Version bump committed"
else
  echo "WARNING: Last commit may not include version bump"
fi
```

### Step 3: Check tag doesn't already exist

```bash
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
  echo "ERROR: Tag $TAG_NAME already exists"
  exit 1
fi
echo "Tag $TAG_NAME is available"
```

### Step 4: Create tag annotation message

```bash
# Get changelog for this version
CHANGELOG_ENTRY=$(sed -n "/## \[$VERSION\]/,/## \[/p" CHANGELOG.md | head -n -1)

# Create annotation message
ANNOTATION="Release $VERSION

$(echo "$CHANGELOG_ENTRY" | tail -n +2)
"

echo "Tag annotation:"
echo "$ANNOTATION"
```

### Step 5: Create annotated tag

```bash
# Create tag with annotation
git tag -a "$TAG_NAME" -m "$ANNOTATION"

if [ $? -eq 0 ]; then
  echo "Tag $TAG_NAME created successfully"
else
  echo "ERROR: Failed to create tag"
  exit 1
fi
```

### Step 6: Verify tag

```bash
# Show tag details
git show "$TAG_NAME" --no-patch

# Verify tag points to HEAD
TAG_COMMIT=$(git rev-parse "$TAG_NAME^{}")
HEAD_COMMIT=$(git rev-parse HEAD)

if [ "$TAG_COMMIT" = "$HEAD_COMMIT" ]; then
  echo "Tag points to HEAD: OK"
else
  echo "WARNING: Tag does not point to HEAD"
fi
```

### Step 7: Push tag to remote

```bash
# Push just the tag
git push origin "$TAG_NAME"

if [ $? -eq 0 ]; then
  echo "Tag $TAG_NAME pushed to origin"
else
  echo "ERROR: Failed to push tag"
  exit 1
fi
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| version | string | yes | Version number (without v prefix) |
| annotation | string | no | Custom annotation message |
| push | boolean | no | Whether to push tag to remote (default: true) |
| sign | boolean | no | Whether to GPG sign the tag |

## Output

| Field | Type | Description |
|-------|------|-------------|
| tag_name | string | Name of created tag |
| commit | string | Commit SHA the tag points to |
| pushed | boolean | Whether tag was pushed |
| annotation | string | Tag annotation message |

## Example Output

```json
{
  "tag_name": "v1.2.4",
  "commit": "abc123def456",
  "pushed": true,
  "annotation": "Release 1.2.4\n\n### Features\n- Add SSO support\n..."
}
```

## Tag Naming Convention

| Type | Format | Example |
|------|--------|---------|
| Release | v{major}.{minor}.{patch} | v1.2.4 |
| Pre-release | v{version}-{type}.{n} | v1.2.4-beta.1 |
| Release candidate | v{version}-rc.{n} | v1.2.4-rc.1 |

## Signed Tags

For GPG-signed tags:

```bash
# Sign with default key
git tag -s "$TAG_NAME" -m "$ANNOTATION"

# Sign with specific key
git tag -u "key-id" "$TAG_NAME" -m "$ANNOTATION"

# Verify signature
git tag -v "$TAG_NAME"
```

## Error Handling

### Tag already exists

**Cause**: Tag name is already in use.

**Solution**: Use different version or delete existing tag (with caution).

### Working directory dirty

**Cause**: Uncommitted changes exist.

**Solution**: Commit or stash changes first.

### Push fails

**Cause**: No push access or tag exists on remote.

**Solution**: Check permissions, verify tag doesn't exist on remote.

### GPG signing fails

**Cause**: GPG key not configured or not available.

**Solution**: Set up GPG signing or skip signing.

## Complete Tag Script

```bash
#!/bin/bash
# create_release_tag.sh

VERSION="$1"
PUSH="${2:-true}"
SIGN="${3:-false}"

if [ -z "$VERSION" ]; then
  echo "Usage: create_release_tag.sh <version> [push=true] [sign=false]"
  exit 1
fi

TAG_NAME="v$VERSION"

echo "=== Creating Release Tag ==="
echo "Tag: $TAG_NAME"

# Check working directory
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: Uncommitted changes exist"
  exit 1
fi

# Check tag availability
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
  echo "ERROR: Tag $TAG_NAME already exists"
  exit 1
fi

# Get changelog
ANNOTATION="Release $VERSION"
if [ -f "CHANGELOG.md" ]; then
  ENTRY=$(sed -n "/## \[$VERSION\]/,/## \[/p" CHANGELOG.md | head -n -1 | tail -n +2)
  if [ -n "$ENTRY" ]; then
    ANNOTATION="$ANNOTATION

$ENTRY"
  fi
fi

# Create tag
if [ "$SIGN" = "true" ]; then
  git tag -s "$TAG_NAME" -m "$ANNOTATION"
else
  git tag -a "$TAG_NAME" -m "$ANNOTATION"
fi

if [ $? -ne 0 ]; then
  echo "ERROR: Failed to create tag"
  exit 1
fi

echo "Tag created"

# Push
if [ "$PUSH" = "true" ]; then
  git push origin "$TAG_NAME"
  if [ $? -eq 0 ]; then
    echo "Tag pushed to origin"
  else
    echo "ERROR: Failed to push tag"
    exit 1
  fi
fi

# Show result
echo ""
echo "=== Tag Details ==="
git show "$TAG_NAME" --no-patch
```

## Verification

After creating tag:

```bash
# List tags
git tag -l "v*" | tail -5

# Show tag details
git show "v$VERSION" --no-patch

# Verify on remote
git ls-remote --tags origin | grep "v$VERSION"
```
