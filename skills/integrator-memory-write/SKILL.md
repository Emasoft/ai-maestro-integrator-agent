---
name: integrator-memory-write
description: Capture a durable, reusable fact as a markdown memory note so a future session recalls it from the SYMPTOM. Use after solving a non-trivial integration/merge/CI bug (a bug-autopsy gotcha), learning a project constraint not derivable from code, a confirmed user preference about reviews/merges/releases, or any "we should remember this" moment — or when the user says "remember this", "save a memory", "capture this gotcha", "note that for next time". Writes a schema-valid note (name/description/metadata + body) with the description indexed by question/symptom vocabulary, and appends the MEMORY.md index line. The INTEGRATOR implementation of the AI-Maestro memory-write protocol (see rules/memory-protocol.md).
license: MIT
compatibility: Requires Python 3.10+ with PyYAML for the bundled note validator.
metadata:
  author: Emasoft
  version: 1.0.0
---

# Integrator memory-write

## Overview

Capture one durable fact as a memory note so a future session — which will have
the SYMPTOM, not the answer — can recall it. The load-bearing decision is the
`description`: it MUST carry the words the problem will present with (the
user's words, the error, the symptom), because recall ranks on `description`
(+ `title` + `tags`). Put the symptom in `description`; put the answer in the
body.

Only capture what is NON-OBVIOUS and reusable: gotchas, constraints not in the
code, confirmed preferences, hard-won debugging facts. Do NOT capture what the
repo already records (code structure, git history, CLAUDE.md) or what only
matters to the current conversation.

## Instructions

1. Resolve the memory dir (same as recall):

   ```bash
   MEMDIR="$HOME/.claude/projects/$(pwd | sed 's#/#-#g')/memory"
   [ -d "$MEMDIR" ] || MEMDIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/memory"
   mkdir -p "$MEMDIR"
   ```

2. Choose `type` ∈ `user | feedback | project | reference` and a kebab slug.

3. Check for an existing note that already covers this (update it rather than
   duplicate) — run the `integrator-memory-recall` skill with the symptom.

4. Write `"$MEMDIR/<slug>.md"` with the Write tool (NOT echo), schema:

   ```yaml
   ---
   name: <slug>
   description: "<the SYMPTOM in the user's / the error's words — the words a future session will search with, NOT the answer's jargon>"
   metadata:
     node_type: memory
     type: <user|feedback|project|reference>
   ---
   <the one fact. For feedback/project, follow with **Why:** and **How to apply:** lines.
   Link related notes with [[their-name]].>
   ```

5. Append a one-line pointer to `"$MEMDIR/MEMORY.md"` (create if missing), in
   the form: dash, bracketed title, parenthesized note filename, em-dash, hook —

   ```text
   - [<Title>](<slug>.md) — <one-line hook>.
   ```

6. Validate the result with the bundled validator (fail-fast on schema drift):

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/integrator-memory-write/scripts/validate_memory_note.py" \
       "$MEMDIR/<slug>.md"
   ```

7. Sanity-check: would a future session, having only the SYMPTOM, find this
   note by searching `description`? If the description reads like the
   *answer*, rewrite it to read like the *question*.

## Correcting a memory — the 2-step non-destructive protocol

When a new discovery CONTRADICTS an existing memory, fix it non-destructively:

1. **Clean the fact in place.** Replace the wrong statement in the body with
   the correct one — the body is the current truth, no "we used to think X"
   clutter inline.
2. **Demote the error to a lesson — the WHY is the point.** Record the error as
   a **numbered footnote**: `[^N]` in the body, and under a bottom
   `## Notes and lessons learned` section, `[^N]: [ocd:<date> lmd:<date>] <the
   root cause — WHY the previous statement was wrong>`. A lesson without a WHY
   cannot stop the next repeat.

This mirrors the Bug Autopsy directive (every fixed bug becomes a guardrail):
the *fact* is corrected, the *error* is never deleted — it is demoted to a
linked lesson so future readers don't repeat it.

## INTEGRATOR wiring

Write a note at these moments of your workflow:

- **After fixing a non-trivial integration/merge/CI bug** — capture the
  bug-autopsy: symptom in `description`, root cause + fix in the body.
- **After a quality-gate failure with a non-obvious root cause** — the next
  gate failure with the same shape should recall this note.
- **When the user confirms a preference** about reviews, merges, or releases —
  `type: feedback`, with **Why:** and **How to apply:** lines.

## Output

One note file + one MEMORY.md index line, validator-clean. Report the note
path and the one-line description; do NOT echo the whole note back into the
conversation.

## Examples

```text
After fixing a flaky CI failure:
  description: "CI job times out on the integration test / pipeline hangs at the merge step"
  body: explains the root cause (orphaned worktree lock) + the cleanup fix.

User: remember that I want squash merges only on this repo
  → type: feedback; description carries "which merge strategy / how should PRs be merged".
```

## Scope

ONLY authors/updates memory notes + the MEMORY.md index. Does NOT recall (use
`integrator-memory-recall`). One fact per note. Symptom-indexed description is
mandatory — it is what makes the note recallable.

## Resources

- `rules/memory-protocol.md` — the protocol (the law, schema, the
  lessons-learned conventions, dual-test method).
- `scripts/validate_memory_note.py` — the bundled schema validator.
- The harness `# Memory` directive — the authoring source-of-truth this skill
  follows.
- `integrator-memory-recall` — the RECALL side (find a note before you
  duplicate or correct it).
