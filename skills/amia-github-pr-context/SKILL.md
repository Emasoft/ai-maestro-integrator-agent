---
name: amia-github-pr-context
description: Use when retrieving PR context including metadata, diff, and changed files for code review planning. Trigger with /review-pr [PR_NUMBER]. Loaded by ai-maestro-integrator-agent-main-agent.
license: Apache-2.0
compatibility: Requires AI Maestro installed.
tags: "pull-request, code-review, diff-analysis, github-api"
metadata:
  version: 1.0.0
  author: Emasoft
  category: github
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
  - Table of Contents
  - 1. PR Metadata JSON Structure
    - 1.1 Core Identification Fields
    - 1.2 Author and Assignee Information
    - 1.3 Branch and Merge Information
    - 1.4 Labels, Milestones, and Projects
    - 1.5 Review and Approval Status
  - 2. Extracting Specific Fields
    - 2.1 Getting PR Title and Description
  - Summary
  - Changes
  - Testing
    - 2.2 Finding the Source and Target Branches
    - 2.3 Checking Mergeable Status and Conflicts
    - 2.4 Listing Reviewers and Their Decisions
  - 3. Common Metadata Queries
    - 3.1 Is This PR Ready to Merge?
    - 3.2 Who Needs to Approve This PR?
    - 3.3 What Labels Are Applied?
- [diff-analysis](references/diff-analysis.md) — Understanding and analyzing PR diffs
  - Table of Contents
  - 1. Understanding Diff Output
    - 1.1 Unified Diff Format Explanation
    - 1.2 File Headers and Hunks
    - 1.3 Addition, Deletion, and Context Lines
  - 2. File-Level Analysis
    - 2.1 Identifying File Types by Extension
    - 2.2 Detecting Rename and Copy Operations
    - 2.3 Binary File Changes
  - 3. Change Statistics
    - 3.1 Lines Added vs Deleted
    - 3.2 Files by Change Type
    - 3.3 Estimating Review Complexity
  - 4. Filtering and Focusing
    - 4.1 Filtering by File Path Patterns
    - 4.2 Ignoring Generated Files
    - 4.3 Focusing on Specific Directories

**Operations:**

- [op-get-pr-context](references/op-get-pr-context.md) — Full PR context retrieval operation
  - Table of Contents
  - Purpose
  - When to Use
  - Prerequisites
  - Input
  - Output
  - Steps
    - Step 1: Run the Context Script
    - Step 2: Parse the JSON Output
    - Step 3: Use Context for Review Planning
  - Command Variants
    - Basic Context
    - Specific Repository
  - Alternative: Direct gh CLI
  - Context Fields Explained
    - Mergeable Status
    - Review Decision
    - File Status
  - Example: Review Planning
  - Extracting Specific Information
    - Get Just File Paths
    - Get Mergeable Status Only
    - Get Author
  - Exit Codes
  - Error Handling
  - Related Operations
- [op-get-pr-files](references/op-get-pr-files.md) — Changed files listing operation
  - Table of Contents
  - Purpose
  - When to Use
  - Prerequisites
  - Input
  - Output
  - Steps
    - Step 1: Run the Files Script
    - Step 2: Parse the Output
    - Step 3: Analyze File Distribution
  - Command Variants
    - Basic File List
    - Include Patch Content
    - Specific Repository
  - Alternative: Direct gh CLI
  - File Status Values
  - Analyzing File Distribution
    - By Directory
    - By File Type
    - By Change Magnitude
  - Example: Review Delegation
  - Example: With Patch Content
  - Large PRs (>100 files)
  - Exit Codes
  - Error Handling
  - Related Operations
- [op-get-pr-diff](references/op-get-pr-diff.md) — Diff retrieval operation
  - Table of Contents
  - Purpose
  - When to Use
  - Prerequisites
  - Input
  - Output
  - Steps
    - Step 1: Run the Diff Script
    - Step 2: Review the Output
  - Command Variants
    - Full Diff
    - Statistics Only
    - Specific Files
    - Combine with Other Tools
  - Alternative: Direct gh CLI
  - Understanding Unified Diff Format
    - Hunk Header Explained
  - Filtering Diff Output
    - Find Added Lines
    - Find Removed Lines
    - Find Files with Specific Changes
  - Example: Security Review
  - Example: Test Coverage Check
  - Large Diffs
  - Exit Codes
  - Error Handling
  - Related Operations
- [op-analyze-pr-complexity](references/op-analyze-pr-complexity.md) — PR complexity analysis operation
  - Table of Contents
  - Purpose
  - When to Use
  - Prerequisites
  - Input
  - Output
  - Complexity Factors
  - Steps
    - Step 1: Gather Metrics
    - Step 2: Calculate Size Category
    - Step 3: Identify Sensitive Files
    - Step 4: Assess Module Spread
    - Step 5: Check Test Coverage
    - Step 6: Calculate Final Score
    - Step 7: Generate Review Time Estimate
    - Step 8: Create Delegation Recommendation
  - Example: Complete Analysis
  - Complexity Score Guide
  - Error Handling
  - Related Operations

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
