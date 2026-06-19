# Changelog

All notable changes to this project will be documented in this file.

## [1.3.0] - 2026-06-09

### Features

- **Markdown memory system (issue #12):** adopt the AI-Maestro memory
  protocol for the INTEGRATOR role — new `rules/memory-protocol.md`
  (recall-before-acting, symptom-indexed notes, the correction protocol),
  new `integrator-memory-recall` skill (symptom → ranked notes via memgrep,
  degrading to a pure-Python grep fallback when the binary is absent) with a
  cross-platform `memory_recall.py` script, new `integrator-memory-write`
  skill with a `validate_memory_note.py` schema validator, INTEGRATOR
  workflow wiring in the main persona (recall before debugging a failing
  gate; bug-autopsy note after a non-trivial fix), and a 7-test suite
  (`tests/test_memory_skills.py`) covering recall, the forced-fallback path,
  and validator accept/reject cases. The optional auto-recall hook was
  deliberately NOT added (opt-in per the issue; can land later).
- **Approval tiers in the persona (issue #11):** new
  `## Approval Tiers, the proposal→planned Lifecycle, and Baseline Governance`
  section in the main-agent persona (verbatim from the MANAGER-authored
  TRDD-495a928e), placing the INTEGRATOR's two Tier-2 gates — the release
  gate and the baseline-deviation gate — on the Tier 0 → COS → MANAGER → USER
  ladder, documenting the `design/proposals/`↔`design/tasks/` lifecycle and
  the ratified baseline ruleset pair. The existing `## Governance Integration`
  merge/release step now cross-references the Tier-2 release gate.

### Bug Fixes

- **R6 communication graph v2 sync (issue #9):** the persona's
  `## Communication Permissions` section now mirrors the server-enforced
  2026-04-22 v2 graph — HUMAN as a reply-only (`1`) recipient for team
  titles (requires `options.inReplyToMessageId`), explicit forbidden rows
  for team peers (ORCHESTRATOR routes) and the governance layer
  (MAINTAINER/AUTONOMOUS — MANAGER routes), and every cross-layer advisory
  refreshed from "route via COS" to "route via COS → MANAGER". Previously
  the persona authorized edges the server rejects with HTTP 403.
- **`validate_skill.py`:** strip fenced code blocks / inline code spans
  before markdown-link extraction and skip `<placeholder>` targets — a
  format template like `- [<Title>](<slug>.md)` inside a code fence was
  flagged as a missing referenced file (guaranteed false positive).
- **`publish.py`:** document WHY `uv.lock` must stay in the Step 11 staged
  tuple (issue #10 — the entry itself landed earlier in 72facc7; the
  explanatory comment from ai-maestro-autonomous-agent is now carried here
  too so it is not "simplified away" later).

### Documentation

- README: add the `amia-prrd-trdd-kanban`, `integrator-memory-recall`, and
  `integrator-memory-write` skills to the components table (the first was
  shipped earlier without a README row), and document the `rules/` and
  `tests/` directories.

## [1.2.16] - 2026-06-09

### Bug Fixes

- **`git-hooks/pre-push`:** The distributable pre-push hook hard-failed with
  "validate_plugin.py not found" (blocking every push for anyone who installed
  it per the README) because the local validator script was retired in commit
  `6058ebc`. It now runs the same CPV remote validation as CI
  (`uvx --from git+https://github.com/Emasoft/claude-plugins-validation
  cpv-remote-validate plugin . --strict --verbose`).
- **Stale validator references:** `README.md`, `docs/AGENT_OPERATIONS.md`, and
  3 skill reference docs (`amia-quality-gates/references/quality-gate-changelog.md`,
  `amia-release-management/references/release-workflow-chain.md`,
  `amia-release-management/references/op-validate-changelog-gate.md`) still
  instructed running the removed `scripts/validate_plugin.py`. All now point
  at the CPV remote validation command used by `.github/workflows/validate.yml`.
- **`amia_stop_hook.py`:** Two leftover bare
  `os.environ.get("CLAUDE_PROJECT_ROOT", ...)` lookups (in
  `check_claude_tasks()` and `check_quality_gates()`) bypassed the unified
  `get_project_root()` helper, so they ignored the Claude Code-standard
  `$CLAUDE_PROJECT_DIR` env var and would resolve to cwd in 2.1.139+ sessions.
  Both now use the helper.
- **License metadata:** `pyproject.toml` and all 20 SKILL.md files declared
  `Apache-2.0` while the repository's `LICENSE` file and `plugin.json` say MIT.
  Aligned all 21 metadata declarations to MIT (the committed LICENSE text is
  the operative artifact and was left untouched).

### Documentation

- **README:** Clarify that `git-hooks/pre-push` is optional and that this
  repo's own checkout uses `core.hooksPath=.githooks` (the publish.py
  process-ancestry gate), which takes precedence over `.git/hooks/`.

## [1.2.15] - 2026-05-16

### Bug Fixes

- **Skills:** Fix `agent:` frontmatter values in all 20 SKILL.md files — every
  skill referenced a short alias (`amia-main`, `api-coordinator`,
  `code-reviewer`, `debug-specialist`, `test-engineer`) that does not match
  any agent's actual `name:` field. Claude Code 2.1.101 fixed skills not
  honoring `context: fork` and `agent` frontmatter; before the fix these
  wrong values were silently ignored, but the fix would cause silent load
  failures. Replaced with the real names
  (`ai-maestro-integrator-agent-main-agent`, `amia-api-coordinator`,
  `amia-code-reviewer`, `amia-debug-specialist`, `amia-test-engineer`).
- **Skill `amia-integration-protocols`:** Add missing `agent:` field
  (pointing at the main agent) and expand the previously vague
  one-line description into concrete triggers (handoff, delegation,
  acknowledgment, completion report, blocker escalation, routing
  decision) so the model can find it.

### Hooks

- **`amia_stop_hook.py`:** Track consecutive Stop-hook blocks per
  `session_id` in `.claude/.stop-hook-blocks/<sid>.count`. Claude Code
  2.1.143+ caps repeated blocks at 8 (overridable via
  `$CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`); at 5/8 (62.5%) the response now
  carries a friendly heads-up annotation so the user knows the
  auto-release is imminent and can either complete the work or set
  `$CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=1` to skip the gate immediately.
  Counter resets on every clean exit.
- **`amia_stop_hook.py`:** Read `session_id` from the stdin payload, fall
  back to `$CLAUDE_CODE_SESSION_ID` (added in Claude Code 2.1.132); read
  the active effort level from `effort.level` in the stdin payload, fall
  back to `$CLAUDE_EFFORT` (added in 2.1.133). Both are logged in the
  FIRED line for cross-hook correlation.
- **`amia_pre_push_hook.py`, `amia_pre_issue_close_hook.py`:** Same
  `session_id` + `effort.level` env-var promotion on stdin parse so log
  lines from all 3 hooks tag the same session.
- **All 3 hooks:** Resolve project root via `$CLAUDE_PROJECT_DIR`
  (Claude Code standard since 2.1.139) with `$CLAUDE_PROJECT_ROOT` as
  legacy fallback; previously only the legacy var was checked.
- **`amia_pre_issue_close_hook.py`:** Route every progress print to
  stderr via a new `_say()` helper. Stdout is now reserved for any
  future JSON response payload Claude Code may parse, so progress text
  can never collide with structured output. Claude Code 2.1.139 removed
  terminal access from hooks; stderr is captured and safe to use
  verbosely.
- **`hooks/hooks.json`:** Document the new 2.1.143 Stop-hook cap, the
  2.1.139 captured-stream behavior, and the 2.1.132 session-id env var
  in per-entry `_description` fields. (No change to exec form —
  `command` form retained for parity with sibling AI Maestro plugins
  and universal Claude Code-version compatibility.)

### Manifest

- **`plugin.json`:** Bump to v1.2.15. Description now names the
  recommended Claude Code baseline (v2.1.132+ for session-id env var,
  2.1.139+ for no-terminal-access hooks, 2.1.143+ for Stop-hook cap).

### Documentation

- Add `design/tasks/TRDD-dbf53e20-…-claude-code-2.1.143-audit.md`
  documenting the full v2.1.101→v2.1.143 changelog audit, every fix
  applied, and the per-phase plan.
- Add `/reports/` to `.gitignore` (was missing — `/reports_dev/` was
  already there). Required by the agent-reports-location rule so
  private agent output never accidentally ships to GitHub.

  ## [1.2.14] - 2026-04-27

### Bug Fixes

- Initialize TDD-check vars to defeat reportPossiblyUnboundVariable
- Pyright-clean the project (0 errors, 0 warnings)
- Clear all non-TOC warnings (88 → 71)
- Defeat ruff I001 false-flag from inline type:ignore comment

### Documentation

- Embed reference TOCs in 8 SKILL.md files (CPV strict 71→38)
- Embed full reference TOCs in 9 agent files (CPV strict 69→38)

### Revert

- Roll back 6 over-budget TOC embeds (CPV strict 5000-char cap)
