---
name: amia-github-pr-context
description: Use when retrieving PR context including metadata, diff, and changed files for code review planning. Trigger with /review-pr [PR_NUMBER]. Loaded by ai-maestro-integrator-agent-main-agent.
license: MIT
compatibility: Requires AI Maestro installed.
tags: "pull-request, code-review, diff-analysis, github-api"
metadata:
  version: 1.0.0
  author: Emasoft
  category: github
agent: amia-api-coordinator
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
  - 1. PR Metadata JSON Structure
    - 1.1 Core identification fields (number, title, state)
    - 1.2 Author and assignee information
    - 1.3 Branch and merge information
    - 1.4 Labels, milestones, and projects
    - 1.5 Review and approval status
  - 1. Extracting Specific Fields
    - 2.1 Getting PR title and description
    - 2.2 Finding the source and target branches
    - 2.3 Checking mergeable status and conflicts
    - 2.4 Listing reviewers and their decisions
  - 1. Common Metadata Queries
    - 3.1 Is this PR ready to merge?
    - 3.2 Who needs to approve this PR?
    - 3.3 What labels are applied?
- [diff-analysis](references/diff-analysis.md) — Understanding and analyzing PR diffs
  - 1. Understanding Diff Output
    - 1.1 Unified diff format explanation
    - 1.2 File headers and hunks
    - 1.3 Addition, deletion, and context lines
  - 1. File-Level Analysis
    - 2.1 Identifying file types by extension
    - 2.2 Detecting rename and copy operations
    - 2.3 Binary file changes
  - 1. Change Statistics
    - 3.1 Lines added vs deleted
    - 3.2 Files by change type (added, modified, deleted)
    - 3.3 Estimating review complexity
  - 1. Filtering and Focusing
    - 4.1 Filtering by file path patterns
    - 4.2 Ignoring generated files
    - 4.3 Focusing on specific directories

**Operations:**

- [op-get-pr-context](references/op-get-pr-context.md) — Full PR context retrieval operation
  - [Purpose](#purpose)
  - [When to Use](#when-to-use)
  - [Prerequisites](#prerequisites)
  - [Input](#input)
  - [Output](#output)
  - [Steps](#steps)
    - [Step 1: Run the Context Script](#step-1-run-the-context-script)
    - [Step 2: Parse the JSON Output](#step-2-parse-the-json-output)
    - [Step 3: Use Context for Review Planning](#step-3-use-context-for-review-planning)
  - [Command Variants](#command-variants)
    - [Basic Context](#basic-context)
    - [Specific Repository](#specific-repository)
  - [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
  - [Context Fields Explained](#context-fields-explained)
    - [Mergeable Status](#mergeable-status)
    - [Review Decision](#review-decision)
    - [File Status](#file-status)
  - [Example: Review Planning](#example-review-planning)
  - [Extracting Specific Information](#extracting-specific-information)
    - [Get Just File Paths](#get-just-file-paths)
    - [Get Mergeable Status Only](#get-mergeable-status-only)
    - [Get Author](#get-author)
  - [Exit Codes](#exit-codes)
  - [Error Handling](#error-handling)
  - [Related Operations](#related-operations)
- [op-get-pr-files](references/op-get-pr-files.md) — Changed files listing operation
  - [Purpose](#purpose)
  - [When to Use](#when-to-use)
  - [Prerequisites](#prerequisites)
  - [Input](#input)
  - [Output](#output)
  - [Steps](#steps)
    - [Step 1: Run the Files Script](#step-1-run-the-files-script)
    - [Step 2: Parse the Output](#step-2-parse-the-output)
    - [Step 3: Analyze File Distribution](#step-3-analyze-file-distribution)
  - [Command Variants](#command-variants)
    - [Basic File List](#basic-file-list)
    - [Include Patch Content](#include-patch-content)
    - [Specific Repository](#specific-repository)
  - [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
  - [File Status Values](#file-status-values)
  - [Analyzing File Distribution](#analyzing-file-distribution)
    - [By Directory](#by-directory)
    - [By File Type](#by-file-type)
    - [By Change Magnitude](#by-change-magnitude)
  - [Example: Review Delegation](#example-review-delegation)
  - [Example: With Patch Content](#example-with-patch-content)
  - [Large PRs (>100 files)](#large-prs-100-files)
  - [Exit Codes](#exit-codes)
  - [Error Handling](#error-handling)
  - [Related Operations](#related-operations)
- [op-get-pr-diff](references/op-get-pr-diff.md) — Diff retrieval operation
  - [Purpose](#purpose)
  - [When to Use](#when-to-use)
  - [Prerequisites](#prerequisites)
  - [Input](#input)
  - [Output](#output)
  - [Steps](#steps)
    - [Step 1: Run the Diff Script](#step-1-run-the-diff-script)
    - [Step 2: Review the Output](#step-2-review-the-output)
  - [Command Variants](#command-variants)
    - [Full Diff](#full-diff)
    - [Statistics Only](#statistics-only)
    - [Specific Files](#specific-files)
    - [Combine with Other Tools](#combine-with-other-tools)
  - [Alternative: Direct gh CLI](#alternative-direct-gh-cli)
  - [Understanding Unified Diff Format](#understanding-unified-diff-format)
    - [Hunk Header Explained](#hunk-header-explained)
  - [Filtering Diff Output](#filtering-diff-output)
    - [Find Added Lines](#find-added-lines)
    - [Find Removed Lines](#find-removed-lines)
    - [Find Files with Specific Changes](#find-files-with-specific-changes)
  - [Example: Security Review](#example-security-review)
  - [Example: Test Coverage Check](#example-test-coverage-check)
  - [Large Diffs](#large-diffs)
  - [Exit Codes](#exit-codes)
  - [Error Handling](#error-handling)
  - [Related Operations](#related-operations)
- [op-analyze-pr-complexity](references/op-analyze-pr-complexity.md) — PR complexity analysis operation
  - [Purpose](#purpose)
  - [When to Use](#when-to-use)
  - [Prerequisites](#prerequisites)
  - [Input](#input)
  - [Output](#output)
  - [Complexity Factors](#complexity-factors)
  - [Steps](#steps)
    - [Step 1: Gather Metrics](#step-1-gather-metrics)
    - [Step 2: Calculate Size Category](#step-2-calculate-size-category)
    - [Step 3: Identify Sensitive Files](#step-3-identify-sensitive-files)
    - [Step 4: Assess Module Spread](#step-4-assess-module-spread)
    - [Step 5: Check Test Coverage](#step-5-check-test-coverage)
    - [Step 6: Calculate Final Score](#step-6-calculate-final-score)
    - [Step 7: Generate Review Time Estimate](#step-7-generate-review-time-estimate)
    - [Step 8: Create Delegation Recommendation](#step-8-create-delegation-recommendation)
  - [Example: Complete Analysis](#example-complete-analysis)
  - [Complexity Score Guide](#complexity-score-guide)
  - [Error Handling](#error-handling)
  - [Related Operations](#related-operations)

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
