---
name: release-workflow-chain
description: "Two-workflow release pipeline pattern: prepare-release detects version bump and creates tag, release builds and publishes"
procedure: support-skill
workflow-instruction: support
---

# Release Workflow Chain

## Contents

- 1. Why release automation uses two separate workflows instead of one
- 2. How the prepare-release workflow works
  - 2.1. Version detection from project metadata
  - 2.2. Version comparison against the latest git tag
  - 2.3. Changelog validation gate
  - 2.4. Tag creation to trigger the downstream workflow
- 3. How the release workflow works
  - 3.1. Triggering on tag push events
  - 3.2. Building artifacts
  - 3.3. Creating the GitHub release with changelog
- 4. How to pass data between workflows using artifacts
  - 4.1. Uploading an artifact in the prepare-release workflow
  - 4.2. Downloading an artifact in the release workflow
  - 4.3. Artifact retention and cleanup
- 5. Why PAT_TOKEN is essential for cross-workflow triggering
- 6. How to detect the version from different project types
  - 6.1. Python projects (pyproject.toml)
  - 6.2. Node.js projects (package.json)
  - 6.3. Rust projects (Cargo.toml)
  - 6.4. Go projects (version variable)
  - 6.5. Generic VERSION file
- 7. Emergency manual release procedure
- 8. Complete two-workflow flow diagram
- 9. Troubleshooting the release workflow chain

## Purpose

Document the two-workflow release pipeline pattern where a `prepare-release` workflow detects that a version bump occurred, validates the changelog, and creates a git tag. The tag creation then triggers a separate `release` workflow that builds artifacts and publishes the release. This separation ensures releases are only published after all builds succeed.

The two-workflow pattern prevents a common failure mode: if building and releasing were in the same workflow, a build failure would leave a tag pointing to broken code. With two workflows, the tag is created only after validation passes, and the release is published only after all builds succeed.

## When to Use

- When setting up release automation for any project type (Python, Node.js, Rust, Go, etc.)
- When debugging why a release did not trigger or did not complete
- When designing a CI/CD pipeline that includes changelog validation

## Prerequisites

1. A git repository with CI/CD configured (e.g., GitHub Actions)
2. A PAT_TOKEN secret configured for cross-workflow triggering (see section 5)
3. Version information stored in a project metadata file
4. A `CHANGELOG.md` file with structured version entries

---

## 1. Why Release Automation Uses Two Separate Workflows Instead of One

A single monolithic release workflow would combine version detection, changelog validation, building, and publishing into one file. This causes several problems:

- **Partial failure risk**: If the build fails after the tag is created, a tag exists for a version that was never released. Users may try to download a version that does not exist.
- **No separation of concerns**: The logic for "should we release?" is mixed with the logic for "how do we build?"
- **Harder to debug**: A single large workflow with many jobs is harder to troubleshoot than two focused workflows.
- **Manual re-trigger difficulty**: Re-running a monolithic workflow repeats all steps, including tag creation, which fails if the tag already exists.

The two-workflow pattern solves these by separating the "decide and tag" step from the "build and publish" step:

| Workflow | Trigger | Responsibility |
|----------|---------|----------------|
| prepare-release | Push to main branch | Detect version bump, validate changelog, create tag |
| release | Tag push (v*) | Build artifacts, publish release, update README |

## 2. How the Prepare-Release Workflow Works

### 2.1. Version Detection from Project Metadata

The first step reads the version number from the project's metadata file. This is language-specific (see section 6 for all languages). The version is stored as a workflow output for use in later steps.

```yaml
- name: Get project version
  id: version
  run: |
    # Example for Python (pyproject.toml)
    VERSION=$(python3 -c "
    import tomllib
    with open('pyproject.toml', 'rb') as f:
        data = tomllib.load(f)
    print(data['project']['version'])
    ")
    echo "version=$VERSION" >> $GITHUB_OUTPUT
    echo "Detected version: $VERSION"
```

### 2.2. Version Comparison Against the Latest Git Tag

After detecting the project version, compare it to the latest git tag to determine if a release is needed. A release is needed only when the project version is strictly greater than the latest tagged version.

```yaml
- name: Check if release needed
  id: check
  run: |
    PACKAGE_VERSION="${{ steps.version.outputs.version }}"
    LATEST_TAG=$(git tag -l 'v*' --sort=-version:refname | head -n1)
    LATEST_VERSION="${LATEST_TAG#v}"
    LATEST_VERSION="${LATEST_VERSION:-0.0.0}"

    echo "Package version: $PACKAGE_VERSION"
    echo "Latest tag version: $LATEST_VERSION"

    # Compare versions using Python (works in any CI environment)
    python3 -c "
    from packaging.version import Version
    import sys
    if Version('$PACKAGE_VERSION') > Version('$LATEST_VERSION'):
        print('Release needed')
        sys.exit(0)
    else:
        print('No release needed')
        sys.exit(1)
    " && NEEDS_RELEASE=true || NEEDS_RELEASE=false

    echo "should_release=$NEEDS_RELEASE" >> $GITHUB_OUTPUT
```

