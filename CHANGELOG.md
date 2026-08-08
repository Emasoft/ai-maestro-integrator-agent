# Changelog

All notable changes to this project will be documented in this file.

## [1.4.1] — 2026-08-08

### Bug Fixes

- Stop CHANGELOG overwriting itself; extract the duplicated test runner
- Per-stage timeouts, clean timeout reporting, and stop git add -A
## [1.4.0] — 2026-08-08

### Bug Fixes

- Refuse --install-branch-rules on a baselined repo (TRDD-RGXRISNX)

### Documentation

- Replace the stale hand-maintained version line with the auto-updated badge

### Features

- Verify CI went green on the released commit (TRDD-9MBKYW9E)

### Miscellaneous Tasks

- Bump version to 1.4.0

### Testing

- Implement GOV-VAL-06 and stamp spec currency (TRDD-K4WQ8ZTC)
## [1.3.9] — 2026-08-08

### Bug Fixes

- Push the {name}--v{version} resolver tag atomically (TRDD-1DG0HQ0H)

### Miscellaneous Tasks

- Bump version to 1.3.9
## [1.3.8] — 2026-08-08

### Bug Fixes

- Price the current model generation, not a retired one (TRDD-8CKKY36P)
- Pin all 19 forked skills to foreground execution (TRDD-GJF8C8SR)
- Re-baseline v2.136.1 -> v5.3.0 and fix the 7 defects it was hiding (TRDD-4KA9L26G)

### Documentation

- Mark TRDD-2581d9ca complete — v1.3.7 CI green (CPV pin verified)
- Record implementation commit for TRDD-8CKKY36P
- Record implementation commit for TRDD-GJF8C8SR
- Record implementation commit for TRDD-4KA9L26G

### Miscellaneous Tasks

- Bump version to 1.3.8

### Testing

- Harden the vacuity guard from "at least one" to a count floor (TRDD-GJF8C8SR)
## [1.3.7] — 2026-06-22

### Bug Fixes

- Pin CPV to v2.136.1 — v2.137.0 REPO LINT hangs CI ~30 min

### Documentation

- Add TRDD-2581d9ca — pin CPV to v2.136.1 (v2.137.0 REPO LINT hang)

### Miscellaneous Tasks

- Sync uv.lock project version (1.3.5 -> 1.3.6)
- Bump version to 1.3.7
## [1.3.6] — 2026-06-20

### Bug Fixes

- Stop Plugin Validation hanging — skip GitHub-integrity fetch + add timeout

### Miscellaneous Tasks

- Sync uv.lock project version (1.3.4 -> 1.3.5)
- Bump version to 1.3.6
## [1.3.5] — 2026-06-20

### Bug Fixes

- Drop CLAUDE_PRIVATE_USERNAMES=owner from CPV validate (self-flags public owner)

### Miscellaneous Tasks

- Sync uv.lock project version (1.3.3 -> 1.3.4)
- Bump version to 1.3.5
## [1.3.4] — 2026-06-20

### Miscellaneous Tasks

- Drop REPOSITORY_GITLEAKS from Mega-Linter (git-history false positives)
- Sync uv.lock project version (1.3.2 -> 1.3.3)
- Upgrade CI/release/notify workflows to CPV canon (SBOM, provenance, timeouts)
- Bump version to 1.3.4
## [1.3.3] — 2026-06-20

### Bug Fixes

- Quote $GITHUB_STEP_SUMMARY in validate.yml (actionlint SC2086)

### Miscellaneous Tasks

- Sync uv.lock project version (1.3.1 -> 1.3.2)
- Bump version to 1.3.3
## [1.3.2] — 2026-06-20

### Bug Fixes

- Define dev extra + suppress CPV isort drift (green CI)

### Documentation

- Mark TRDD-8ddc5f37 published (v1.3.1)

### Miscellaneous Tasks

- Bump version to 1.3.2
## [1.3.1] — 2026-06-20

### Bug Fixes

- Clear --strict gate for v1.3.1 (2 MAJOR + 1 NIT → 0/0/0/0)

