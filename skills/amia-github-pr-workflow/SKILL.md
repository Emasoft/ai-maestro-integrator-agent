---
name: amia-github-pr-workflow
description: Use when coordinating PR review work as orchestrator. Defines delegation rules, verification, and completion criteria. Includes AI Maestro AMP project scripts for repo management, PR review, and task reporting. Trigger with /start-pr-review [PR_NUMBER].
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: 1.0.0
  author: Emasoft
  category: workflow
  tags: "pr-review, orchestration, delegation, verification, github"
agent: api-coordinator
context: fork
user-invocable: false
---

# Orchestrator PR Workflow Skill

## Overview

Orchestrator workflow for delegating PR reviews to subagents, verifying completion, and reporting to user.

## Prerequisites

- GitHub CLI (`gh`) authenticated
- Python 3.8+ and AI Maestro configured
- Subagent spawning capability

## Instructions

1. **Poll** -- Run `amia_orchestrator_pr_poll.py` to get open PRs
2. **Classify** -- Human PR = escalate; AI/bot PR = delegate directly
3. **Delegate** -- Spawn subagent for review/changes (never do work yourself)
4. **Monitor** -- Poll progress via background tasks (never block)
5. **Verify** -- Run `amia_verify_pr_completion.py` before reporting

### Checklist

Copy this checklist and track your progress:

- [ ] Poll PRs using `amia_orchestrator_pr_poll.py`
- [ ] Classify author type and work needed
- [ ] Delegate to subagent
- [ ] Monitor and verify using `amia_verify_pr_completion.py`
- [ ] Report to user, await merge decision
- [ ] Handle failures by delegating fixes

### Critical Rules

- Never block, write code, or merge without user approval
- Always verify before reporting status
- Escalate human PRs to user

## Output

| Output Type | Format | Description |
|---|---|---|
| Subagent Delegation | Task spawn | Spawned subagent with PR review/fix instructions |
| Status Report | Text/JSON | Current PR status and action recommendations |
| Verification Result | JSON | Pass/fail status for all completion criteria |
| User Notification | Text | Human-readable summary of PR readiness |

> **Output discipline:** All scripts support `--output-file <path>`. Use it to minimize token consumption.

## AI Maestro Project Scripts — PR Lifecycle

The following AMP project scripts (from AI Maestro `scripts/` directory, installed to `~/.local/bin/`) provide end-to-end PR lifecycle automation.

### Full PR Review Workflow

When the Orchestrator assigns a PR review task, follow this sequence:

1. **Receive PR notification** from Orchestrator (via AMP message or task assignment).
2. **Clone the repo** if not already local:
   ```bash
   amp-clone-repo.sh <repo-url>
   # or with a custom local name:
   amp-clone-repo.sh <repo-url> <local-name>
   ```
3. **Fetch the PR branch** for local review:
   ```bash
   # Target repo must be inside $AGENT_DIR/repos/<repo-name>
   git -C "$AGENT_DIR/repos/<repo-name>" fetch origin pull/<N>/head:pr-<N>
   git -C "$AGENT_DIR/repos/<repo-name>" checkout pr-<N>
   ```
4. **Review code changes** — read diffs, check patterns, verify against specs.
5. **Run tests** on the PR branch to confirm nothing is broken.
6. **Submit the review** via GitHub CLI:
   ```bash
   # All gh commands MUST specify --repo since the integrator works across multiple repos
   # Approve
   gh pr review <N> --repo "$OWNER/$REPO" --approve --body "LGTM — tests pass, code reviewed."
   # Or request changes
   gh pr review <N> --repo "$OWNER/$REPO" --request-changes --body "See inline comments for required fixes."
   ```
7. **Merge if approved** (only when authorized by the team governance rules):
   ```bash
   gh pr merge <N> --repo "$OWNER/$REPO" --squash
   ```
8. **Report completion** to the Orchestrator:
   ```bash
   amp-task-done.sh "PR #<N> merged in <repo>"
   ```

If blocked at any step, report immediately:
```bash
amp-task-blocked.sh "PR #<N>: tests fail on pr-<N> branch — see log"
```

### Repo & Branch Management Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `amp-clone-repo.sh` | Clone a repo to the agent's work directory | `amp-clone-repo.sh <url> [<localName>]` |
| `amp-create-repo.sh` | Create a new GitHub repo (optionally register with team) | `amp-create-repo.sh <name> [--org <org>] [--private] [--description "..."] [--team <team-id>]` |
| `amp-create-branch.sh` | Create and push a new branch | `amp-create-branch.sh <repo-path> <branch-name>` |
| `amp-submit-pr.sh` | Push branch and create a pull request | `amp-submit-pr.sh <repo-path> <title> [--body "..."] [--base main]` |
| `amp-list-local-repos.sh` | List git repos in the agent's work directory (JSON output) | `amp-list-local-repos.sh` |
| `amp-project-info.sh` | Get project/repo metadata | `amp-project-info.sh` |
| `amp-project-repos.sh` | List team project repos | `amp-project-repos.sh` |

### Task Reporting Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `amp-task-done.sh` | Report task completion to the Orchestrator | `amp-task-done.sh "<message>"` |
| `amp-task-blocked.sh` | Report a blocking issue (high priority) | `amp-task-blocked.sh "<reason>"` |

### When to Create a New Repo

If the PR review workflow requires setting up a new repository (e.g., extracting a module, creating a fork for patches):

```bash
amp-create-repo.sh my-new-repo --org myorg --private --description "Extracted auth module"
# Then clone it locally:
amp-clone-repo.sh https://github.com/myorg/my-new-repo.git
```

## Reference Documents

See `references/` directory for all reference documents. Full index in `references/detailed-guide.md`.

## Error Handling

Script failures return non-zero exit codes. See `references/detailed-guide.md` for details.

## Examples

```bash
python scripts/amia_orchestrator_pr_poll.py --repo owner/repo
python scripts/amia_verify_pr_completion.py --repo owner/repo --pr 123
# Output: {"complete": true, "recommendation": "ready_to_merge"}
```

## Resources

See `references/detailed-guide.md` for decision tree, scripts, and extended examples.
