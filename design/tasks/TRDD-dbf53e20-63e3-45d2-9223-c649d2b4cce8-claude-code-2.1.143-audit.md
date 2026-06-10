# TRDD-dbf53e20 — Claude Code 2.1.101 → 2.1.143 compatibility audit and update

**TRDD ID:** `dbf53e20-63e3-45d2-9223-c649d2b4cce8`
**Filename:** `design/tasks/TRDD-dbf53e20-63e3-45d2-9223-c649d2b4cce8-claude-code-2.1.143-audit.md`
**Tracked in:** this repo (design/tasks/ is git-tracked)
**Status:** In progress
**Created:** 2026-05-16

## User request (verbatim)

> One month ago we were at v2.1.80! Today we reached v2.1.143! So many updates of claude code were released in the last month, Anthropic is on a roll! Read all the recent changes and update the plugin accordingly: https://code.claude.com/docs/en/changelog.md
>
> fix all issues, no matter how small.

User answers from `AskUserQuestion`:

- **Plugin scope:** `ai-maestro-integrator-agent (cwd)` (this plugin, v1.2.14)
- **Update depth:** `Comprehensive audit` — every relevant changelog entry, including edge-case fixes, error-message changes, and defensive coding around fixed bugs

## Scope

Audit and update `ai-maestro-integrator-agent` (working directory: the
plugin repo root) against the changelog from **v2.1.101 (April 10, 2026)**
through **v2.1.143 (May 15, 2026)**.

The changelog source was fetched from
<https://code.claude.com/docs/en/changelog.md>; the published doc starts at
v2.1.101, so v2.1.80–v2.1.100 are not directly auditable from that page (they
fall through). The fetch was cached in the authoring session's tool-results
directory (ephemeral; re-fetch the URL if needed).

## Plugin inventory (snapshot)

| Component | Count | Path |
|---|---|---|
| Manifest | 1 | `.claude-plugin/plugin.json` |
| Hooks | 3 (PreToolUse×2, Stop) | `hooks/hooks.json` + `scripts/amia_pre_push_hook.py`, `amia_pre_issue_close_hook.py`, `amia_stop_hook.py` |
| Agents | 11 | `agents/*.md` |
| Skills | 20 | `skills/<dir>/SKILL.md` (+ references/, scripts/, examples/) under skills/ |
| Commands | 0 | — |
| MCP servers | 0 declared in plugin manifest | — |
| Monitors | 0 declared in plugin manifest | — |
| Themes | 0 declared in plugin manifest | — |
| Python scripts | ~30 | `scripts/*.py` |
| GitHub workflows | 3 | `.github/workflows/*.yml` |

## High-impact changelog entries that affect plugin authors

### Plugin manifest schema

| Version | Change | Action |
|---|---|---|
| 2.1.129 | `themes` / `monitors` should move under `"experimental": { ... }` — top-level still works but `claude plugin validate` will warn | N/A — plugin has none |
| 2.1.142 | Plugins with a root-level `SKILL.md` and no `skills/` subdirectory are now surfaced as a skill | N/A — we have `skills/` |
| 2.1.140 | Plugins warn when a default component folder (e.g. `commands/`) is silently ignored because `plugin.json` sets the matching key | N/A — manifest does not override |
| 2.1.139 | `claude plugin details <name>` shows component inventory and projected per-session token cost | Defensive — review skill descriptions for clarity |
| 2.1.118 | Added `claude plugin tag` to create release git tags for plugins with version validation | Document in CONTRIBUTING |
| 2.1.120 | `claude plugin validate` now accepts `$schema`, `version`, `description` at the top level of `marketplace.json` and `$schema` in `plugin.json` | Add `$schema` and richer description |
| 2.1.105 | Skill description listing cap raised from 250 to 1,536 characters | Review every skill SKILL.md description |

### Hook system

| Version | Change | Action |
|---|---|---|
| 2.1.143 | Stop hooks blocking repeatedly now end the turn after 8 consecutive blocks (override `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`) | `amia_stop_hook.py` MUST yield within 8 blocks. Document this in the script + add tracking. |
| 2.1.142 | Configuring prompt- or agent-type hook for `SessionStart`/`Setup`/`SubagentStart` now shows clear error | N/A — we use command-type |
| 2.1.141 | New `terminalSequence` field in hook JSON output (desktop notifications, window titles, bells) | Optional — could be used in Stop hook for "blocked" notifications |
| 2.1.139 | New `args: string[]` field (exec form) — no shell, no quoting | Migrate from `command` to `args` form on all 3 hooks to avoid shell-injection on plugin paths with spaces |
| 2.1.139 | New `continueOnBlock` config for `PostToolUse` | N/A — we have no PostToolUse hooks |
| 2.1.139 | Hooks now run without terminal access — writes to terminal will not corrupt prompts | Defensive — audit scripts for stdout printing |
| 2.1.139 | MCP stdio servers receive `CLAUDE_PROJECT_DIR`; plugin configs can reference `${CLAUDE_PROJECT_DIR}` | Document |
| 2.1.133 | Hooks receive `effort.level` via JSON and `$CLAUDE_EFFORT` env var; Bash tool commands also see `$CLAUDE_EFFORT` | Scripts can adapt verbosity to effort level |
| 2.1.132 | `CLAUDE_CODE_SESSION_ID` available in Bash subprocesses, matching the `session_id` passed to hooks | Use it to correlate hook output across the session |
| 2.1.119 | `PostToolUse` / `PostToolUseFailure` inputs now include `duration_ms` | N/A — no PostToolUse hooks |
| 2.1.118 | Hooks can invoke MCP tools directly via `type: "mcp_tool"` | Not yet useful for AMIA |
| 2.1.105 | `PreCompact` hook can block compaction by exiting code 2 or `{"decision":"block"}` | Optional |
| 2.1.122 | A malformed hooks entry in `settings.json` no longer invalidates the entire file | Defensive — strict JSON validation in hooks.json |