### Documentation

- Add TRDD-8ddc5f37 — MAESTRO persona + SCEN + v1.3.1 (R26–R40 9/9)

### Features

- Add R26–R40 MAESTRO persona section + SCEN suite ([#15](https://github.com/Emasoft/ai-maestro-integrator-agent/issues/15))

### Miscellaneous Tasks

- Gitignore .janitor/ runtime state
- Bump version to 1.3.1
## [1.3.0] — 2026-06-19

### Bug Fixes

- Replace broken references/ link with universal-skill prose pointer
- Restructure amia-prrd-trdd-kanban to CPV 7-section format (<5000)
- V1.2.16 — repair broken pre-push hook, stale validator refs, license metadata
- Make test_memory_skills.py pytest-compatible
- Clear the CPV strict gate's CRITICAL+MAJOR wave (50 skillaudit findings → 0)
- Devitalize scanner-needle tokens in 3 runtime scripts
- Remove broken ../CLAUDE.md link in main-agent Memory Protocol (CPV MAJOR)
- Make extracted worktree scripts executable + clear residual env/fs findings
- Abstract 4 residual exec-class doc edge-cases (os-system demo, curl/jq CI, systemd-install)
- Clear mypy MINORs (publish.py fallback shims + 2 extracted scripts)

### Documentation

- Rewrite ROLE_BOUNDARIES + TEAM_REGISTRY to R29/R30 authority model
- R37 user->MAESTRO escalation sweep across references ([#18](https://github.com/Emasoft/ai-maestro-integrator-agent/issues/18))
- Re-sync 32 embedded reference TOCs to verbatim source TOC blocks ([#23](https://github.com/Emasoft/ai-maestro-integrator-agent/issues/23))

### Features

- Add INT's PRRD/TRDD/Kanban layer + DEPLOYER + RELEASER subagents
- Add Approval discipline section to amia-prrd-trdd-kanban
- Bootstrap PRRD with G1 GitHub self-id golden rule
- V1.3.0 — implement issues #9, #11, #12; document #10
- Close fleet-readiness audit findings ([#13](https://github.com/Emasoft/ai-maestro-integrator-agent/issues/13))
- Align integrator for the AI Maestro restart
- Repoint integrator off server /api/* to the frozen CLI ([#14](https://github.com/Emasoft/ai-maestro-integrator-agent/issues/14))
- Align main agent + profile to global janitor-memory (R24, #15 MAJOR-2 pt1)
- Retire per-plugin integrator-memory; R24 global directive on all subagents (#15 MAJOR-2 pt2)

### Miscellaneous Tasks

- Add /reports_dev/ and /scripts_dev/ (report-location + dev-tooling hygiene)
- Standardize to CPV canonical publish pipeline (--force-templates)
- Bump version to 1.3.0

### Refactor

- Extract worktree exec-class examples to real scripts (CPV NIT, fleet house style)
- Extract github/review exec-class examples to scripts + clear markdownlint NITs

### Testing

- Add R23/R24/R29/R30/R37 compliance oracle (issues #15-#19)
## [1.2.14] — 2026-04-27

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
## [1.2.13] — 2026-04-25

### Bug Fixes

- Stage uv.lock in the release commit
## [1.2.12] — 2026-04-25

### Bug Fixes

- Wrap module-level sys.exit in _cli_entry() for CPV strict

### Miscellaneous Tasks

- Gitignore rechecker artifacts and sync uv.lock to 1.2.11

### Styling

- Apply ruff isort (I001) — alphabetic import ordering across 27 files
## [1.2.11] — 2026-04-13

### Miscellaneous Tasks

- Fix notify-marketplace.yml to use canonical CPV workflow
- Update uv.lock
## [1.2.10] — 2026-04-10

### Features

- Implement shared/cross_platform.py (run_command + atomic_write_json)

### Miscellaneous Tasks

- Update uv.lock
## [1.2.9] — 2026-04-10

### Bug Fixes

- Add AMP communication restriction to all sub-agents
- Correct governance terminology, version sync, and communication rules
- Resolve all CPV validation issues
- Publish.py runs CPV validation remotely + pre-push enforces --strict
- Ruff F541 — remove extraneous f-prefix in publish.py
- Remove CPV_PUBLISH_PIPELINE bypass from pre-push hook — CPV --strict always runs
- Publish.py + pre-push use cpv-remote-validate via uvx
- Move shutil/subprocess imports to top of file (ruff E402)
- Use permissive markdownlint config (default: false)

### Features

- Add compatible-titles and compatible-clients to agent profile
- Add communication permissions from title-based graph
- Add smart publish pipeline + pre-push hook enforcement

### Miscellaneous Tasks

- Update validate.yml to use cpv-remote-validate --strict
- Strict publish.py + pre-push hook + release.yml propagation
- Update uv.lock
## [1.2.7] — 2026-03-27

### Bug Fixes

- Correct 9 governance violations in AMIA skills (COS routing, delegated authority)

### Miscellaneous Tasks

- Bump version to 1.2.6
- Bump version to 1.2.7 (v1.2.6 tag conflict)
## [1.2.6] — 2026-03-27

### Bug Fixes

- Add pyproject.toml recommended by plugin validator
## [1.2.5] — 2026-03-26

### Bug Fixes

- Embed TOCs in all SKILL.md and agent .md Resources
## [1.2.4] — 2026-03-26

### Bug Fixes

- Resolve 4 MAJOR regressions (missing Examples sections)
## [1.2.3] — 2026-03-26

### Bug Fixes

- Resolve all CPV MINOR issues (TOC embedding, checklists, examples)
## [1.2.2] — 2026-03-26

### Bug Fixes

- Target Emasoft fork for marketplace notifications
- Embed complete TOCs in skill SKILL.md files for CPV compliance
## [1.2.1] — 2026-03-26

### Bug Fixes

- Add missing Nixtla sections to 2 SKILL.md files, add TOC to 112 reference files
- Add missing skill sections + sync CPV validation scripts
- Replace parent traversal refs with name-only references
- Extract dict bracket access from f-strings in release.yml
- Resolve all MINOR validation issues (TOC, SKILL.md metadata, mypy)
- Resolve remaining validation issues
- Replace broken legacy atlas/cross_platform imports in ci_webhook_handler
- Restore strict pre-push hook, sync CPV with expanded path allowlist
- Comprehensive audit fixes — 40+ issues across 46 files
- Resolve all validation issues — 0 CRITICAL/MAJOR/MINOR/NIT
- Suppress mypy import-untyped errors in CI validation
- Repair 8 broken markdown links in git-worktree-operations references
- Cross-platform compatibility fixes (CC-XP-001 through CC-XP-012)
- Resolve all code correctness and cross-platform audit issues
- Round 2 audit - resolve all correctness, security, and config issues (33 files)
- Add missing TechnicalTimeouts/GitHubThresholds classes and fix import path
- Resolve remaining P1 security issues (SC-P1-005/007/010/014)
- Round 3 audit - hooks, agents, datetime, imports (16 files)
- Embed inline TOC blocks for all .md references (resolve 39 MINOR validation issues)
- Remove unknown frontmatter fields + fix hook timeouts
- Embed inline TOC blocks for 111 list-item warnings + document non-standard dirs
- Trim 6 SKILL.md files under 500-line/3500-word thresholds
- Update CPV scripts to v1.7.6 + fix remaining validation issues
- Remove unused json import from amia_cleanup_worktree.py
- Remove 8 unused json imports flagged by ruff F401
- Rename ambiguous variable l to lbl (E741)
- Resolve all ruff lint errors (F541, E402, E741, F401)
- Add shared/__init__.py to resolve mypy module resolution
- Add type annotation for label_counter (mypy var-annotated)
- Resolve all markdownlint errors (9528 → 0)
- Add --with pyyaml to uv run for validate_plugin.py
- Add TOC to 174 reference files for progressive discovery
- Rewrite 20 SKILL.md files for progressive disclosure (≤5000 chars)
- Add Error Handling, Resources sections and checklist phrases to all SKILL.md files
- Replace markdown links in agent files, tolerate MINOR in publish
- Resolve all markdownlint errors (MD012/MD022/MD031/MD041)
- Trim all SKILL.md files under 4000 chars, add missing examples
- Resolve all 3 open GitHub issues (#1, #2, #3)
- Resolve issues #4, #5, #6
- Address verification failures from LLM audit
- Revert all EAMA references back to AMAMA ([#8](https://github.com/Emasoft/ai-maestro-integrator-agent/issues/8))
- Purge all remaining Emasoft e-prefixes from repo
- Allow MINOR issues to pass validation gate (exit 3 = pass)
- Resolve CPV validation issues, update quality gate

### Documentation

- Standardize validator references to validate_plugin.py
- Add marketplace installation instructions with --scope local
- Update README with --scope local per-agent installation instructions
- Update all documentation to v1.1.17

### Features

- Convert bash script to Python for cross-platform support
- Adapt plugin to Claude Code 2.1.69 changes
- Implement 11 missing plugin automation scripts
- Add output discipline + sync validation scripts v1.9.9
- Add Token-Saving Tools section to all agents, bump to v1.2.0

### Miscellaneous Tasks

- Safety commit before migration
- Sync validation scripts from CPV
- Sync validation scripts from CPV
- Sync validation scripts from CPV
- Bump version to 1.1.3
- Bump version to 1.1.4
- Bump version to 1.1.5
- Bump version to 1.1.6
- Remove plugin-specific eia_validate_changelog.py, use CPV validator
- Bump version to 1.1.7
- Sync validation scripts, hooks, and workflows from CPV
- Bump version to 1.1.8
- Update .DS_Store
- Replace validation scripts with CPV v1.7.3, add auto-sync
- Update CPV validation scripts from upstream
- Allow MINOR validation issues to pass (block only CRITICAL/MAJOR)
- Add .github/workflows to paths trigger for self-testing
- Update CPV validation scripts + bump to v1.1.10
- Update CPV validation scripts + bump to v1.1.12
- Update CPV validation scripts (bugfix) + bump to v1.1.13
- Bump version to 1.1.15
- Sync validation scripts from CPV v1.10.5
- Add .DS_Store and .claude/ to .gitignore
- Remove .DS_Store from tracking
- Add markdownlint config to disable MD013/MD060 for agent files
- Bump version to 1.1.16
- Bump version to 1.1.17
- Track Serena MCP project configuration
- Replace local validators with CPV uvx remote validation

### Refactor

- Rename atlas_/kanban_ scripts to eia_ prefix

### Rename

- Emasoft-* → ai-maestro-*, eia- → amia- (full plugin rebrand)
## [1.1.2] — 2026-02-08

### Bug Fixes

- Fix plugin.json schema for Claude Code compatibility
- Add manifest schema checks for repository type and unknown keys

### Features

- Bump version to 1.1.2
## [1.1.1] — 2026-02-08

### Bug Fixes

- Update ao-/atlas references to int- naming
- Update remaining int- prefix references to eia-
- Validation fixes for agents and scripts
- Add required Nixtla sections to all 18 skills
- Fix YAML syntax error in validate.yml heredoc
- Standardize all author fields to Emasoft, add missing frontmatter, update README
- Blocked/blocker terminology, add blocker issue creation
- Resolve all audit issues - broken refs, API refs, ambiguous messaging, verify checklists
- Remove extraneous f-string prefixes in validate_changelog

### Features

- Initial plugin structure for integrator-agent
- Add agents, skills, and scripts from atlas-orchestrator
- CRITICAL fixes + safety warnings
- Bump version to 1.1.1

### Refactor

- Apply eia- prefix to integrator-agent
- Rename to emasoft-integrator-agent and fix runtime paths

### Add

- Blocker lifecycle checklist to blocking-workflow.md
---
*Generated by [git-cliff](https://git-cliff.org)*
