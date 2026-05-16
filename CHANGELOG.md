# Changelog

All notable changes to this project will be documented in this file.

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


