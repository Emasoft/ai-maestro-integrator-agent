---
name: ci-pr-auto-labeling
description: "How to automatically label pull requests by type (from commit prefix), area (from file paths), and size (from lines changed)."
---

# CI PR Auto-Labeling

## Table of Contents

- 7.1 Three Label Categories
  - 7.1.1 Type labels from conventional commit prefixes
  - 7.1.2 Area labels from changed file paths
  - 7.1.3 Size labels from total lines changed
- 7.2 Conventional Commit Type Extraction
  - 7.2.1 Regex pattern with ReDoS protection
  - 7.2.2 TYPE_MAP: mapping commit prefixes to label names
  - 7.2.3 Input slicing and bounded repetition for safety
- 7.3 Size Classification Thresholds
  - 7.3.1 Default threshold table (XS, S, M, L, XL)
  - 7.3.2 Customizing thresholds via CONFIG object
- 7.4 Area Detection from File Path Prefixes
  - 7.4.1 Configurable AREA_PATHS mapping
  - 7.4.2 Matching changed files against area definitions
- 7.5 Fork PR Security
  - 7.5.1 Why fork PRs need special handling
  - 7.5.2 The `head.repo.full_name` guard condition
- 7.6 Pagination for Large PRs
  - 7.6.1 Using `github.paginate()` to fetch all changed files
  - 7.6.2 Why default API responses are limited to 30 files
- 7.7 Idempotent Label Management
  - 7.7.1 Remove old labels before adding new ones
  - 7.7.2 Using `Promise.allSettled` for parallel removal with 404 handling
- 7.8 Job Summary Table
  - 7.8.1 Writing a summary of applied labels
- 7.9 Complete YAML Example
  - 7.9.1 Full workflow with `actions/github-script`
  - 7.9.2 CONFIG object pattern for maintainability

---

## 7.1 Three Label Categories

### 7.1.1 Type Labels from Conventional Commit Prefixes

Type labels indicate the nature of the change. They are derived from the pull
request title, which typically follows conventional commit format (for example,
`feat: add authentication`, `fix: resolve timeout issue`).

Common type labels:

| Commit prefix | Label name |
|--------------|------------|
| `feat` | `feature` |
| `fix` | `bug` |
| `docs` | `documentation` |
| `chore` | `chore` |
| `refactor` | `refactor` |
| `test` | `testing` |
| `ci` | `ci` |
| `perf` | `performance` |
| `style` | `style` |
| `build` | `build` |

### 7.1.2 Area Labels from Changed File Paths

Area labels indicate which part of the codebase is affected. They are derived
from the file paths changed in the pull request. For example, if files under
`src/api/` are changed, the pull request gets a `area:api` label.

### 7.1.3 Size Labels from Total Lines Changed

Size labels indicate the scope of the change based on total lines added and
removed. Small pull requests are easier to review and less risky.

---

## 7.2 Conventional Commit Type Extraction

### 7.2.1 Regex Pattern with ReDoS Protection

The regex must handle malformed titles gracefully without catastrophic backtracking
(Regular Expression Denial of Service). Use bounded repetition and input slicing:

```javascript
// Slice the title to at most 200 characters to prevent ReDoS on very long titles
const titleSlice = context.payload.pull_request.title.slice(0, 200);
// Bounded repetition: {1,30} instead of + to prevent catastrophic backtracking
const typeMatch = titleSlice.match(/^([a-z]{1,30})(?:\(.{0,50}\))?!?:/);
```

The first capture group extracts the type prefix (for example, `feat`, `fix`, `docs`).

### 7.2.2 TYPE_MAP: Mapping Commit Prefixes to Label Names

```javascript
const TYPE_MAP = {
  feat:     'feature',
  fix:      'bug',
  docs:     'documentation',
  chore:    'chore',
  refactor: 'refactor',
  test:     'testing',
  ci:       'ci',
  perf:     'performance',
  style:    'style',
  build:    'build',
};
```

### 7.2.3 Input Slicing and Bounded Repetition for Safety

Two defenses against ReDoS:

1. **Input slicing**: `title.slice(0, 200)` limits the input length. Even a
   pathological regex cannot backtrack through more than 200 characters.

2. **Bounded repetition**: `{1,30}` instead of `+` or `*` caps the number of
   characters the quantifier can match. This prevents exponential backtracking
   on adversarial inputs.

---

## 7.3 Size Classification Thresholds

### 7.3.1 Default Threshold Table

