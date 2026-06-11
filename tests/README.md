# Tests

Real tests for `ai-maestro-integrator-agent` — no mocks. Every test exercises
the actual script/hook/skill against real fixtures (tmp dirs, tmp git repos,
real subprocess invocations).

## Running

Aggregate runner (pytest-independent; prints each file's table + one verdict):

```bash
uv run python tests/run-all-tests.py
```

Pytest mode (what the publish pipeline's test gate runs):

```bash
uv run --with pytest pytest tests/ -q
```

Each `test_*.py` is also a standalone runner: `uv run python tests/test_<x>.py`
prints a Unicode result table and exits 0 (all pass) / 1 (any fail). The
aggregate runner discovers every `test_*.py`, runs it in standalone mode, and
exits non-zero if any file fails — suitable as a publish gate.

## Coverage

| Test file | Surface under test | Style |
|---|---|---|
| `test_release_governance.py` | `shared/release_governance.py` + `amia_create_release.py` + `amia_rollback.py` — the Tier-2 MANAGER-approval gate (issue #13 / M5) | gate-function unit + real CLI subprocess (exit codes), no network |
| `test_hooks.py` | `scripts/amia_pre_push_hook.py` — branch-protection PreToolUse hook (issue #13 / M12) | real tmp git repos + real stdin-JSON subprocess |
| `test_memory_skills.py` | `integrator-memory-recall` + `integrator-memory-write` scripts (issue #12) | real fixture memory dir + real subprocess |

## Why some scripts are exercised by exit-code paths, not live API calls

Most of `scripts/` are thin `gh`-CLI wrappers (release create, changelog
generate, version bump, PR checks, issue ops, projects sync). Per project
policy **mocks are forbidden** — a mocked `gh` test proves nothing. Their
fully-deterministic, no-network surfaces ARE tested here (argument validation,
the missing-file `NOT_FOUND` path, and the governance-gate refusal). Their
*live* API behavior requires an authenticated `gh` session and a throwaway
repo, which belongs in a manual / CI integration run, not the unit gate. When
adding such an integration test, gate it on `gh auth status` and a disposable
fixture repo so it skips cleanly when no live session is present.

## Resource hygiene

Every test creates its fixtures under a tmp dir (`tempfile.mkdtemp` /
pytest `tmp_path_factory`) and removes them before returning. The tmp git
repos created by `test_hooks.py` are local-only (no remotes, no pushes) so no
network or shared state is touched. A run leaves the process table and the
working tree unchanged.
