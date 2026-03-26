---
name: amia-github-pr-context
description: Use when retrieving PR context including metadata, diff, and changed files for code review planning. Trigger with /review-pr [PR_NUMBER].
license: Apache-2.0
compatibility: Requires AI Maestro installed.
metadata:
  version: 1.0.0
  author: Emasoft
  category: github
  tags: "pull-request, code-review, diff-analysis, github-api"
agent: api-coordinator
context: fork
user-invocable: false
---

# GitHub PR Context Skill

## Overview

Retrieves comprehensive GitHub Pull Request context (metadata, changed files, diffs) for code review planning and task delegation.

## Prerequisites

- **GitHub CLI (gh)** installed and authenticated (`gh auth status`)
- **Python 3.8+** available in PATH
- **Read access** to the target repository

## Instructions

1. **Verify prerequisites**: run `gh auth status` and `python3 --version`
2. **Choose the right script** based on what you need:
   - Full PR overview → `amia_get_pr_context.py`
   - Changed files list → `amia_get_pr_files.py`
   - Code diff → `amia_get_pr_diff.py`
3. **Run with required params**: always pass `--pr NUMBER`, optionally `--repo OWNER/REPO`
4. **For diffs**: add `--stat` for summary or `--files f1.py f2.py` for specific files
5. **Parse output**: pipe JSON to `jq`; check exit codes (0=ok, 1=bad params, 2=not found, 3=API error, 4=not authed)

### Checklist

Copy this checklist and track your progress:

- [ ] GitHub CLI authenticated
- [ ] Python 3.8+ available
- [ ] Read access to target repo confirmed
- [ ] Correct script selected for the task
- [ ] `--pr NUMBER` parameter provided
- [ ] Output parsed (JSON or diff)
- [ ] Exit codes checked

## Output

| Script | Output | Key Fields |
|--------|--------|------------|
| `amia_get_pr_context.py` | JSON | `number`, `title`, `state`, `author`, `mergeable`, `files[]`, `labels[]`, `reviewers[]` |
| `amia_get_pr_files.py` | JSON array | `filename`, `status`, `additions`, `deletions`, `patch` (optional) |
| `amia_get_pr_diff.py` | Diff text or JSON stats | Diff hunks or `files_changed`, `insertions`, `deletions` |

> **Output discipline:** All scripts support `--output-file <path>`.

## Reference Documents

**PR Analysis:**

- [pr-metadata](references/pr-metadata.md) — PR metadata JSON structure and field extraction
- [diff-analysis](references/diff-analysis.md) — Understanding and analyzing PR diffs

**Operations:**

- [op-get-pr-context](references/op-get-pr-context.md) — Full PR context retrieval operation
- [op-get-pr-files](references/op-get-pr-files.md) — Changed files listing operation
- [op-get-pr-diff](references/op-get-pr-diff.md) — Diff retrieval operation
- [op-analyze-pr-complexity](references/op-analyze-pr-complexity.md) — PR complexity analysis operation

**Extended Guide:**

See [detailed-guide](references/detailed-guide.md) for full reference:
  - When to Use This Skill
  - Decision Tree: Which Script to Use
  - Exit Codes
  - Error Handling
  - Integration with Integrator Agent
  - Detailed Examples

## Error Handling

If a script fails, check the exit code and stderr output. Common issues:

- **Exit 1**: Invalid parameters or missing arguments
- **Exit 2-4**: GitHub API errors (auth, not found, rate limit)

See the detailed guide above for detailed error scenarios.

## Resources

Full reference: [detailed-guide](references/detailed-guide.md):
  - When to Use This Skill
  - Decision Tree: Which Script to Use
  - Exit Codes
  - Error Handling
  - Integration with Integrator Agent
  - Detailed Examples
    - Get Full PR Context
    - List Changed Files
    - Get Diff
    - Extracting Specific Information

## Examples

### Get PR context and extract files

```bash
python3 amia_get_pr_context.py --pr 123
python3 amia_get_pr_context.py --pr 456 --repo owner/repo-name
python3 amia_get_pr_diff.py --pr 123 --stat
```
