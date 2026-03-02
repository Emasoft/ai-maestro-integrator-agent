---
name: op-validate-changelog-gate
description: "Validate that CHANGELOG.md has an entry for a given version before allowing release"
procedure: support-skill
workflow-instruction: support
---

# Operation: Validate Changelog Gate

## Contents

- 1. When to enforce changelog validation as a release gate
- 2. How to extract a version section from CHANGELOG.md using AWK
  - 2.1. AWK command for Keep a Changelog format
  - 2.2. AWK command for git-cliff format
- 3. How to block a release when changelog entry is missing
  - 3.1. Exit code conventions for release gates
  - 3.2. Error message with fix instructions
- 4. How to produce a job summary for CI/CD systems
  - 4.1. Success summary
  - 4.2. Failure summary with remediation steps
  - 4.3. Skip summary when no release is needed
- 5. How to integrate changelog validation into a release pipeline
- 6. Troubleshooting changelog validation failures

## Purpose

Enforce a release gate that blocks releases when `CHANGELOG.md` does not contain an entry for the version being released. This ensures every release ships with documented changes, making release notes available to users and auditors.

A "release gate" is a mandatory check that must pass before a release can proceed. If the check fails, the release process stops with an actionable error message explaining how to fix the problem.

## When to Use

- Before creating a release tag in a CI/CD pipeline
- As part of a `prepare-release` workflow that runs on push to the main branch
- As a local pre-release validation step before pushing a version bump

## Prerequisites

1. A `CHANGELOG.md` file exists in the repository root
2. The changelog follows a structured format with version headers (e.g., `## 1.2.3` or `## [1.2.3]`)
3. The version number to validate is known (extracted from project metadata)

---

## 1. When to Enforce Changelog Validation as a Release Gate

Changelog validation should run after the version number has been determined but before the release tag is created. The typical position in a pipeline is:

```
Version detected --> Changelog validated --> Tag created --> Release published
```

If changelog validation fails, no tag is created, and no release is published. This prevents "empty" releases that have no documented changes.

## 2. How to Extract a Version Section from CHANGELOG.md Using AWK

AWK is a text processing tool available on all Unix-like systems (Linux, macOS). It reads input line by line and applies pattern-action rules. AWK is used here because it can search for a specific markdown header and capture all lines until the next header.

### 2.1. AWK Command for Keep a Changelog Format

The "Keep a Changelog" format uses headers like `## [1.2.3] - 2025-02-05` or `## 1.2.3 - Release Title`. Sections are separated by the next `## ` header or a horizontal rule (`---`).

```bash
VERSION="1.2.3"
CHANGELOG_FILE="CHANGELOG.md"

CHANGELOG_CONTENT=$(awk -v ver="$VERSION" '
  BEGIN { found=0; content="" }
  /^## / {
    if (found) exit
    # Match "## 1.2.3" or "## [1.2.3]" or "## 1.2.3 - Title"
    if ($2 == ver || $2 == "["ver"]" || $2 ~ "^\\[?"ver"\\]?[[:space:]]*-") {
      found=1
      next
    }
  }
  /^---$/ { if (found) exit }
  found { content = content $0 "\n" }
  END {
    if (!found) {
      print "NOT_FOUND"
      exit 1
    }
    # Remove leading and trailing whitespace
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", content)
    print content
  }
' "$CHANGELOG_FILE")
```

**How this AWK command works, line by line:**

- `BEGIN { found=0; content="" }` -- Initialize: not yet found, content buffer empty
- `/^## /` -- When a line starts with `## ` (a level-2 markdown header):
  - `if (found) exit` -- If we already found our version, the next header means we are done
  - The `if` condition matches the version with or without brackets, with or without a trailing title
  - `found=1; next` -- Mark as found, skip the header line itself (we only want the body)
- `/^---$/` -- If we encounter a horizontal rule while capturing, stop
- `found { content = content $0 "\n" }` -- While found is true, append each line to the buffer
- `END` block -- After all lines are processed, if nothing was found, print `NOT_FOUND` and exit with code 1

### 2.2. AWK Command for git-cliff Format

git-cliff (a Rust-based changelog generator) produces headers like `## [1.2.3] - 2025-02-05` with grouped sections. The same AWK command from section 2.1 works for git-cliff output because it also uses `## ` headers for version separation.

## 3. How to Block a Release When Changelog Entry Is Missing

### 3.1. Exit Code Conventions for Release Gates

