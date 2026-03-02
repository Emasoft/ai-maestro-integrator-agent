---
name: git-cliff-integration
description: "Configure and use git-cliff for automated changelog generation from conventional commits"
procedure: support-skill
workflow-instruction: support
---

# git-cliff Integration

## Contents

- 1. What git-cliff is and when to use it
- 2. How to install git-cliff
  - 2.1. Installing on developer machines
  - 2.2. Installing in CI/CD environments
- 3. How to configure git-cliff with cliff.toml
  - 3.1. Minimal cliff.toml configuration
  - 3.2. Commit group categories (Features, Bug Fixes, Refactoring, etc.)
  - 3.3. Commit parsers and regular expression patterns
  - 3.4. Template customization for changelog output format
  - 3.5. Filtering out unwanted commits
- 4. How to run git-cliff to generate a changelog
  - 4.1. Generating a full changelog
  - 4.2. Generating changelog for a specific version range
  - 4.3. Generating changelog for an unreleased version
  - 4.4. Prepending to an existing CHANGELOG.md
- 5. How to integrate git-cliff into CI/CD workflows
  - 5.1. GitHub Actions integration
  - 5.2. Using git-cliff output as release notes
- 6. Troubleshooting git-cliff issues

## Purpose

git-cliff is a Rust-based command-line tool that generates changelogs from git commit history. It parses commit messages that follow the Conventional Commits specification and groups them into categories (Features, Bug Fixes, Refactoring, etc.). The generated changelog follows a structured markdown format suitable for `CHANGELOG.md` files and GitHub release notes.

"Conventional Commits" is a commit message convention that prefixes each message with a type (such as `feat:`, `fix:`, `docs:`) to indicate the nature of the change. git-cliff uses these prefixes to automatically categorize commits.

## When to Use

- When you want automated changelog generation instead of manually writing release notes
- When the project uses Conventional Commits for all commit messages
- When you need consistent changelog formatting across releases
- When you want to generate release notes during a CI/CD pipeline

## Prerequisites

1. Git repository with commit history
2. Commits follow the Conventional Commits convention (e.g., `feat: add user login`)
3. git-cliff installed (see section 2)

---

## 1. What git-cliff Is and When to Use It

git-cliff reads the git log, parses each commit message according to configurable regular expressions, groups the commits by type, and outputs a formatted changelog. It is written in Rust, which makes it fast even on repositories with thousands of commits.

Unlike manually maintained changelogs, git-cliff produces changelogs directly from the commit history. This means the changelog is always in sync with what was actually committed. However, it requires disciplined use of Conventional Commits to produce useful output.

Key features:

- Parses Conventional Commits (feat, fix, docs, refactor, perf, test, chore, etc.)
- Groups commits by category with configurable headings
- Supports custom regular expressions for commit parsing
- Generates markdown output with configurable templates
- Can prepend to an existing CHANGELOG.md without overwriting previous entries
- Supports tag-based version detection

## 2. How to Install git-cliff

### 2.1. Installing on Developer Machines

```bash
# Using cargo (Rust package manager)
cargo install git-cliff

# Using Homebrew (macOS and Linux)
brew install git-cliff

# Using npm/npx (runs without permanent installation)
npx git-cliff@latest

# Using pip
pip install git-cliff
```

After installation, verify it works:

```bash
git-cliff --version
```

### 2.2. Installing in CI/CD Environments

In GitHub Actions, use the official action or install directly:

```yaml
# Option 1: Use the official GitHub Action
- name: Generate changelog
  uses: orhun/git-cliff-action@v4
  with:
    config: cliff.toml
    args: --latest --strip header

# Option 2: Install manually in a workflow step
- name: Install git-cliff
  run: cargo install git-cliff

# Option 3: Use npx (no install needed, Node.js already available)
- name: Generate changelog
  run: npx git-cliff@latest --config cliff.toml --latest
```

## 3. How to Configure git-cliff with cliff.toml

git-cliff reads its configuration from a file named `cliff.toml` in the repository root. This file defines how commits are parsed, categorized, and formatted.

### 3.1. Minimal cliff.toml Configuration

