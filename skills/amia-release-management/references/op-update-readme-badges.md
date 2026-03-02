---
name: op-update-readme-badges
description: "Update version badges and download links in README using marker-delimited sections"
procedure: support-skill
workflow-instruction: support
---

# Operation: Update README Badges

## Contents

- 1. When to update README badges as part of a release
- 2. How to define marker-delimited sections in README
  - 2.1. HTML comment marker syntax
  - 2.2. Choosing marker names
- 3. How to construct Shields.io badge URLs
  - 3.1. Static badge URL format
  - 3.2. URL encoding for special characters
  - 3.3. Stable vs pre-release badge colors
- 4. How to update content within marker-delimited sections using sed
  - 4.1. Single-line replacement with sed
  - 4.2. Multi-line replacement with perl
  - 4.3. Platform differences (macOS sed vs GNU sed)
- 5. How to implement dual-channel badge updates (stable and beta)
  - 5.1. Detecting pre-release versions
  - 5.2. Updating only the correct channel
- 6. How to auto-stage modified files after badge updates
- 7. Troubleshooting badge update failures

## Purpose

Automatically update version badges, download links, and other version-dependent content in `README.md` after a successful release. This operation uses HTML comment markers to scope updates to specific sections, preventing accidental modification of unrelated README content.

"Markers" are invisible HTML comments embedded in the README that define the start and end of an updatable section. The update script only modifies content between a pair of matching markers, leaving everything else untouched.

## When to Use

- After a successful release has been published (not before -- to prevent showing a version that does not yet exist)
- As part of a post-release workflow step
- When manually syncing README badges after a hotfix release

## Prerequisites

1. README.md contains properly formatted HTML comment markers around each updatable section
2. The new version number is known
3. Write access to the repository (for committing updated README)

---

## 1. When to Update README Badges as Part of a Release

README badges should be updated **after** the release is successfully published, not before. If the release build fails, the README should still show the previous working version. This prevents users from seeing download links for versions that do not exist.

The typical position in a pipeline is:

```
Tag created --> Builds pass --> Release published --> README updated  <-- THIS STEP
```

## 2. How to Define Marker-Delimited Sections in README

### 2.1. HTML Comment Marker Syntax

HTML comments are invisible when the README is rendered on GitHub, npm, PyPI, or any other markdown viewer. They serve as boundary markers for automated updates.

A marker pair consists of an opening marker and a closing marker. The content between them is the updatable section.

```markdown
<!-- VERSION_BADGE -->
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/user/repo/releases)
<!-- VERSION_BADGE_END -->
```

Everything between `<!-- VERSION_BADGE -->` and `<!-- VERSION_BADGE_END -->` will be replaced by the update script. Everything outside these markers is never modified.

### 2.2. Choosing Marker Names

Use descriptive, uppercase names with underscores. Always use a `_END` suffix for the closing marker.

| Marker Pair | Purpose |
|-------------|---------|
| `VERSION_BADGE` / `VERSION_BADGE_END` | Stable version badge |
| `BETA_BADGE` / `BETA_BADGE_END` | Pre-release version badge |
| `DOWNLOADS` / `DOWNLOADS_END` | Stable download links |
| `BETA_DOWNLOADS` / `BETA_DOWNLOADS_END` | Pre-release download links |
| `INSTALL_CMD` / `INSTALL_CMD_END` | Installation command with version |

Example README structure with markers:

```markdown
# My Project

<!-- VERSION_BADGE -->
[![Version](https://img.shields.io/badge/version-1.2.3-blue)](https://github.com/user/repo/releases/tag/v1.2.3)
<!-- VERSION_BADGE_END -->

<!-- BETA_BADGE -->
[![Beta](https://img.shields.io/badge/beta-1.3.0--beta.1-orange)](https://github.com/user/repo/releases/tag/v1.3.0-beta.1)
<!-- BETA_BADGE_END -->

## Installation

<!-- INSTALL_CMD -->
pip install mypackage==1.2.3
<!-- INSTALL_CMD_END -->
```

