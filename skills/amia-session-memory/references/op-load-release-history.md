---
name: op-load-release-history
description: "Load release history from handoff documents"
procedure: support-skill
workflow-instruction: support
---

# Operation: Load Release History

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Locate release history file](#step-1-locate-release-history-file)
  - [Step 2: Check file exists](#step-2-check-file-exists)
  - [Step 3: Load file content](#step-3-load-file-content)
  - [Step 4: Parse release entries](#step-4-parse-release-entries)
  - [Step 5: Get latest release](#step-5-get-latest-release)
  - [Step 6: Check for rollbacks](#step-6-check-for-rollbacks)
  - [Step 7: Verify against GitHub releases](#step-7-verify-against-github-releases)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Release History Format](#release-history-format)
- [Releases](#releases)
- [Rollback History](#rollback-history)
- [Notes](#notes)
- [Version Extraction Patterns](#version-extraction-patterns)
- [Error Handling](#error-handling)
  - [File not found](#file-not-found)
  - [Out of sync with GitHub](#out-of-sync-with-github)
  - [Malformed entries](#malformed-entries)
- [Initialize from Git Tags](#initialize-from-git-tags)
- [Verification](#verification)

## Purpose

Load the release history document to understand past releases, version progression, and any rollback events for informed release decision-making.

## When to Use

- Before creating a new release
- When determining next version number
- When investigating rollback history
- When auditing release practices

## Prerequisites

1. `$CLAUDE_PROJECT_DIR` environment variable set
2. Read access to handoff directory
3. For verification: GitHub CLI for comparing with actual releases

## Procedure

### Step 1: Locate release history file

```bash
HANDOFF_DIR="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"
RELEASE_HISTORY="$HANDOFF_DIR/release-history.md"
```

### Step 2: Check file exists

```bash
if [ ! -f "$RELEASE_HISTORY" ]; then
  echo "No release history found"
  # Optionally initialize from git tags
  exit 0
fi
```

### Step 3: Load file content

```bash
HISTORY_CONTENT=$(cat "$RELEASE_HISTORY")
```

### Step 4: Parse release entries

```bash
# Extract release table (assuming markdown table format)
# | Version | Date | Type | Notes |
RELEASES=$(echo "$HISTORY_CONTENT" | grep -E '^\|[0-9v]' | while read line; do
  VERSION=$(echo "$line" | cut -d'|' -f2 | tr -d ' ')
  DATE=$(echo "$line" | cut -d'|' -f3 | tr -d ' ')
  TYPE=$(echo "$line" | cut -d'|' -f4 | tr -d ' ')
  echo "$VERSION,$DATE,$TYPE"
done)
```

### Step 5: Get latest release

```bash
LATEST_VERSION=$(echo "$RELEASES" | tail -1 | cut -d',' -f1)
LATEST_DATE=$(echo "$RELEASES" | tail -1 | cut -d',' -f2)

echo "Latest release: $LATEST_VERSION on $LATEST_DATE"
```

### Step 6: Check for rollbacks

```bash
# Look for rollback entries
ROLLBACKS=$(echo "$HISTORY_CONTENT" | grep -i "rollback\|reverted" | wc -l)
echo "Rollback events: $ROLLBACKS"
```

### Step 7: Verify against GitHub releases

```bash
# Compare with actual GitHub releases
GH_LATEST=$(gh release list --limit 1 --json tagName --jq '.[0].tagName')

if [ "$GH_LATEST" != "$LATEST_VERSION" ]; then
  echo "WARNING: History may be out of sync"
  echo "  History: $LATEST_VERSION"
  echo "  GitHub: $GH_LATEST"
fi
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| verify_with_github | boolean | no | Whether to verify against GitHub releases |
| include_rollbacks | boolean | no | Whether to include rollback analysis |

## Output

| Field | Type | Description |
|-------|------|-------------|
| found | boolean | Whether release history was found |
| latest_version | string | Most recent release version |
| latest_date | string | Date of most recent release |
| total_releases | number | Total number of releases tracked |
| rollback_count | number | Number of rollback events |
| releases | object[] | Array of release entries |
| synced_with_github | boolean | Whether history matches GitHub |

## Example Output

```json
{
  "found": true,
  "latest_version": "1.2.3",
  "latest_date": "2025-02-01",
  "total_releases": 15,
  "rollback_count": 1,
  "releases": [
    {
      "version": "1.2.3",
      "date": "2025-02-01",
      "type": "patch",
      "notes": "Bug fixes"
    },
    {
      "version": "1.2.2",
      "date": "2025-01-28",
      "type": "patch",
      "notes": "Security fix"
    }
  ],
  "synced_with_github": true
}
```

## Release History Format

```markdown
# Release History

**Repository**: owner/repo
**Last Updated**: 2025-02-05T10:00:00Z

## Releases

| Version | Date | Type | Deployed | Notes |
|---------|------|------|----------|-------|
| 1.2.3 | 2025-02-01 | patch | production | Bug fixes for auth |
| 1.2.2 | 2025-01-28 | patch | production | Security fix |
| 1.2.1 | 2025-01-25 | patch | production | Hotfix for API |
| 1.2.0 | 2025-01-20 | minor | production | New feature: SSO |
| 1.1.0 | 2025-01-10 | minor | production | Dashboard updates |
| 1.0.0 | 2025-01-01 | major | production | Initial release |

## Rollback History

| Date | From | To | Reason | Duration |
|------|------|-----|--------|----------|
| 2025-01-26 | 1.2.2 | 1.2.1 | API regression | 2 hours |

## Notes

- v1.2.0 required database migration
- v1.0.0 baseline for API versioning
```

## Version Extraction Patterns

```bash
# Extract version from different formats
# v1.2.3, 1.2.3, v1.2.3-beta
VERSION=$(echo "$TAG" | grep -oP '[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+\.[0-9]+)?')
```

## Error Handling

### File not found

**Cause**: No release history file exists.

**Solution**: Initialize from git tags or GitHub releases.

### Out of sync with GitHub

**Cause**: History file doesn't match actual releases.

**Solution**: Warn user, recommend running release history update.

### Malformed entries

**Cause**: Table format is corrupted.

**Solution**: Fall back to GitHub releases as source of truth.

## Initialize from Git Tags

If no history file exists, initialize from git tags:

```bash
#!/bin/bash
# Initialize release history from git tags

echo "# Release History" > "$RELEASE_HISTORY"
echo "" >> "$RELEASE_HISTORY"
echo "| Version | Date | Type | Notes |" >> "$RELEASE_HISTORY"
echo "|---------|------|------|-------|" >> "$RELEASE_HISTORY"

git tag -l 'v*' --sort=-version:refname | while read tag; do
  DATE=$(git log -1 --format=%ai "$tag" | cut -d' ' -f1)
  echo "| $tag | $DATE | - | - |" >> "$RELEASE_HISTORY"
done
```

## Verification

After loading:

```bash
# Verify release history is usable
if [ "$FOUND" = "true" ]; then
  echo "Release history loaded"
  echo "Latest: $LATEST_VERSION"
  echo "Total releases: $TOTAL_RELEASES"

  # Check sync status
  if [ "$SYNCED_WITH_GITHUB" = "false" ]; then
    echo "WARNING: History out of sync - recommend update"
  fi
else
  echo "No release history - will initialize from git tags"
fi
```