### 2.3. Changelog Validation Gate

Before creating the tag, validate that CHANGELOG.md contains an entry for the version being released. See the reference document `op-validate-changelog-gate.md` for the full AWK extraction command and error message format.

```yaml
- name: Validate changelog
  if: steps.check.outputs.should_release == 'true'
  run: |
    VERSION="${{ steps.version.outputs.version }}"
    # Changelog validation is handled by the CPV plugin validator.
    # Use: uv run --with pyyaml python scripts/validate_plugin.py . --verbose
    # For inline changelog extraction, see the AWK command in op-validate-changelog-gate.md section 2.
    uv run --with pyyaml python scripts/validate_plugin.py . --verbose
```

### 2.4. Tag Creation to Trigger the Downstream Workflow

After validation passes, create an annotated git tag and push it. The push event triggers the release workflow.

```yaml
- name: Create and push tag
  if: steps.check.outputs.should_release == 'true'
  run: |
    VERSION="${{ steps.version.outputs.version }}"
    TAG="v$VERSION"
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git tag -a "$TAG" -m "Release $TAG"
    git push origin "$TAG"
```

## 3. How the Release Workflow Works

### 3.1. Triggering on Tag Push Events

The release workflow triggers when a tag matching the pattern `v*` is pushed:

```yaml
on:
  push:
    tags:
      - 'v*'
```

This fires for any tag starting with `v`, such as `v1.2.3`, `v2.0.0-beta.1`, etc.

### 3.2. Building Artifacts

The release workflow builds whatever artifacts the project needs (wheels, binaries, Docker images, etc.). This step is project-specific but follows a common pattern:

```yaml
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: |
          # Project-specific build commands here
          echo "Building on ${{ matrix.os }}"
      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: build-${{ matrix.os }}
          path: dist/
```

### 3.3. Creating the GitHub Release with Changelog

After all builds succeed, create the GitHub release using the changelog content:

```yaml
  release:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Download all build artifacts
        uses: actions/download-artifact@v4
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ github.ref_name }}
          body_path: changelog-extract.md
          files: |
            build-*/*
```

## 4. How to Pass Data Between Workflows Using Artifacts

GitHub Actions workflows are isolated -- they do not share filesystem or environment variables. Artifacts are the official mechanism for passing files between workflow runs.

### 4.1. Uploading an Artifact in the Prepare-Release Workflow

```yaml
- name: Save changelog for release workflow
  run: |
    echo "$CHANGELOG_CONTENT" > changelog-extract.md

- name: Upload changelog artifact
  uses: actions/upload-artifact@v4
  with:
    name: changelog-${{ steps.version.outputs.version }}
    path: changelog-extract.md
    retention-days: 1
```

### 4.2. Downloading an Artifact in the Release Workflow

```yaml
- name: Download changelog artifact
  uses: actions/download-artifact@v4
  with:
    name: changelog-${{ needs.prepare.outputs.version }}
    path: .

- name: Read changelog
  run: cat changelog-extract.md
```

**Important limitation**: Artifacts can only be downloaded within the same workflow run or from a completed workflow run using the GitHub API. Cross-workflow artifact download requires the `actions/download-artifact` action with `run-id` parameter or a separate API call.

### 4.3. Artifact Retention and Cleanup

Set `retention-days: 1` for changelog artifacts since they are only needed during the release process. This prevents storage accumulation over time.

For long-lived artifacts (like build binaries attached to releases), the GitHub Release itself handles storage -- artifacts uploaded to a release are retained indefinitely.

## 5. Why PAT_TOKEN Is Essential for Cross-Workflow Triggering

When the prepare-release workflow pushes a tag using the default `GITHUB_TOKEN`, GitHub's security model prevents that tag push from triggering the release workflow. This is a deliberate security feature to prevent infinite workflow loops.

A Personal Access Token (PAT_TOKEN) bypasses this restriction because it represents a real user, not the automated workflow identity. Tags pushed with PAT_TOKEN are treated as user actions and trigger downstream workflows normally.

See the reference document `op-validate-release-tags.md` sections 3.1 through 3.3 for detailed PAT_TOKEN setup instructions.

## 6. How to Detect the Version from Different Project Types

### 6.1. Python Projects (pyproject.toml)

