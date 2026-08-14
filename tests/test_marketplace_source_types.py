#!/usr/bin/env python3
"""Real tests pinning marketplace source-type invariants (no mocks — imports the real modules).

Claude Code 2.1.232's own accepted-source-type set (verified in the binary:
`new Set(["npm","url","github","git-subdir","archive","command","unsupported"])`) is the
ceiling on what `validate_marketplace.py` may accept: a wider `VALID_SOURCE_TYPES` here would
pass a marketplace entry the platform silently drops at load, and a narrower one would reject
an entry Claude Code actually installs. "archive" (2.1.224) and "command" (2.1.229) are real,
recent additions; "pip" was never in Claude Code's set; "unsupported" is the platform's own
internal sentinel for a dropped entry and must never be authorable.

`SOURCE_REQUIRED_FIELDS` is a second table keyed the same way — a key added to one table and
forgotten in the other is exactly the kind of drift that passes review and fails at install
time, so this file asserts the two tables' key sets are identical.

`claude-plugin-install.py` merges two settings.json spellings for known marketplaces
(`extraKnownMarketplaces` and the 2.1.232 alias `additionalMarketplaces`) so a marketplace
registered under either spelling is recognised. The merge order matters: the canonical key
must win a name collision, because writes always go to the canonical key.

Runs two ways:

  uv run --with pytest pytest tests/test_marketplace_source_types.py -q
  uv run python tests/test_marketplace_source_types.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(PLUGIN_ROOT / "tests"))
sys.path.insert(0, str(SCRIPTS_DIR))

from _table_runner import (
    run_table,  # noqa: E402  # pyright: ignore[reportMissingImports]
)

import validate_marketplace as vm  # noqa: E402  # pyright: ignore[reportMissingImports]


def _load_claude_plugin_install() -> ModuleType:
    """Import `claude-plugin-install.py` (a dashed filename — no plain `import` works).

    `main()` in that file is guarded by `if __name__ == "__main__":`, so a real
    `spec.loader.exec_module()` import runs only module-level code (imports, constant
    tables, function/class definitions) — no CLI side effects. Verified by reading the
    file's tail before relying on this loader; if that guard is ever removed this import
    would start executing the CLI, so prefer the real import over re-parsing the source
    with regex — it exercises the actual code, not a text approximation of it.
    """
    path = SCRIPTS_DIR / "claude-plugin-install.py"
    spec = importlib.util.spec_from_file_location("claude_plugin_install", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not build an import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CPI = _load_claude_plugin_install()


# ── The checks (shared by pytest wrappers and the standalone runner) ──

EXPECTED_SOURCE_TYPES = {"github", "url", "npm", "git-subdir", "archive", "command"}


def check_valid_source_types_matches_claude_code() -> str:
    """VALID_SOURCE_TYPES equals Claude Code 2.1.232's own accepted set exactly."""
    if vm.VALID_SOURCE_TYPES != EXPECTED_SOURCE_TYPES:
        missing = EXPECTED_SOURCE_TYPES - vm.VALID_SOURCE_TYPES
        extra = vm.VALID_SOURCE_TYPES - EXPECTED_SOURCE_TYPES
        return f"FAIL: VALID_SOURCE_TYPES drifted — missing={sorted(missing)} extra={sorted(extra)}"
    return "PASS"


def check_archive_and_command_are_present() -> str:
    """'archive' (2.1.224) and 'command' (2.1.229) are authorable source types."""
    missing = {"archive", "command"} - vm.VALID_SOURCE_TYPES
    if missing:
        return f"FAIL: missing recent source type(s): {sorted(missing)}"
    return "PASS"


def check_pip_is_not_a_valid_source_type() -> str:
    """'pip' was never in Claude Code's accepted set and stays rejected here."""
    if "pip" in vm.VALID_SOURCE_TYPES:
        return "FAIL: 'pip' is present in VALID_SOURCE_TYPES but Claude Code never accepted it"
    return "PASS"


