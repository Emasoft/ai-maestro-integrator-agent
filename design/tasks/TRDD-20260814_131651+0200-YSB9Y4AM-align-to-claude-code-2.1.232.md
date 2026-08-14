---
trdd-id: YSB9Y4AM
title: Align the plugin to Claude Code 2.1.221 through 2.1.232
column: complete
created: 2026-08-14T13:16:51+0200
updated: 2026-08-14T13:16:51+0200
current-owner: integrator
task-type: infra
min-approval-requirement: none
scope: project
relevant-rules: []
---

# Align the plugin to Claude Code 2.1.221 through 2.1.232

## What changed and why

Three real misalignments with the platform, each verified against the **2.1.232
binary itself** rather than against the changelog prose, because the changelog
names features but not field names — and a guessed field name in a validator is
worse than no validation at all.

### 1. Plugin source types — two false MAJORs and one false green

`VALID_SOURCE_TYPES` was `{github, url, npm, pip, git-subdir}`. Claude Code's own
set, read out of the 2.1.232 binary, is:

```
new Set(["npm","url","github","git-subdir","archive","command","unsupported"])
```

- **`archive`** (added 2.1.224) and **`command`** (added 2.1.229) were missing, so
  a legitimate marketplace using either got a MAJOR "invalid source type" from us
  and could not pass a publish gate.
- **`pip` was never in Claude Code's set.** It is not a typo for anything: there is
  no `At("pip")` schema anywhere in the binary. The predicate that consumes the set
  (`typeof r==="string" && !kPy.has(r)`) marks such an entry *unusable* and the
  loader drops it with a warning. So accepting `pip` was a **false green** — we
  would have passed a marketplace Claude Code silently refuses to load.

`"unsupported"` is Claude Code's internal sentinel for the dropped case and is
deliberately not authorable here.

### 2. Archive sources need their own field rules

An `archive` source pins with **`sha256`** (64 hex) — a different field and width
from git's 40-hex `sha`, which was the only digest we validated. Claude Code also
refuses an archive URL that is not `https://` or that resolves to a loopback,
link-local, or cloud-metadata host (its own message: *"Archive URLs must use
https:// and must not point at a loopback, link-local, or cloud-metadata host"*).
`validate_archive_source()` now enforces both as MAJOR, since such an entry cannot
install at all. The metadata-host rule is a genuine SSRF guard: an "archive" that
fetches the cloud metadata endpoint is pulling instance credentials, not a plugin.

Hosts are judged **structurally**, by IP range via the stdlib `ipaddress` module,
rather than against a list of literal addresses. That covers every address in
`127.0.0.0/8`, `::1`, `169.254.0.0/16` and `fe80::/10` — including the whole
link-local block the metadata endpoint lives inside — instead of the three literals
a list could name. It also keeps a live IMDS address out of the source, where
SSRF/secret scanners flag it and cannot tell a denylist from a target: CPV's RC-65
raised MAJOR on the first cut for exactly that reason.

### 3. Marketplace settings aliases

2.1.232 accepts `additionalMarketplaces` / `allowedMarketplaces` as aliases for
`extraKnownMarketplaces` / `strictKnownMarketplaces`. The installer read only the
canonical key, so a marketplace registered under an alias looked unregistered and
produced a false *"Not in extraKnownMarketplaces"* hint — sending the user to fix a
registration they already had. `_known_marketplaces()` now merges every accepted
spelling on read (canonical wins a name collision); writes stay canonical.

### 4. Background-by-default agent spawns

2.1.232 makes non-teammate agent spawns run in the **background** in interactive
sessions. `amia-prrd-trdd-kanban` told INTEGRATOR to spawn RELEASER/DEPLOYER and
act on the result; the Agent call now returns the agent's *name*, with the outcome
arriving later as a task notification. The skill now says to wait for the
notification before advancing the column. Acting on the spawn's return would mark a
TRDD `published`/`live` while the releaser is still running — and if it then fails,
the board asserts a release that never happened.

## Deliberately NOT changed (checked, and correct as-is)

- **`/ultrareview`, `/ultraplan`, `/review`** — the retirements and the
  `/review` → `/code-review` aliasing affect nothing: the tree contains no
  reference to any of them.
- **The four `/reload-plugins` hints** in `claude-plugin-install.py` — 2.1.221 made
  `/plugin`-driven installs activate without a reload, but every one of those hints
  follows a direct `save_json_safe(SETTINGS_TARGET, ...)` write, which still needs
  one. Accurate as written.
- **`MAX_NAME_LENGTH = 70`** — the binary's `/^[A-Za-z0-9_$.-]{1,40}$/` sits beside
  the marketplace schema and looks like a 40-char name cap, but it is only used by
  `_Tr()`, which redacts unusual JSON-path keys to `<key>` in error messages. The
  real name validator (`JXc`) has no length cap. Lowering our limit on that
  resemblance would have invented a false MAJOR for every 41–70-char name.
- **The 19 `context: fork` + `background: false` pins** (TRDD-GJF8C8SR) — 2.1.232
  widens the background default to agent spawns, which reinforces those pins rather
  than invalidating them.

## Verification

- `tests/test_marketplace_source_types.py` — 17 checks, all passing.
- Full suite: **11/11 test files**, 85 pytest tests.
- `ruff` and `mypy` clean on both edited scripts.
- **Non-vacuity proved by breaking it:** injecting `pip` into the table fails 3
  checks by name (`VALID_SOURCE_TYPES drifted — missing=[] extra=['pip']`);
  removing `archive` fails 4; restoring returns green. The URL guard accepts
  `https://ex.com/p.zip` and rejects `http://`, a link-local address, the IPv6
  loopback, and `localhost`.

## Notes and lessons learned

The load-bearing habit here was reading the **binary** instead of the changelog.
The changelog announced `archive` "with optional SHA-256 pinning" without naming
the field, and announced `command` without naming its field; both guesses would
have been wrong in a way tests written from the same guess could never catch. The
same habit killed a change I was about to make (the 40-char name cap) that would
have introduced a fresh false failure.