### Skills

| Version | Change | Action |
|---|---|---|
| 2.1.139 | `Skill(name *)` permission rules now work as prefix match (like `Bash(ls *)`) | Document — adjust any permission examples in skill READMEs |
| 2.1.139 | `/context` shows providing plugin's name for plugin-sourced skills | Already works |
| 2.1.120 | Skills can reference current effort level with `${CLAUDE_EFFORT}` in their content | Could be used to adapt skill workflows |
| 2.1.105 | Skill description cap raised to 1,536 chars | Audit & expand short descriptions where it adds clarity |
| 2.1.133 | Subagents now discover project, user, plugin skills via the Skill tool | N/A — already works |
| 2.1.119 | `--print` mode honors agent's `tools:` and `disallowedTools:` frontmatter | Audit agents — ensure tools/disallowedTools lists are correct |
| 2.1.119 | `--agent <name>` honors agent definition's `permissionMode` for built-in agents | Audit agent frontmatter |
| 2.1.119 | Plugin skills loading from a stale version cache fixed | N/A — Claude-side fix |
| 2.1.101 | Skills not honoring `context: fork` and `agent` frontmatter fields fixed | Verify our skills declare these correctly |
| 2.1.136 | A `skills` entry in `plugin.json` hiding the plugin's default `skills/` directory fixed | N/A — manifest doesn't override |

### Settings/permissions

| Version | Change | Action |
|---|---|---|
| 2.1.143 | `worktree.bgIsolation: "none"` setting | Document in docs |
| 2.1.133 | `worktree.baseRef` setting (`fresh` \| `head`) — default `fresh` changes back to `origin/<default>` | Document in worktree skill |
| 2.1.121 | `alwaysLoad` MCP server option — tools skip tool-search deferral | N/A — no MCP |
| 2.1.121 | `PostToolUse` hooks can replace tool output via `hookSpecificOutput.updatedToolOutput` (was MCP-only) | Document |
| 2.1.139 | `autoAllowBashIfSandboxed` now auto-approves commands with shell expansions like `$VAR` and `$(cmd)` | N/A |
| 2.1.122 | A malformed `hooks` entry no longer invalidates the entire `settings.json` | Defensive |

### Removed surfaces / behaviors that affect plugin design

| Version | Change | Action |
|---|---|---|
| 2.1.139 | Remote Control, `/schedule`, claude.ai MCP connectors, notification preferences are now disabled when `ANTHROPIC_API_KEY` / `apiKeyHelper` / `ANTHROPIC_AUTH_TOKEN` is set | Document in README |
| 2.1.119 | Tool search disabled by default on Vertex AI; opt in with `ENABLE_TOOL_SEARCH` | Defensive |

### Defensive scripts (fixed bugs we want to avoid relying on)

| Version | Bug fixed | Action |
|---|---|---|
| 2.1.143 | Stop hooks looping forever now cap at 8 blocks | **Critical** — `amia_stop_hook.py` must converge |
| 2.1.142 | Plugin cache cleanup deleting the active plugin version directory when no installation metadata is present | Ensure publish.py writes installation metadata |
| 2.1.139 | Plugin MCP servers with unset config variables showing generic connection failure instead of "config issue" message | N/A |
| 2.1.137 / 2.1.131 | VS Code extension fixes | N/A |
| 2.1.121 | `--resume` failing on large sessions when transcript was corrupted | N/A |

## Acceptance criteria

1. All 3 hooks (`amia_pre_push_hook.py`, `amia_pre_issue_close_hook.py`,
   `amia_stop_hook.py`) explicitly tracked against the 2.1.143 Stop-hook
   block cap (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=8`).
2. All 20 SKILL.md files audited for `context:` and `agent:` frontmatter and
   description quality (cap raised to 1,536 chars).
3. All 11 agent .md files audited for `tools:`, `disallowedTools:`, and
   `permissionMode:` correctness (now respected in `--print` and `--agent`).
4. `plugin.json` adds `$schema` field (now validated by 2.1.120).
5. `hooks/hooks.json` retains backward-compat `command` form for now; a
   companion `args`-form table is documented (recommended for plugins on
   2.1.139+).
6. README documents Claude Code v2.1.139+ feature dependencies (e.g.
   `--agent` flag, `claude plugin tag` / `prune`).
7. Defensive: `amia_stop_hook.py` cannot infinite-loop block — it must
   either approve or block-with-exit conditions, never block more than 7
   consecutive times for the same session_id.

## Phased plan

- **Phase 1:** read everything → enumerate violations (this TRDD's audit
  table)
- **Phase 2:** fix manifest (`plugin.json` $schema + experimental block)
- **Phase 3:** fix hooks (`hooks.json` + 3 hook scripts) — Stop hook cap is
  the priority
- **Phase 4:** audit all 20 SKILL.md frontmatter & descriptions; fix in
  parallel via batched agents
- **Phase 5:** audit all 11 agent .md frontmatter (`tools:`,
  `disallowedTools:`, `permissionMode:`)
- **Phase 6:** update README/CHANGELOG; document new Claude Code feature
  dependencies
- **Phase 7:** run plugin validation (`/cpv-validate-plugin`); ship
