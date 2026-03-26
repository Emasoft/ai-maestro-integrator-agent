# Handoff Documents

## Table of Contents

- [When to Create Handoff Documents](#when-to-create-handoff-documents)
- [Handoff Document Format](#handoff-document-format)
- [Handoff Checklist](#handoff-checklist)
- [Handoff File Locations](#handoff-file-locations)
- [Cross-Agent Handoff](#cross-agent-handoff)
- [Reading Handoffs (Next Session)](#reading-handoffs-next-session)
- [Archiving Completed Handoffs](#archiving-completed-handoffs)

## When to Create Handoff Documents

Create handoff documents in these situations:

| Situation | Handoff Type | File |
|-----------|--------------|------|
| Session ending mid-review | Current work state | `current.md` |
| Integration work incomplete | Integration handoff | `current.md` |
| Context compaction approaching | Preemptive handoff | `current.md` |
| Delegating to another agent | Cross-agent handoff | `current.md` + issue comment |

**DO NOT create handoff if:**

- Work is 100% complete
- All state is already in PR/issue comments
- No continuation needed

## Handoff Document Format

All handoff documents follow this template:

```markdown
# [Handoff Title]

**Last Updated**: [ISO 8601 timestamp]
**Session**: [Session ID or agent name]
**Created By**: AMIA [agent role]

## Current Task

[One-line description of what you're working on]

## Progress

- [x] Completed action 1
- [x] Completed action 2
- [ ] In progress: action 3 (50% done)
- [ ] Pending: action 4
- [ ] Pending: action 5

## Context

[Critical information needed to continue work]

### Key Decisions Made

- Decision 1 and rationale
- Decision 2 and rationale

### Patterns Observed

- Pattern 1 (observed in file X)
- Pattern 2 (observed in PR Y)

## Blockers

[List any blockers with workarounds if available]

## Next Steps

1. [Most urgent action]
2. [Second action]
3. [Third action]

## Links

- PR: #[number]
- Issue: #[number]
- Workflow run: [URL]
- Related docs: [URLs]

## Notes

[Any additional context or warnings]
```

## Handoff Checklist

Before ending session, verify:

- [ ] All incomplete work documented in `current.md`
- [ ] Blockers clearly stated
- [ ] Next steps prioritized (1, 2, 3...)
- [ ] Links to all relevant PRs/issues/runs included
- [ ] File written and readable
- [ ] If urgent, issue comment posted with handoff link

## Handoff File Locations

| File | Purpose | Retention |
|------|---------|-----------|
| `current.md` | Active work state | 30 days after completion |
| `patterns-learned.md` | Accumulated patterns | Indefinite |
| `release-history.md` | Release log | 1 year |
| `ci-states.md` | CI/CD states | Until resolved |

**Base Path**: `$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/`

## Cross-Agent Handoff

When handing off to another agent (e.g., Orchestrator, Architect):

1. Write detailed `current.md` handoff
2. Post comment on related issue:

   ```markdown
   @[agent-name] - AMIA handoff available

   **Task**: [One-line task description]
   **Status**: [Progress percentage]
   **Handoff**: `thoughts/shared/handoffs/amia-integration/current.md`
   **Blockers**: [List blockers]

   Please continue from where I left off. All context is in the handoff document.
   ```

3. If using AI Maestro messaging, send a message using the `agent-messaging` skill with:
   - **Recipient**: `target-agent-session`
   - **Subject**: `AMIA Integration Handoff`
   - **Priority**: `high`
   - **Content**: `{"type": "handoff", "message": "Integration work requires continuation. Handoff at thoughts/shared/handoffs/amia-integration/current.md"}`
   - **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

## Reading Handoffs (Next Session)

When you receive a handoff:

1. Load handoff document:

   ```bash
   cat "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md"
   ```

2. Verify freshness:

   ```bash
   stat -f "%Sm" "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md"
   ```

3. Check if links still valid:

   ```bash
   # Verify PR still open
   gh pr view <PR_NUMBER> --json state -q .state
   ```

4. Continue from "Next Steps" section

5. Update handoff as you make progress

## Archiving Completed Handoffs

When work is complete, archive the handoff:

```bash
# Move to archive subdirectory
mkdir -p "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/archive"
mv "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/current.md" \
   "$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration/archive/$(date +%Y-%m-%d)-[task-name].md"
```

**Retention**: Archive files are kept for 90 days, then deleted.
