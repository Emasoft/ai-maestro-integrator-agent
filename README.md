# Integrator Agent (amia-)

**Version**: 1.1.8

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
| `amia-integrator-main-agent.md` | Main integrator agent |
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
| `amia-github-integration` | GitHub API integration |
| `amia-github-pr-workflow` | PR workflow patterns |
| `amia-github-pr-checks` | PR check patterns |
| `amia-github-pr-merge` | PR merge strategies |
| `amia-github-pr-context` | PR context management |
| `amia-github-issue-operations` | Issue CRUD operations |
| `amia-kanban-orchestration` | Kanban board patterns |
| `amia-github-projects-sync` | Projects sync |
| `amia-github-thread-management` | Thread management |
| `amia-code-review-patterns` | Code review patterns |
| `amia-multilanguage-pr-review` | Multi-language reviews |
| `amia-tdd-enforcement` | TDD enforcement |
| `amia-ci-failure-patterns` | CI failure patterns |
| `amia-git-worktree-operations` | Worktree operations |
| `amia-integration-protocols` | Shared utilities |
| `amia-quality-gates` | Quality gate pipelines and enforcement |
| `amia-release-management` | Release verification and changelog |
| `amia-ai-pr-review-methodology` | AI-assisted PR review methodology |
| `amia-label-taxonomy` | Issue/PR label taxonomy and standards |
| `amia-session-memory` | Session state persistence |

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
claude --agent amia-integrator-main-agent --plugin-dir ./ai-maestro-integrator-agent
```

> **Note:** Marketplace distribution is TBD. For now, use `--plugin-dir` with a local clone.

## Validation

```bash
cd ai-maestro-integrator-agent
uv run python scripts/validate_plugin.py . --verbose
```
