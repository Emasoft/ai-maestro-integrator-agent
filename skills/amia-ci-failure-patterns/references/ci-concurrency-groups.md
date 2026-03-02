---
name: ci-concurrency-groups
description: "How to configure concurrency groups with cancel-in-progress to save CI minutes and avoid redundant runs."
---

# CI Concurrency Groups

## Table of Contents

- 2.1 Understanding Concurrency Groups
  - 2.1.1 What is a concurrency group
  - 2.1.2 Why concurrency groups save CI minutes and reduce queue congestion
- 2.2 PR-Based Grouping Pattern
  - 2.2.1 Group key expression for pull request workflows
  - 2.2.2 Fallback to `github.ref` for non-PR triggers
  - 2.2.3 Complete YAML example for PR-based grouping
- 2.3 Branch-Based Grouping for Push Workflows
  - 2.3.1 Group key expression using `github.ref`
  - 2.3.2 Complete YAML example for push-triggered workflows
- 2.4 The `cancel-in-progress` Setting
  - 2.4.1 Behavior when `cancel-in-progress` is true
  - 2.4.2 Behavior when `cancel-in-progress` is false
  - 2.4.3 Trade-offs between the two settings
- 2.5 Best Practices for Group Naming
  - 2.5.1 Unique group names per workflow to prevent cross-workflow cancellation
  - 2.5.2 Including workflow name in the group key
- 2.6 When NOT to Cancel In-Progress Runs
  - 2.6.1 Release and deployment workflows
  - 2.6.2 Scheduled scans and audits
  - 2.6.3 Workflows that produce artifacts consumed by other systems
- 2.7 Real-World Savings Example
  - 2.7.1 Scenario with rapid successive pushes
  - 2.7.2 Minute savings calculation

---

## 2.1 Understanding Concurrency Groups

### 2.1.1 What Is a Concurrency Group

A concurrency group is a named queue in GitHub Actions. When a new workflow run
joins a group that already has a running or pending member, GitHub Actions can
either queue the new run (waiting for the current one to finish) or cancel the
in-progress run and start the new one.

You define a concurrency group by adding a `concurrency` key at the workflow
level or at the individual job level:

```yaml
concurrency:
  group: my-group-name
  cancel-in-progress: true
```

### 2.1.2 Why Concurrency Groups Save CI Minutes and Reduce Queue Congestion

Without concurrency groups, every push to a pull request triggers a full CI run.
If a developer pushes 5 commits in 10 minutes, all 5 runs execute in parallel
(or sequentially if runners are limited). Only the result of the last run matters
because it reflects the latest code state.

Concurrency groups with `cancel-in-progress: true` cancel the older, now-obsolete
runs as soon as a newer push arrives. This frees up runner capacity and avoids
paying for CI minutes on code that has already been superseded.

---

## 2.2 PR-Based Grouping Pattern

### 2.2.1 Group Key Expression for Pull Request Workflows

For workflows triggered by pull request events, the group key should be unique
per pull request. Use the pull request number:

```yaml
concurrency:
  group: ci-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```

This ensures that pushes to PR number 42 cancel previous runs for PR 42, but
do not affect runs for PR 43 or any other pull request.

### 2.2.2 Fallback to `github.ref` for Non-PR Triggers

If the same workflow also triggers on `push` events (not associated with a PR),
`github.event.pull_request.number` will be empty. Use a fallback:

```yaml
concurrency:
  group: ci-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

For a push to the `main` branch, the group key becomes `ci-refs/heads/main`.
For a push to PR 42, the group key becomes `ci-42`.

### 2.2.3 Complete YAML Example for PR-Based Grouping

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          pip install -e ".[test]"
          pytest tests/
```

When a developer pushes commit A to PR 42, CI starts. If the developer pushes
commit B to the same PR before the first run finishes, GitHub Actions cancels
the run for commit A and starts a new run for commit B.

---

## 2.3 Branch-Based Grouping for Push Workflows

### 2.3.1 Group Key Expression Using `github.ref`

For workflows that only trigger on `push` events (no pull request context),
use the branch reference directly:

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false
```

This groups all pushes to the same branch together. A push to `main` gets
group key `deploy-refs/heads/main`. A push to `feature/auth` gets group key
`deploy-refs/heads/feature/auth`.

### 2.3.2 Complete YAML Example for Push-Triggered Workflows

```yaml
name: Build and Test on Push

on:
  push:
    branches: [main, develop]

concurrency:
  group: build-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build project
        run: make build
      - name: Run tests
        run: make test
