---
name: ci-minimum-permissions
description: "How to apply the principle of least privilege to GITHUB_TOKEN permissions in workflow definitions."
---

# CI Minimum Permissions

## Table of Contents

- 9.1 Understanding Default GITHUB_TOKEN Permissions
  - 9.1.1 What the GITHUB_TOKEN is and how it is created
  - 9.1.2 Default permission scope (broad vs restricted)
  - 9.1.3 Organization-level default settings
- 9.2 Declaring Explicit Permissions at Workflow Level
  - 9.2.1 The `permissions:` key at workflow root
  - 9.2.2 How explicit permissions override defaults
  - 9.2.3 The empty permissions pattern for maximum restriction
- 9.3 Per-Job Permission Overrides
  - 9.3.1 Job-level `permissions:` syntax
  - 9.3.2 How job permissions interact with workflow permissions
  - 9.3.3 When to use job-level overrides
- 9.4 Common Permission Sets by Workflow Type
  - 9.4.1 Read-only CI (lint, test, build)
  - 9.4.2 PR-commenting workflows (lint annotations, test reports)
  - 9.4.3 Security scanning workflows
  - 9.4.4 Package publishing workflows
  - 9.4.5 Release and tag creation workflows
  - 9.4.6 GitHub Pages deployment workflows
- 9.5 Personal Access Tokens for Cross-Workflow Triggers
  - 9.5.1 Why GITHUB_TOKEN cannot trigger other workflows
  - 9.5.2 Creating a Personal Access Token with minimal scopes
  - 9.5.3 Storing the token as a repository secret
  - 9.5.4 Using the token in workflow steps
- 9.6 Complete YAML Examples
  - 9.6.1 Minimal CI workflow permissions
  - 9.6.2 PR review workflow permissions
  - 9.6.3 Release workflow permissions
- 9.7 Security Benefits
  - 9.7.1 Limiting blast radius of compromised workflows
  - 9.7.2 Defense against supply chain attacks via actions
  - 9.7.3 Audit trail for permission changes

---

## 9.1 Understanding Default GITHUB_TOKEN Permissions

### 9.1.1 What the GITHUB_TOKEN Is and How It Is Created

Every GitHub Actions workflow run automatically receives a `GITHUB_TOKEN`. This
token is created at the start of the run and expires when the run completes. It
authenticates API calls made by the workflow (checking out code, posting comments,
creating releases, uploading artifacts).

The token is available as `${{ secrets.GITHUB_TOKEN }}` or `${{ github.token }}`
in workflow expressions, and as the `GITHUB_TOKEN` environment variable in steps.

### 9.1.2 Default Permission Scope (Broad vs Restricted)

By default, the GITHUB_TOKEN has broad read/write permissions on the repository:

| Permission | Default (permissive) |
|------------|---------------------|
| `actions` | read/write |
| `contents` | read/write |
| `issues` | read/write |
| `pull-requests` | read/write |
| `packages` | read/write |
| `deployments` | read/write |
| `security-events` | read/write |

This means any workflow step can modify repository contents, close issues, merge
pull requests, or publish packages -- even if the workflow only needs to run tests.

### 9.1.3 Organization-Level Default Settings

Organization administrators can set the default GITHUB_TOKEN permissions to
"Read repository contents and packages permissions" in Organization Settings
> Actions > General > Workflow permissions. This changes the default for all
repositories in the organization.

Individual repositories can further restrict (but not broaden) the organization
default.

---

## 9.2 Declaring Explicit Permissions at Workflow Level

### 9.2.1 The `permissions:` Key at Workflow Root

Add a `permissions:` block at the top level of the workflow file to declare
exactly which permissions the workflow needs:

```yaml
name: CI

permissions:
  contents: read
  actions: read

on:
  pull_request:
    branches: [main]
```

When you declare explicit permissions, all permissions not listed are set to
`none`. This is the key security benefit: you opt in to only what you need.

### 9.2.2 How Explicit Permissions Override Defaults

| Scenario | Result |
|----------|--------|
| No `permissions:` in workflow | Uses repository/org default (usually broad) |
| `permissions:` with specific scopes | Listed scopes get declared level; all others get `none` |
| `permissions: {}` (empty object) | All permissions set to `none` |

### 9.2.3 The Empty Permissions Pattern for Maximum Restriction

```yaml
permissions: {}
```

This sets all permissions to `none`. Individual jobs must then declare their
own permissions. This is the most secure pattern because it forces each job
to explicitly request only what it needs:

```yaml
permissions: {}

jobs:
  test:
    permissions:
      contents: read
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test

  deploy:
    permissions:
      contents: write
      packages: write
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make deploy
```

---

## 9.3 Per-Job Permission Overrides

### 9.3.1 Job-Level `permissions:` Syntax

Each job can declare its own permissions:

```yaml
jobs:
  lint:
    permissions:
      contents: read
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ruff check src/

  comment:
    permissions:
      contents: read
      pull-requests: write
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: 'Lint passed!'
            });
```

### 9.3.2 How Job Permissions Interact with Workflow Permissions

Job-level permissions can only restrict, never broaden, the workflow-level
permissions. If the workflow declares `contents: read`, a job cannot escalate
to `contents: write`.

| Workflow level | Job level | Effective |
|---------------|-----------|-----------|
| `contents: read` | `contents: write` | `contents: read` (cannot escalate) |
| `contents: write` | `contents: read` | `contents: read` (job restricts) |
| Not declared | `contents: read` | `contents: read` |

