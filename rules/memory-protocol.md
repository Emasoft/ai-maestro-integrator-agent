# Markdown memory — the INTEGRATOR's recall + write protocol

The harness `# Memory` directive (injected each session) tells you how to
**WRITE** memories. This rule is the missing half for the INTEGRATOR role: how
to **RECALL** them, the **discipline** that makes recall work, and the **tool**
(`memgrep`) that powers it. Together they are "the memory system": authoring
(directive + `integrator-memory-write`) + recall (this rule +
`integrator-memory-recall`) + the search tool (memgrep) + the note corpus.

This recalls *curated, symptom-indexed markdown notes* in the project's
`memory/` dir — it is distinct from conversation/transcript search, which
searches raw chat history.

## The one law that makes memory work: index by the QUESTION, not the answer

A memory is found from the SYMPTOM, not the solution. When you write a note,
its `description:` (and `title`/`tags`) MUST carry the words a future session
will have when the problem RECURS — the user's words, the error text, the
symptom — NOT the jargon of the fix.

- WRONG `description`: "OAuth creds live in the macOS keychain services".
  (Findable only if you already know the answer is "keychain".)
- RIGHT `description`: "rotator failed, had to log in manually — where are the
  creds / why did the swap fail" + the keychain fact in the BODY.

Two-hop recall: a symptom query lands you on the note; the note's BODY gives the
answer. The `description` is the load-bearing surface — `memgrep recall` ranks
on `description + title + tags` ONLY (the `metadata.type` taxonomy does NOT
affect ranking). Put symptom vocabulary in `description`; put the answer in the
body.

## Recall BEFORE acting (the protocol)

Before debugging a recurring problem (a failing quality gate, a CI failure
pattern, a merge conflict you have seen before), making a design decision, or
acting on a recurring alert, RECALL first — "have we hit this before?". Cheap,
and it's the whole point of having a memory.

```bash
# memdir is the harness per-project memory dir:
MEMDIR="$HOME/.claude/projects/<project-slug>/memory"   # slug = project path, dashed
SYMPTOM="the user's words / the error / the symptom"     # NOT the answer's jargon

if command -v memgrep >/dev/null 2>&1; then
  memgrep recall "$SYMPTOM" "$MEMDIR"      # notes ranked best-first as: path — description
else
  grep -rliE "$SYMPTOM" "$MEMDIR"          # fallback: plain grep, degrade-not-break
fi
```

Cross-platform equivalent (the skill ships it):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/integrator-memory-recall/scripts/memory_recall.py" \
    --symptom "$SYMPTOM" --memdir "$MEMDIR"
```

Read the top 1-3 notes the recall returns; the answer is in their bodies. If
recall returns nothing, the memory doesn't exist yet — solve the problem, then
capture it per the `integrator-memory-write` skill.

## memgrep — the recall engine

`memgrep` is `rg` for markdown (gitignore-aware tree walk, per-line regex,
markdown-structural filters, and the memory subcommands `recall`/`find`/
`index`). Its teaching doc is `tools/memgrep/SKILL.md` in `ai-maestro-janitor`.

- **Availability:** memgrep is a Rust binary. If `command -v memgrep` is empty,
  install it once: `cargo install --path <…>/ai-maestro-janitor/tools/memgrep`
  (puts it on `~/.cargo/bin`). Until then, the plain-`grep` fallback above
  works on note frontmatter + bodies — recall **degrades, never breaks**.
- **recall** `memgrep recall "SYMPTOM" <memdir>` — symptom-ranked notes,
  precision-first (surface matches suppress body-only matches unless nothing
  matched the surface), printed `path — description`, best first.
- **find** `memgrep find "+TERM -TERM" <memdir>` — note-level keyword search
  with a `+` (mandatory) / `-` (exclude) / wildcard / phrase DSL.

## Read-the-notes rule — a memory's lessons are part of the memory

When you read ANY memory, also read **all the lessons attached to it** — every
`[^N]` footnote reference and the `## Notes and lessons learned` entries they
point to. The lessons are *why* the facts are the way they are and *what errors
not to repeat*. `memgrep recall`/`find` auto-append each returned note's
resolved lessons, so one call yields the facts AND every linked WHY.

## The note format (recall-relevant fields)

The harness `# Memory` directive is the authoring source-of-truth. On disk:

```yaml
---
name: <kebab-slug>                 # == filename stem
description: "<symptom surface — the load-bearing recall field>"
metadata:
  node_type: memory
  type: user | feedback | project | reference
---
<body: the one fact; for feedback/project add **Why:** and **How to apply:**>
```

`MEMORY.md` is the human index (`- [Title](file.md) — hook`, one line per note)
loaded each session. Recall does not need the index — it scans the notes
directly.

## Correcting a memory — the 2-step non-destructive protocol

When a new discovery CONTRADICTS an existing memory:

1. **Clean the fact in place** — replace the wrong statement in the body with
   the correct one. The body is the current truth, no "we used to think X"
   clutter inline.
2. **Demote the error to a lesson** — record the error as a numbered footnote
   (`[^N]` in the body, `[^N]: [ocd:… lmd:…] <the WHY>` under a bottom
   `## Notes and lessons learned` section). The load-bearing content is *why*
   the previous statement was wrong — a lesson without a WHY cannot stop the
   next repeat.

This mirrors the Bug Autopsy directive: the *fact* is corrected, the *error*
is never deleted — it is demoted to a linked lesson.

## INTEGRATOR wiring (when this fires for you)

| Moment | Action |
|---|---|
| A quality gate fails and feels familiar | RECALL the symptom before re-deriving the diagnosis |
| A CI failure matches a known pattern | RECALL; the prior root cause may be written down |
| You fixed a non-obvious integration/merge/CI bug | WRITE the bug-autopsy note (symptom-indexed) |
| A user confirms a preference about reviews/merges/releases | WRITE a `feedback` note with **Why** and **How to apply** |

## Evaluating / improving the system: the dual-test method

- **Test A — cold-recall:** simulate a session with NO prior recollection;
  build the query ONLY from the symptom/user's words. Tests "is the right note
  findable from the symptom?".
- **Test B — write-then-recall:** author a note, then retrieve it. Tests the
  round-trip.

**Contamination warning:** after you WRITE a note you are biased toward its
wording — your own cold-recall is no longer cold. Do cold-recall from a clean
framing, or have the symptom come from the user verbatim.

## Why this rule exists

Without a standing rule, every fresh INTEGRATOR session re-derives the same
facts (architecture, gotchas, prior gate failures) even when the answer was
written down last week. This rule makes "recall before acting" and "index by
symptom" a standing discipline, with a tool command that degrades to grep when
the binary isn't present. (Adopted per issue #12; reference implementation in
`ai-maestro-janitor`.)
