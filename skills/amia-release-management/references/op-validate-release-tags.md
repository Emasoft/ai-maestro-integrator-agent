---
name: op-validate-release-tags
description: "Prevent branch/tag collisions and validate release tag configuration"
procedure: support-skill
workflow-instruction: support
---

# Operation: Validate Release Tags

## Contents

- 1. When to validate release tags before creating them
- 2. How to compare version numbers against existing tags using semantic versioning
  - 2.1. Listing existing tags sorted by version
  - 2.2. Semver comparison using npx semver
  - 2.3. Semver comparison using Python (no external tools)
- 3. Why PAT_TOKEN is required for cross-workflow triggers
  - 3.1. The GITHUB_TOKEN limitation
  - 3.2. How to validate PAT_TOKEN is configured
  - 3.3. How to create a PAT_TOKEN
- 4. How to create annotated tags vs lightweight tags
  - 4.1. Annotated tags (recommended for releases)
  - 4.2. Lightweight tags (not recommended for releases)
- 5. How to use workflow_dispatch with a force option as a safety valve
- 6. How to prevent HTTP 300 errors from branch/tag name collisions
- 7. Troubleshooting release tag issues

## Purpose

Validate that a release tag can be safely created without colliding with existing branches or tags, and ensure the required credentials are in place for cross-workflow triggering. This operation prevents silent failures where a tag is created but the downstream release workflow never fires.

A "tag collision" occurs when a git tag name matches an existing branch name. GitHub's API returns an HTTP 300 (multiple choices) error when a reference is ambiguous because a branch and tag share the same name. This blocks API operations and confuses automated workflows.

## When to Use

- Before creating a release tag in a CI/CD pipeline
- When setting up a new repository's release automation
- When debugging why a release workflow did not trigger after a tag push

## Prerequisites

1. Git access to the repository with full history (`fetch-depth: 0` in CI)
2. Knowledge of the version number to tag
3. Understanding of the CI/CD system's workflow trigger mechanism

---

## 1. When to Validate Release Tags Before Creating Them

Tag validation should happen after the version is determined to be newer than the latest tag, but before the tag is actually created. The validation checks:

1. No existing tag with the same name
2. No branch with the same name as the tag
3. The version is strictly greater than the latest tag (not equal, not less)
4. The PAT_TOKEN secret is configured (if cross-workflow triggering is needed)

```
Version detected --> Version compared --> Tag validated --> Tag created
```

## 2. How to Compare Version Numbers Against Existing Tags

### 2.1. Listing Existing Tags Sorted by Version

```bash
# List all version tags, sorted by semantic version (newest first)
git tag -l 'v*' --sort=-version:refname

# Get the single latest tag
LATEST_TAG=$(git tag -l 'v*' --sort=-version:refname | head -n1)

# Handle the case where no tags exist yet
if [ -z "$LATEST_TAG" ]; then
  echo "No existing tags found. This will be the first release."
  LATEST_VERSION="0.0.0"
else
  # Remove the 'v' prefix to get the bare version number
  LATEST_VERSION="${LATEST_TAG#v}"
  echo "Latest tag: $LATEST_TAG (version: $LATEST_VERSION)"
fi
```

### 2.2. Semver Comparison Using npx semver

The `semver` npm package provides correct semantic version comparison, including proper handling of pre-release versions. For example, `1.0.0` is greater than `1.0.0-beta.1` even though the beta string looks "larger" alphabetically.

```bash
PACKAGE_VERSION="1.2.4"
LATEST_VERSION="1.2.3"

# npx -y automatically installs and runs the semver package
# The -r flag tests if the version satisfies a range expression
# ">1.2.3" means "strictly greater than 1.2.3"
if npx -y semver "$PACKAGE_VERSION" -r ">$LATEST_VERSION" > /dev/null 2>&1; then
  echo "Version $PACKAGE_VERSION is newer than $LATEST_VERSION. Release needed."
else
  echo "Version $PACKAGE_VERSION is NOT newer than $LATEST_VERSION. No release needed."
fi
```

### 2.3. Semver Comparison Using Python (No External Tools)

If Node.js is not available, Python can compare version numbers using the `packaging` library (included with pip) or the standard library's `tuple` comparison for simple cases.

```bash
# Simple comparison (works for stable versions without pre-release suffixes)
python3 -c "
from packaging.version import Version
import sys
current = Version('$PACKAGE_VERSION')
latest = Version('$LATEST_VERSION')
if current > latest:
    print(f'{current} is newer than {latest}')
    sys.exit(0)
else:
    print(f'{current} is NOT newer than {latest}')
    sys.exit(1)
"
```

If the `packaging` library is not available, use tuple comparison for non-pre-release versions:

```bash
python3 -c "
import sys
current = tuple(int(x) for x in '$PACKAGE_VERSION'.split('.'))
latest = tuple(int(x) for x in '$LATEST_VERSION'.split('.'))
sys.exit(0 if current > latest else 1)
"
```

## 3. Why PAT_TOKEN Is Required for Cross-Workflow Triggers

### 3.1. The GITHUB_TOKEN Limitation

GitHub Actions provides a built-in `GITHUB_TOKEN` secret for each workflow run. However, GitHub has a security feature that prevents events created by `GITHUB_TOKEN` from triggering other workflows. This is intentional -- it prevents accidental infinite loops where workflow A triggers workflow B which triggers workflow A again.

The consequence: if a `prepare-release` workflow creates a tag using `GITHUB_TOKEN`, the `release` workflow (triggered by tag creation) will **silently never fire**. There is no error message. The tag is created, but the release workflow does not start.

### 3.2. How to Validate PAT_TOKEN Is Configured

Fail fast with a clear error message if the required token is missing. This avoids a confusing silent failure later when the tag is pushed but nothing happens.