```toml
[changelog]
# The header text prepended to the full changelog
header = """
# Changelog\n
All notable changes to this project will be documented in this file.\n
"""

# The template for each release section
# Uses the Tera templating engine
body = """
{% if version %}\
    ## [{{ version | trim_start_matches(pat="v") }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
    ## [unreleased]
{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}
    ### {{ group | upper_first }}
    {% for commit in commits %}
        - {{ commit.message | upper_first }}\
    {% endfor %}
{% endfor %}\n
"""

# Remove leading and trailing whitespace from the template output
trim = true

[git]
# Parse conventional commits
conventional_commits = true

# Filter out commits that do not follow the convention
filter_unconventional = true

# Process each line of a commit message as an individual commit
split_commits = false
```

### 3.2. Commit Group Categories

Commit groups define how conventional commit types are mapped to changelog section headings. Each group has a display title and a list of commit types that belong to it.

```toml
[git]
conventional_commits = true
filter_unconventional = true

commit_parsers = [
  { message = "^feat", group = "Features" },
  { message = "^fix", group = "Bug Fixes" },
  { message = "^doc", group = "Documentation" },
  { message = "^perf", group = "Performance" },
  { message = "^refactor", group = "Refactoring" },
  { message = "^style", group = "Style" },
  { message = "^test", group = "Testing" },
  { message = "^chore\\(release\\)", skip = true },
  { message = "^chore", group = "Miscellaneous" },
  { message = "^ci", group = "CI/CD" },
  { message = "^build", group = "Build" },
  { message = "^revert", group = "Reverts" },
]
```

This maps commit prefixes to section headings:

| Commit Prefix | Changelog Section |
|---------------|-------------------|
| `feat:` | Features |
| `fix:` | Bug Fixes |
| `doc:` or `docs:` | Documentation |
| `perf:` | Performance |
| `refactor:` | Refactoring |
| `style:` | Style |
| `test:` | Testing |
| `chore:` | Miscellaneous |
| `ci:` | CI/CD |
| `build:` | Build |
| `revert:` | Reverts |
| `chore(release):` | Skipped (not shown) |

### 3.3. Commit Parsers and Regular Expression Patterns

Each entry in `commit_parsers` is checked against the commit message in order. The first matching pattern wins. Patterns use Rust regex syntax.

```toml
commit_parsers = [
  # Skip merge commits entirely
  { message = "^Merge", skip = true },

  # Skip release chore commits
  { message = "^chore\\(release\\)", skip = true },

  # Breaking changes (indicated by ! after type)
  { message = "^.*!:", group = "Breaking Changes" },

  # Standard conventional commit types
  { message = "^feat", group = "Features" },
  { message = "^fix", group = "Bug Fixes" },

  # Catch-all for anything not matched above
  { message = "^.*", group = "Other" },
]
```

Important regex notes:

- `^feat` matches any message starting with "feat" (including "feat:", "feat(scope):")
- `^chore\\(release\\)` matches "chore(release)" -- parentheses must be escaped with double backslash in TOML
- `^.*!:` matches any type with a `!` breaking change indicator before the colon
- Order matters -- put more specific patterns before general ones

### 3.4. Template Customization for Changelog Output Format

The `body` field in `[changelog]` uses the Tera templating engine (similar to Jinja2). Available variables:

| Variable | Description |
|----------|-------------|
| `version` | The tag name (e.g., `v1.2.3`) |
| `timestamp` | The tag creation timestamp |
| `commits` | Array of commit objects |
| `commit.message` | The commit message text |
| `commit.group` | The group name from commit_parsers |
| `commit.scope` | The scope from conventional commit (if present) |
| `commit.id` | The full commit hash |

Example template with scope and commit hash:

```toml
body = """
{% if version %}\
    ## [{{ version | trim_start_matches(pat="v") }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
    ## [unreleased]
{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}
    ### {{ group | upper_first }}
    {% for commit in commits %}
        - {% if commit.scope %}**{{ commit.scope }}**: {% endif %}\
            {{ commit.message | upper_first }} \
            ([{{ commit.id | truncate(length=7, end="") }}](https://github.com/user/repo/commit/{{ commit.id }}))\
    {% endfor %}
{% endfor %}\n
"""
```

