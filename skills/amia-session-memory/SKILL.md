---
name: amia-session-memory
description: "Session memory for PR reviews and integration work. Use when resuming reviews, tracking releases, or persisting context across sessions. Trigger with session resumption."
license: Apache-2.0
version: 1.0.0
compatibility: Requires familiarity with AMIA role responsibilities (code review, integration, releases). Designed for maintaining context across Claude Code session boundaries. Requires AI Maestro installed.
metadata:
  author: Emasoft
  version: 1.0.0
agent: amia-main
context: fork
user-invocable: false
---

# AMIA Session Memory Skill

## Overview

Persist and retrieve session context across session boundaries using PR comments, issue comments, and handoff documents.

## Prerequisites

- AMIA role understood (quality gates, reviews, merging, releases)
- `gh` CLI configured and authenticated
- `$CLAUDE_PROJECT_DIR` set and writable

## Instructions

1. **Detect triggers** — Check for PR numbers, GitHub URLs, or issue refs in user prompt
2. **Load memory** — PR-related: load PR comment state; integration: load handoff docs from `$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/`; release: load release history
3. **Verify freshness** — Compare timestamps in memory against actual GitHub state (PR status, CI runs, tags)
4. **Execute task** — Use loaded memory to inform decisions; update memory as work progresses
5. **Persist state** — Update PR comments with state markers; write handoff docs if work incomplete
6. **Verify writes** — Confirm PR comments posted and handoff files written

### Checklist

Copy this checklist and track your progress:

- [ ] Detect state-based triggers (PR review, integration, release)
- [ ] Load relevant memory (PR comments, handoff docs, release history)
- [ ] Verify memory freshness against GitHub state
- [ ] Execute task using loaded context
- [ ] Persist updated state (PR comments + handoff docs)
- [ ] Verify all writes succeeded

## Output

| Memory Type | Storage Location | Format |
|-------------|-----------------|--------|
| **PR Review State** | GitHub PR comment | Markdown with HTML state marker |
| **Integration Patterns** | Handoff document | Markdown with timestamped entries |
| **Release History** | Handoff document | Markdown table with release metadata |
| **CI/CD State** | Issue comment or handoff | Markdown with workflow run links |

> **Output discipline:** All scripts support `--output-file <path>`.

## Reference Documents

- [memory-architecture](references/memory-architecture.md) — Storage locations and persistence patterns
- [memory-retrieval](references/memory-retrieval.md) — Triggers and retrieval commands
- [memory-updates](references/memory-updates.md) — Update triggers and commands
- [handoff-documents](references/handoff-documents.md) — Handoff format and checklist
- [detailed-guide](references/detailed-guide.md) — Error handling, examples, troubleshooting

See `references/` directory for remaining documents.

## Error Handling

Non-zero exit codes on failure. See detailed guide in Resources.

## Resources

Full reference: [detailed-guide](references/detailed-guide.md):
  - Error Handling
    - Missing Memory
    - Stale Memory
    - Write Failures
  - Examples
    - Example 1: Resume PR Review
    - Example 2: Handoff Integration Work
    - Example 3: Log Release Decision
  - Memory Architecture
  - What to Remember
  - Memory Retrieval
  - Memory Updates
  - Handoff Documents
  - Integration with Other Skills
  - Troubleshooting
    - Memory Not Found
    - Stale Memory
    - Memory Conflicts
  - Quick Reference Commands
    - Load Memory Commands
    - Save Memory Commands
  - State Markers
  - Full Reference Document Listing

## Examples

```bash
# Resume a PR review from a previous session
gh pr view 42 --json comments --jq '.comments[] | select(.body | contains("AMIA-STATE"))' > /tmp/pr42-state.json
# Load the state marker and continue review from where you left off
# Save updated state when done
gh pr comment 42 --body "<!-- AMIA-STATE: {\"phase\": 3, \"dimensions_completed\": [1,2,3], \"timestamp\": \"2026-03-26T12:00:00Z\"} -->"
```

**Expected result:** The session state is loaded from the PR comment containing the `AMIA-STATE` marker. After completing remaining work, an updated state marker is posted so the next session can resume seamlessly.
