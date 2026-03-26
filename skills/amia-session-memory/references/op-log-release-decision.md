# Operation: Log Release Decision

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Locate release history file](#step-1-locate-release-history-file)
  - [Step 2: Initialize if not exists](#step-2-initialize-if-not-exists)
- [Releases](#releases)
- [Rollback History](#rollback-history)
- [Notes](#notes)
  - [Step 3: Prepare release entry](#step-3-prepare-release-entry)
  - [Step 4: Add release entry](#step-4-add-release-entry)
  - [Step 5: Update timestamp](#step-5-update-timestamp)
  - [Step 6: Log rollback (if applicable)](#step-6-log-rollback-if-applicable)
  - [Step 7: Verify entry was added](#step-7-verify-entry-was-added)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Release History Format](#release-history-format)
- [Releases](#releases)
- [Rollback History](#rollback-history)
- [Notes](#notes)
- [Error Handling](#error-handling)
  - [File not writable](#file-not-writable)
  - [Duplicate entry](#duplicate-entry)
  - [Malformed table](#malformed-table)
- [Complete Logging Script](#complete-logging-script)
- [Releases](#releases)
- [Rollback History](#rollback-history)
- [Verification](#verification)

## Purpose

Record a release decision (approval, deployment, rollback) in the release history document for future reference and audit trail.

## When to Use

- After approving a release
- After deploying to production/staging
- After a rollback event
- When documenting release decisions

## Prerequisites

1. `$CLAUDE_PROJECT_DIR` environment variable set
2. Write access to handoff directory
3. Release details available (version, target, rationale)

## Procedure

### Step 1: Locate release history file

```bash
HANDOFF_DIR="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"
RELEASE_HISTORY="$HANDOFF_DIR/release-history.md"
```

### Step 2: Initialize if not exists

```bash
if [ ! -f "$RELEASE_HISTORY" ]; then
  cat > "$RELEASE_HISTORY" << 'EOF'
# Release History

**Repository**: (to be filled)
**Last Updated**: (auto-updated)

## Releases

| Version | Date | Type | Deployed | Notes |
|---------|------|------|----------|-------|

## Rollback History

| Date | From | To | Reason | Duration |
|------|------|-----|--------|----------|

## Notes

(Release notes and important decisions)
EOF
  echo "Initialized release history"
fi
```

### Step 3: Prepare release entry

```bash
VERSION="1.2.4"
DATE=$(date +%Y-%m-%d)
TYPE="patch"  # patch, minor, major
DEPLOYED="production"  # staging, production
NOTES="Bug fixes for authentication flow"
```

### Step 4: Add release entry

```bash
# Find the releases table and add entry
TEMP_FILE=$(mktemp)

awk -v ver="$VERSION" -v date="$DATE" -v type="$TYPE" -v dep="$DEPLOYED" -v notes="$NOTES" '
  /^\| Version \| Date \| Type \| Deployed \| Notes \|$/ {
    print
    getline  # Print the separator line
    print
    printf "| %s | %s | %s | %s | %s |\n", ver, date, type, dep, notes
    next
  }
  { print }
' "$RELEASE_HISTORY" > "$TEMP_FILE"

mv "$TEMP_FILE" "$RELEASE_HISTORY"
```

### Step 5: Update timestamp

```bash
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
sed -i '' "s/\*\*Last Updated\*\*:.*/\*\*Last Updated\*\*: $TIMESTAMP/" "$RELEASE_HISTORY"
```

### Step 6: Log rollback (if applicable)

```bash
# For rollback events
if [ "$IS_ROLLBACK" = "true" ]; then
  ROLLBACK_FROM="1.2.4"
  ROLLBACK_TO="1.2.3"
  ROLLBACK_REASON="Critical regression in API"
  ROLLBACK_DURATION="2 hours"

  # Add to rollback table
  awk -v date="$DATE" -v from="$ROLLBACK_FROM" -v to="$ROLLBACK_TO" -v reason="$ROLLBACK_REASON" -v dur="$ROLLBACK_DURATION" '
    /^\| Date \| From \| To \| Reason \| Duration \|$/ {
      print
      getline  # separator
      print
      printf "| %s | %s | %s | %s | %s |\n", date, from, to, reason, dur
      next
    }
    { print }
  ' "$RELEASE_HISTORY" > "$TEMP_FILE"

  mv "$TEMP_FILE" "$RELEASE_HISTORY"
fi
```

### Step 7: Verify entry was added

```bash
if grep -q "| $VERSION |" "$RELEASE_HISTORY"; then
  echo "Release entry added successfully"
else
  echo "ERROR: Failed to add release entry"
  exit 1
fi
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| version | string | yes | Release version (e.g., "1.2.4") |
| type | string | yes | Release type: patch, minor, major |
| deployed | string | yes | Deployment target: staging, production |
| notes | string | no | Brief release notes |
| is_rollback | boolean | no | Whether this is a rollback |
| rollback_from | string | cond | Version rolled back from |
| rollback_to | string | cond | Version rolled back to |
| rollback_reason | string | cond | Reason for rollback |

## Output

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether entry was logged |
| version | string | Version that was logged |
| entry_type | string | release or rollback |
| history_path | string | Path to release history file |

## Example Output

```json
{
  "success": true,
  "version": "1.2.4",
  "entry_type": "release",
  "history_path": "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/release-history.md"
}
```

## Release History Format

```markdown
# Release History

**Repository**: owner/repo
**Last Updated**: 2025-02-05T14:30:00Z

## Releases

| Version | Date | Type | Deployed | Notes |
|---------|------|------|----------|-------|
| 1.2.4 | 2025-02-05 | patch | production | Bug fixes for auth |
| 1.2.3 | 2025-02-01 | patch | production | Security fix |
| 1.2.2 | 2025-01-28 | patch | production | Hotfix |

## Rollback History

| Date | From | To | Reason | Duration |
|------|------|-----|--------|----------|
| 2025-01-26 | 1.2.2 | 1.2.1 | API regression | 2 hours |

## Notes

- v1.2.0: Introduced SSO feature
- v1.0.0: Baseline for API versioning
```

## Error Handling

### File not writable

**Cause**: Permission denied on release history file.

**Solution**: Check file permissions, verify CLAUDE_PROJECT_DIR.

### Duplicate entry

**Cause**: Version already exists in history.

**Solution**: Check if update is intended, or use different version.

### Malformed table

**Cause**: Table format is corrupted.

**Solution**: Manually fix table format or rebuild from git tags.

## Complete Logging Script

```bash
#!/bin/bash
# log_release_decision.sh

VERSION="$1"
TYPE="$2"      # patch, minor, major
DEPLOYED="$3"  # staging, production
NOTES="$4"

HANDOFF_DIR="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"
RELEASE_HISTORY="$HANDOFF_DIR/release-history.md"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Ensure directory exists
mkdir -p "$HANDOFF_DIR"

# Initialize if needed
if [ ! -f "$RELEASE_HISTORY" ]; then
  cat > "$RELEASE_HISTORY" << 'EOF'
# Release History

**Repository**:
**Last Updated**:

## Releases

| Version | Date | Type | Deployed | Notes |
|---------|------|------|----------|-------|

## Rollback History

| Date | From | To | Reason | Duration |
|------|------|-----|--------|----------|
EOF
fi

# Add entry
TEMP=$(mktemp)
awk -v ver="$VERSION" -v date="$DATE" -v type="$TYPE" -v dep="$DEPLOYED" -v notes="$NOTES" '
  /^\| Version \| Date \| Type \| Deployed \| Notes \|$/ {
    print; getline; print
    printf "| %s | %s | %s | %s | %s |\n", ver, date, type, dep, notes
    next
  }
  { print }
' "$RELEASE_HISTORY" > "$TEMP"
mv "$TEMP" "$RELEASE_HISTORY"

# Update timestamp
sed -i '' "s/\*\*Last Updated\*\*:.*/\*\*Last Updated\*\*: $TIMESTAMP/" "$RELEASE_HISTORY"

echo "Logged release $VERSION"
```

## Verification

After logging:

```bash
# Verify entry exists
grep "| $VERSION |" "$RELEASE_HISTORY"

# Show recent entries
grep -E "^\|" "$RELEASE_HISTORY" | head -5
```
