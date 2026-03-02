# GitHub Infrastructure CI Failure Patterns

## Table of Contents

- 5.1 Missing Labels
  - 5.1.1 Creating labels before workflow uses them
  - 5.1.2 Label API format and authentication
  - 5.1.3 Label naming conventions
- 5.2 Platform Exceptions and Documentation
  - 5.2.1 Runner operating system differences
  - 5.2.2 Pre-installed software differences
  - 5.2.3 Environment variable differences
- 5.3 Runner Architecture
  - 5.3.1 x64 vs ARM runner differences
  - 5.3.2 Self-hosted runner considerations
  - 5.3.3 Runner resource limits

---

## 5.1 Missing Labels

Labels are often used to control workflows, but missing labels cause silent failures or unexpected behavior.

### 5.1.1 Creating Labels Before Workflow Uses Them

**Common CI Failure**: Workflow tries to add a label that doesn't exist.

**Error Message**:
```
Resource not accessible by integration
```
or
```
Label "my-label" not found
```

**Why This Happens**: GitHub API requires labels to exist before they can be applied.

**Solution 1**: Create labels in repository setup
```yaml
# .github/workflows/setup-labels.yml
name: Setup Repository Labels

on:
  workflow_dispatch:  # Manual trigger

jobs:
  create-labels:
    runs-on: ubuntu-latest
    steps:
      - name: Create labels
        uses: actions/github-script@v7
        with:
          script: |
            const labels = [
              { name: 'bug', color: 'd73a4a', description: 'Something isn\'t working' },
              { name: 'enhancement', color: 'a2eeef', description: 'New feature or request' },
              { name: 'ci-passed', color: '0e8a16', description: 'CI tests passed' },
              { name: 'ai-review', color: 'fbca04', description: 'Awaiting code review' }
            ];

            for (const label of labels) {
              try {
                await github.rest.issues.createLabel({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  ...label
                });
                console.log(`Created label: ${label.name}`);
              } catch (e) {
                if (e.status === 422) {
                  console.log(`Label already exists: ${label.name}`);
                } else {
                  throw e;
                }
              }
            }
```

**Solution 2**: Check and create label before use
```yaml
- name: Ensure label exists and apply
  uses: actions/github-script@v7
  with:
    script: |
      const labelName = 'ci-passed';

      // Try to get the label
      try {
        await github.rest.issues.getLabel({
          owner: context.repo.owner,
          repo: context.repo.repo,
          name: labelName
        });
      } catch (e) {
        if (e.status === 404) {
          // Label doesn't exist, create it
          await github.rest.issues.createLabel({
            owner: context.repo.owner,
            repo: context.repo.repo,
            name: labelName,
            color: '0e8a16'
          });
        }
      }

      // Now safely add the label
      await github.rest.issues.addLabels({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.issue.number,
        labels: [labelName]
      });
```

### 5.1.2 Label API Format and Authentication

**GitHub API Label Format**:
```json
{
  "name": "bug",
  "color": "d73a4a",
  "description": "Something isn't working"
}
```

**Important**: Color is a 6-character hex code WITHOUT the `#` prefix.

**WRONG**:
```json
{ "color": "#d73a4a" }
```

**CORRECT**:
```json
{ "color": "d73a4a" }
```

**Authentication**: Use `${{ secrets.GITHUB_TOKEN }}` for default permissions.

```yaml
- name: Manage labels
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh label create "my-label" --color "0e8a16" --description "My label"
```

**Permissions Required**:
```yaml
permissions:
  issues: write        # To add labels to issues
  pull-requests: write # To add labels to PRs
```

### 5.1.3 Label Naming Conventions

**Best Practices**:
- Use lowercase with hyphens: `ai-review` not `AI Review`
- Prefix with category: `type/bug`, `status/in-progress`, `priority/high`
- Keep names short but descriptive

**Label Categories**:
```
type/bug
type/enhancement
type/documentation
status/in-progress
status/review-needed
status/blocked
priority/critical
priority/high
priority/low
```

