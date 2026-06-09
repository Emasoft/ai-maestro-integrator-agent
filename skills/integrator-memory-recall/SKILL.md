---
name: integrator-memory-recall
description: Recall durable project memories from a SYMPTOM before debugging, deciding, or acting on a recurring problem. Searches the project's markdown memory notes with memgrep (degrading to plain grep when memgrep is absent), ranking notes by how well your symptom query hits each note's description/title/tags, and returns the top notes to read. Use when you think "have we hit this before?", before investigating a failing quality gate or a familiar CI failure, or when the user says "recall memories about X", "did we already solve this", "search the memory notes", "check what we learned about Y". The INTEGRATOR implementation of the AI-Maestro memory-recall protocol (see rules/memory-protocol.md).
license: MIT
compatibility: Works with or without the memgrep binary (degrades to grep). Requires Python 3.10+ for the cross-platform script.
metadata:
  author: Emasoft
  version: 1.0.0
---

# Integrator memory-recall

## Overview

Recall is the FIRST step before debugging a recurring problem, making a design
decision, or acting on a recurring alert — "have we hit this before?". It
searches the project's curated markdown memory notes (the `memory/` dir the
harness maintains) and returns the notes whose `description`/`title`/`tags`
best match your SYMPTOM. The answer is in the matched note's body.

This is distinct from conversation/transcript search: it recalls *curated,
symptom-indexed notes*, not raw chat history.

## The one law

Query with the SYMPTOM — the user's words, the error text, the problem — NOT
the answer's jargon. A note is findable from the symptom because its author put
symptom vocabulary in `description`. (If you query "keychain" you only find it
once you already know the answer; query "rotator failed, had to log in" and you
find it from the problem.)

## Instructions

1. Resolve the project memory dir (the harness per-project notes dir):

   ```bash
   MEMDIR="$HOME/.claude/projects/$(pwd | sed 's#/#-#g')/memory"
   # If that path doesn't exist, fall back to a project-local memory/ dir:
   [ -d "$MEMDIR" ] || MEMDIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/memory"
   ```

2. Build a SYMPTOM query from the user's words / the error / the problem (never
   the answer's jargon), then recall with the bundled cross-platform script —
   it uses memgrep when present and degrades to a pure-Python grep otherwise:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/integrator-memory-recall/scripts/memory_recall.py" \
       --symptom "the symptom in the user's / the error's words" \
       --memdir "$MEMDIR"
   ```

   POSIX shells can equivalently run the raw recipe:

   ```bash
   SYMPTOM="the symptom in the user's / the error's words"
   if command -v memgrep >/dev/null 2>&1; then
     memgrep recall "$SYMPTOM" "$MEMDIR"        # notes ranked best-first: path — description
   else
     grep -rliE "$SYMPTOM" "$MEMDIR" 2>/dev/null # fallback: degrade, never break
   fi
   ```

   If `memgrep` is not installed, install it once:
   `cargo install --path <…>/ai-maestro-janitor/tools/memgrep` — until then the
   fallback works on note frontmatter + bodies.

3. Read the top 1-3 notes the recall returns; the fact you need is in their
   bodies — INCLUDING each note's `[^N]` lessons (memgrep appends them
   automatically). If recall returns nothing, the memory doesn't exist yet —
   solve the problem, then capture it with the `integrator-memory-write` skill.

## INTEGRATOR wiring

Run recall at these moments of your workflow:

- **Before debugging a failing quality gate** — the gate failure may be a known
  pattern with a written root cause ("known failure?").
- **Before diagnosing a CI failure** that looks familiar.
- **Before re-deriving architecture/gotchas** a past session may have noted.

## Output

A short ranked list of `path — description` lines (memgrep) or matching paths
(fallback), best first. Read the top few; do NOT dump full note bodies into
the conversation — open the one you need.

## Examples

```text
User: this quality gate failed the same way last month, did we write that down?
User: recall memories about the merge conflict in the release branch
User: have we hit this CI timeout before?
```

## Scope

ONLY searches + surfaces existing memory notes (read-only). Does NOT write
notes (use `integrator-memory-write`). Degrades to plain grep / pure-Python
search when memgrep is absent; never blocks on a missing binary.

## Resources

- `rules/memory-protocol.md` — the INTEGRATOR recall protocol (the law, the
  schema, the read-the-notes rule, the dual-test method).
- `scripts/memory_recall.py` — the bundled cross-platform recall script.
- `integrator-memory-write` — the WRITE side (authoring + the correction
  protocol).
