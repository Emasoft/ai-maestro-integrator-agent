---
name: Semantic Versioning
description: Complete guide to semantic versioning principles, rules, and best practices for release management
version: 1.0.0
---

# Semantic Versioning

## Table of Contents

- [Overview](#overview)
- [Version Format](#version-format)
  - [Basic Structure](#basic-structure)
  - [When to Increment Each Number](#when-to-increment-each-number)
- [Pre-Release Versions](#pre-release-versions)
  - [Format](#format)
  - [Pre-Release Identifiers](#pre-release-identifiers)
- [Build Metadata](#build-metadata)
  - [Format](#format-1)
  - [When to Use Build Metadata](#when-to-use-build-metadata)
- [Version Precedence](#version-precedence)
  - [Ordering Rules](#ordering-rules)
  - [Examples of Precedence](#examples-of-precedence)
  - [Pre-Release Ordering](#pre-release-ordering)
- [Initial Development](#initial-development)
  - [Version 0.y.z](#version-0yz)
  - [Transitioning to 1.0.0](#transitioning-to-100)
- [Version Ranges and Dependencies](#version-ranges-and-dependencies)
  - [Specifying Dependencies](#specifying-dependencies)
  - [Dependency Range Best Practices](#dependency-range-best-practices)
- [Versioning Different Types of Projects](#versioning-different-types-of-projects)
  - [Libraries and Frameworks](#libraries-and-frameworks)
  - [Applications and Services](#applications-and-services)
  - [APIs (REST, GraphQL, etc.)](#apis-rest-graphql-etc)
  - [Database Schemas](#database-schemas)
- [Changelog Practices](#changelog-practices)
  - [Format](#format-2)
  - [Categories](#categories)
- [Deprecation Strategy](#deprecation-strategy)
  - [Process](#process)
  - [Example Timeline](#example-timeline)
  - [Deprecation Notice Format](#deprecation-notice-format)
- [Version Branches and Git Strategy](#version-branches-and-git-strategy)
  - [Branching Model](#branching-model)
  - [Branch Purposes](#branch-purposes)
  - [Tagging Strategy](#tagging-strategy)
- [Automated Versioning](#automated-versioning)
  - [Version Bumping Tools](#version-bumping-tools)
  - [CI/CD Integration](#cicd-integration)
- [Conventional Commits and SemVer](#conventional-commits-and-semver)
  - [Commit Message Format](#commit-message-format)
  - [Type to Version Mapping](#type-to-version-mapping)
  - [Examples](#examples)
- [Version Communication](#version-communication)
  - [Release Notes Template](#release-notes-template)
  - [User Communication Strategy](#user-communication-strategy)
- [Common Mistakes and How to Avoid Them](#common-mistakes-and-how-to-avoid-them)
  - [Mistake 1: Incrementing Wrong Number](#mistake-1-incrementing-wrong-number)
  - [Mistake 2: Breaking Changes in MINOR/PATCH](#mistake-2-breaking-changes-in-minorpatch)
  - [Mistake 3: Not Documenting Changes](#mistake-3-not-documenting-changes)
  - [Mistake 4: Skipping Versions](#mistake-4-skipping-versions)
  - [Mistake 5: Incorrect Pre-Release Naming](#mistake-5-incorrect-pre-release-naming)
- [SemVer Tools and Resources](#semver-tools-and-resources)
  - [Version Checking Tools](#version-checking-tools)
  - [Validation](#validation)
- [Best Practices Summary](#best-practices-summary)

## Overview

Semantic Versioning (SemVer) is a versioning scheme that conveys meaning about the underlying changes in a release. It provides a universal convention for version numbers that allows developers and users to understand the nature and impact of changes at a glance.

## Version Format

### Basic Structure

**Format**: `MAJOR.MINOR.PATCH`

**Example**: `2.4.7`
- **MAJOR**: 2
- **MINOR**: 4
- **PATCH**: 7

### When to Increment Each Number

#### MAJOR Version
**Increment when**: Making incompatible API changes or breaking changes

**Examples**:
- Removing or renaming public API methods
- Changing function signatures (parameters, return types)
- Removing configuration options
- Changing data formats in backward-incompatible ways
- Dropping support for older platforms or dependencies
- Restructuring project architecture fundamentally

**Impact**: Users must update their code to work with the new version

**Example Transition**: 1.9.5 → 2.0.0

#### MINOR Version
**Increment when**: Adding functionality in a backward-compatible manner

**Examples**:
- Adding new API methods or functions
- Adding new features to existing commands
- Adding optional parameters to existing functions
- Deprecating functionality (but not removing it)
- Performance improvements
- Adding new configuration options

**Impact**: Users can upgrade without code changes

**Example Transition**: 2.3.5 → 2.4.0

#### PATCH Version
**Increment when**: Making backward-compatible bug fixes

**Examples**:
- Fixing incorrect behavior or bugs
- Correcting documentation errors
- Fixing security vulnerabilities (non-breaking)
- Performance fixes that don't change functionality
- Internal refactoring with no external impact

**Impact**: Users can upgrade immediately with minimal risk

**Example Transition**: 2.4.6 → 2.4.7

## Pre-Release Versions

### Format

**Structure**: `MAJOR.MINOR.PATCH-PRERELEASE`

**Examples**:
- `1.0.0-alpha.1`
- `1.0.0-beta.2`
- `1.0.0-rc.1`
- `2.0.0-dev.20240204`

### Pre-Release Identifiers

#### alpha
**Purpose**: Early development stage, unstable, features incomplete

**Example**: `1.0.0-alpha.1`

**Characteristics**:
- Features under active development
- API may change frequently
- Known bugs expected
- Not feature-complete
- Internal testing only

**Progression**: alpha.1 → alpha.2 → alpha.3

#### beta
**Purpose**: Feature-complete but may contain bugs

**Example**: `1.0.0-beta.1`

**Characteristics**:
- All planned features implemented
- API stabilizing
- Suitable for testing by early adopters
- Bug fixes ongoing
- Performance optimization in progress

**Progression**: beta.1 → beta.2 → beta.3

#### rc (Release Candidate)
**Purpose**: Potentially final version, pending validation

**Example**: `1.0.0-rc.1`

**Characteristics**:
- Feature-complete and tested
- API locked unless critical issues found
- Ready for production testing
- Only critical bug fixes allowed
- Documentation complete

**Progression**: rc.1 → rc.2 → 1.0.0 (release)

#### dev
**Purpose**: Development snapshot or nightly build

**Example**: `1.0.0-dev.20240204`

**Characteristics**:
- Continuous integration builds
- May be unstable
- For automated testing
- Date or commit hash as identifier

## Build Metadata

### Format

**Structure**: `MAJOR.MINOR.PATCH+BUILD_METADATA`

**Examples**:
- `1.0.0+20240204`
- `1.0.0+sha.5114f85`
- `1.0.0-beta.1+exp.sha.5114f85`

### When to Use Build Metadata

Build metadata should be used for:
- Build timestamps
- Commit hashes
- Build numbers from CI/CD
- Platform-specific builds

Build metadata does NOT affect version precedence.

**Example Comparison**:
- `1.0.0+build.1` equals `1.0.0+build.2` in precedence
- Both are the same version, just different builds

## Version Precedence

### Ordering Rules

Versions are compared from left to right:

1. **MAJOR** version differences take priority
2. If MAJOR is equal, compare **MINOR**
3. If MINOR is equal, compare **PATCH**
4. Pre-release versions have lower precedence than normal versions
5. When comparing pre-release identifiers, numeric identifiers are compared as integers

### Examples of Precedence

```
1.0.0-alpha.1 < 1.0.0-alpha.2 < 1.0.0-beta.1 < 1.0.0-rc.1 < 1.0.0
< 1.0.1 < 1.1.0 < 2.0.0
```

### Pre-Release Ordering

```
1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta
< 1.0.0-beta.2 < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0
```

## Initial Development

### Version 0.y.z

**Convention**: During initial development, use `0.y.z` versions

**Characteristics**:
- Major version 0 indicates "under development"
- Breaking changes can occur in any 0.y.z release
- No stability guarantees
- Suitable for projects not yet ready for production

**When to Use**:
- New projects before first stable release
- Experimental features
- Proof-of-concept implementations
- Prototypes

**Progression Example**:
```
0.1.0 → 0.2.0 → 0.3.0 → 0.9.0 → 1.0.0
```

### Transitioning to 1.0.0

**Release 1.0.0 when**:
- The software is being used in production
- API is stable and documented
- You're ready to commit to backward compatibility
- Breaking changes will trigger major version increments

## Version Ranges and Dependencies

### Specifying Dependencies

#### Exact Version
**Format**: `1.2.3`
**Matches**: Only version 1.2.3
**Use When**: Strict version control required

#### Tilde Range
**Format**: `~1.2.3`
**Matches**: >=1.2.3 <1.3.0 (same MAJOR and MINOR, any PATCH)
**Use When**: Allowing patch updates only

#### Caret Range
**Format**: `^1.2.3`
**Matches**: >=1.2.3 <2.0.0 (same MAJOR, any compatible MINOR/PATCH)
**Use When**: Allowing backward-compatible updates

#### Wildcard
**Format**: `1.2.*` or `1.x`
**Matches**: Any version in specified range
**Use When**: Maximum flexibility within range

#### Comparison Operators
**Formats**: `>1.2.3`, `>=1.2.3`, `<2.0.0`, `<=1.9.0`
**Use When**: Specific constraints needed

### Dependency Range Best Practices

**For Libraries**:
- Use caret (`^`) for maximum compatibility
- Example: `^1.2.0` allows 1.2.0 up to (but not including) 2.0.0

**For Applications**:
- Use exact versions or tilde (`~`) for predictability
- Example: `~1.2.3` allows patches but not minor updates

**For Development Dependencies**:
- More flexible ranges acceptable
- Example: `^1.0.0` for testing frameworks

## Versioning Different Types of Projects

### Libraries and Frameworks

**Requirements**:
- Strict adherence to SemVer
- Clear changelog documenting all changes
- Deprecation warnings before breaking changes
- Multiple versions maintained if possible

**Considerations**:
- Breaking changes are expensive for users
- Provide migration guides for major versions
- Consider feature flags for gradual transitions

### Applications and Services

**Requirements**:
- SemVer for API versioning
- Flexible versioning for internal changes
- Clear communication of changes to users

**Considerations**:
- Internal refactoring doesn't require version bumps
- UI changes may not follow strict SemVer
- Consider CalVer (Calendar Versioning) for user-facing apps

### APIs (REST, GraphQL, etc.)

**Requirements**:
- Version in URL or header: `/api/v1/`, `/api/v2/`
- Major version for breaking changes
- Maintain multiple versions simultaneously
- Clear deprecation timeline

**Considerations**:
- Multiple major versions in production
- Gradual migration periods for clients
- Sunset policies for old versions

### Database Schemas

**Versioning Strategy**:
- Migration scripts with version numbers
- Forward-compatible migrations when possible
- Rollback scripts for each migration

**Example**:
```
001_initial_schema.sql
002_add_user_email.sql
003_create_orders_table.sql
```

## Changelog Practices

### Format

Use [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

## [2.1.0] - 2024-02-04

### Added
- New export functionality for reports
- API endpoint for bulk operations

### Changed
- Improved performance of search queries
- Updated UI for better accessibility

### Deprecated
- `oldFunction()` - use `newFunction()` instead

### Removed
- Support for deprecated API v1

### Fixed
- Bug where dates displayed incorrectly in UTC
- Memory leak in background worker

### Security
- Patched SQL injection vulnerability in search
```

### Categories

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Now removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

## Deprecation Strategy

### Process

1. **Announcement**: Mark feature as deprecated in documentation
2. **Warning**: Add runtime warnings when deprecated feature used
3. **Migration Guide**: Provide clear path to replacement
4. **Grace Period**: Maintain deprecated feature for at least one minor version
5. **Removal**: Remove in next major version

### Example Timeline

```
v1.5.0: Feature fully supported
v1.6.0: Feature marked deprecated, warnings added
v1.7.0: Feature still available with warnings
v2.0.0: Feature removed
```

### Deprecation Notice Format

```python
import warnings

def old_function():
    warnings.warn(
        "old_function() is deprecated and will be removed in v2.0.0. "
        "Use new_function() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... implementation
```

## Version Branches and Git Strategy

### Branching Model

```
main (or master)
├── develop
├── release/1.x
├── release/2.x
└── hotfix/1.2.1
```

### Branch Purposes

**main**: Always contains the latest release
**develop**: Integration branch for next release
**release/X.x**: Maintenance branches for major versions
**hotfix/X.Y.Z**: Emergency fixes for specific versions

### Tagging Strategy

**Tag Format**: `vMAJOR.MINOR.PATCH`

**Examples**:
- `v1.0.0`
- `v1.1.0-rc.1`
- `v2.0.0-beta.1`

**Best Practices**:
- Tag every release
- Sign tags for security
- Include changelog in tag message

## Automated Versioning

### Version Bumping Tools

**For JavaScript/Node.js**:
```bash
npm version patch  # 1.0.0 -> 1.0.1
npm version minor  # 1.0.1 -> 1.1.0
npm version major  # 1.1.0 -> 2.0.0
```

**For Python**:
```bash
bumpversion patch  # Using bumpversion tool
bumpversion minor
bumpversion major
```

### CI/CD Integration

**Automated Version Detection**:
1. Analyze commit messages since last release
2. Determine version bump based on conventional commits
3. Update version files
4. Create git tag
5. Build and publish

**Example GitHub Actions**:
```yaml
- name: Determine version bump
  id: version
  uses: mathieudutour/github-tag-action@v6.1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    default_bump: patch
```

## Conventional Commits and SemVer

### Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type to Version Mapping

| Commit Type | Version Impact | Example |
|-------------|---------------|---------|
| `feat:` | MINOR | `feat: add user export functionality` |
| `fix:` | PATCH | `fix: correct date formatting bug` |
| `BREAKING CHANGE:` | MAJOR | `feat!: redesign API authentication` |
| `chore:`, `docs:` | None | `chore: update dependencies` |

### Examples

**Patch Release**:
```
fix: prevent SQL injection in search queries

Security vulnerability fixed by parameterizing all SQL queries.
```

**Minor Release**:
```
feat: add bulk delete operation

Users can now delete multiple items at once through the UI.
```

**Major Release**:
```
feat!: migrate to TypeScript and redesign API

BREAKING CHANGE: All API endpoints now require authentication tokens.
The old API key approach is no longer supported.

Migration guide available at docs/migration/v2.md
```

## Version Communication

### Release Notes Template

```markdown
# Version X.Y.Z

Release Date: YYYY-MM-DD

## Highlights
- Brief description of most important changes

## Breaking Changes (for MAJOR versions)
- List of breaking changes
- Migration instructions

## New Features (for MINOR versions)
- Feature 1 description
- Feature 2 description

## Bug Fixes
- Bug fix 1
- Bug fix 2

## Upgrade Instructions
Step-by-step guide for upgrading from previous version

## Known Issues
- Any known issues or limitations

## Contributors
Thank contributors to this release
```

### User Communication Strategy

**For MAJOR versions**:
- Blog post announcement
- Migration guide
- Webinar or video walkthrough
- Advance notice (30-90 days)

**For MINOR versions**:
- Release notes
- Email to users
- Social media announcement

**For PATCH versions**:
- Changelog update
- Notification in app (if applicable)
- Security advisory (if security fix)

## Common Mistakes and How to Avoid Them

### Mistake 1: Incrementing Wrong Number
**Wrong**: Bumping PATCH for a new feature
**Right**: Bump MINOR for new features, even small ones

### Mistake 2: Breaking Changes in MINOR/PATCH
**Wrong**: Removing a parameter in version 1.2.0
**Right**: Deprecate in 1.2.0, remove in 2.0.0

### Mistake 3: Not Documenting Changes
**Wrong**: "Bug fixes and improvements"
**Right**: Specific list of what changed and why

### Mistake 4: Skipping Versions
**Wrong**: 1.2.0 → 1.4.0 (skipping 1.3.0)
**Right**: Sequential versioning: 1.2.0 → 1.3.0 → 1.4.0

### Mistake 5: Incorrect Pre-Release Naming
**Wrong**: `1.0.0-beta` (no numeric identifier)
**Right**: `1.0.0-beta.1` (with numeric identifier for iteration)

## SemVer Tools and Resources

### Version Checking Tools
- `semver.org` - Official specification
- `semver` npm package - Version parsing and comparison
- `python-semantic-version` - Python implementation

### Validation
- `semantic-release` - Automated versioning and publishing
- `standard-version` - Automated CHANGELOG generation
- `commitizen` - Conventional commit message tool

## Best Practices Summary

1. **Be Consistent**: Apply SemVer rules uniformly across all releases
2. **Communicate Clearly**: Document changes thoroughly
3. **Plan Breaking Changes**: Group breaking changes into major releases
4. **Test Thoroughly**: More extensive testing for higher version changes
5. **Automate**: Use tools to enforce versioning standards
6. **Document**: Maintain detailed CHANGELOG
7. **Deprecate Gracefully**: Provide migration paths before removal
8. **Tag Releases**: Use git tags for every release
9. **Consider Users**: Think about upgrade impact on users
10. **Be Predictable**: Users should know what to expect from version numbers