def check_unsupported_is_not_authorable() -> str:
    """'unsupported' is Claude Code's internal drop-sentinel, never an authorable type."""
    if "unsupported" in vm.VALID_SOURCE_TYPES:
        return "FAIL: 'unsupported' is authorable — it is Claude Code's internal sentinel for a dropped entry"
    return "PASS"


def check_valid_source_types_floor() -> str:
    """A vacuity floor: VALID_SOURCE_TYPES has at least 6 entries.

    Without this floor, deleting entries from VALID_SOURCE_TYPES could make every
    per-type check above pass vacuously (an empty or near-empty set still satisfies
    "'pip' not in set" and "'unsupported' not in set").
    """
    if len(vm.VALID_SOURCE_TYPES) < 6:
        return f"FAIL: VALID_SOURCE_TYPES has only {len(vm.VALID_SOURCE_TYPES)} entries, below the floor of 6"
    return "PASS"


def check_source_required_fields_has_archive_and_command() -> str:
    """SOURCE_REQUIRED_FIELDS maps 'archive' -> {url} and 'command' -> {command}."""
    offenders = []
    if vm.SOURCE_REQUIRED_FIELDS.get("archive") != {"url"}:
        offenders.append(f"archive -> {vm.SOURCE_REQUIRED_FIELDS.get('archive')!r} (want {{'url'}})")
    if vm.SOURCE_REQUIRED_FIELDS.get("command") != {"command"}:
        offenders.append(f"command -> {vm.SOURCE_REQUIRED_FIELDS.get('command')!r} (want {{'command'}})")
    if offenders:
        return f"FAIL: {'; '.join(offenders)}"
    return "PASS"


def check_source_required_fields_keys_match_valid_source_types() -> str:
    """No drift between VALID_SOURCE_TYPES and SOURCE_REQUIRED_FIELDS's key set."""
    required_keys = set(vm.SOURCE_REQUIRED_FIELDS)
    if required_keys != vm.VALID_SOURCE_TYPES:
        missing_in_required = vm.VALID_SOURCE_TYPES - required_keys
        extra_in_required = required_keys - vm.VALID_SOURCE_TYPES
        return (
            "FAIL: table key sets diverged — "
            f"in VALID_SOURCE_TYPES but not SOURCE_REQUIRED_FIELDS={sorted(missing_in_required)}, "
            f"in SOURCE_REQUIRED_FIELDS but not VALID_SOURCE_TYPES={sorted(extra_in_required)}"
        )
    return "PASS"


def check_validate_archive_source_accepts_plain_https() -> str:
    """A plain https:// archive url produces no results."""
    results = vm.validate_archive_source("plugin-a", {"url": "https://example.com/p.zip"}, "marketplace.json")
    if results:
        return f"FAIL: expected no results, got {[r.message for r in results]}"
    return "PASS"


def check_validate_archive_source_rejects_non_https() -> str:
    """A non-https archive url is a MAJOR — Claude Code refuses it outright."""
    results = vm.validate_archive_source("plugin-a", {"url": "http://example.com/p.zip"}, "marketplace.json")
    if not any(r.level == "MAJOR" for r in results):
        return f"FAIL: expected a MAJOR result for http:// url, got {[(r.level, r.message) for r in results]}"
    return "PASS"


def check_validate_archive_source_rejects_cloud_metadata_host() -> str:
    """An archive url pointing at the cloud-metadata IP is a MAJOR (SSRF guard)."""
    results = vm.validate_archive_source(
        "plugin-a", {"url": "https://169.254.169.254/p.zip"}, "marketplace.json"
    )
    if not any(r.level == "MAJOR" for r in results):
        return f"FAIL: expected a MAJOR result for cloud-metadata host, got {[(r.level, r.message) for r in results]}"
    return "PASS"


def check_validate_archive_source_rejects_localhost() -> str:
    """An archive url pointing at localhost is a MAJOR (loopback guard)."""
    results = vm.validate_archive_source("plugin-a", {"url": "https://localhost/p.zip"}, "marketplace.json")
    if not any(r.level == "MAJOR" for r in results):
        return f"FAIL: expected a MAJOR result for localhost host, got {[(r.level, r.message) for r in results]}"
    return "PASS"