### 3.5. Filtering Out Unwanted Commits

Use `skip = true` in commit_parsers to exclude commits from the changelog:

```toml
commit_parsers = [
  # Skip merge commits
  { message = "^Merge", skip = true },
  # Skip release automation commits
  { message = "^chore\\(release\\)", skip = true },
  # Skip CI-only changes
  { message = "^ci:", skip = true },
  # Skip dependency bumps (automated by Dependabot)
  { message = "^chore\\(deps\\)", skip = true },
]
```

## 4. How to Run git-cliff to Generate a Changelog

### 4.1. Generating a Full Changelog

```bash
# Generate the full changelog from all tags to stdout
git-cliff

# Generate and write to CHANGELOG.md
git-cliff --output CHANGELOG.md
```

### 4.2. Generating Changelog for a Specific Version Range

```bash
# Generate changelog between two tags
git-cliff v1.0.0..v1.2.3

# Generate changelog from a specific tag to HEAD
git-cliff v1.2.3..HEAD
```

### 4.3. Generating Changelog for an Unreleased Version

```bash
# Generate changelog for commits since the latest tag
# The --unreleased flag shows only commits not yet included in any tag
git-cliff --unreleased

# Generate changelog for the latest tag only
# The --latest flag shows only commits in the most recent tag
git-cliff --latest

# Strip the header (useful when appending to existing changelog)
git-cliff --latest --strip header
```

### 4.4. Prepending to an Existing CHANGELOG.md

```bash
# The --prepend flag inserts the new content at the top of the file,
# after the header but before existing entries
git-cliff --latest --prepend CHANGELOG.md
```

## 5. How to Integrate git-cliff into CI/CD Workflows

### 5.1. GitHub Actions Integration

```yaml
name: Generate Changelog
on:
  push:
    tags:
      - 'v*'

jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # Full history needed for changelog generation

      - name: Generate changelog for this release
        uses: orhun/git-cliff-action@v4
        id: changelog
        with:
          config: cliff.toml
          args: --latest --strip header
        env:
          OUTPUT: CHANGES.md

      - name: Read generated changelog
        id: read_changelog
        run: |
          CONTENT=$(cat CHANGES.md)
          echo "content<<EOF" >> $GITHUB_OUTPUT
          echo "$CONTENT" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT
```

### 5.2. Using git-cliff Output as Release Notes

The generated changelog can be passed to the GitHub release creation step:

```yaml
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          body: ${{ steps.read_changelog.outputs.content }}
          tag_name: ${{ github.ref_name }}
```

## 6. Troubleshooting git-cliff Issues

### Empty changelog generated

**Cause**: No commits match the configured commit_parsers patterns. If `filter_unconventional = true` is set, commits that do not follow the conventional format are excluded.

**Solution**: Check that commits use conventional prefixes (`feat:`, `fix:`, etc.). Or set `filter_unconventional = false` and add a catch-all parser: `{ message = "^.*", group = "Other" }`.

### Wrong version in changelog header

**Cause**: git-cliff uses git tags to determine version numbers. If the tag does not exist yet, the version shows as "unreleased".

**Solution**: Create the tag before running git-cliff, or use the `--tag` flag to specify the version manually: `git-cliff --tag v1.2.4`.

### Commits from wrong range included

**Cause**: Missing or incorrect `fetch-depth` in CI checkout. Without full history, git-cliff cannot find previous tags.

**Solution**: Use `fetch-depth: 0` in the checkout action to clone full history.

### Duplicate entries in changelog

**Cause**: Running `git-cliff --output CHANGELOG.md` overwrites the file. Running `git-cliff --prepend CHANGELOG.md` twice without a new tag in between will duplicate the entries.

**Solution**: Use `--prepend` only once per release. Use `--latest` to limit output to the most recent tag's commits.

### cliff.toml not found

**Cause**: git-cliff looks for `cliff.toml` in the current working directory by default.

**Solution**: Specify the path explicitly: `git-cliff --config path/to/cliff.toml`. In CI, ensure the working directory is the repository root.
