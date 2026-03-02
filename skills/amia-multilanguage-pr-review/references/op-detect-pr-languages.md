---
name: op-detect-pr-languages
description: Detect all programming languages affected by a pull request
procedure: proc-evaluate-pr
workflow-instruction: Step 21 - PR Evaluation
---

# Operation: Detect PR Languages


## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Output](#output)
- [Output Structure](#output-structure)
- [Procedure](#procedure)
- [Command](#command)
- [Example](#example)
- [Detection Methods](#detection-methods)
- [Supported Languages](#supported-languages)
- [Handling Special Cases](#handling-special-cases)
- [Next Steps After Detection](#next-steps-after-detection)
- [Error Handling](#error-handling)
- [Related Operations](#related-operations)

## Purpose

Identify all programming languages present in the files changed by a pull request. This determines which language-specific review patterns and linters to apply.

## When to Use

- At the start of any multilanguage PR review
- When determining which linters to run
- When routing review tasks to appropriate reviewers
- When planning review strategy

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+ for running detection script
- PR number and repository identifier

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--repo` | String | Yes* | Repository in owner/repo format |
| `--pr` | Integer | Yes* | Pull request number |
| `--diff-file` | Path | Alt | Local diff file to analyze |

*Either --repo/--pr OR --diff-file is required

## Output

| Field | Type | Description |
|-------|------|-------------|
| `languages` | Object | Map of language to file statistics |
| `primary_language` | String | Language with most changes |
| `file_count` | Integer | Total files changed |
| `lines_changed` | Integer | Total lines changed |

## Output Structure

```json
{
  "languages": {
    "python": {
      "files": 12,
      "lines_changed": 450,
      "percentage": 56.25
    },
    "typescript": {
      "files": 5,
      "lines_changed": 200,
      "percentage": 25.0
    },
    "bash": {
      "files": 2,
      "lines_changed": 50,
      "percentage": 6.25
    }
  },
  "primary_language": "python",
  "total_files": 19,
  "total_lines_changed": 700
}
```

## Procedure

1. Run the language detection script with PR details
2. Parse the JSON output
3. Note all detected languages
4. Identify the primary language (most changes)
5. Use results to plan review approach

## Command

```bash
# Detect languages in a GitHub PR
python scripts/amia_detect_pr_languages.py --repo <OWNER/REPO> --pr <NUMBER>

# Detect languages in a local diff file
python scripts/amia_detect_pr_languages.py --diff-file changes.diff
```

## Example

```bash
# Detect languages in PR #456
python scripts/amia_detect_pr_languages.py --repo myorg/myrepo --pr 456

# Output:
# {
#   "languages": {
#     "python": {"files": 12, "lines_changed": 450},
#     "typescript": {"files": 5, "lines_changed": 200},
#     "bash": {"files": 2, "lines_changed": 50}
#   },
#   "primary_language": "python"
# }
```

## Detection Methods

The script uses multiple methods to detect languages:

1. **File extension** - `.py` -> Python, `.ts` -> TypeScript
2. **Shebang line** - `#!/usr/bin/env python3` -> Python
3. **Linguist hints** - `.gitattributes` overrides
4. **Content analysis** - For ambiguous files

## Supported Languages

| Language | Extensions | Shebang |
|----------|------------|---------|
| Python | .py, .pyi | `#!/usr/bin/env python` |
| JavaScript | .js, .jsx, .mjs | `#!/usr/bin/env node` |
| TypeScript | .ts, .tsx | N/A |
| Rust | .rs | N/A |
| Go | .go | N/A |
| Bash | .sh, .bash | `#!/bin/bash`, `#!/bin/sh` |
| Shell | .zsh, .fish | Various |

## Handling Special Cases

| Case | Handling |
|------|----------|
| Mixed-language files | Reported under primary language |
| Generated files | Check .gitattributes for `linguist-generated` |
| Vendored code | Check .gitattributes for `linguist-vendored` |
| Unknown extension | Content analysis fallback |

## Next Steps After Detection

For each detected language:
1. Read the corresponding review patterns document
2. Run `op-get-language-linters` to get appropriate linters
3. Execute language-specific review checks

## Error Handling

| Scenario | Action |
|----------|--------|
| No files changed | Empty languages object returned |
| Unknown file type | Logged but not included in languages |
| API error | Retry or use local diff file |

## Related Operations

- [op-get-language-linters.md](op-get-language-linters.md) - Get linters for detected languages
- [op-run-multilang-linters.md](op-run-multilang-linters.md) - Execute linters
- [op-compile-multilang-review.md](op-compile-multilang-review.md) - Compile final review