**Reserved Label Patterns** (used by GitHub features):
- `dependencies` - Used by Dependabot
- `security` - Used by security alerts
- `good first issue` - Used by contributor suggestions

---

## 5.2 Platform Exceptions and Documentation

### 5.2.1 Runner Operating System Differences

**GitHub-Hosted Runner Images**:

| Runner | OS | Architecture |
|--------|------|--------------|
| `ubuntu-latest` | Ubuntu 22.04 | x64 |
| `ubuntu-22.04` | Ubuntu 22.04 | x64 |
| `ubuntu-20.04` | Ubuntu 20.04 | x64 |
| `windows-latest` | Windows Server 2022 | x64 |
| `windows-2022` | Windows Server 2022 | x64 |
| `windows-2019` | Windows Server 2019 | x64 |
| `macos-latest` | macOS 14 (Sonoma) | ARM64 |
| `macos-14` | macOS 14 (Sonoma) | ARM64 |
| `macos-13` | macOS 13 (Ventura) | x64 |

**Critical Note**: `macos-latest` changed from Intel (x64) to Apple Silicon (ARM64)!

**Common CI Failure**: Code assumes x64 architecture on macOS.

**Detection**:
```yaml
- name: Check architecture
  run: |
    echo "OS: $RUNNER_OS"
    echo "Arch: $RUNNER_ARCH"
    uname -m
```

**Conditional Logic**:
```yaml
- name: Install x64-specific tool
  if: runner.arch == 'X64'
  run: ./install-x64.sh

- name: Install ARM64-specific tool
  if: runner.arch == 'ARM64'
  run: ./install-arm64.sh
```

### 5.2.2 Pre-Installed Software Differences

Each runner image has different pre-installed software.

**Check Installed Software**:
```yaml
- name: List installed software
  run: |
    # Ubuntu
    apt list --installed

    # macOS
    brew list

    # Check specific tool
    python --version
    node --version
    java --version
```

**Common CI Failure**: Assuming a tool is installed.

**Error Message**:
```
/bin/bash: python: command not found
```

**Solution**: Use setup actions
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- uses: actions/setup-node@v4
  with:
    node-version: '20'

- uses: actions/setup-java@v4
  with:
    java-version: '17'
    distribution: 'temurin'
```

**Pre-Installed Tools by Runner**:

| Tool | ubuntu-latest | windows-latest | macos-latest |
|------|---------------|----------------|--------------|
| Python | 3.10, 3.11, 3.12 | 3.9 - 3.12 | 3.11, 3.12 |
| Node.js | 18, 20 | 18, 20 | 18, 20 |
| Git | Yes | Yes | Yes |
| Docker | Yes | Yes | Yes |
| PowerShell | Yes | Yes | Yes |

**Important**: Exact versions change frequently. Always use setup actions for reproducibility.

### 5.2.3 Environment Variable Differences

**GitHub Actions Environment Variables**:

| Variable | Description | All Platforms |
|----------|-------------|---------------|
| `GITHUB_WORKSPACE` | Repository root | Yes |
| `GITHUB_TOKEN` | Auth token | Yes |
| `RUNNER_OS` | `Linux`, `Windows`, `macOS` | Yes |
| `RUNNER_ARCH` | `X64`, `ARM64` | Yes |
| `HOME` | Home directory | Linux/macOS |
| `USERPROFILE` | Home directory | Windows |
| `TEMP`/`TMP` | Temp directory | Windows |
| `TMPDIR` | Temp directory | macOS |
| `RUNNER_TEMP` | Runner temp | Yes |

**Cross-Platform Home Directory**:
```yaml
- name: Get home directory
  run: |
    # Cross-platform
    echo "Home: $HOME"  # Works on all via Git Bash on Windows

    # Or use runner context
    echo "Home: ${{ runner.temp }}/.."  # Approximate
```

**Shell Differences**:
```yaml
- name: Default shells differ
  shell: bash  # Explicitly set for cross-platform
  run: |
    # bash available on all platforms
    echo "Running in bash"
