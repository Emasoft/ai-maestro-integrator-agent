---
trdd-id: 1DG0HQ0H
title: Push the plugin-name resolver tag on every release so dependants can resolve this plugin
column: completed
created: 2026-08-08T10:57:19+0200
updated: 2026-08-15T00:33:41+0200
current-owner: integrator-session
task-type: bugfix
release-via: publish
external-refs: [integrator#22, integrator#23, ai-maestro TRDD-JT3U4ZVM]
implementation-commits: []
npt: []
eht: []
---

# Push the plugin-name resolver tag on every release so dependants can resolve this plugin

## ⏵ STATE — READ THIS FIRST ON RESUME (authoritative; supersedes the body) — 2026-08-08

- **Done.** `publish.py` now creates `{plugin-name}--v{version}` and pushes it in the
  SAME `--atomic` transaction as `v{version}`.
- Also fixed here: `uv.lock` is re-locked during the bump, so it stops dirtying the tree
  and aborting the NEXT publish at `[1/11]`.
- **Verified:** 44 pytest · 6/6 test files · ruff + mypy clean · both guardrails falsified.
- **NEXT ACTION:** none. The first release carrying the resolver tag is the next publish.

## Why

Claude Code resolves a **versioned** plugin dependency (`{"name": "x", "version":
"^2.7.0"}`) only via a `{name}--v{version}` tag. A plain `v{version}` tag is **not
enough** — the resolver reports *"has no git tag satisfying >=…"* while
`git ls-remote --tags` plainly lists the versions. That mismatch grounded the entire
plugin fleet for a day (ai-maestro `TRDD-JT3U4ZVM`, raised here as integrator#22).

Measured before the fix: `publish.py` built `tag = f"v{new_ver}"` at three sites and
nothing else. The remote carried `v1.3.6`, `v1.3.7`, `v1.3.8` and **zero**
`ai-maestro-integrator-agent--v*` tags, against **20** on the reference plugin.

**The failure is silent and lands DOWNSTREAM.** This repo publishes perfectly well
without the tag; it is whoever *depends* on this repo that cannot install. No local
publish would ever surface it — which is precisely why it needed a test rather than a
one-time fix.

## What changed

- `scripts/publish.py`
  - `get_plugin_name()` + `resolver_tag()` — derive the tag from the manifest and
    **hard-fail** on a nameless one. A degraded fallback tag would recreate the exact
    silent-wrongness being fixed.
  - `stage_commit_and_push()` — creates both tags and pushes them in **one** `--atomic`
    transaction. Separate pushes would permit a published release that no dependant can
    resolve, which is the failure shape itself.
  - `_refresh_uv_lock()` — see below.
- `tests/test_publish_resolver_tag.py` — 6 checks, real temp git repos, no mocks.

**Do NOT "fix" this with `claude plugin tag <tagname>`.** That CLI's positional argument
is a **path**, not a tag name, so the call silently creates nothing and the publish
"succeeds" with the tag still missing.

## The uv.lock fix that rode along

The bump rewrites `pyproject.toml`'s `version`, but `uv.lock` keeps its own copy. Left
stale, the next `uv run` re-locks as a **side effect**, dirtying the tree — and the
*next* publish then aborts at `[1/11] Working tree is dirty` over a change nobody made
deliberately. This bit twice: once folded into an unrelated commit by hand, once
observed again immediately after v1.3.8. Re-locking inside the bump puts the new lock in
the release's own commit, where it belongs. Non-fatal by design: `uv` is not a hard
dependency of the pipeline, and a lock refresh failing is no reason to abandon a release
that already passed lint, tests and validation. (Upstream shape: CPV#149.)

## Falsification

Both guardrails were broken on purpose against the real tree, because a test that cannot
fail is decoration:

| Injected regression | Result |
|---|---|
| resolver tag collapses to the plain `v{version}` | `FAIL: resolver tag not announced` |
| nameless manifest degrades to a fallback instead of hard-failing | `FAIL: expected SystemExit, got tag 'fallback--v1.0.0'` |

`check_resolver_tag_differs_from_release_tag` exists for the same reason: if a future
refactor collapses the two tag names, every other check here would still pass while the
bug returned.

## Verification

| Gate | Result |
|---|---|
| `pytest tests/` | 44 passed |
| `tests/run-all-tests.py` | 6/6 test files |
| `ruff --select=E,F,W,I --ignore=E501` | clean |
| `mypy --ignore-missing-imports` | clean |
| resolver tag for this repo | `ai-maestro-integrator-agent--v<version>` |

## Approval log

- 2026-08-15T00:33:41+0200 — COMPLETED by integrator. Archived: work finished and shipped.