## 3. How to Construct Shields.io Badge URLs

Shields.io is a free service that generates badge images in SVG or PNG format. Badges are commonly displayed in README files to show version, build status, coverage, and other project metadata.

### 3.1. Static Badge URL Format

A static badge URL follows this pattern:

```
https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>
```

- `LABEL`: The left side of the badge (e.g., "version", "release")
- `MESSAGE`: The right side of the badge (e.g., "1.2.3")
- `COLOR`: A named color or hex code (e.g., "blue", "green", "orange", "brightgreen")

Example:

```
https://img.shields.io/badge/version-1.2.3-blue
```

This produces a badge that reads "version | 1.2.3" with a blue background on the right side.

### 3.2. URL Encoding for Special Characters

Certain characters in version strings must be URL-encoded in Shields.io URLs:

| Character | URL Encoding | Example |
|-----------|-------------|---------|
| `-` (hyphen) | `--` (double hyphen) | `1.0.0-beta.1` becomes `1.0.0--beta.1` |
| `_` (underscore) | `__` (double underscore) | `pre_release` becomes `pre__release` |
| space | `%20` or `_` | `My Label` becomes `My%20Label` |

Example with a pre-release version:

```
https://img.shields.io/badge/version-2.0.0--beta.1-orange
```

### 3.3. Stable vs Pre-Release Badge Colors

| Version Type | Recommended Color | Color Code |
|-------------|-------------------|------------|
| Stable release | Blue or green | `blue` or `brightgreen` |
| Beta / pre-release | Orange | `orange` |
| Release candidate | Yellow | `yellow` |
| Deprecated | Red | `red` |

## 4. How to Update Content Within Marker-Delimited Sections Using sed

### 4.1. Single-Line Replacement with sed

When the updatable section contains a single line (such as a badge), use `sed` to find the line between the markers and replace it.

```bash
VERSION="1.2.4"
BADGE_URL="https://img.shields.io/badge/version-${VERSION}-blue"
RELEASE_URL="https://github.com/user/repo/releases/tag/v${VERSION}"

# Replace the line between VERSION_BADGE markers
# GNU sed (Linux):
sed -i '/<!-- VERSION_BADGE -->/,/<!-- VERSION_BADGE_END -->/{
  /<!-- VERSION_BADGE -->/!{/<!-- VERSION_BADGE_END -->/!d}
}' README.md

sed -i "/<!-- VERSION_BADGE -->/a\\
[![Version](${BADGE_URL})](${RELEASE_URL})" README.md

# macOS sed (requires empty string after -i):
sed -i '' '/<!-- VERSION_BADGE -->/,/<!-- VERSION_BADGE_END -->/{
  /<!-- VERSION_BADGE -->/!{/<!-- VERSION_BADGE_END -->/!d}
}' README.md
```

**How this sed command works:**

1. `/<!-- VERSION_BADGE -->/,/<!-- VERSION_BADGE_END -->/` -- Select lines between the two markers (inclusive)
2. `{/<!-- VERSION_BADGE -->/!{/<!-- VERSION_BADGE_END -->/!d}}` -- Delete all lines that are NOT the markers themselves
3. The `a\` command appends the new badge line after the opening marker

### 4.2. Multi-Line Replacement with perl

For replacing multiple lines between markers, `perl` is often more reliable than `sed` because it handles multi-line patterns natively and works identically on macOS and Linux.

```bash
VERSION="1.2.4"

