---
trdd-id: GJF8C8SR
title: Pin every forked skill to foreground execution after the CC 2.1.218 default flip
column: complete
created: 2026-08-07T20:43:23+0200
updated: 2026-08-07T20:43:23+0200
current-owner: integrator-session
task-type: bugfix
release-via: publish
implementation-commits: [84d39aa]
npt: []
eht: []
---

# Pin every forked skill to foreground execution after the CC 2.1.218 default flip

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-07

- **Done.** All 19 `context: fork` skills now declare `background: false` explicitly, and
  `tests/test_skill_frontmatter.py` (6 checks) pins the invariant.
- **Verified:** 38 pytest passed · 5/5 test files · ruff + mypy clean under MegaLinter's
  exact args · `claude plugin validate .` ✔ · both negative controls fire naming the file.
- **NEXT ACTION:** none. Closed; the commit rides the next publish.

## Why

Claude Code **2.1.218** changed skills declaring `context: fork` to run in the
**background by default**, with `background: false` as the per-skill opt-out.

A backgrounded skill hands its caller an agent name immediately and delivers the real
result later as a notification. All 19 forked skills in this plugin are
`user-invocable: false` knowledge-or-data skills that a specialist agent loads **in order
to act on the result** — PR context before reviewing, quality gates before merging, a
label taxonomy before labelling. Delivered asynchronously, the result lands *after* the
caller has already acted.

That is the bad failure mode: **silently wrong, not loudly broken**. Nothing errors; the
caller simply proceeds without the input it asked for. This was live in published v1.3.7.

## The test applied per skill

> *Does the caller need this skill's output in the same turn it asks for it?*

All 19 answered yes, in two groups:

| Group | Skills | Why in-turn |
|---|---|---|
| Data / action (9, `amia-api-coordinator`) | pr-context, pr-checks, pr-merge, pr-workflow, issue-operations, projects-sync, thread-management, github-integration, kanban-orchestration | the caller acts **on the returned data** |
| Knowledge / methodology (10) | ai-pr-review-methodology, code-review-patterns, git-worktree-operations, integration-protocols, label-taxonomy, quality-gates, release-management, ci-failure-patterns, multilanguage-pr-review, tdd-enforcement | guidance is useless once the caller has already acted |

Each file was read and judged individually — no blanket rewrite. Had any skill been a
genuine fire-and-forget, it would have kept `background: true` **with a comment saying
why**; none was.

## Why declare it rather than rely on the default

The declaration is the whole point. Relying on the current default means the next platform
change silently alters how the plugin runs. An explicit `background: false` survives it.

## The guardrail, and its negative control

`tests/test_skill_frontmatter.py` — 6 checks, real shipped `SKILL.md` files, no mocks,
dependency-free indentation-aware frontmatter parse (so nested `metadata:` children are
never mistaken for top-level fields).

The load-bearing pair is `check_every_forked_skill_declares_background` (catches a NEW
forked skill added without the field) and `check_forked_skills_are_not_backgrounded`
(catches a flip). `check_forked_skills_exist` guards against the vacuous-pass case where
deleting every forked skill would leave the file green while asserting nothing.

**Both were falsified against the real tree, because a test that cannot fail is
decoration** — a mistake made earlier the same day in
[[TRDD-8CKKY36P]], where a key-order check passed even with the table deliberately
mis-ordered:

| Injected regression | Check that fired | Message |
|---|---|---|
| `background: false` → `true` on amia-quality-gates | `check_forked_skills_are_not_backgrounded` | names `skills/amia-quality-gates/SKILL.md (background: true)` |
| `background:` line removed entirely | `check_every_forked_skill_declares_background` (+ the other) | names the same file |

Both name the offending file, so a future failure is actionable without investigation.

## Governance note

No ratified fleet convention for `context: fork` exists — confirmed with the CORE peer
session, which explicitly disclaimed authority over this repo. The decision rests on the
in-turn test above, which is this project's own judgement, not a peer's directive.

## Verification

| Gate | Result |
|---|---|
| `uv run --with pytest pytest tests/ -q` | 38 passed |
| `uv run python tests/run-all-tests.py` | 5/5 test files passed |
| `claude plugin validate .` | ✔ passed |
| `ruff check --select=E,F,W,I --ignore=E501` | All checks passed |
| `mypy --ignore-missing-imports` | Success, no issues |
| forked skills / with `background: false` / missing | 19 / 19 / **0** |
