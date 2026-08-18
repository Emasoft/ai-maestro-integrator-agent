---
trdd-id: LBAN7T2K
title: Remove the 13-file dead vendored CPV validator suite and the 5 unwired orphan scripts
column: todo
created: 2026-08-18T19:58:41+0200
updated: 2026-08-18T19:58:41+0200
current-owner: integrator
task-type: refactor
min-approval-requirement: none
scope: project
severity: medium
relevant-rules: []
---

# Remove dead vendored code (audit axis-3, pass-2-falsified)

Phase-1 audit confirmed, after an adversarial pass-2 that REFUTED 3 of the original 16
candidates through the import graph: **13 vendored `validate_*.py` files under `scripts/`
are unreachable from any entry point** (no import, subprocess, runpy, entry-point,
workflow, skill, or hook reference — bare-name needles, not `filename.py`), plus 5
unwired standalone scripts (`setup_git_hooks.py`, `setup_marketplace_automation.py`,
`update_marketplace_metadata.py`, `check_version_consistency.py`, `lint_files.py`*,
`amia_github_lifecycle*.py` subsystem, `amia_sync_github_issues.py`).

Validation is fetched remotely (`publish.py` G3: `uvx cpv-remote-validate @v5.3.0`), so
the local snapshot can silently drift from the tool actually run, with no test ever
exercising the local copy to catch it.

## HARD GUARDS — the three pass-2 refutations, never delete these

| file | why it is LIVE |
|---|---|
| `cpv_validation_common.py` | imported by wired `validate_marketplace.py` (test loads it) |
| `cpv_network_resilience.py` | `publish.py:75` binds its real `gh_with_retry`/`git_with_retry`; sits under `except ImportError` shims, so deleting it breaks NOTHING loudly and silently removes network retry |
| `gitignore_filter.py` | 5 importers, 3 in live modules |

`validate_marketplace.py` is also LIVE (imported at `tests/test_marketplace_source_types.py:41`).
`lint_files.py` imports live modules but is itself unwired — verify direction before judging.

## Approach

1. RULE 0: everything is git-tracked and committed — verify with `git ls-files` before
   any `git rm`, and commit the removal so it is one-revert recoverable.
2. Re-run the pass-2 reachability check per file AT deletion time (the tree may have
   changed since the audit): bare-name import grep + subprocess/runpy + entry points.
3. `git rm` the dead set; run suite + CPV; check `ruff`/`mypy` CI surface shrinks.
4. Sweep prose per check-all-files-after-breaking-change: any doc/skill naming a removed
   script gets fixed in the same change.

## Acceptance criteria

1. Each removed file's reachability re-verified at deletion time with a bare-name needle
   (recorded in the commit body), not carried from the audit.
2. The three HARD-GUARD files plus `validate_marketplace.py` untouched — asserted by grep
   in the commit body.
3. Suite 12/12, handle guard green, CPV --strict 0/0/0/0 AFTER removal.
4. `grep -rn '<each removed basename>' --include='*.md' .` — no doc still instructs
   running a removed script.
