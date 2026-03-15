# Integrator Agent (amia-)

**Version**: 1.2.0

## Overview

The Integrator Agent handles **quality gates, testing, merging, and release candidates**. It ensures code quality before integration into the main branch.

## Core Responsibilities

1. **Code Review**: Review PRs for quality and correctness
2. **Quality Gates**: Enforce TDD, tests, and standards
3. **Branch Protection**: Prevent direct pushes to protected branches
4. **Issue Closure Gates**: Verify requirements before closing issues
5. **GitHub Integration**: Manage PRs, issues, and projects

## Components

### Agents

| Agent | Description |
|-------|-------------|
| `ai-maestro-integrator-agent-main-agent.md` | Main integrator agent |
| `amia-api-coordinator.md` | Coordinates GitHub API operations |
| `amia-bug-investigator.md` | Investigates reported bugs |
| `amia-code-reviewer.md` | Reviews code for quality |
| `amia-committer.md` | Handles git commit operations |
| `amia-debug-specialist.md` | Debugs CI/CD and test failures |
| `amia-github-sync.md` | Syncs GitHub state |
| `amia-integration-verifier.md` | Verifies integration success |
| `amia-pr-evaluator.md` | Evaluates PR readiness |
| `amia-screenshot-analyzer.md` | Analyzes screenshots for visual regressions |
| `amia-test-engineer.md` | Manages test execution and coverage |

### Skills

| Skill | Description |
|-------|-------------|
| `amia-github-integration` | GitHub Projects integration, label setup, PR workflows |
| `amia-github-pr-workflow` | PR review orchestration with delegation and verification |
| `amia-github-pr-checks` | CI status monitoring and PR readiness verification |
| `amia-github-pr-merge` | PR merge strategies and auto-merge configuration |
| `amia-github-pr-context` | PR metadata, diff, and changed files retrieval |
| `amia-github-issue-operations` | Issue creation, labels, milestones, assignees, comments |
| `amia-kanban-orchestration` | GitHub Kanban board state and card management |
| `amia-github-projects-sync` | GitHub Projects V2 synchronization via GraphQL |
| `amia-github-thread-management` | PR review thread management and resolution |
| `amia-code-review-patterns` | Two-stage PR review with 8-dimension analysis |
| `amia-multilanguage-pr-review` | Multi-language PR review routing |
| `amia-tdd-enforcement` | TDD enforcement via RED-GREEN-REFACTOR |
| `amia-ci-failure-patterns` | CI/CD failure diagnosis and pattern matching |
| `amia-git-worktree-operations` | Parallel PR processing with git worktrees |
| `amia-integration-protocols` | Shared utilities and cross-skill protocols |
| `amia-quality-gates` | Pre-review, review, pre-merge, post-merge checkpoints |
| `amia-release-management` | Version bumping, changelogs, release coordination |
| `amia-ai-pr-review-methodology` | Evidence-based PR review (4 phases, 5 dimensions) |
| `amia-label-taxonomy` | GitHub label taxonomy for PR/issue management |
| `amia-session-memory` | Session state persistence for PR reviews |

### Hooks

| Hook | Event | Description |
|------|-------|-------------|
| `amia-branch-protection` | PreToolUse | Block pushes to main/master |
| `amia-issue-closure-gate` | PreToolUse | Verify before issue closure |
| `amia-stop-check` | Stop | Block exit until integration work is complete |

## Quality Gates

1. **Branch Protection**: No direct pushes to main/master
2. **Issue Closure Gate**: Requires:
   - Merged PR linked to issue
   - All checkboxes checked
   - Evidence of testing
   - TDD compliance

## Workflow

1. Receives completion signal from Orchestrator
2. Reviews code changes
3. Runs quality gates
4. Verifies tests pass
5. Creates/reviews PR
6. Merges when approved
7. Reports to Assistant Manager

## Prerequisites

- **Python 3.8+** (recommended: 3.12)
- **`gh` CLI** installed and authenticated (`gh auth login`)
- **`uv`** for running Python scripts (`pip install uv`)
- **AI Maestro** installed and running (for inter-agent messaging)

## Installation

Clone the plugin repo and load it with `--plugin-dir`:

```bash
git clone https://github.com/Emasoft/ai-maestro-integrator-agent.git
claude --plugin-dir ./ai-maestro-integrator-agent
```

Or start a session with the main agent directly:

```bash
claude --agent ai-maestro-integrator-agent-main-agent --plugin-dir ./ai-maestro-integrator-agent
```

> **Note:** Marketplace distribution is TBD. For now, use `--plugin-dir` with a local clone.

## Non-Standard Directories

| Directory | Purpose |
|-----------|---------|
| `shared/` | Shared Python modules (thresholds, constants) used by multiple plugin scripts across skills and hooks |
| `git-hooks/` | Git hook scripts (e.g., `pre-push`) for local repository protection; installed via `cp git-hooks/pre-push .git/hooks/pre-push` |

## Platform Requirements

All plugin scripts are written in Python for cross-platform compatibility (Linux, macOS, Windows).

## Skill Architecture

Skills use a **progressive discovery** pattern: each `SKILL.md` is a compact index (under 4000 chars) that agents read first, with detailed content in `references/*.md` files discovered on demand. All 60+ scripts support `--output-file <path>` to write full JSON to a file and print only a summary to stdout, minimizing token consumption.

## Validation

```bash
cd ai-maestro-integrator-agent
uv run --with pyyaml python scripts/validate_plugin.py . --verbose
```

Current status: **0 CRITICAL, 0 MAJOR, 0 MINOR, 0 NIT** issues.
