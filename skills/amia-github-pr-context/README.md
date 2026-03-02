# GitHub PR Context Skill

Retrieve and analyze GitHub Pull Request context including metadata, diff, and changed files for informed code review and task planning.

## When to Use

- **Before code review**: Get full PR context (metadata, files, status)
- **Task delegation**: Identify changed files to assign subagents appropriately
- **Merge readiness**: Check mergeable status, conflicts, and CI state

## Quick Reference

| Script | Purpose | Example |
|--------|---------|---------|
| `amia_get_pr_context.py` | Full metadata & status | `python3 amia_get_pr_context.py --pr 123` |
| `amia_get_pr_files.py` | List changed files | `python3 amia_get_pr_files.py --pr 123` |
| `amia_get_pr_diff.py` | Get code diff | `python3 amia_get_pr_diff.py --pr 123 --stat` |

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Python 3.8+
- Read access to the repository

## Directory Contents

```
github-pr-context/
├── SKILL.md              # Full skill documentation
├── README.md             # This file
├── scripts/              # Python scripts for PR operations
│   ├── amia_get_pr_context.py
│   ├── amia_get_pr_files.py
│   └── amia_get_pr_diff.py
└── references/           # Detailed reference documentation
    ├── pr-metadata.md    # PR metadata field reference
    └── diff-analysis.md  # Diff interpretation guide
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid parameters |
| 2 | Resource not found |
| 3 | API error |
| 4 | Not authenticated |

See [SKILL.md](SKILL.md) for complete documentation.
