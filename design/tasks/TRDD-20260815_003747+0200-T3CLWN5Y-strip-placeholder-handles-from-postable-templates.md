---
trdd-id: T3CLWN5Y
title: Strip placeholder GitHub handles from postable templates without breaking the real bot triggers
column: todo
created: 2026-08-15T00:37:47+0200
updated: 2026-08-15T00:37:47+0200
current-owner: integrator
task-type: security
min-approval-requirement: none
scope: project
relevant-rules: []
---

# Strip placeholder GitHub handles from postable templates

Hub fleet-alignment TRDD-BDRWMBDC, point 7: *templates carry NO `@`*. Filed as a
card rather than swept inline because a blind sweep here would break working
functionality — see the classification below, which is the whole point of the task.

## Why this is a real hazard, not tidiness

An `@name` outside a code span **pages a real GitHub account**. The worst instance
in this repo is directly copy-pasteable:

```
skills/amia-kanban-orchestration/references/ai-agent-vs-human-workflow-part1-fundamentals.md:297
gh issue comment 42 --body "@human-dev Please review the blockers section"
```

These are not hypothetical names. Checked with `gh api users/<name>` — **five of
the six placeholders resolve to real GitHub accounts:**

| Placeholder | `gh api users/<name>` |
|---|---|
| `@human-dev` | **HUMAN-DEV — a real Organization** |
| `@user` | real User |
| `@tech-lead` | real User (`Tech-lead`) |
| `@backend-dev` | real User |
| `@agent-1` | real User |
| `@username` | 404 — the only safe one |

So the copy-pasteable `gh issue comment` line above pages a real organization, and
the descriptive-sounding names are the trap: `human-dev` *feels* like an obvious
placeholder, which is exactly why nobody checks it. A template is the artifact that
gets copied verbatim under time pressure, which is why the rule is "no `@` at all"
rather than "no real handles" — you cannot eyeball which names are taken.

## The classification — 172 raw hits, ~68 are the defect

Measured with `grep -rn '@[a-z][a-z0-9-]\{2,\}' --include=*.md skills agents`
minus decorator/npm/email noise. **~104 of the hits MUST be preserved:**

| Token | Count | Verdict |
|---|---|---|
| `@claude` | 27 | **KEEP — load-bearing.** The real Claude GitHub-app trigger. `gh pr comment --body "@claude …"` only works with the `@`; backticking it breaks the documented workflow. |
| `@latest`, `@biomejs` | 11 | KEEP — npm specifiers (`biome@latest`, `@biomejs/biome`), not handles. |
| `@mention`, `@mentions` | 8 | KEEP — prose *about* mentions. Backtick if convenient; not a pager. |
| `@username` `@user` `@agent-1` `@agent-2` `@backend-dev` `@human-dev` `@tech-lead` `@org-name` `@github-secondary` | ~68 | **FIX** — placeholder handles inside postable bodies. |

Per the hub, `@me` / `@copilot` are permitted **only as assignee-flag values**
(`--assignee @me`), never inside a body.

## Approach

1. Port the hub's guard — `tests/governance/no-handles-in-postable-bodies.test.ts`,
   which the hub states is free to copy — to a Python check under `tests/`, so the
   allow/deny classification is encoded once and enforced, not re-derived by hand
   each time. **This is the load-bearing step:** a one-off sweep decays, a test does
   not.
2. Fix only what the ported check flags. Placeholders become plain words
   (`the reviewer`, `the backend dev`) or backticked (`` `@username` ``) where the
   text is genuinely *about* a handle.
3. Leave every KEEP row untouched — but allow them **BY POSITION, NEVER BY NAME**
   (hub guidance, and it is the load-bearing design choice here). `@claude` is
   permitted because it sits in *trigger position in an issue body*, the same way
   `@me` / `@copilot` are permitted only as *assignee-flag values*. A name
   allowlist would say "the string `@claude` is fine anywhere", which re-opens the
   hole one rename later and teaches the next author that some handles are
   intrinsically safe. No handle is intrinsically safe; only positions are.

## Acceptance criteria

1. A test in `tests/` fails on a bare placeholder handle in a postable body and
   passes on `@claude`, npm specifiers, and `--assignee @me` / `@copilot`.
2. Non-vacuity proved by breaking it: injecting `@someone` into a template body
   fails the test by name; removing it returns green.
3. `gh pr comment --body "@claude …"` examples still read literally — verified by
   grep, not by assumption.
4. The full suite still passes and CPV stays at 0/0/0/0.

## Notes and lessons learned

The instinct on receiving "templates carry no `@`" was to sweep all 172 hits. That
would have silently disabled the `@claude` bot trigger in 27 places — a rule
applied without classifying its own exceptions causes the damage it was written to
prevent. Counting the tokens before editing any of them is what surfaced the split.
