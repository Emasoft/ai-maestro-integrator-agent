#!/usr/bin/env python3
"""Real tests pinning `do_uninstall`'s ownership gate (no mocks — calls the real function).

Claude Code 2.1.239 made `<name>@synced` a real plugin-key namespace that Claude Code
itself manages for plugins synced from claude.ai. Before the gate, `--uninstall
foo@synced` fell straight through to the settings writes: a missing plugin directory
only warns, so `remaining` came out empty and the function popped
`extraKnownMarketplaces["synced"]` and `enabledPlugins["foo@synced"]` out of
settings.local.json — state this installer never created and does not own.

The gate refuses when there is neither an `installed_plugins.json` record nor a local
marketplace directory, and it exits *before* any mutation. Ownership is deliberately NOT
`plug_dir.exists()`: a half-removed install (directory already gone, settings entries
left behind) must stay cleanable, which is why the missing-directory case warns instead
of exiting. `check_uninstall_half_removed_install_still_cleans_up` is the regression
guard for exactly that, and `check_uninstall_synced_key_leaves_settings_untouched` is the
non-vacuity check — it is the one that fails if the gate is deleted.

SAFETY: `claude-plugin-install.py` resolves its paths into the real `~/.claude` at import
time. Every check here runs inside `sandboxed_cpi()`, which loads a FRESH module object
(the loader never registers the spec in `sys.modules`) and repoints every filesystem
constant into a `tempfile.TemporaryDirectory` before anything is called. The redirection
is asserted, not assumed — `_verify_redirected` raises if any constant still points at,
or under, the real `~/.claude`. A fresh module per check also means there is no shared
state to restore and nothing that can leak into another suite.

Runs two ways:

  uv run --with pytest pytest tests/test_uninstall_ownership_gate.py -q
  uv run python tests/test_uninstall_ownership_gate.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "tests"))

from _table_runner import (  # pyright: ignore[reportMissingImports]
    load_claude_plugin_install,
    run_table,
)

# Every module-level constant `do_uninstall` reaches the filesystem through. Named here
# once so `_verify_redirected` cannot drift out of sync with `sandboxed_cpi`.
REDIRECTED_CONSTANTS = (
    "CLAUDE_DIR",
    "PLUGINS_DIR",
    "MARKETPLACES_DIR",
    "CACHE_DIR",
    "INSTALLED_FILE",
    "SETTINGS_TARGET",
)


def _verify_redirected(cpi: ModuleType, root: Path) -> None:
    """Raise unless every path constant now lives under `root` and outside the real ~/.claude."""
    real = (Path.home() / ".claude").resolve()
    for name in REDIRECTED_CONSTANTS:
        value = getattr(cpi, name)
        if not isinstance(value, Path):
            raise AssertionError(
                f"{name} is {type(value).__name__}, not a Path — redirection failed"
            )
        resolved = value.resolve()
        if root != resolved and root not in resolved.parents:
            raise AssertionError(
                f"{name} escaped the sandbox: {resolved} is not under {root}"
            )
        if resolved == real or real in resolved.parents:
            raise AssertionError(
                f"{name} still points into the REAL user config: {resolved}"
            )


@contextmanager
def sandboxed_cpi() -> Iterator[tuple[ModuleType, Path]]:
    """Yield a fresh `claude-plugin-install` module with every path repointed into a temp dir."""
    with tempfile.TemporaryDirectory(prefix="cpi-uninstall-gate-") as td:
        root = Path(td).resolve()
        claude = root / ".claude"
        plugins = claude / "plugins"
        cpi = load_claude_plugin_install()
        layout = {
            "CLAUDE_DIR": claude,
            "PLUGINS_DIR": plugins,
            "MARKETPLACES_DIR": plugins / "marketplaces",
            "CACHE_DIR": plugins / "cache",
            "INSTALLED_FILE": plugins / "installed_plugins.json",
            "SETTINGS_TARGET": claude / "settings.local.json",
        }
        for name, value in layout.items():
            setattr(cpi, name, value)
        _verify_redirected(cpi, root)
        layout["MARKETPLACES_DIR"].mkdir(parents=True, exist_ok=True)
        # `do_uninstall` prints progress unconditionally; swallow it so the result table
        # below stays readable. Nothing is asserted on stdout.
        with contextlib.redirect_stdout(io.StringIO()):
            yield cpi, root


def _write_installed(cpi: ModuleType, plugins: dict[str, object]) -> None:
    """Write an installed_plugins.json in the v1 envelope the loader expects."""
    path: Path = cpi.INSTALLED_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": 1, "plugins": plugins}), encoding="utf-8")


def _read_installed_plugins(cpi: ModuleType) -> dict[str, object]:
    """Read back installed_plugins.json's plugin map."""
    data = json.loads(Path(cpi.INSTALLED_FILE).read_text(encoding="utf-8"))
    plugins = data.get("plugins", data)
    return plugins if isinstance(plugins, dict) else {}


# ── The checks (shared by the pytest wrapper and the standalone runner) ──