### 9.3.3 When to Use Job-Level Overrides

Use job-level permissions when:
- Different jobs need different permission sets (test job vs deploy job)
- You want to apply the empty permissions pattern at workflow level
- A specific job needs write access that other jobs do not need

---

## 9.4 Common Permission Sets by Workflow Type

### 9.4.1 Read-Only CI (Lint, Test, Build)

```yaml
permissions:
  contents: read
  actions: read
```

This is the minimum for checking out code and reading workflow run metadata.

### 9.4.2 PR-Commenting Workflows (Lint Annotations, Test Reports)

```yaml
permissions:
  contents: read
  pull-requests: write
```

The `pull-requests: write` permission allows creating PR comments and adding
review comments. Without it, any attempt to post a comment fails with 403.

### 9.4.3 Security Scanning Workflows

```yaml
permissions:
  contents: read
  actions: read
  security-events: write
```

The `security-events: write` permission is required for uploading CodeQL results
and SARIF files to the GitHub Security tab.

### 9.4.4 Package Publishing Workflows

```yaml
permissions:
  contents: read
  packages: write
```

The `packages: write` permission allows publishing to GitHub Packages (container
registry, npm registry, Maven repository).

### 9.4.5 Release and Tag Creation Workflows

```yaml
permissions:
  contents: write
```

The `contents: write` permission is required for creating tags, releases, and
uploading release assets. This is the most sensitive common permission because
it allows modifying repository contents.

### 9.4.6 GitHub Pages Deployment Workflows

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

The `pages: write` permission allows deploying to GitHub Pages. The `id-token: write`
permission is needed for OIDC-based authentication in the deployment action.

---

## 9.5 Personal Access Tokens for Cross-Workflow Triggers

### 9.5.1 Why GITHUB_TOKEN Cannot Trigger Other Workflows

To prevent infinite workflow loops, events created using the GITHUB_TOKEN do
not trigger new workflow runs. If workflow A pushes a commit using GITHUB_TOKEN,
workflow B (triggered by push events) will NOT run.

This is a deliberate safety feature. It means that release workflows that
need to trigger CI on the newly created tag must use a different authentication
method.

### 9.5.2 Creating a Personal Access Token with Minimal Scopes

1. Go to GitHub Settings > Developer settings > Personal access tokens > Fine-grained tokens
2. Click "Generate new token"
3. Set token name (for example, `CI_TRIGGER_TOKEN`)
4. Set expiration (maximum 1 year; consider 90 days for security)
5. Select the specific repository (not "All repositories")
6. Under "Repository permissions", grant only:
   - `Contents: Read and write` (to push commits/tags that trigger workflows)
7. Generate the token and copy it immediately

### 9.5.3 Storing the Token as a Repository Secret

1. Go to repository Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Name: `PAT_TOKEN` (or another descriptive name)
4. Value: paste the token
5. Click "Add secret"

### 9.5.4 Using the Token in Workflow Steps

```yaml
- name: Push tag to trigger release workflow
  env:
    GITHUB_TOKEN: ${{ secrets.PAT_TOKEN }}
  run: |
    git tag v1.2.3
    git push origin v1.2.3
```

The push event created by this step will trigger other workflows because it
uses the PAT, not the default GITHUB_TOKEN.

---

## 9.6 Complete YAML Examples

### 9.6.1 Minimal CI Workflow Permissions

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

permissions:
  contents: read
  actions: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[test]"
      - run: pytest tests/
```

### 9.6.2 PR Review Workflow Permissions

```yaml
name: PR Review

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run checks and comment
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: 'Automated review checks passed.'
            });
```

### 9.6.3 Release Workflow Permissions

```yaml
name: Release

on:
  push:
    tags: ["v*"]

permissions:
  contents: write
  packages: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build package
        run: |
          pip install build
          python -m build

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: dist/*

      - name: Publish to package registry
        run: |
          pip install twine
          twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

---

## 9.7 Security Benefits

### 9.7.1 Limiting Blast Radius of Compromised Workflows

If a third-party action is compromised (supply chain attack), the attacker gains
the permissions of the workflow that uses it. With broad default permissions, the
attacker can:
- Push malicious code to the repository
- Close or reopen issues to cause confusion
- Publish malicious packages
- Delete releases

With minimal permissions (`contents: read` only), the attacker can only read
code -- they cannot modify anything.

### 9.7.2 Defense Against Supply Chain Attacks via Actions

Pin action versions to full SHA hashes instead of tags to prevent tag-swapping
attacks:

```yaml
# GOOD: Pinned to exact commit hash
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1

# ACCEPTABLE: Pinned to major version tag (auto-updates within major)
- uses: actions/checkout@v4

# BAD: Unpinned (always gets latest, including potentially compromised versions)
- uses: actions/checkout@main
```

Combined with minimal permissions, SHA-pinned actions provide defense in depth:
even if a dependency is compromised, the damage is limited by the declared
permissions.

### 9.7.3 Audit Trail for Permission Changes

When permissions are explicitly declared in the workflow YAML file, any change
to permissions shows up in the pull request diff. This provides a clear audit
trail: reviewers can see when a workflow requests new permissions and evaluate
whether the request is justified.

Without explicit permissions, the workflow silently uses whatever the repository
default allows, and there is no visible record of what permissions are being
used.
