---
name: quality-gate-changelog
description: "Verify changelog is updated for version bumps before approving a PR through pre-merge gate."
---

# Changelog Verification for Quality Gates

## Table of Contents

- [1. When to Require Changelog Verification as a Quality Gate](#1-when-to-require-changelog-verification-as-a-quality-gate)
  - [1.1 PRs that trigger changelog verification](#11-prs-that-trigger-changelog-verification)
  - [1.2 PRs that are exempt from changelog verification](#12-prs-that-are-exempt-from-changelog-verification)
- [2. How to Check If CHANGELOG.md Has an Entry for the Current Version](#2-how-to-check-if-changelogmd-has-an-entry-for-the-current-version)
  - [2.1 Extracting the version from project configuration files](#21-extracting-the-version-from-project-configuration-files)
  - [2.2 Searching CHANGELOG.md for a matching version header](#22-searching-changelogmd-for-a-matching-version-header)
- [3. What Constitutes a Valid Changelog Entry](#3-what-constitutes-a-valid-changelog-entry)
  - [3.1 Required section header format](#31-required-section-header-format)
  - [3.2 Required change categories](#32-required-change-categories)
  - [3.3 Breaking change documentation](#33-breaking-change-documentation)
- [4. What to Do When Changelog Is Missing for a Version Bump](#4-what-to-do-when-changelog-is-missing-for-a-version-bump)
- [5. How to Enforce Changelog Updates in PR Review](#5-how-to-enforce-changelog-updates-in-pr-review)
  - [5.1 Reviewer checklist for changelog completeness](#51-reviewer-checklist-for-changelog-completeness)
  - [5.2 Automated enforcement reference](#52-automated-enforcement-reference)
- [6. Verification Procedure: Step-by-Step](#6-verification-procedure-step-by-step)
- [7. Integration with the Quality Gate Pipeline](#7-integration-with-the-quality-gate-pipeline)
- [8. Troubleshooting](#8-troubleshooting)

---

## 1. When to Require Changelog Verification as a Quality Gate

### 1.1 PRs that trigger changelog verification

Changelog verification is required when any of these conditions is met:

1. **Version field is modified**: The PR changes the `version` field in any project configuration file: `pyproject.toml`, `package.json`, `Cargo.toml`, `build.gradle`, `*.csproj`, `setup.cfg`, `Chart.yaml`, or any file the repository designates as the version source of truth.
2. **PR targets a release branch**: The base branch matches `release/*`, `release-*`, or another branch documented as a release branch.
3. **PR carries a release label**: Labels such as `release`, `version-bump`, `semver-major`, `semver-minor`, or `semver-patch`.

### 1.2 PRs that are exempt from changelog verification

- Internal refactoring or CI configuration changes that do not bump the version.
- Dependency bumps that do not change the project's own version (unless a major dependency upgrade).
- Documentation-only changes with no source code or version modifications.
- Draft PRs (verification is deferred until marked ready for review).

---

## 2. How to Check If CHANGELOG.md Has an Entry for the Current Version

### 2.1 Extracting the version from project configuration files

Extract the new version from the relevant configuration file. Examples:

```bash
# Python (pyproject.toml)
grep -m 1 'version' pyproject.toml | sed 's/.*"\(.*\)".*/\1/'

# JavaScript/TypeScript (package.json)
jq -r '.version' package.json

# Rust (Cargo.toml)
grep -m 1 'version' Cargo.toml | sed 's/.*"\(.*\)".*/\1/'

# .NET (*.csproj)
grep '<Version>' *.csproj | sed 's/.*<Version>\(.*\)<\/Version>.*/\1/'
```

Store the result: `VERSION="1.2.0"`

### 2.2 Searching CHANGELOG.md for a matching version header

```bash
# Search for a header line containing the version
grep -n "## \[${VERSION}\]" CHANGELOG.md
```

If no match is found, the entry is missing -- proceed to section 4. If found, verify the section is not empty by counting list items between this header and the next `##` header:

```bash
HEADER_LINE=$(grep -n "## \[${VERSION}\]" CHANGELOG.md | head -1 | cut -d: -f1)
NEXT_HEADER=$(awk "NR > $HEADER_LINE && /^## /{print NR; exit}" CHANGELOG.md)
[ -z "$NEXT_HEADER" ] && NEXT_HEADER=$(wc -l < CHANGELOG.md)
ENTRY_COUNT=$(awk "NR > $HEADER_LINE && NR < $NEXT_HEADER && /^[[:space:]]*[-*] /" CHANGELOG.md | wc -l)
```

If `ENTRY_COUNT` is 0, treat it the same as a missing section and block the gate.

---

## 3. What Constitutes a Valid Changelog Entry

### 3.1 Required section header format

Headers must follow Keep a Changelog format: `## [X.Y.Z] - YYYY-MM-DD`

Valid examples:
```
## [1.2.0] - 2026-02-07
## [0.5.1] - 2026-01-15
```

Invalid examples:
```
## 1.2.0                    (missing brackets and date)
## [1.2.0]                  (missing date)
## [1.2.0] - TBD            (date not in ISO 8601 format)
```

An `[Unreleased]` header must be replaced with the actual version and date before merging.

### 3.2 Required change categories

Entries must be organized under Keep a Changelog category headings:

| Category | When to use |
|----------|-------------|
| `### Added` | New features, capabilities, files |
| `### Changed` | Modifications to existing functionality |
| `### Deprecated` | Features marked for future removal |
| `### Removed` | Deleted features or files |
| `### Fixed` | Bug fixes |
| `### Security` | Vulnerability patches, security improvements |

At minimum, one category with at least one list item must be present. Example:

```markdown
## [1.2.0] - 2026-02-07

### Added
- Support for YAML configuration files in addition to JSON

### Fixed
- Resolved race condition in concurrent file processing
```

### 3.3 Breaking change documentation

For major version bumps (for example, 1.x.x to 2.0.0), breaking changes must be explicitly documented. Use either a dedicated `### BREAKING CHANGES` subsection or inline `**BREAKING**:` markers within the relevant categories:

```markdown
## [2.0.0] - 2026-02-07

### Changed
- **BREAKING**: Configuration format changed from INI to TOML
- **BREAKING**: Minimum supported Python version raised from 3.8 to 3.10
```

A major version bump with no documented breaking changes blocks the gate.

---

## 4. What to Do When Changelog Is Missing for a Version Bump

Block the pre-merge gate and apply the `eia/changelog-missing` label:

```bash
gh pr edit $PR_NUMBER --add-label "eia/changelog-missing"
gh pr edit $PR_NUMBER --remove-label "eia/changelog-passed" 2>/dev/null || true
```

Post instructions to the PR author:

```bash
gh pr comment $PR_NUMBER --body "Pre-merge gate blocked: CHANGELOG.md does not contain an entry for version ${VERSION}.

Please add a section to CHANGELOG.md:

\`\`\`markdown
## [${VERSION}] - $(date +%Y-%m-%d)

### Added/Changed/Fixed
- Description of your changes
\`\`\`

Use the appropriate Keep a Changelog categories.
The gate will re-evaluate when you push the updated CHANGELOG.md."
```

After the author pushes the update, re-run verification. If it passes, swap labels:

```bash
gh pr edit $PR_NUMBER --remove-label "eia/changelog-missing"
gh pr edit $PR_NUMBER --add-label "eia/changelog-passed"
```

---

## 5. How to Enforce Changelog Updates in PR Review

### 5.1 Reviewer checklist for changelog completeness

- [ ] CHANGELOG.md has a section header matching the new version (`## [X.Y.Z] - YYYY-MM-DD`)
- [ ] The date is today or the intended release date
- [ ] At least one category heading and one list item are present
- [ ] Entries accurately describe the changes in the PR
- [ ] Breaking changes are documented if this is a major version bump
- [ ] The `[Unreleased]` section (if any) was moved to the new version section

### 5.2 Automated enforcement reference

For automated CI enforcement, see the `amia-release-management` skill's `references/op-validate-changelog-gate.md`, which describes the changelog validation procedure. For plugin-level validation (including changelog checks), use the CPV plugin validator: `uv run --with pyyaml python scripts/validate_plugin.py . --verbose`.

---

## 6. Verification Procedure: Step-by-Step

1. **Determine applicability** (section 1.1): Does the PR modify a version field, target a release branch, or carry a release label? If none, skip changelog verification.
2. **Extract version** (section 2.1): Read the new version from the project configuration file.
3. **Search CHANGELOG.md** (section 2.2): Look for `## [VERSION] - YYYY-MM-DD`. If absent, block (section 4).
4. **Verify non-empty** (section 2.2): Count list items in the section. If zero, block (section 4).
5. **Validate format** (section 3): Check header format, category headings, and breaking change docs.
6. **Cross-reference with PR description**: Compare changelog entries with the PR body (non-blocking warning if discrepancies found).
7. **Apply result label**: `eia/changelog-passed` if all checks pass, `eia/changelog-missing` if any fail.

---

## 7. Integration with the Quality Gate Pipeline

Changelog verification is a sub-step of the pre-merge gate, evaluated alongside CI check verification (see [quality-gate-ci-checks.md](quality-gate-ci-checks.md)) and the other pre-merge checks in [pre-merge-gate.md](pre-merge-gate.md).

**Position in the pre-merge gate sequence**:
1. Verify CI status (see [quality-gate-ci-checks.md](quality-gate-ci-checks.md))
2. Verify changelog (this document)
3. Verify no merge conflicts (see [pre-merge-gate.md](pre-merge-gate.md), section 2)
4. Verify valid approval (see [pre-merge-gate.md](pre-merge-gate.md), section 3)
5. Verify branch is up-to-date (see [pre-merge-gate.md](pre-merge-gate.md), section 4)

**Labels**: `eia/changelog-missing` (blocks gate), `eia/changelog-passed` (cleared).

---

## 8. Troubleshooting

### CHANGELOG.md does not exist

Check for alternative filenames (`CHANGES.md`, `HISTORY.md`, `NEWS.md`) or alternative locations (`docs/CHANGELOG.md`). If no changelog exists, block the gate and comment requesting its creation following the Keep a Changelog format.

### Version has a `v` prefix mismatch

The changelog may use `## [v1.2.0]` while the config file contains `1.2.0`. Search with an optional prefix: `grep -n "## \[v\?${VERSION}\]" CHANGELOG.md`. Accept the repository's convention but recommend standardization.

### Duplicate entries for the same version

Multiple headers with the same version number indicate a formatting error. Block the gate and comment requesting consolidation into a single section.

### Future date in changelog header

A date in the future is acceptable for scheduled releases. Leave a non-blocking warning noting the future date.

### Version mismatch across configuration files

If the PR modifies `version` in multiple files with different values (for example, `pyproject.toml` says `1.2.0` and `package.json` says `1.3.0`), block the gate and comment requesting version consistency before changelog verification can proceed.