def check_uninstall_synced_key_refuses() -> str:
    """A '<name>@synced' key with no record and no marketplace dir exits 1 instead of proceeding."""
    with sandboxed_cpi() as (cpi, _root):
        try:
            cpi.do_uninstall("foo@synced")
        except SystemExit as exc:
            if exc.code != 1:
                return f"FAIL: expected SystemExit(1) from the ownership gate, got SystemExit({exc.code!r})"
            return "PASS"
        return "FAIL: do_uninstall returned normally for an unowned key — the ownership gate did not fire"


def check_uninstall_synced_key_leaves_settings_untouched() -> str:
    """A refused uninstall leaves settings.local.json byte-identical — the gate exits before any write."""
    with sandboxed_cpi() as (cpi, _root):
        settings_path: Path = cpi.SETTINGS_TARGET
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        # Both keys the pre-gate code popped, plus a distinctive indent, so a rewrite
        # differs in bytes even where the surviving content would have matched.
        original = json.dumps(
            {
                "enabledPlugins": {"foo@synced": True, "other@mp": True},
                "extraKnownMarketplaces": {
                    "synced": {"source": {"source": "github", "repo": "a/b"}}
                },
            },
            indent=4,
        )
        settings_path.write_text(original, encoding="utf-8")
        before = settings_path.read_bytes()

        with contextlib.suppress(SystemExit):
            cpi.do_uninstall("foo@synced")

        after = settings_path.read_bytes()
        if after != before:
            return f"FAIL: settings.local.json was mutated by a refused uninstall — now {after.decode('utf-8')!r}"
        strays = sorted(
            p.name for p in settings_path.parent.glob(f"{settings_path.name}.*.bak")
        )
        if strays:
            return f"FAIL: a refused uninstall still ran save_json_safe (backups created: {strays})"
        return "PASS"


def check_uninstall_half_removed_install_still_cleans_up() -> str:
    """A recorded plugin whose directory is already gone still uninstalls — the gate must not block cleanup."""
    key = "bar@local-mp"
    with sandboxed_cpi() as (cpi, _root):
        _write_installed(cpi, {key: {"marketplace": "local-mp", "name": "bar"}})
        settings_path: Path = cpi.SETTINGS_TARGET
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps({"enabledPlugins": {key: True}}), encoding="utf-8"
        )

        mp_dir = Path(cpi.MARKETPLACES_DIR) / "local-mp"
        if mp_dir.exists():
            return f"FAIL: fixture invalid — {mp_dir} exists, so this is not the half-removed case"

        try:
            cpi.do_uninstall(key)
        except SystemExit as exc:
            return f"FAIL: the gate blocked a deliberate cleanup of a recorded plugin — SystemExit({exc.code!r})"

        remaining = _read_installed_plugins(cpi)
        if key in remaining:
            return f"FAIL: {key} survived in installed_plugins.json — plugins map is {remaining}"
        return "PASS"


def check_uninstall_owned_plugin_proceeds() -> str:
    """A normally-installed plugin uninstalls cleanly — directory removed, enabledPlugins key dropped."""
    key = "baz@local-mp"
    with sandboxed_cpi() as (cpi, _root):
        plug_dir = Path(cpi.MARKETPLACES_DIR) / "local-mp" / "plugins" / "baz"
        plug_dir.mkdir(parents=True)
        (plug_dir / "plugin.json").write_text('{"name": "baz"}', encoding="utf-8")

        _write_installed(cpi, {key: {"marketplace": "local-mp", "name": "baz"}})
        settings_path: Path = cpi.SETTINGS_TARGET
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps(
                {
                    "enabledPlugins": {key: True, "keep@other-mp": True},
                    "extraKnownMarketplaces": {
                        "local-mp": {"source": {"source": "github", "repo": "a/b"}}
                    },
                }
            ),
            encoding="utf-8",
        )

        try:
            cpi.do_uninstall(key)
        except SystemExit as exc:
            return f"FAIL: an owned plugin was refused — SystemExit({exc.code!r})"

        if plug_dir.exists():
            return f"FAIL: plugin directory survived the uninstall: {plug_dir}"
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        enabled = settings.get("enabledPlugins", {})
        if key in enabled:
            return f"FAIL: {key} survived in enabledPlugins — now {enabled}"
        if "keep@other-mp" not in enabled:
            return f"FAIL: an unrelated enabledPlugins entry was collateral damage — now {enabled}"
        if key in _read_installed_plugins(cpi):
            return f"FAIL: {key} survived in installed_plugins.json"
        return "PASS"


CHECKS = [
    "check_uninstall_synced_key_refuses",
    "check_uninstall_synced_key_leaves_settings_untouched",
    "check_uninstall_half_removed_install_still_cleans_up",
    "check_uninstall_owned_plugin_proceeds",
]


# ── pytest wrappers (the publish pipeline runs `pytest tests/`) ──

try:
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.mark.parametrize("check_name", CHECKS)
    def test_uninstall_ownership_gate(check_name: str) -> None:
        outcome = globals()[check_name]()
        assert outcome.startswith("PASS"), outcome

except ImportError:
    pass


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    return run_table(CHECKS, lambda n: globals()[n](), lambda n: globals()[n].__doc__)


if __name__ == "__main__":
    sys.exit(main())