```bash
VERSION=$(python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
print(data['project']['version'])
")
```

### 6.2. Node.js Projects (package.json)

```bash
VERSION=$(node -p "require('./package.json').version")
```

### 6.3. Rust Projects (Cargo.toml)

```bash
VERSION=$(grep '^version' Cargo.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
```

### 6.4. Go Projects (version variable)

Go projects often define a version variable in a source file:

```bash
VERSION=$(grep 'Version =' cmd/version.go | sed 's/.*"\(.*\)".*/\1/')
```

### 6.5. Generic VERSION File

```bash
VERSION=$(cat VERSION | tr -d '[:space:]')
```

## 7. Emergency Manual Release Procedure

When the automated pipeline is broken and an urgent release is needed, tags can be created manually. Use this only as a last resort.

```bash
# 1. Ensure you are on the main branch with the latest code
git checkout main
git pull origin main

# 2. Verify the version in the project metadata
# (use the appropriate command for your project type from section 6)

# 3. Create an annotated tag
VERSION="1.2.4"
git tag -a "v$VERSION" -m "Release v$VERSION"

# 4. Push the tag (this triggers the release workflow)
git push origin "v$VERSION"
```

**Warnings for manual releases:**

- Ensure the version in the project metadata matches the tag version
- Ensure CHANGELOG.md has an entry for this version (the release workflow may still validate this)
- Do not reuse a version number that was previously tagged, even if the old release failed
- Document the manual release in the project's issue tracker so the team knows the automation was bypassed

## 8. Complete Two-Workflow Flow Diagram

```
Push to main branch
      |
      v
[prepare-release.yml]
      |
      +-- Read version from project metadata
      |
      +-- Get latest git tag
      |
      +-- Compare: is version > latest tag?
      |       |
      |     No --> Exit (no release needed)
      |       |
      |     Yes
      |       |
      +-- Validate CHANGELOG.md has entry for version
      |       |
      |     Missing --> EXIT WITH ERROR (release blocked)
      |       |
      |     Found
      |       |
      +-- Extract changelog content
      |
      +-- Upload changelog as artifact
      |
      +-- Create annotated tag (using PAT_TOKEN)
      |
      +-- Push tag to remote
              |
              v
        Tag push event (v*)
              |
              v
      [release.yml]
              |
              +-- Checkout code at tag
              |
              +-- Build artifacts (all platforms)
              |       |
              |     Build failed --> EXIT (no release published)
              |       |
              |     Build passed
              |       |
              +-- Download changelog artifact
              |
              +-- Create GitHub Release with:
              |       - Tag name
              |       - Changelog as release notes
              |       - Build artifacts as downloads
              |
              +-- Update README badges (post-release)
              |
              v
          Release published
```

## 9. Troubleshooting the Release Workflow Chain

### Release did not trigger after merge to main

**Cause**: The prepare-release workflow detected that the package version is not newer than the latest tag.

**Diagnosis**: Check the prepare-release workflow log. Look for "No release needed" or "package version not newer than latest tag."

**Solution**: Bump the version in the project metadata file, commit, and push to main again.

### Changelog validation failed

**Cause**: CHANGELOG.md does not have an entry for the version being released.

**Diagnosis**: The prepare-release workflow log shows "CHANGELOG VALIDATION FAILED" with the expected format.

**Solution**: Add an entry to CHANGELOG.md following the format `## X.Y.Z - Title`, commit, and push to main. The workflow will automatically retry.

### Tag was created but release workflow did not fire

**Cause**: The tag was pushed using GITHUB_TOKEN instead of PAT_TOKEN.

**Diagnosis**: Check the prepare-release workflow. The checkout step should use `token: ${{ secrets.PAT_TOKEN }}`.

**Solution**: Delete the tag (`git push origin --delete v1.2.4`), configure PAT_TOKEN, bump to a new version, and retry.

### Build failed after tag was created

**Cause**: The code at the tagged commit has a build error.

**Solution**: Do not reuse the failed version number. Fix the build error, bump to a new patch version (e.g., `1.2.5`), update CHANGELOG.md, commit, and push to main. A new tag will be created for the new version.

### Artifact not found in release workflow

**Cause**: The changelog artifact uploaded by prepare-release has expired (retention-days) or the artifact name does not match.

**Solution**: Ensure artifact names are consistent between upload and download steps. Check that `retention-days` is long enough for the release workflow to complete (1 day is usually sufficient).

### README badges not updated after release

**Cause**: The README update step ran before the release was published, or the workflow lacks `contents: write` permission.

**Solution**: Ensure the README update step runs after the release is published. Verify the workflow has `contents: write` permission. See `op-update-readme-badges.md` for detailed troubleshooting.