```

| Platform | Default Shell |
|----------|---------------|
| Linux | `bash` |
| macOS | `bash` |
| Windows | `pwsh` (PowerShell Core) |

---

## 5.3 Runner Architecture

### 5.3.1 x64 vs ARM64 Runner Differences

**macOS Architecture Change**:
- `macos-latest` now points to ARM64 (Apple Silicon)
- `macos-13` is the last x64 (Intel) macOS runner

**Common CI Failure**: Binary incompatibility.

**Error Message**:
```
cannot execute binary file: Exec format error
```

**Solution 1**: Use architecture-specific runners
```yaml
strategy:
  matrix:
    include:
      - os: macos-13   # Intel
        arch: x64
      - os: macos-14   # Apple Silicon
        arch: arm64
```

**Solution 2**: Use Rosetta 2 on ARM64 macOS
```yaml
- name: Run x64 binary on ARM64
  if: runner.arch == 'ARM64' && runner.os == 'macOS'
  run: |
    # Rosetta 2 auto-translates most x64 binaries
    arch -x86_64 ./my-x64-binary
```

**Solution 3**: Build for both architectures
```yaml
- name: Build universal binary
  if: runner.os == 'macOS'
  run: |
    # Build for both architectures
    cargo build --target aarch64-apple-darwin
    cargo build --target x86_64-apple-darwin

    # Create universal binary
    lipo -create -output binary-universal \
      target/aarch64-apple-darwin/release/binary \
      target/x86_64-apple-darwin/release/binary
```

### 5.3.2 Self-Hosted Runner Considerations

Self-hosted runners have different characteristics:

**Differences from GitHub-Hosted**:
- Persistent state between runs (cleanup required)
- Custom tools pre-installed
- Different resource limits
- Network configuration varies

**Common CI Failure**: Leftover files from previous run.

**Solution**: Clean workspace
```yaml
- name: Clean workspace
  run: |
    git clean -ffdx
    git reset --hard HEAD
```

**Labeling Self-Hosted Runners**:
```yaml
runs-on: [self-hosted, linux, x64, gpu]  # Multiple labels
```

### 5.3.3 Runner Resource Limits

**GitHub-Hosted Runner Limits**:

| Resource | Linux | Windows | macOS |
|----------|-------|---------|-------|
| vCPU | 4 | 4 | 3-4 |
| RAM | 16 GB | 16 GB | 14 GB |
| Storage | 14 GB | 14 GB | 14 GB |
| Max job time | 6 hours | 6 hours | 6 hours |

**Common CI Failure**: Out of disk space.

**Error Message**:
```
No space left on device
```

**Solution**: Free disk space
```yaml
- name: Free disk space
  run: |
    # Remove unnecessary tools
    sudo rm -rf /usr/share/dotnet
    sudo rm -rf /usr/local/lib/android
    sudo rm -rf /opt/ghc

    # Check available space
    df -h
```

**Common CI Failure**: Out of memory.

**Error Message**:
```
FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory
```

**Solution**: Increase Node.js memory
```yaml
- name: Build with more memory
  env:
    NODE_OPTIONS: '--max-old-space-size=4096'
  run: npm run build
```

---

## Quick Reference: Infrastructure Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Label not found | Label doesn't exist | Create label before using |
| Command not found | Tool not installed | Use setup action |
| Exec format error | Architecture mismatch | Use correct arch runner |
| No space left | Disk full | Free space, clean artifacts |
| Out of memory | Resource limit | Increase memory, optimize build |
| Permission denied | Token scope | Add required permissions |

---

## Summary: Infrastructure Checklist

Before committing CI workflows:

- [ ] Labels created before workflow uses them
- [ ] Correct permissions declared
- [ ] Tools installed via setup actions (not assumed)
- [ ] Architecture differences handled (x64 vs ARM64)
- [ ] Environment variables are cross-platform
- [ ] Default shell explicitly set when needed
- [ ] Disk space cleanup for large builds
- [ ] Memory limits increased if needed
- [ ] Self-hosted runner cleanup included
