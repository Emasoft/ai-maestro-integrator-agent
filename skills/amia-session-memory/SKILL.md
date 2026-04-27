---
name: amia-session-memory
description: "Use when resuming sessions. Trigger with session resumption. Loaded by ai-maestro-integrator-agent-main-agent."
license: Apache-2.0
version: 1.0.0
compatibility: Requires AMIA role knowledge. Requires AI Maestro installed.
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
  - Table of Contents
  - Storage Locations
    - PR Comments
    - Issue Comments
    - Handoff Documents
  - Memory File Structure
  - Current State
  - Context
  - Next Steps
  - Data Persistence Patterns
    - Write-Through
    - Read-On-Demand
  - Retention Policy
- [memory-retrieval](references/memory-retrieval.md) — Triggers and retrieval commands
  - Table of Contents
  - State-Based Triggers
  - Retrieval Decision Tree
  - Memory Retrieval Commands
    - Load PR State
    - Load Handoff Documents
    - Verify Memory Freshness
  - Handling Missing Memory
  - Memory Freshness Checks
- [memory-updates](references/memory-updates.md) — Update triggers and commands
  - Table of Contents
  - State-Based Update Triggers
  - Update Decision Tree
  - Memory Update Commands
    - Update PR State Comment
  - AMIA Review - Round 2
    - Append to Patterns Learned
  - Pattern Name - YYYY-MM-DD
    - Update Release History
    - Update CI States
  - Latest Workflow Run
    - Write Handoff Document
  - Current Task
  - Progress
  - Blockers
  - Next Steps
  - Context
  - Links
  - Update Patterns
    - Write-Through (Immediate)
    - Append (Accumulate)
    - Overwrite (Latest State)
  - Verification
  - Error Handling
- [handoff-documents](references/handoff-documents.md) — Handoff format and checklist
  - Table of Contents
  - When to Create Handoff Documents
  - Handoff Document Format
  - Current Task
  - Progress
  - Context
    - Key Decisions Made
    - Patterns Observed
  - Blockers
  - Next Steps
  - Links
  - Notes
  - Handoff Checklist
  - Handoff File Locations
  - Cross-Agent Handoff
  - Reading Handoffs (Next Session)
  - Archiving Completed Handoffs
- [detailed-guide](references/detailed-guide.md) — Error handling, examples, troubleshooting

See `references/` directory for remaining documents.

## Error Handling

Non-zero exit codes on failure. See detailed guide in Resources.

## Resources

- [detailed-guide](references/detailed-guide.md) — Full reference
  - Error Handling
  - Examples
  - Memory Architecture
  - What to Remember
  - Memory Retrieval
  - Memory Updates
  - Handoff Documents
  - Integration with Other Skills
  - Troubleshooting
  - Quick Reference Commands
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