| Label | Lines changed | Description |
|-------|--------------|-------------|
| `size:XS` | 1-9 | Trivial change (typo, one-liner) |
| `size:S` | 10-99 | Small change (single function or config tweak) |
| `size:M` | 100-499 | Medium change (feature addition, refactor) |
| `size:L` | 500-999 | Large change (multi-file feature, major refactor) |
| `size:XL` | 1000+ | Extra large change (new module, migration) |

Lines changed = additions + deletions across all files in the pull request.

### 7.3.2 Customizing Thresholds via CONFIG Object

```javascript
const CONFIG = {
  SIZE_THRESHOLDS: [
    { label: 'size:XS', max: 10 },
    { label: 'size:S',  max: 100 },
    { label: 'size:M',  max: 500 },
    { label: 'size:L',  max: 1000 },
    { label: 'size:XL', max: Infinity },
  ],
};
```

Place the CONFIG object at the top of the script for easy customization.

---

## 7.4 Area Detection from File Path Prefixes

### 7.4.1 Configurable AREA_PATHS Mapping

```javascript
const AREA_PATHS = {
  'area:api':       ['src/api/', 'src/routes/'],
  'area:ui':        ['src/components/', 'src/pages/', 'src/styles/'],
  'area:core':      ['src/core/', 'src/lib/'],
  'area:tests':     ['tests/', 'test/'],
  'area:ci':        ['.github/'],
  'area:docs':      ['docs/', 'README.md'],
  'area:config':    ['pyproject.toml', 'package.json', 'tsconfig.json'],
};
```

### 7.4.2 Matching Changed Files Against Area Definitions

```javascript
function detectAreas(files) {
  const areas = new Set();
  for (const file of files) {
    for (const [label, prefixes] of Object.entries(AREA_PATHS)) {
      if (prefixes.some(prefix => file.filename.startsWith(prefix))) {
        areas.add(label);
      }
    }
  }
  return Array.from(areas);
}
```

---

## 7.5 Fork PR Security

### 7.5.1 Why Fork PRs Need Special Handling

Workflows triggered by pull requests from forks run with read-only GITHUB_TOKEN
permissions. A fork PR auto-labeling workflow that tries to add labels will fail
with a 403 error unless the workflow has write permissions.

More importantly, fork PRs can contain malicious workflow modifications. A labeling
workflow should verify that the PR comes from the same repository before applying
labels with write permissions.

### 7.5.2 The `head.repo.full_name` Guard Condition

```yaml
jobs:
  label-pr:
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
```

This condition ensures the job only runs when the pull request originates from
the same repository (not a fork). Fork PRs are silently skipped.

---

## 7.6 Pagination for Large PRs

### 7.6.1 Using `github.paginate()` to Fetch All Changed Files

```javascript
const files = await github.paginate(
  github.rest.pulls.listFiles,
  {
    owner: context.repo.owner,
    repo: context.repo.repo,
    pull_number: context.payload.pull_request.number,
    per_page: 100,
  }
);
```

### 7.6.2 Why Default API Responses Are Limited to 30 Files

The GitHub REST API returns at most 30 items per page by default, or up to 100
with `per_page: 100`. A large pull request with 200+ changed files requires
pagination to see all files. Without pagination, area detection misses files on
later pages.

---

## 7.7 Idempotent Label Management

### 7.7.1 Remove Old Labels Before Adding New Ones

When a pull request title changes from `feat: add login` to `fix: login timeout`,
the type label should change from `feature` to `bug`. The workflow must remove
the old label before adding the new one:

```javascript
// Collect all managed labels (all type, area, and size labels)
const managedPrefixes = ['size:', 'area:'];
const managedExact = Object.values(TYPE_MAP);

const currentLabels = context.payload.pull_request.labels.map(l => l.name);
const toRemove = currentLabels.filter(name =>
  managedPrefixes.some(p => name.startsWith(p)) ||
  managedExact.includes(name)
);
```

### 7.7.2 Using `Promise.allSettled` for Parallel Removal with 404 Handling

```javascript
await Promise.allSettled(
  toRemove.map(name =>
    github.rest.issues.removeLabel({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: context.payload.pull_request.number,
      name: name,
    }).catch(err => {
      // 404 means the label was already removed -- ignore
      if (err.status !== 404) throw err;
    })
  )
);
```

`Promise.allSettled` runs all removals in parallel and waits for all to complete,
even if some fail. The 404 catch prevents errors when a label was already removed
by another process.

---

## 7.8 Job Summary Table

### 7.8.1 Writing a Summary of Applied Labels

```javascript
const summary = [
  '## PR Labels Applied',
  '',
  '| Category | Label |',
  '|----------|-------|',
];

if (typeLabel) summary.push(`| Type | \`${typeLabel}\` |`);
for (const area of areaLabels) {
  summary.push(`| Area | \`${area}\` |`);
}
summary.push(`| Size | \`${sizeLabel}\` |`);
summary.push('');
summary.push(`Total lines changed: ${totalChanges}`);