| Exit Code | Meaning | Action Taken |
|-----------|---------|--------------|
| 0 | Changelog entry found and valid | Release proceeds |
| 1 | Changelog entry missing or empty | Release is blocked |

### 3.2. Error Message with Fix Instructions

When the changelog entry is missing, the error message must tell the developer exactly what to do. A vague error like "validation failed" wastes time. A good error message includes the expected format and a copy-paste template.

```bash
if [ "$CHANGELOG_CONTENT" = "NOT_FOUND" ] || [ -z "$CHANGELOG_CONTENT" ]; then
  echo "ERROR: CHANGELOG VALIDATION FAILED"
  echo ""
  echo "  Version $VERSION was not found in CHANGELOG.md."
  echo ""
  echo "  Before releasing, add an entry to CHANGELOG.md with this format:"
  echo ""
  echo "    ## $VERSION - Your Release Title"
  echo ""
  echo "    ### Features"
  echo "    - Description of new feature"
  echo ""
  echo "    ### Bug Fixes"
  echo "    - Description of bug fix"
  echo ""
  echo "  Then commit and push the updated CHANGELOG.md."
  exit 1
fi

echo "Changelog entry found for version $VERSION"
echo ""
echo "--- Extracted Release Notes ---"
echo "$CHANGELOG_CONTENT"
echo "--- End Release Notes ---"
```

## 4. How to Produce a Job Summary for CI/CD Systems

A "job summary" is a formatted report visible in the CI/CD web interface (for example, GitHub Actions uses the special file `$GITHUB_STEP_SUMMARY`). Job summaries provide at-a-glance results without digging into logs.

### 4.1. Success Summary

```bash
# Write success summary (GitHub Actions example)
echo "## Release Triggered" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY
echo "**Version:** v$VERSION" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY
echo "Changelog validated and extracted from CHANGELOG.md." >> $GITHUB_STEP_SUMMARY
```

### 4.2. Failure Summary with Remediation Steps

```bash
# Write failure summary with how-to-fix steps
echo "## Release Blocked: Missing Changelog" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY
echo "Version **$VERSION** was not found in CHANGELOG.md." >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY
echo "### How to fix:" >> $GITHUB_STEP_SUMMARY
echo "1. Update CHANGELOG.md with release notes for version $VERSION" >> $GITHUB_STEP_SUMMARY
echo "2. Commit and push the changes" >> $GITHUB_STEP_SUMMARY
echo "3. The release will automatically retry" >> $GITHUB_STEP_SUMMARY
```

### 4.3. Skip Summary When No Release Is Needed

```bash
echo "## No Release Needed" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY
echo "Package version is not newer than the latest tag." >> $GITHUB_STEP_SUMMARY
echo "To trigger a release, bump the version first." >> $GITHUB_STEP_SUMMARY
```

## 5. How to Integrate Changelog Validation into a Release Pipeline

The validation step should sit between version detection and tag creation. The following pseudocode shows the position:

```
Step 1: Detect version from project metadata
Step 2: Compare version against latest git tag
Step 3: If version is newer, run changelog validation   <-- THIS STEP
Step 4: If changelog valid, create annotated git tag
Step 5: Tag push triggers downstream release workflow
```

Changelog validation is handled by the CPV plugin validator. Run it from the plugin root:

```bash
uv run --with pyyaml python scripts/validate_plugin.py . --verbose
```

For standalone changelog extraction in a CI/CD pipeline, use the AWK command from section 2 above. Exit code 0 means the changelog is valid. Exit code 1 means the changelog entry is missing.

## 6. Troubleshooting Changelog Validation Failures

### Changelog file not found

**Cause**: No `CHANGELOG.md` exists in the repository root.

**Solution**: Create `CHANGELOG.md` with at least one version entry. Use the format `## X.Y.Z - Title` for headers.

### Version found but content is empty

**Cause**: The version header exists but there are no lines between it and the next header.

**Solution**: Add at least one line of content (a feature description, a bug fix note, etc.) under the version header.

### Version not matched despite being present

**Cause**: The version header format does not match the expected pattern. For example, `## v1.2.3` (with the `v` prefix) will not match if the validator expects `## 1.2.3` (without prefix).

**Solution**: Ensure the header uses the bare version number: `## 1.2.3` or `## [1.2.3]`, not `## v1.2.3`.

### AWK not available on system

**Cause**: Minimal container images may not include AWK.

**Solution**: Use the CPV plugin validator (`uv run --with pyyaml python scripts/validate_plugin.py . --verbose`) or install `gawk` or `mawk` in your container.