```bash
# Validate PAT_TOKEN at the start of the workflow, before any work is done
if [ -z "$PAT_TOKEN" ]; then
  echo "ERROR: PAT_TOKEN secret is not configured."
  echo ""
  echo "PAT_TOKEN is a Personal Access Token required for automatic release triggering."
  echo "When GITHUB_TOKEN pushes a tag, it does NOT trigger other workflows."
  echo "PAT_TOKEN allows the tag push to trigger the release workflow."
  echo ""
  echo "To fix this:"
  echo "  1. Go to GitHub Settings > Developer Settings > Personal Access Tokens"
  echo "  2. Create a token with 'repo' scope"
  echo "  3. Add it as a repository secret named 'PAT_TOKEN'"
  exit 1
fi
```

In a GitHub Actions workflow, use it in the checkout step:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0     # Full history needed for tag comparison
    token: ${{ secrets.PAT_TOKEN }}   # Use PAT instead of GITHUB_TOKEN
```

### 3.3. How to Create a PAT_TOKEN

1. Go to GitHub > Settings > Developer settings > Personal access tokens > Fine-grained tokens
2. Create a new token with:
   - Repository access: Select the specific repository
   - Permissions: Contents (read and write), Actions (read)
3. Copy the token value
4. Go to your repository > Settings > Secrets and variables > Actions
5. Create a new secret named `PAT_TOKEN` with the token value

For classic tokens (simpler but broader scope):

1. Go to GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Create a new token with `repo` scope
3. Add it as a repository secret named `PAT_TOKEN`

## 4. How to Create Annotated Tags vs Lightweight Tags

### 4.1. Annotated Tags (Recommended for Releases)

An "annotated tag" stores metadata: the tagger name, email, date, and a message. It is a full git object. Annotated tags are recommended for releases because they provide an audit trail.

```bash
VERSION="1.2.4"
TAG="v$VERSION"

# Configure git identity (required in CI environments)
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

# Create an annotated tag with a descriptive message
git tag -a "$TAG" -m "Release $TAG"

# Push the tag to the remote repository
# This push triggers the release workflow (if using PAT_TOKEN)
git push origin "$TAG"
```

### 4.2. Lightweight Tags (Not Recommended for Releases)

A "lightweight tag" is just a pointer to a commit with no additional metadata. It is essentially a named bookmark.

```bash
# NOT recommended for releases -- no metadata stored
git tag "v1.2.4"
git push origin "v1.2.4"
```

Lightweight tags should only be used for temporary or internal markers, not for releases.

## 5. How to Use workflow_dispatch with a Force Option

The `workflow_dispatch` trigger allows manually running a workflow from the GitHub Actions web interface. Adding a `force` input parameter creates a safety valve for edge cases where the automated version check needs to be bypassed.

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      force:
        description: 'Force release even if version check fails (use with caution)'
        required: false
        default: false
        type: boolean
```

In the workflow steps, check the force flag:

```bash
FORCE="${{ github.event.inputs.force }}"

if [ "$VERSION_IS_NEWER" = "true" ]; then
  echo "Version is newer. Proceeding with release."
elif [ "$FORCE" = "true" ]; then
  echo "WARNING: Force release enabled. Bypassing version check."
else
  echo "No release needed. Version is not newer than latest tag."
  exit 0
fi
```

Use the force option only for emergency situations, such as when a tag was accidentally deleted and needs to be recreated, or when a release build failed and needs to be retried with the same version.

## 6. How to Prevent HTTP 300 Errors from Branch/Tag Name Collisions

An HTTP 300 error from the GitHub API means "ambiguous reference" -- the given name matches both a branch and a tag. This happens when someone creates a branch with a name like `v1.2.4` that collides with the release tag `v1.2.4`.

To prevent this:

```bash
TAG="v$VERSION"

# Check for existing tag with the same name
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "ERROR: Tag $TAG already exists."
  echo "Do not reuse version numbers. Create a new patch version instead."
  exit 1
fi

# Check for existing branch with the same name as the tag
if git branch -r --list "origin/$TAG" | grep -q .; then
  echo "ERROR: A branch named $TAG exists on the remote."
  echo "This will cause ambiguous reference errors in the GitHub API."
  echo "Delete the branch or use a different tag name."
  exit 1
fi
```

Convention: Always prefix release tags with `v` (e.g., `v1.2.4`) and never create branches with the `v` prefix. This naturally avoids collisions.

## 7. Troubleshooting Release Tag Issues

### Release workflow did not trigger after tag push

**Cause**: The tag was pushed using `GITHUB_TOKEN`, which does not trigger downstream workflows.

**Solution**: Use `PAT_TOKEN` instead. See section 3 for setup instructions.

### Tag already exists

**Cause**: A previous release attempt created the tag, but the release build failed.

**Solution**: Do not reuse version numbers. Increment to a new patch version (e.g., `1.2.4` to `1.2.5`), fix the issue, and release again.

### Ambiguous reference (HTTP 300)

**Cause**: A branch and tag share the same name.

**Solution**: Delete the conflicting branch: `git push origin --delete <branch-name>`. Then retry the tag operation.

### Tag push rejected by branch protection

**Cause**: Branch protection rules may prevent pushing tags to protected branches.

**Solution**: Tag pushes do not modify branch content. Ensure the workflow uses `contents: write` permission and authenticates with `PAT_TOKEN`.

### Semver comparison gives wrong result for pre-release versions

**Cause**: String comparison treats `1.0.0-beta.1` as greater than `1.0.0` because `b` > empty. But in semver, pre-release versions have lower precedence.

**Solution**: Use a proper semver comparison tool (`npx semver` or Python's `packaging.version.Version`), not string or tuple comparison.