await core.summary.addRaw(summary.join('\n')).write();
```

---

## 7.9 Complete YAML Example

### 7.9.1 Full Workflow with `actions/github-script`

```yaml
name: PR Auto-Label

on:
  pull_request:
    types: [opened, synchronize, edited]

permissions:
  pull-requests: write
  contents: read

jobs:
  label-pr:
    name: Auto-Label PR
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    steps:
      - name: Apply labels
        uses: actions/github-script@v7
        with:
          script: |
            // --- CONFIG ---
            const TYPE_MAP = {
              feat: 'feature', fix: 'bug', docs: 'documentation',
              chore: 'chore', refactor: 'refactor', test: 'testing',
              ci: 'ci', perf: 'performance', style: 'style', build: 'build',
            };

            const AREA_PATHS = {
              'area:api':    ['src/api/', 'src/routes/'],
              'area:ui':     ['src/components/', 'src/pages/'],
              'area:core':   ['src/core/', 'src/lib/'],
              'area:tests':  ['tests/', 'test/'],
              'area:ci':     ['.github/'],
              'area:docs':   ['docs/'],
            };

            const SIZE_THRESHOLDS = [
              { label: 'size:XS', max: 10 },
              { label: 'size:S',  max: 100 },
              { label: 'size:M',  max: 500 },
              { label: 'size:L',  max: 1000 },
              { label: 'size:XL', max: Infinity },
            ];

            // --- TYPE DETECTION ---
            const titleSlice = context.payload.pull_request.title.slice(0, 200);
            const typeMatch = titleSlice.match(/^([a-z]{1,30})(?:\(.{0,50}\))?!?:/);
            const typeLabel = typeMatch ? TYPE_MAP[typeMatch[1]] || null : null;

            // --- FILE FETCHING ---
            const files = await github.paginate(
              github.rest.pulls.listFiles,
              {
                owner: context.repo.owner,
                repo: context.repo.repo,
                pull_number: context.payload.pull_request.number,
                per_page: 100,
              }
            );

            // --- AREA DETECTION ---
            const areas = new Set();
            for (const file of files) {
              for (const [label, prefixes] of Object.entries(AREA_PATHS)) {
                if (prefixes.some(p => file.filename.startsWith(p))) {
                  areas.add(label);
                }
              }
            }

            // --- SIZE DETECTION ---
            const totalChanges = files.reduce(
              (sum, f) => sum + f.additions + f.deletions, 0
            );
            const sizeLabel = SIZE_THRESHOLDS.find(
              t => totalChanges < t.max
            ).label;

            // --- REMOVE OLD MANAGED LABELS ---
            const managedPrefixes = ['size:', 'area:'];
            const managedExact = Object.values(TYPE_MAP);
            const current = context.payload.pull_request.labels.map(l => l.name);
            const toRemove = current.filter(name =>
              managedPrefixes.some(p => name.startsWith(p)) ||
              managedExact.includes(name)
            );

            await Promise.allSettled(
              toRemove.map(name =>
                github.rest.issues.removeLabel({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: context.payload.pull_request.number,
                  name,
                }).catch(err => { if (err.status !== 404) throw err; })
              )
            );

            // --- ADD NEW LABELS ---
            const newLabels = [
              ...(typeLabel ? [typeLabel] : []),
              ...Array.from(areas),
              sizeLabel,
            ];

            if (newLabels.length > 0) {
              await github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.payload.pull_request.number,
                labels: newLabels,
              });
            }

            // --- JOB SUMMARY ---
            const rows = [];
            if (typeLabel) rows.push(`| Type | \`${typeLabel}\` |`);
            for (const a of areas) rows.push(`| Area | \`${a}\` |`);
            rows.push(`| Size | \`${sizeLabel}\` |`);

            await core.summary
              .addHeading('PR Labels Applied', 2)
              .addTable([
                [{data: 'Category', header: true}, {data: 'Label', header: true}],
                ...rows.map(r => {
                  const cells = r.replace(/^\||\|$/g, '').split('|').map(c => c.trim());
                  return cells;
                }),
              ])
              .addRaw(`\nTotal lines changed: ${totalChanges}`)
              .write();
```

### 7.9.2 CONFIG Object Pattern for Maintainability

All configurable values (TYPE_MAP, AREA_PATHS, SIZE_THRESHOLDS) are defined at
the top of the script. This makes it easy for maintainers to customize label
names, area mappings, and size thresholds without modifying the logic below.