# Replace everything between markers with new content
perl -i -0pe '
  s{(<!-- DOWNLOADS -->).*?(<!-- DOWNLOADS_END -->)}
   {$1\n[Download v'"$VERSION"'](https://github.com/user/repo/releases/tag/v'"$VERSION"')\n$2}s
' README.md
```

**How this perl command works:**

- `-i` -- Edit the file in place
- `-0pe` -- Slurp the entire file as one string, apply the substitution, print
- The regex captures the opening and closing markers (`$1` and `$2`) and replaces everything between them
- The `s` flag at the end makes `.` match newlines

### 4.3. Platform Differences (macOS sed vs GNU sed)

| Feature | macOS sed | GNU sed (Linux) |
|---------|-----------|-----------------|
| In-place editing | `sed -i '' 'command'` | `sed -i 'command'` |
| Newline in append | `sed '/pattern/a\` then newline | `sed '/pattern/a TEXT'` |
| Extended regex | `sed -E` | `sed -E` or `sed -r` |

To avoid platform issues, use `perl` for any non-trivial replacement, since `perl` behaves identically on all platforms.

## 5. How to Implement Dual-Channel Badge Updates (Stable and Beta)

### 5.1. Detecting Pre-Release Versions

A pre-release version contains a hyphen followed by a pre-release identifier, as defined by Semantic Versioning. For example, `1.2.3-beta.1` is a pre-release, while `1.2.3` is a stable release.

```bash
VERSION="1.2.3-beta.1"

if echo "$VERSION" | grep -qE '-'; then
  CHANNEL="beta"
  BADGE_COLOR="orange"
else
  CHANNEL="stable"
  BADGE_COLOR="blue"
fi

echo "Channel: $CHANNEL, Color: $BADGE_COLOR"
```

### 5.2. Updating Only the Correct Channel

When releasing a stable version, update only the stable badge and stable download links. When releasing a pre-release, update only the beta badge and beta download links. Never update both at the same time.

```bash
if [ "$CHANNEL" = "stable" ]; then
  BADGE_MARKER="VERSION_BADGE"
  DOWNLOAD_MARKER="DOWNLOADS"
else
  BADGE_MARKER="BETA_BADGE"
  DOWNLOAD_MARKER="BETA_DOWNLOADS"
fi

# Update badge for the appropriate channel
perl -i -0pe '
  s{(<!-- '"$BADGE_MARKER"' -->).*?(<!-- '"$BADGE_MARKER"'_END -->)}
   {$1\n[![Version](https://img.shields.io/badge/version-'"$VERSION"'-'"$BADGE_COLOR"')](https://github.com/user/repo/releases/tag/v'"$VERSION"')\n$2}s
' README.md
```

## 6. How to Auto-Stage Modified Files After Badge Updates

After updating the README, stage the modified file for the next commit. In a CI/CD pipeline, the workflow typically commits and pushes the README update automatically.

```bash
# Stage the modified README
git add README.md

# Commit with a descriptive message
git commit -m "docs: update README badges for v${VERSION}"

# Push to the default branch
git push origin main
```

In GitHub Actions, the workflow must configure git identity before committing:

```bash
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
git add README.md
git commit -m "docs: update README badges for v${VERSION}"
git push
```

## 7. Troubleshooting Badge Update Failures

### Badge image not updating after commit

**Cause**: Shields.io caches badge images. After updating the README, the old badge image may be served from cache.

**Solution**: Append a cache-busting query parameter to the badge URL: `?cacheSeconds=0`. Or wait a few minutes for the cache to expire (Shields.io cache duration is typically 5 minutes).

### sed command modifies wrong section

**Cause**: Marker names are duplicated or the closing marker is missing.

**Solution**: Verify that each marker pair is unique in the file. Search for duplicates: `grep -c 'VERSION_BADGE' README.md` should return exactly 2 (one opening, one closing).

### Badge shows URL-encoded characters instead of version

**Cause**: The version string was not properly escaped for Shields.io URLs. Hyphens in version strings like `1.0.0-beta.1` must be doubled: `1.0.0--beta.1`.

**Solution**: Use a sed substitution to double hyphens before constructing the badge URL:

```bash
ESCAPED_VERSION=$(echo "$VERSION" | sed 's/-/--/g')
BADGE_URL="https://img.shields.io/badge/version-${ESCAPED_VERSION}-blue"
```

### Permission denied when pushing README update in CI

**Cause**: The default `GITHUB_TOKEN` may not have write permissions to the repository contents.

**Solution**: Ensure the workflow has `contents: write` permission:

```yaml
permissions:
  contents: write
```

Or use a Personal Access Token (PAT_TOKEN) with `repo` scope for the push step.