```

---

## 2.4 The `cancel-in-progress` Setting

### 2.4.1 Behavior When `cancel-in-progress` Is True

When a new run joins a concurrency group and `cancel-in-progress` is true:
1. Any currently running workflow run in that group is immediately cancelled
2. Any pending (queued but not started) runs in that group are also cancelled
3. The new run starts immediately (subject to runner availability)

Cancelled runs show status `cancelled` in the GitHub Actions UI.

### 2.4.2 Behavior When `cancel-in-progress` Is False

When `cancel-in-progress` is false (the default):
1. The currently running workflow run continues to completion
2. The new run is queued and waits
3. Once the current run finishes, the next queued run starts
4. If multiple runs are queued, only the most recent one runs; others are dropped

### 2.4.3 Trade-Offs Between the Two Settings

| Setting | Advantage | Disadvantage |
|---------|-----------|--------------|
| `true` | Saves CI minutes, faster feedback on latest code | Intermediate results are lost |
| `false` | Every run completes, no lost results | Wastes CI minutes on outdated code |

**Recommended**: Use `cancel-in-progress: true` for CI/test workflows where only
the latest code matters. Use `cancel-in-progress: false` for deployment workflows
where interrupting a half-finished deployment could leave the system in a broken state.

---

## 2.5 Best Practices for Group Naming

### 2.5.1 Unique Group Names per Workflow to Prevent Cross-Workflow Cancellation

If two different workflows use the same concurrency group name, they will cancel
each other. A push that triggers both a `CI` workflow and a `Lint` workflow with
the same group key will cause one to cancel the other.

Always include the workflow name (or a unique prefix) in the group key:

```yaml
# In ci.yml
concurrency:
  group: ci-${{ github.event.pull_request.number || github.ref }}

# In lint.yml
concurrency:
  group: lint-${{ github.event.pull_request.number || github.ref }}
```

### 2.5.2 Including Workflow Name in the Group Key

A reliable pattern is to use `github.workflow` which resolves to the `name:` field
of the workflow:

```yaml
name: CI

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

This automatically creates unique group keys per workflow without manual naming.

---

## 2.6 When NOT to Cancel In-Progress Runs

### 2.6.1 Release and Deployment Workflows

Deployment workflows that modify live infrastructure should never be cancelled
mid-execution. A cancelled deployment may leave resources in a partially configured
state (for example, database migrations applied but application code not updated).

```yaml
name: Deploy to Production

on:
  push:
    tags: ["v*"]

concurrency:
  group: deploy-production
  cancel-in-progress: false   # NEVER cancel deployments
```

### 2.6.2 Scheduled Scans and Audits

Security scans, dependency audits, and compliance checks should run to completion
even if a newer scan is triggered. Partial scan results are unreliable:

```yaml
name: Weekly Security Scan

on:
  schedule:
    - cron: "0 0 * * 1"

concurrency:
  group: security-scan
  cancel-in-progress: false
```

### 2.6.3 Workflows That Produce Artifacts Consumed by Other Systems

If a workflow uploads build artifacts, generates reports, or pushes container
images that downstream systems depend on, cancelling it mid-execution can leave
the downstream system referencing non-existent or incomplete artifacts.

---

## 2.7 Real-World Savings Example

### 2.7.1 Scenario with Rapid Successive Pushes

A developer is working on a feature branch with an open pull request. They push
5 commits in 10 minutes while iterating on a fix:

| Time | Event | Without Concurrency | With Concurrency (`cancel-in-progress: true`) |
|------|-------|--------------------|-------------------------------------------------|
| 0:00 | Push commit 1 | Run 1 starts (8 min) | Run 1 starts |
| 0:02 | Push commit 2 | Run 2 starts (8 min) | Run 1 cancelled, Run 2 starts |
| 0:04 | Push commit 3 | Run 3 starts (8 min) | Run 2 cancelled, Run 3 starts |
| 0:06 | Push commit 4 | Run 4 starts (8 min) | Run 3 cancelled, Run 4 starts |
| 0:08 | Push commit 5 | Run 5 starts (8 min) | Run 4 cancelled, Run 5 starts |

### 2.7.2 Minute Savings Calculation

Without concurrency groups:
- 5 runs, each using 8 minutes = 40 CI minutes consumed

With concurrency groups and cancel-in-progress:
- Runs 1-4 cancelled after approximately 2 minutes each = 8 minutes consumed
- Run 5 completes fully = 8 minutes consumed
- Total: approximately 16 CI minutes consumed

**Savings**: approximately 24 CI minutes per burst of 5 pushes. Over a team of
10 developers each doing this twice per day, that is 480 CI minutes saved daily.