def check_validate_archive_source_defers_missing_url() -> str:
    """A missing 'url' key produces no results — the required-fields check owns that case."""
    results = vm.validate_archive_source("plugin-a", {}, "marketplace.json")
    if results:
        return f"FAIL: expected no results for a missing url (owned elsewhere), got {[r.message for r in results]}"
    return "PASS"


def check_known_marketplaces_merges_both_spellings() -> str:
    """_known_marketplaces merges extraKnownMarketplaces and the additionalMarketplaces alias."""
    settings = {
        "extraKnownMarketplaces": {"canonical-mp": {"source": {"source": "github", "repo": "a/b"}}},
        "additionalMarketplaces": {"alias-mp": {"source": {"source": "github", "repo": "c/d"}}},
    }
    merged = CPI._known_marketplaces(settings)
    if set(merged) != {"canonical-mp", "alias-mp"}:
        return f"FAIL: expected both entries merged, got keys {sorted(merged)}"
    return "PASS"


def check_known_marketplaces_canonical_wins_on_name_collision() -> str:
    """On a duplicate marketplace name, the canonical extraKnownMarketplaces entry wins."""
    settings = {
        "extraKnownMarketplaces": {"dup-mp": {"source": {"source": "github", "repo": "canonical/repo"}}},
        "additionalMarketplaces": {"dup-mp": {"source": {"source": "github", "repo": "alias/repo"}}},
    }
    merged = CPI._known_marketplaces(settings)
    got = merged.get("dup-mp", {}).get("source", {}).get("repo")
    if got != "canonical/repo":
        return f"FAIL: expected the canonical entry to win, got repo={got!r}"
    return "PASS"


def check_known_marketplaces_ignores_non_dict_values() -> str:
    """A non-dict value under either known-marketplaces key is ignored, not raised on."""
    settings = {
        "extraKnownMarketplaces": "not-a-dict",
        "additionalMarketplaces": ["also", "not", "a", "dict"],
    }
    merged = CPI._known_marketplaces(settings)
    if merged != {}:
        return f"FAIL: expected an empty merge for non-dict inputs, got {merged}"
    return "PASS"


def check_known_marketplaces_empty_settings_round_trips() -> str:
    """An empty settings dict merges to an empty dict."""
    merged = CPI._known_marketplaces({})
    if merged != {}:
        return f"FAIL: expected {{}} for empty settings, got {merged}"
    return "PASS"


CHECKS = [
    "check_valid_source_types_matches_claude_code",
    "check_archive_and_command_are_present",
    "check_pip_is_not_a_valid_source_type",
    "check_unsupported_is_not_authorable",
    "check_valid_source_types_floor",
    "check_source_required_fields_has_archive_and_command",
    "check_source_required_fields_keys_match_valid_source_types",
    "check_validate_archive_source_accepts_plain_https",
    "check_validate_archive_source_rejects_non_https",
    "check_validate_archive_source_rejects_cloud_metadata_host",
    "check_validate_archive_source_rejects_localhost",
    "check_validate_archive_source_defers_missing_url",
    "check_known_marketplaces_merges_both_spellings",
    "check_known_marketplaces_canonical_wins_on_name_collision",
    "check_known_marketplaces_ignores_non_dict_values",
    "check_known_marketplaces_empty_settings_round_trips",
]


# ── pytest wrappers (the publish pipeline runs `pytest tests/`) ──

try:
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.mark.parametrize("check_name", CHECKS)
    def test_marketplace_source_types(check_name: str) -> None:
        outcome = globals()[check_name]()
        assert outcome.startswith("PASS"), outcome

except ImportError:
    pass


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    return run_table(CHECKS, lambda n: globals()[n](), lambda n: globals()[n].__doc__)


if __name__ == "__main__":
    sys.exit(main())
