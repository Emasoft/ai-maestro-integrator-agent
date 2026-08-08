#!/usr/bin/env python3
"""Unified publish pipeline: bypass-guard -> lint -> validate (remote CPV) -> test -> bump -> badge -> changelog -> commit -> push -> release.

Modes:
  --gate                  Pre-push gate: orchestrator check + lint + validate + tests
                          only (no bump/push). Called by git-hooks/pre-push automatically.
  --install-hook          Install git-hooks/pre-push into .git/hooks/ and set core.hooksPath.
  --install-branch-rules  Apply the cpv-branch-rules GitHub ruleset to the origin
                          (server-side CI enforcement — run once after first push).
  (no flag)               Full release pipeline (11 stages, fail-fast). The bump type
                          is AUTO-DETECTED via `git-cliff --bumped-version` from the
                          conventional commits on HEAD.
  --patch/--minor/--major Force a specific bump type (overrides auto-detection).

Pipeline stages (all fail-fast — any non-zero exit aborts):
   0. Bypass guard — reject CPV_SKIP_*, SKIP_*, NO_VERIFY env vars
   1. Check working tree is clean
   2. Lint files (ruff)
   3. Validate plugin (uvx cpv-remote-validate plugin . --strict — fetches
      the canonical CPV validator from GitHub so this plugin never vendors
      a local copy and never drifts from upstream rules)
   4. Run tests (pytest)
   5. Marketplace-registration check (Layout A: notify workflow + PAT secret +
      remote marketplace.json registration + remote receiver workflow;
      Layout B: must run from marketplace root + nested plugin must be listed)
   6. Check version consistency across all sources
   7. Bump version in plugin.json, pyproject.toml, and __version__ vars
   8. Update README version badge
   9. Generate changelog (git-cliff)
  10. Commit, tag, push
  11. Create GitHub release (gh CLI)

Gate stages (--gate mode, called by pre-push hook):
   G0. Orchestrator check — direct `git push` is blocked; only publish.py
       may initiate a push (verified via process ancestry, NOT env vars).
   G1. Version bump check (local vs remote, auto-detects origin/HEAD)
   G2. Lint (ruff)
   G3. Validate (uvx cpv-remote-validate plugin . --strict)
   G4. Tests (pytest)

Usage:
    uv run python scripts/publish.py                      # auto-bump from git-cliff
    uv run python scripts/publish.py --gate
    uv run python scripts/publish.py --install-hook
    uv run python scripts/publish.py --install-branch-rules
    uv run python scripts/publish.py --patch              # force patch
    uv run python scripts/publish.py --minor              # force minor
    uv run python scripts/publish.py --major              # force major
    uv run python scripts/publish.py --dry-run            # preview (auto-bump)

Cornerstone rule: a plugin CANNOT be pushed unless validation passes with
0 issues (WARNING allowed). There are no exceptions and no bypass flags.
Every push is blocked unless scripts/publish.py orchestrates it end-to-end
AND stage_validate / stage_tests / stage_lint all succeed.
"""

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Load gh / git retry wrappers from the sibling module so every push +
# `gh release create` survives transient github.com hiccups (the retry
# pattern from ~/.claude/rules/github-timeouts.md). Shipped verbatim
# from the canonical CPV install via gen_cpv_network_resilience_py().
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from cpv_network_resilience import gh_with_retry, git_with_retry
except ImportError:
    # Fallback: scripts/cpv_network_resilience.py was not shipped with this
    # plugin (older scaffold). Define no-op shims so publish.py still works,
    # but warn so the user knows to refresh via `cpv standardize --force-templates`.
    print(
        "[publish.py] WARNING: scripts/cpv_network_resilience.py missing — "
        "network calls will not auto-retry on transient errors. "
        "Run `cpv standardize --force-templates` to refresh.",
        file=sys.stderr,
    )
    def gh_with_retry(cmd, **kwargs):  # type: ignore[no-redef, misc]
        kwargs.pop("max_attempts", None)
        kwargs.pop("backoff", None)
        kwargs.setdefault("check", True)
        kwargs.setdefault("capture_output", False)
        return subprocess.run(cmd, **kwargs)
    def git_with_retry(cmd, **kwargs):  # type: ignore[no-redef, misc]
        kwargs.pop("max_attempts", None)
        kwargs.pop("backoff", None)
        kwargs.setdefault("check", True)
        kwargs.setdefault("capture_output", False)
        return subprocess.run(cmd, **kwargs)

# -- ANSI colors ---------------------------------------------------------------


def _colors_ok() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


_C = _colors_ok()
RED    = "\033[0;31m" if _C else ""
GREEN  = "\033[0;32m" if _C else ""
YELLOW = "\033[1;33m" if _C else ""
BLUE   = "\033[0;34m" if _C else ""
BOLD   = "\033[1m" if _C else ""
DIM    = "\033[2m" if _C else ""
NC     = "\033[0m" if _C else ""


# -- Helpers -------------------------------------------------------------------


def cprint(msg: str) -> None:
    print(msg, flush=True)

def run(
    cmd: list[str], cwd: Path | None = None, *, check: bool = True, capture: bool = False,
    timeout: int = 300,
) -> subprocess.CompletedProcess[str]:
    """Run a command, stream output, fail-fast on error.

    `timeout` is a parameter rather than a hardcoded 300s because the stages do
    not remotely resemble each other in duration: a `git rev-parse` is
    milliseconds, while remote CPV validation cold-builds from git and routinely
    runs 3.5 minutes ALONE. Sharing one ceiling meant the slowest stage on the
    machine set the limit for everything, and it was set for the fastest.

    Measured 2026-08-08: a v1.4.1 publish died at exactly 300s in stage 4 while
    two other CPV validations were running concurrently on this host (other
    plugins publishing). Nothing was wrong with the plugin — the ceiling was
    simply below the real duration under contention.

    A breach is reported, not raised. Previously TimeoutExpired escaped as a
    30-line traceback ending in subprocess internals, which reads like a crash in
    the pipeline rather than "this command ran out of time" — and buries the one
    fact the operator needs (which command, and how long it was given).
    """
    cprint(f"  {BLUE}$ {' '.join(cmd)}{NC}")
    try:
        result = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True,
                                capture_output=capture, timeout=timeout)
    except subprocess.TimeoutExpired:
        cprint(f"  {RED}TIMED OUT after {timeout}s: {' '.join(cmd[:4])}…{NC}")
        cprint(f"  {YELLOW}This is a timeout, NOT a validation verdict — nothing was "
               f"judged. Re-run when the host is quieter, or raise the stage timeout.{NC}")
        sys.exit(1)
    if check and result.returncode != 0:
        cprint(f"  {RED}Command failed (exit {result.returncode}){NC}")
        sys.exit(result.returncode)
    return result

def get_repo_root() -> Path:
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, check=True)
    return Path(r.stdout.strip())


# -- gh-auth precheck (TRDD-bbff5bc5) ---------------------------------------


def _parse_owner_repo_from_remote(remote_url: str) -> tuple[str, str] | None:
    """Extract (owner, repo) from `git@host:owner/repo.git` or
    `https://host/owner/repo[.git]`. Returns None on unparseable input.
    """
    if not remote_url:
        return None
    url = remote_url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    match = re.search(r"[:/]([^:/\s]+)/([^/\s]+)$", url)
    if not match:
        return None
    return match.group(1), match.group(2)


def _resolve_owner_repo(plugin_root: Path) -> tuple[str, str]:
    """Read remote.origin.url, parse (owner, repo). Exit 1 on failure."""
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=str(plugin_root), capture_output=True, text=True, timeout=10, check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        cprint(f"  {RED}Could not read remote.origin.url. Run: git remote add origin <url>{NC}")
        sys.exit(1)
    parsed = _parse_owner_repo_from_remote(result.stdout.strip())
    if parsed is None:
        cprint(f"  {RED}Could not parse owner/repo from remote URL: {result.stdout.strip()!r}{NC}")
        sys.exit(1)
    return parsed


def _ensure_gh_auth(owner: str, repo: str) -> None:
    """Verify gh CLI installed + authenticated + push perm on owner/repo.

    Called BEFORE every push gate. Exits 1 on any of: gh missing, not
    authed, no push permission. Per TRDD-bbff5bc5 §4.1: never invokes
    `gh auth token`; uses only `gh auth status` and `gh api` so PAT-shaped
    strings cannot leak to stdout/stderr.
    """
    if os.environ.get("CPV_SKIP_GH_AUTH_CHECK") == "1":
        return
    gh_bin = shutil.which("gh")
    if gh_bin is None:
        cprint(f"  {RED}gh CLI not installed. Install: brew install gh{NC}")
        sys.exit(1)
    # 60s timeout (was 15s) — slow-link tolerance; downstream push gates
    # still enforce real auth on failure.
    try:
        status = subprocess.run(
            [gh_bin, "auth", "status"],
            capture_output=True, text=True, timeout=60, check=False,
        )
    except subprocess.TimeoutExpired:
        cprint(f"  {RED}gh auth status timed out after 60 s — flaky network. Retry, or set CPV_SKIP_GH_AUTH_CHECK=1.{NC}")
        sys.exit(1)
    if status.returncode != 0:
        cprint(f"  {RED}gh CLI not authenticated.{NC}")
        cprint(f"  {YELLOW}Run: gh auth login --hostname github.com --git-protocol https{NC}")
        sys.exit(1)
    try:
        perms = subprocess.run(
            [gh_bin, "api", f"repos/{owner}/{repo}", "--jq", ".permissions.push"],
            capture_output=True, text=True, timeout=60, check=False,
        )
    except subprocess.TimeoutExpired:
        cprint(f"  {RED}gh permission check timed out after 60 s — set CPV_SKIP_GH_AUTH_CHECK=1 to bypass this gate.{NC}")
        sys.exit(1)
    if perms.returncode != 0 or perms.stdout.strip() != "true":
        active_login = ""
        for line in (status.stdout + status.stderr).splitlines():
            line = line.strip()
            if "account " in line and ("Logged in" in line or "Active" in line):
                m = re.search(r"account\s+(\S+)", line)
                if m:
                    active_login = m.group(1)
                    break
        login_str = f" '{active_login}'" if active_login else ""
        cprint(f"  {RED}gh user{login_str} has no push permission on {owner}/{repo}.{NC}")
        cprint(f"  {YELLOW}Diagnose:{NC}")
        cprint(f"  {YELLOW}  1. Ask the repo owner to add you as a collaborator with write access.{NC}")
        cprint(f"  {YELLOW}  2. If you have multiple gh accounts: gh auth status; gh auth switch{NC}")
        cprint(f"  {YELLOW}  3. If using a fine-grained token: ensure 'Contents: write' on this repo.{NC}")
        sys.exit(1)


# -- Semver --------------------------------------------------------------------

def parse_semver(version: str) -> tuple[int, int, int] | None:
    """Parse 'X.Y.Z' into (major, minor, patch)."""
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version.strip())
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))

def bump_semver(current: str, bump_type: str) -> str | None:
    """Bump version by major/minor/patch. Returns new version string or None."""
    parsed = parse_semver(current)
    if not parsed:
        return None
    major, minor, patch = parsed
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    return None


# -- Version readers/writers ---------------------------------------------------

def get_current_version(plugin_root: Path) -> str | None:
    """Read version from .claude-plugin/plugin.json."""
    pj = plugin_root / ".claude-plugin" / "plugin.json"
    if not pj.is_file():
        return None
    try:
        data = json.loads(pj.read_text(encoding="utf-8"))
        ver = data.get("version")
        return str(ver) if ver is not None else None
    except (json.JSONDecodeError, OSError):
        return None

def get_plugin_name(plugin_root: Path) -> str | None:
    """Read `name` from .claude-plugin/plugin.json."""
    pj = plugin_root / ".claude-plugin" / "plugin.json"
    if not pj.is_file():
        return None
    try:
        data = json.loads(pj.read_text(encoding="utf-8"))
        name = data.get("name")
        return str(name) if name else None
    except (json.JSONDecodeError, OSError):
        return None


def resolver_tag(plugin_root: Path, version: str) -> str:
    """Build the `{plugin-name}--v{version}` tag the Claude Code resolver needs.

    A plain `v{version}` tag is NOT enough. Claude Code resolves a VERSIONED
    plugin dependency (`{"name": "x", "version": "^2.7.0"}`) only via a
    `{name}--v{version}` tag; with just `v{version}` the resolver reports
    "has no git tag satisfying >=..." even though `git ls-remote --tags` clearly
    lists the versions. That failure grounded the whole fleet for a day
    (ai-maestro TRDD-JT3U4ZVM, integrator#22), so this tag is load-bearing for
    every DOWNSTREAM plugin that depends on this one.

    HARD-FAILS on a nameless manifest rather than returning a degraded tag: a
    silently-wrong tag name is exactly the failure mode being fixed here.

    Do NOT reach for `claude plugin tag <tagname>` instead — that CLI's
    positional argument is a PATH, not a tag name, so it silently creates
    nothing and the publish "succeeds" with the tag still missing.
    """
    name = get_plugin_name(plugin_root)
    if not name:
        raise SystemExit(
            "BLOCKED: .claude-plugin/plugin.json has no `name` — cannot build the "
            "{name}--v{version} resolver tag that downstream dependants need."
        )
    return f"{name}--v{version}"


def update_plugin_json(root: Path, new_ver: str) -> tuple[bool, str]:
    """Write version to .claude-plugin/plugin.json."""
    pj = root / ".claude-plugin" / "plugin.json"
    if not pj.is_file():
        return False, "plugin.json not found"
    try:
        data = json.loads(pj.read_text(encoding="utf-8"))
        data["version"] = new_ver
        pj.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return True, f"plugin.json -> {new_ver}"
    except (json.JSONDecodeError, OSError) as e:
        return False, f"plugin.json update failed: {e}"

def update_self_marketplace_json(root: Path, new_ver: str) -> tuple[bool, str]:
    """Write version to .claude-plugin/marketplace.json (Layout C — both metadata and self-entry)."""
    mp = root / ".claude-plugin" / "marketplace.json"
    if not mp.is_file():
        return False, "no marketplace.json (not Layout C)"
    try:
        data = json.loads(mp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return False, f"marketplace.json read failed: {e}"
    # Bump metadata.version if present
    metadata = data.get("metadata")
    if isinstance(metadata, dict):
        metadata["version"] = new_ver
    # Bump the self-entry's version (the entry whose name matches plugin.json's name AND source is "./")
    plugin_json_path = root / ".claude-plugin" / "plugin.json"
    plugin_name: str | None = None
    if plugin_json_path.is_file():
        try:
            pdata = json.loads(plugin_json_path.read_text(encoding="utf-8"))
            plugin_name = pdata.get("name")
        except (json.JSONDecodeError, OSError):
            plugin_name = None
    plugins = data.get("plugins")
    bumped_entry = False
    if isinstance(plugins, list):
        for entry in plugins:
            if not isinstance(entry, dict):
                continue
            entry_name = entry.get("name")
            entry_source = entry.get("source")
            is_self = (
                (entry_name == plugin_name or plugin_name is None)
                and entry_source in ("./", {"source": "directory", "path": "./"})
            )
            if is_self:
                entry["version"] = new_ver
                bumped_entry = True
                break
    try:
        mp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except OSError as e:
        return False, f"marketplace.json write failed: {e}"
    if bumped_entry:
        return True, f"marketplace.json (metadata + self-entry) -> {new_ver}"
    return True, f"marketplace.json (metadata only — no self-entry matched) -> {new_ver}"

def update_pyproject_toml(root: Path, new_ver: str) -> tuple[bool, str]:
    """Write version to pyproject.toml."""
    pp = root / "pyproject.toml"
    if not pp.is_file():
        return False, "pyproject.toml not found"
    try:
        content = pp.read_text(encoding="utf-8")
        updated = re.sub(
            r'^(version\s*=\s*")[^"]*(")',
            rf'\g<1>{new_ver}\2',
            content,
            count=1,
            flags=re.MULTILINE,
        )
        if updated == content:
            return False, "pyproject.toml: version field not found"
        pp.write_text(updated, encoding="utf-8")
        return True, f"pyproject.toml -> {new_ver}"
    except OSError as e:
        return False, f"pyproject.toml update failed: {e}"

def update_python_versions(root: Path, new_ver: str) -> list[tuple[bool, str]]:
    """Update __version__ = '...' in all .py files under scripts/."""
    results: list[tuple[bool, str]] = []
    scripts_dir = root / "scripts"
    if not scripts_dir.is_dir():
        return results
    pattern = re.compile(r'^(__version__\s*=\s*["\'])([^"\']*)(["\']\s*)$', re.MULTILINE)
    for py_file in scripts_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
        except OSError:
            continue
        if not pattern.search(content):
            continue
        updated = pattern.sub(rf"\g<1>{new_ver}\3", content)
        if updated != content:
            py_file.write_text(updated, encoding="utf-8")
            results.append((True, f"{py_file.relative_to(root)} -> {new_ver}"))
    return results

def check_version_consistency(root: Path) -> tuple[bool, str]:
    """Verify all version sources match. Includes marketplace.json metadata
    and self-entry (Layout C) when present."""
    versions: dict[str, str | None] = {}

    # plugin.json
    pj = root / ".claude-plugin" / "plugin.json"
    if pj.is_file():
        try:
            versions["plugin.json"] = json.loads(pj.read_text(encoding="utf-8")).get("version")
        except (json.JSONDecodeError, OSError):
            versions["plugin.json"] = None

    # marketplace.json (Layout C) — both metadata.version and the self-entry's version
    mp = root / ".claude-plugin" / "marketplace.json"
    if mp.is_file():
        try:
            mp_data = json.loads(mp.read_text(encoding="utf-8"))
            md = mp_data.get("metadata")
            if isinstance(md, dict):
                versions["marketplace.json:metadata"] = md.get("version")
            plugins_arr = mp_data.get("plugins")
            if isinstance(plugins_arr, list):
                for entry in plugins_arr:
                    if not isinstance(entry, dict):
                        continue
                    src = entry.get("source")
                    if src == "./" or (
                        isinstance(src, dict) and src.get("source") == "directory" and src.get("path") == "./"
                    ):
                        versions["marketplace.json:self-entry"] = entry.get("version")
                        break
        except (json.JSONDecodeError, OSError):
            versions["marketplace.json"] = None

    # pyproject.toml
    pp = root / "pyproject.toml"
    if pp.is_file():
        m = re.search(r'^version\s*=\s*"([^"]*)"', pp.read_text(encoding="utf-8"), re.MULTILINE)
        versions["pyproject.toml"] = m.group(1) if m else None

    found = {k: v for k, v in versions.items() if v is not None}
    if not found:
        return False, "No version sources found"
    unique = set(found.values())
    if len(unique) == 1:
        return True, f"All versions match: {unique.pop()}"
    details = ", ".join(f"{k}={v}" for k, v in found.items())
    return False, f"Version mismatch: {details}"

def do_bump(root: Path, new_ver: str, dry_run: bool = False) -> bool:
    """Orchestrate all version updates. Detects Layout C (marketplace.json at repo root)
    and bumps both manifests atomically when present."""
    cprint(f"\n{BOLD}Bumping to {new_ver}{' (dry-run)' if dry_run else ''}{NC}")

    is_layout_c = (root / ".claude-plugin" / "marketplace.json").is_file()

    if dry_run:
        cprint(f"  Would update plugin.json -> {new_ver}")
        if is_layout_c:
            cprint(f"  Would update marketplace.json (metadata + self-entry, Layout C) -> {new_ver}")
        cprint(f"  Would update pyproject.toml -> {new_ver}")
        cprint(f"  Would update __version__ vars -> {new_ver}")
        return True

    ok1, msg1 = update_plugin_json(root, new_ver)
    cprint(f"  {'OK' if ok1 else 'FAIL'}: {msg1}")

    ok_mp = True
    if is_layout_c:
        ok_mp, msg_mp = update_self_marketplace_json(root, new_ver)
        cprint(f"  {'OK' if ok_mp else 'FAIL'}: {msg_mp}")

    ok2, msg2 = update_pyproject_toml(root, new_ver)
    cprint(f"  {'OK' if ok2 else 'FAIL'}: {msg2}")

    py_results = update_python_versions(root, new_ver)
    for ok, msg in py_results:
        cprint(f"  {'OK' if ok else 'FAIL'}: {msg}")

    return ok1 and ok2 and ok_mp


# -- Hook installer ------------------------------------------------------------

def install_hook(root: Path) -> int:
    """Copy git-hooks/pre-push to .git/hooks/pre-push and set core.hooksPath."""
    cprint(f"\n{BOLD}Installing git hooks...{NC}")
    source = root / "git-hooks" / "pre-push"
    if not source.is_file():
        cprint(f"  {RED}git-hooks/pre-push not found{NC}")
        return 1
    git_dir = root / ".git"
    if not git_dir.is_dir():
        cprint(f"  {RED}.git/ not found — is this a git repository?{NC}")
        return 1
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    dest = hooks_dir / "pre-push"
    shutil.copy2(source, dest)
    dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    cprint(f"  {GREEN}Installed: git-hooks/pre-push -> .git/hooks/pre-push{NC}")
    # Also set core.hooksPath so git finds hooks in git-hooks/ directly
    subprocess.run(["git", "config", "core.hooksPath", "git-hooks"],
                   cwd=str(root), check=False)
    cprint(f"  {GREEN}Set git config core.hooksPath = git-hooks{NC}")
    return 0


def _get_origin_slug(root: Path) -> str | None:
    """Return OWNER/REPO parsed from the current repo's origin remote, or None."""
    try:
        r = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True, text=True, cwd=str(root), check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    url = r.stdout.strip()
    # Handle git@github.com:OWNER/REPO.git and https://github.com/OWNER/REPO.git
    if url.startswith("git@"):
        _, _, path = url.partition(":")
    elif "//" in url:
        _, _, path = url.partition("//")
        # path is now "github.com/OWNER/REPO.git"
        path = path.split("/", 1)[1] if "/" in path else ""
    else:
        return None
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.strip("/").split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None
    return f"{parts[0]}/{parts[1]}"


# The two ruleset names that ARE the ratified baseline (manager-approval-defaults
# §F). Applying this pair as-is is EXEMPT; adding any OTHER ruleset that affects
# the default branch is NON-EXEMPT and needs MANAGER approval.
RATIFIED_BASELINE_RULESETS = ("baseline-history-protect", "baseline-pr-and-checks")


def _ratified_baseline_present(slug: str) -> bool | None:
    """Does `slug` already carry a ratified `baseline-*` ruleset?

    Returns True/False on a successful read, and **None when the list could not
    be read at all**. The distinction is the whole point: a bare `[]` on failure
    would read as "no baseline here", the caller would step aside, and the
    destructive command would run against precisely the repo nobody could
    inspect. Fail CLOSED — see the caller.

    Routed through gh_with_retry so a transient github.com hiccup is not the
    thing that decides a repo is unbaselined.
    """
    try:
        r = gh_with_retry(
            ["gh", "api", f"repos/{slug}/rulesets", "--jq", ".[].name"],
            check=False, capture_output=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if getattr(r, "returncode", 1) != 0:
        return None
    names = {ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()}
    return any(n in names for n in RATIFIED_BASELINE_RULESETS)


def install_branch_rules(root: Path) -> int:
    """Apply the cpv-branch-rules ruleset to the repo's GitHub origin.

    Auto-detects the OWNER/REPO slug from `git config remote.origin.url` and
    shells out to `uvx cpv-setup-branch-rules`. This is the server-side gate
    that enforces CI as a required status check — the local pre-push hook alone
    is bypassable with `git push --no-verify`, but a ruleset is enforced by
    GitHub itself.

    REFUSES on a repo that already carries the ratified baseline, because
    `cpv-setup-branch-rules` does NOT bring that baseline to spec — verified in
    its source at v5.3.0 (claude-plugins-validation#203):

      * `scripts/setup_branch_rules.py:110` — `RULESET_NAME = "cpv-branch-rules"`
        is hardcoded, and the file contains ZERO occurrences of `baseline-`, so
        it cannot target the ratified pair even in principle.
      * `:326 fetch_legacy_protection_rulesets()` classifies as "legacy" any
        ruleset whose rules intersect {pull_request, required_status_checks,
        required_signatures, code_quality} — which `baseline-pr-and-checks`
        always does.
      * `:694` then prints `gh api --method DELETE …/rulesets/<id>` for each.

    So on a baselined repo the command ADDS a non-ratified ruleset (§F
    NON-EXEMPT) and advises DELETING the ratified one. Do not remove this guard
    as over-caution: it was added after the command was actually run here and
    produced exactly that outcome.
    """
    cprint(f"\n{BOLD}Installing branch-protection ruleset...{NC}")
    slug = _get_origin_slug(root)
    if slug is None:
        cprint(f"  {RED}Could not read origin remote URL — skipping.{NC}")
        cprint(f"  {YELLOW}Set `git remote add origin <url>` first, then retry.{NC}")
        return 1
    cprint(f"  Target repo: {slug}")

    baselined = _ratified_baseline_present(slug)
    if baselined is None:
        cprint(f"  {RED}REFUSED: could not read the ruleset list for {slug}.{NC}")
        cprint(f"  {YELLOW}Failing closed — an unreadable list is NOT evidence that "
               f"no ratified baseline exists.{NC}")
        return 1
    if baselined:
        cprint(f"  {RED}REFUSED: {slug} already carries the ratified baseline.{NC}")
        cprint(f"  {YELLOW}cpv-setup-branch-rules would add a separate 'cpv-branch-rules' "
               f"ruleset (§F NON-EXEMPT) and advise DELETING baseline-pr-and-checks "
               f"(claude-plugins-validation#203).{NC}")
        cprint(f"  {YELLOW}To bring the ratified pair to spec, PUT the baseline-* rulesets "
               f"directly instead.{NC}")
        return 1
    try:
        r = subprocess.run(
            [
                "uvx",
                "--from",
                "git+https://github.com/Emasoft/claude-plugins-validation@v5.3.0",
                "--with",
                "pyyaml",
                "cpv-setup-branch-rules",
                slug,
            ],
            cwd=str(root),
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        cprint(f"  {RED}uvx call failed: {exc}{NC}")
        return 1
    if r.returncode != 0:
        cprint(f"  {RED}cpv-setup-branch-rules exited with code {r.returncode}{NC}")
        return r.returncode
    cprint(f"  {GREEN}Branch rules applied to {slug}.{NC}")
    return 0


# -- Gate mode (pre-push quality checks) --------------------------------------

def _get_process_ancestry(max_depth: int = 30) -> list[tuple[int, str]]:
    """Walk parent processes via ps(1). Returns [(pid, cmdline), ...] closest-first.

    Used by the orchestrator check to verify that scripts/publish.py is an
    ancestor of the current pre-push gate invocation. Process ancestry is
    non-spoofable (unlike env vars, which a user could set with
    `CPV_PIPELINE=1 git push`).
    """
    ancestry: list[tuple[int, str]] = []
    pid = os.getpid()
    seen: set[int] = set()
    for _ in range(max_depth):
        if pid in seen or pid <= 0:
            break
        seen.add(pid)
        try:
            r = subprocess.run(
                ["ps", "-p", str(pid), "-o", "ppid=,args="],
                capture_output=True, text=True, timeout=5,
            )
        except (OSError, subprocess.SubprocessError):
            return []
        if r.returncode != 0:
            break
        line = r.stdout.strip()
        if not line:
            break
        parts = line.split(None, 1)
        if not parts:
            break
        try:
            ppid = int(parts[0])
        except ValueError:
            break
        cmdline = parts[1] if len(parts) > 1 else ""
        ancestry.append((pid, cmdline))
        if ppid <= 1:
            break
        pid = ppid
    return ancestry


def _called_by_publish_orchestrator(root: Path) -> bool:
    """Verify that scripts/publish.py (in publish mode, NOT --gate) is an ancestor.

    Expected chain for an orchestrated push:
        publish.py --patch|--minor|--major   (orchestrator)
          └─ git push
              └─ git (runs pre-push hook)
                  └─ sh (hook script)
                      └─ publish.py --gate   (this process)

    Walk the parent chain. At least one ancestor must be scripts/publish.py
    WITHOUT the --gate flag (that is, a publish orchestrator — not our own
    gate-mode re-entry).
    """
    expected_abs = str((root / "scripts" / "publish.py").resolve())
    expected_rel = "scripts/publish.py"
    for _pid, cmdline in _get_process_ancestry():
        if "publish.py" not in cmdline:
            continue
        if "--gate" in cmdline:
            continue
        if expected_abs in cmdline or expected_rel in cmdline:
            return True
    return False


def run_gate(root: Path) -> int:
    """Pre-push gate: blocks on any quality issue. Returns 0 if clean."""
    cprint(f"\n{BOLD}Pre-push gate checks{NC}\n")

    # Gate 0: Orchestrator check — only publish.py may trigger a push.
    # Prevents a user from running `git push` directly and bypassing the
    # version-bump / changelog / tag / release pipeline. Uses process
    # ancestry (non-spoofable), NOT env vars.
    cprint(f"{BLUE}[G0] Checking push orchestrator...{NC}")
    if not _called_by_publish_orchestrator(root):
        cprint("")
        cprint(f"  {RED}========================================{NC}")
        cprint(f"  {RED}  BLOCKED: Direct push not allowed{NC}")
        cprint(f"  {RED}  This pre-push hook only accepts pushes{NC}")
        cprint(f"  {RED}  initiated by scripts/publish.py.{NC}")
        cprint(f"  {RED}  Run one of:{NC}")
        cprint(f"  {RED}    uv run python scripts/publish.py --patch{NC}")
        cprint(f"  {RED}    uv run python scripts/publish.py --minor{NC}")
        cprint(f"  {RED}    uv run python scripts/publish.py --major{NC}")
        cprint(f"  {RED}========================================{NC}")
        return 1
    cprint(f"  {GREEN}Orchestrated by publish.py.{NC}")

    # Gate 1: Version bump check — local vs remote
    # Resolves origin/HEAD dynamically so the gate works on both `main` and
    # `master` default branches (and any other name). If none of the
    # candidates return a remote plugin.json, it's a first push and we allow.
    cprint(f"\n{BLUE}[G1] Checking version bump...{NC}")
    local_ver = get_current_version(root)
    if local_ver:
        # Try origin/HEAD first (most reliable), then explicit main/master
        candidates: list[str] = []
        try:
            sym = subprocess.run(
                ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                capture_output=True, text=True, cwd=str(root), timeout=10,
            )
            if sym.returncode == 0 and sym.stdout.strip():
                # Output looks like "refs/remotes/origin/main"
                branch = sym.stdout.strip().split("/")[-1]
                candidates.append(f"origin/{branch}")
        except (OSError, subprocess.SubprocessError):
            pass
        for fallback in ("origin/main", "origin/master"):
            if fallback not in candidates:
                candidates.append(fallback)
        remote_ver: str | None = None
        matched_ref: str | None = None
        for ref in candidates:
            try:
                r = subprocess.run(
                    ["git", "show", f"{ref}:.claude-plugin/plugin.json"],
                    capture_output=True, text=True, cwd=str(root), timeout=10,
                )
            except (OSError, subprocess.SubprocessError):
                continue
            if r.returncode == 0 and r.stdout:
                try:
                    data = json.loads(r.stdout)
                    rv = data.get("version")
                    if isinstance(rv, str):
                        remote_ver = rv
                        matched_ref = ref
                        break
                except json.JSONDecodeError:
                    continue
        if remote_ver is None:
            cprint(f"  {YELLOW}No remote plugin.json found (first push?) — skipping version-bump check.{NC}")
        elif local_ver == remote_ver:
            cprint(f"  {RED}BLOCKED: Version not bumped — local {local_ver} == {matched_ref} {remote_ver}{NC}")
            return 1
        else:
            cprint(f"  {GREEN}Version bump OK: {remote_ver} → {local_ver} (via {matched_ref}){NC}")

    # Gate 2: Lint with ruff. MANDATORY — missing scripts/ dir is a BLOCK.
    cprint(f"\n{BLUE}[G2] Linting...{NC}")
    scripts_dir = root / "scripts"
    if not scripts_dir.is_dir():
        cprint(f"  {RED}BLOCKED: scripts/ directory missing — cannot lint.{NC}")
        return 1
    lint_result = subprocess.run(
        ["uv", "run", "ruff", "check", "scripts/"],
        cwd=str(root), timeout=120)
    if lint_result.returncode != 0:
        cprint(f"  {RED}BLOCKED: Lint issues found{NC}")
        return 1
    cprint(f"  {GREEN}Lint passed.{NC}")

    # Gate 3: Validate via REMOTE CPV validator. MANDATORY — no skip, no exceptions.
    # CORNERSTONE: a plugin cannot be pushed unless validation passes with 0
    # blocking issues (WARNING allowed). The validator is ALWAYS fetched from
    # GitHub so a tampered local copy cannot weaken the rules.
    cprint(f"\n{BLUE}[G3] Validating plugin (remote CPV)...{NC}")
    if not shutil.which("uvx"):
        cprint(f"  {RED}BLOCKED: uvx not found on PATH.{NC}")
        return 1
    ve = subprocess.run(
        ["uvx", "--from",
         "git+https://github.com/Emasoft/claude-plugins-validation@v5.3.0",
         "--with", "pyyaml",
         "cpv-remote-validate", "plugin", ".", "--strict"],
        cwd=str(root), timeout=600).returncode
    # Exit codes: 0=pass, 1=CRITICAL, 2=MAJOR, 3=MINOR, 4=NIT, 5+=WARNING
    if ve != 0 and ve < 5:
        labels = {1: "CRITICAL", 2: "MAJOR", 3: "MINOR", 4: "NIT"}
        cprint(f"  {RED}BLOCKED: {labels.get(ve, f'exit {ve}')} issues found{NC}")
        return 1
    cprint(f"  {GREEN}Validation passed (0 blocking issues).{NC}")

    # Gate 4: Tests. MANDATORY — missing tests/ dir or zero tests is a BLOCK.
    cprint(f"\n{BLUE}[G4] Running tests...{NC}")
    test_dir = root / "tests"
    if not (test_dir.is_dir() and any(test_dir.glob("test_*.py"))):
        cprint(f"  {RED}BLOCKED: tests/ directory missing or empty.{NC}")
        cprint(f"  {RED}Every CPV plugin MUST ship tests.{NC}")
        return 1
    try:
        te = subprocess.run(
            ["uv", "run", "pytest", "tests/", "-x", "-q", "--tb=short"],
            cwd=str(root), timeout=300).returncode
    except subprocess.TimeoutExpired:
        cprint(f"  {RED}BLOCKED: Tests timed out after 300s.{NC}")
        return 1
    if te == 5:
        cprint(f"  {RED}BLOCKED: pytest collected 0 tests.{NC}")
        return 1
    if te != 0:
        cprint(f"  {RED}BLOCKED: Tests failed{NC}")
        return 1
    cprint(f"  {GREEN}Tests passed.{NC}")

    cprint(f"\n{GREEN}{BOLD}All gates passed.{NC}")
    return 0


# -- Pipeline stages -----------------------------------------------------------

def stage_bypass_guard() -> None:
    """Step 0: Reject any env var that could bypass a check. No exceptions.

    Issue #22 hardening (v2.86.0): broadened from a fixed allowlist to
    prefix-pattern matching. Any env var matching ``PLUGIN_SKIP_*``,
    ``CPV_SKIP_*``, ``SKIP_*``, or named ``NO_VERIFY`` aborts the publish.
    Closes the loophole where a fresh skip name (e.g. ``CPV_SKIP_GATE7``)
    that was not in the original explicit list would silently slip past.

    Two explicit infrastructure exemptions remain — both are read-only
    overrides used by CPV's own integrity / auth subsystems and never
    skip a gate:
        * ``CPV_SKIP_GITHUB_INTEGRITY=1`` — used to bypass GitHub-anchored
          integrity check (see cpv_integrity.py). The integrity check is
          a defence against tampering, NOT a publish gate.
        * ``CPV_SKIP_GH_AUTH_CHECK=1`` — used by `_ensure_gh_auth` to bypass
          the `gh auth status` round-trip on flaky networks. Auth still
          has to work for the actual `git push` / `gh release create`;
          this only skips the precheck.

    Both are documented exemptions, listed below and excluded from the
    pattern match.
    """
    cprint(f"\n{BOLD}[0/11] Checking for bypass attempts...{NC}")
    # Explicit infrastructure exemptions — see docstring above.
    exemptions = {"CPV_SKIP_GITHUB_INTEGRITY", "CPV_SKIP_GH_AUTH_CHECK"}
    forbidden_prefixes = ("PLUGIN_SKIP_", "CPV_SKIP_", "SKIP_")
    forbidden_exact = {"NO_VERIFY"}
    attempted = [
        v
        for v in sorted(os.environ)
        if (v.startswith(forbidden_prefixes) or v in forbidden_exact) and v not in exemptions
        if os.environ.get(v)
    ]
    if attempted:
        cprint(f"  {RED}BLOCKED: forbidden env vars set: {', '.join(attempted)}{NC}")
        cprint(f"  {RED}The publish pipeline enforces every check. "
               f"Fix failures, do not skip them.{NC}")
        cprint(f"  {DIM}(infrastructure exemptions: {', '.join(sorted(exemptions))}){NC}")
        sys.exit(1)
    cprint(f"  {GREEN}No bypass vars set.{NC}")

def stage_check_clean(root: Path) -> None:
    """Step 1: Working tree must be clean."""
    cprint(f"\n{BOLD}[1/11] Checking working tree...{NC}")
    r = run(["git", "status", "--porcelain"], cwd=root, capture=True)
    if r.stdout.strip():
        cprint(f"  {RED}Working tree is dirty. Commit or stash changes first.{NC}")
        cprint(r.stdout)
        sys.exit(1)
    cprint(f"  {GREEN}Clean.{NC}")

def stage_lint(root: Path) -> None:
    """Step 2: Lint + typecheck (ruff + mypy). MANDATORY — no skip.

    Runs ruff for style/syntax and mypy for static types in the same stage.
    Both must succeed — the cornerstone rule forbids any push with lint or
    type errors. Type-checking runs BEFORE the test suite so the cheap fails
    come before the expensive ones.
    """
    cprint(f"\n{BOLD}[2/11] Linting + type-checking...{NC}")
    scripts_dir = root / "scripts"
    if not scripts_dir.is_dir():
        cprint(f"  {RED}BLOCKED: scripts/ directory missing — cannot lint.{NC}")
        sys.exit(1)
    cprint(f"  {BLUE}ruff check scripts/{NC}")
    run(["uv", "run", "ruff", "check", "scripts/"], cwd=root)
    cprint(f"  {BLUE}mypy scripts/ --ignore-missing-imports{NC}")
    run(["uv", "run", "mypy", "scripts/", "--ignore-missing-imports"], cwd=root)
    cprint(f"  {GREEN}Lint + typecheck passed.{NC}")

# Issue #31 (v2.98.0): browser-orphan cleanup signatures.
#
# A pytest run that spawns Playwright / dev-browser pages can leave
# behind dozens of `Chrome for Testing` / `chromium` / `headless_shell`
# processes if the test code (or fixtures) forget to close pages. Over
# a long debug session those orphans pile up, exhausting file
# descriptors or RAM and eventually crashing the browser or making
# the machine unresponsive. The baseline-diff cleanup below catches
# every leak regardless of test-code quality. NEVER skips tests — the
# iron rule (no plugin with issues pushed) is preserved.
_BROWSER_ORPHAN_SIGNATURES = (
    "Chrome for Testing",
    "chrome-for-testing",
    "headless_shell",
    "Chromium.app/Contents",
    "chromium-browser",
    "/playwright/",
    "playwright-core",
)


def _snapshot_browser_pids() -> set:
    """Snapshot-then-grep — never live-grep — for browser-signature PIDs."""
    try:
        snap = subprocess.run(
            ["ps", "-eo", "pid,command"],
            capture_output=True, text=True, check=False, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return set()
    if snap.returncode != 0 or not snap.stdout:
        return set()
    pids = set()
    for raw_line in snap.stdout.strip().split("\n")[1:]:
        line = raw_line.strip()
        if not line:
            continue
        try:
            pid_str, cmd = line.split(None, 1)
            pid = int(pid_str)
        except (ValueError, IndexError):
            continue
        if any(sig in cmd for sig in _BROWSER_ORPHAN_SIGNATURES):
            pids.add(pid)
    return pids


def _cleanup_browser_orphans(baseline_pids: set) -> int:
    """Kill browser-signature PIDs that appeared since ``baseline_pids``.

    Baseline-diff: PIDs in baseline are pre-existing (maintainer's own
    daily browser) — NEVER killed. Only PIDs that came into existence
    during the pytest run are candidates.
    """
    import signal
    import time

    current = _snapshot_browser_pids()
    new_pids = current - baseline_pids
    if not new_pids:
        return 0
    killed = 0
    for pid in new_pids:
        try:
            os.kill(pid, signal.SIGTERM)
            killed += 1
        except (ProcessLookupError, PermissionError, OSError):
            pass
    if killed:
        time.sleep(1.5)
        for pid in new_pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                pass
    return killed


def stage_tests(root: Path) -> None:
    """Step 3: Run pytest. MANDATORY — no skip, no exceptions.

    Cornerstone rule: failing tests block the push. Missing tests/ directory
    is a scaffolding bug and must be fixed, not bypassed.

    Order: tests run BEFORE the CPV validator so behavioral regressions fail
    fast on unit tests before the structural validator inspects the manifest.

    Issue #31 (v2.98.0): wrap the pytest invocation in a baseline-diff
    browser-orphan cleanup so dev-browser / Playwright leaks do not
    pile up Chrome-for-Testing processes. Tests still run
    unconditionally — the cleanup is a safety net, not a skip
    mechanism.
    """
    cprint(f"\n{BOLD}[3/11] Running tests...{NC}")
    test_dir = root / "tests"
    if not test_dir.is_dir():
        cprint(f"  {RED}BLOCKED: tests/ directory missing.{NC}")
        cprint(f"  {RED}Every CPV plugin MUST ship a tests/ directory.{NC}")
        sys.exit(1)
    baseline_browser_pids = _snapshot_browser_pids()
    try:
        r = run(["uv", "run", "pytest", "tests/", "-x", "-q", "--tb=short"], cwd=root, check=False)
    finally:
        killed = _cleanup_browser_orphans(baseline_browser_pids)
        if killed:
            cprint(f"  {YELLOW}Cleaned up {killed} orphaned browser process(es) spawned by pytest.{NC}")
    if r.returncode == 5:
        # pytest exit 5 = no tests collected. This is ALSO a block — no exceptions.
        cprint(f"  {RED}BLOCKED: pytest collected 0 tests.{NC}")
        cprint(f"  {RED}Every CPV plugin MUST ship at least one test.{NC}")
        sys.exit(1)
    if r.returncode != 0:
        cprint(f"  {RED}BLOCKED: tests failed (exit {r.returncode}).{NC}")
        sys.exit(r.returncode)
    cprint(f"  {GREEN}Tests passed.{NC}")


def stage_validate(root: Path) -> None:
    """Step 4: Validate plugin via REMOTE CPV validator. MANDATORY — no skip.

    Cornerstone rule: a plugin cannot be pushed unless validation passes
    with 0 issues (WARNING allowed). The validator is ALWAYS fetched from
    GitHub (git+https://github.com/Emasoft/claude-plugins-validation@v5.3.0)
    via uvx so a local tampered copy cannot weaken the rules. No exceptions.

    Order: runs AFTER lint + tests so behavioral regressions fail fast
    before the structural validator even looks at the manifest.
    """
    cprint(f"\n{BOLD}[4/11] Validating plugin (remote CPV)...{NC}")
    if not shutil.which("uvx"):
        cprint(f"  {RED}BLOCKED: uvx not found on PATH.{NC}")
        cprint(f"  {RED}Install via: brew install uv  or  pip install uv{NC}")
        sys.exit(1)
    # Fetch CPV from GitHub and run validate_plugin remotely. --strict blocks
    # on CRITICAL(1), MAJOR(2), MINOR(3), NIT(4); WARNING(5+) passes.
    # CPV is PINNED to an IMMUTABLE TAG at every callsite. Never @main (404s —
    # CPV's default branch is master, #139) and never bare master: a CI-gating
    # tool fetched from a moving ref inherits upstream regressions silently, which
    # is how v2.137.0's 30-min "[REPO LINT]" hang reached CI (#148).
    #
    # RE-BASELINED v2.136.1 -> v5.3.0 on 2026-08-08. #148 and #149 were fixed in
    # v2.145.1, so the old pin's justification had been dead for six weeks — and
    # its narrower ruleset was HIDING 7 real defects in our own hooks (3x naive
    # datetime, an implicit subprocess check, a dead glob alternative in the push
    # gate). Measured on v5.3.0 after fixing them: CRITICAL=0 MAJOR=0 MINOR=0
    # NIT=0, 3m26s cold — no hang.
    #
    # A pin is a baseline to RE-MEASURE, not a workaround to carry forward. When
    # bumping it, re-run the validate and read the SUMMARY line from a captured
    # file — uvx caches aggressively, so use --refresh or you will measure the
    # OLD version and believe it was the new one.
    # 20 min, not the 300s default. Measured cold-and-alone: 3m26s. A v1.4.1
    # publish nonetheless died at exactly 300s here while two OTHER plugins were
    # running their own CPV validations on this host — the machine, not the
    # plugin, decides this duration, and several agents publish concurrently.
    # A timeout here is the worst kind of failure: it judges nothing and looks
    # like a verdict.
    run([
        "uvx", "--from",
        "git+https://github.com/Emasoft/claude-plugins-validation@v5.3.0",
        "--with", "pyyaml",
        "cpv-remote-validate", "plugin", ".", "--strict",
    ], cwd=root, timeout=1200)
    cprint(f"  {GREEN}Validation passed (0 blocking issues).{NC}")


# ── Marketplace-registration helpers (mirror of CPV's own publish.py Gate 6) ─

def _find_parent_marketplace(plugin_root: Path) -> Path | None:
    """Walk up looking for a parent marketplace.json (Layout B signature)."""
    current = plugin_root.resolve().parent
    while current != current.parent:
        mp = current / ".claude-plugin" / "marketplace.json"
        if mp.is_file():
            try:
                rel = plugin_root.resolve().relative_to(current)
                parts = rel.parts
                if len(parts) >= 2 and parts[0] == "plugins":
                    return current
            except ValueError:
                pass
            return None
        current = current.parent
    return None


def _detect_layout(plugin_root: Path) -> tuple[str, dict]:
    """Detect Layout A (standalone+notify), Layout B (nested), or 'none'."""
    parent = _find_parent_marketplace(plugin_root)
    if parent is not None:
        return "B", {"marketplace_root": parent, "plugin_name": plugin_root.name}
    notify_wf = plugin_root / ".github" / "workflows" / "notify-marketplace.yml"
    if notify_wf.is_file():
        try:
            content = notify_wf.read_text(encoding="utf-8")
        except OSError:
            content = ""
        m_owner = re.search(r"^\s*MARKETPLACE_OWNER:\s*[\"']?([^\"'\s]+)[\"']?\s*$", content, re.MULTILINE)
        m_repo = re.search(r"^\s*MARKETPLACE_REPO:\s*[\"']?([^\"'\s]+)[\"']?\s*$", content, re.MULTILINE)
        return "A", {
            "notify_workflow": notify_wf,
            "mkt_owner": m_owner.group(1) if m_owner else None,
            "mkt_repo": m_repo.group(1) if m_repo else None,
        }
    return "none", {}


def _gh_secret_exists(plugin_root: Path, secret_name: str) -> bool:
    """Check whether a GitHub secret with the given name exists on this repo."""
    gh = shutil.which("gh")
    if gh is None:
        return False
    r = subprocess.run([gh, "secret", "list"], cwd=str(plugin_root),
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return False
    for line in r.stdout.splitlines():
        if line.split("\t", 1)[0].strip() == secret_name:
            return True
    return False


def _current_repo_slug(plugin_root: Path) -> str | None:
    """Return owner/repo slug for current git origin, or None."""
    r = subprocess.run(["git", "remote", "get-url", "origin"], cwd=str(plugin_root),
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return None
    m = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?$", r.stdout.strip())
    return f"{m.group(1)}/{m.group(2)}" if m else None


def _read_plugin_name(plugin_root: Path) -> str:
    pj = plugin_root / ".claude-plugin" / "plugin.json"
    if pj.is_file():
        try:
            data = json.loads(pj.read_text(encoding="utf-8"))
            name = data.get("name")
            if isinstance(name, str) and name:
                return name
        except (OSError, json.JSONDecodeError):
            pass
    return plugin_root.name


def _fetch_remote_marketplace_json(owner: str, repo: str) -> dict | None:
    gh = shutil.which("gh")
    if gh is None:
        return None
    r = subprocess.run(
        [gh, "api", f"repos/{owner}/{repo}/contents/.claude-plugin/marketplace.json",
         "-H", "Accept: application/vnd.github.raw+json"],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode != 0:
        return None
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _remote_has_receiver_workflow(owner: str, repo: str) -> bool:
    gh = shutil.which("gh")
    if gh is None:
        return False
    r = subprocess.run(
        [gh, "api", f"repos/{owner}/{repo}/contents/.github/workflows"],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode != 0:
        return False
    try:
        entries = json.loads(r.stdout)
    except json.JSONDecodeError:
        return False
    if not isinstance(entries, list):
        return False
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name", "")
        if not isinstance(name, str) or not name.endswith((".yml", ".yaml")):
            continue
        f = subprocess.run(
            [gh, "api", f"repos/{owner}/{repo}/contents/.github/workflows/{name}",
             "-H", "Accept: application/vnd.github.raw+json"],
            capture_output=True, text=True, timeout=60,
        )
        if f.returncode == 0 and "repository_dispatch" in f.stdout:
            return True
    return False


def _plugin_in_remote_marketplace(mkt_json: dict, plugin_name: str, expected_repo: str | None) -> bool:
    """Accept github/url/git source forms; match URL slug for url|git (issue #25 Defect A)."""
    plugins = mkt_json.get("plugins")
    if not isinstance(plugins, list):
        return False
    for entry in plugins:
        if not isinstance(entry, dict):
            continue
        if entry.get("name") != plugin_name:
            continue
        source = entry.get("source")
        if not isinstance(source, dict):
            continue
        stype = source.get("source") or source.get("type")
        if stype == "github":
            if expected_repo is None or source.get("repo") == expected_repo:
                return True
        elif stype in ("url", "git"):
            url = source.get("url")
            if expected_repo is None:
                return True
            if isinstance(url, str):
                norm = url.removesuffix(".git").rstrip("/")
                if norm.endswith("/" + expected_repo) or norm.endswith(":" + expected_repo):
                    return True
    return False


def stage_marketplace_registration(root: Path) -> None:
    """Step 5: Verify the plugin is wired to its marketplace for auto-updates.

    Mirror of CPV's own publish.py Gate 6. Three modes:
      - Layout A (standalone + notify-marketplace.yml): verifies workflow,
        MARKETPLACE_PAT secret, remote marketplace.json registration,
        remote receiver workflow with repository_dispatch trigger
      - Layout B (nested under <marketplace>/plugins/<name>/): refuses to
        publish from the nested folder, requires running at marketplace root
      - 'none' (no marketplace wiring): emits a WARNING and proceeds — valid
        for first releases or experimental standalone plugins
    """
    cprint(f"\n{BOLD}[5/11] Marketplace-registration check...{NC}")
    layout, details = _detect_layout(root)

    if layout == "none":
        cprint(f"  {YELLOW}WARNING: no marketplace registration found for this plugin.{NC}")
        cprint(f"  {YELLOW}If you intend to publish to a marketplace, run the{NC}")
        cprint(f"  {YELLOW}setup-marketplace-auto-notification skill to wire up auto-updates.{NC}")
        cprint(f"  {YELLOW}Allowing release to proceed (standalone/experimental mode).{NC}")
        return

    if layout == "A":
        cprint("  Layout A detected (standalone plugin repo)")
        notify_wf = details.get("notify_workflow")
        mkt_owner = details.get("mkt_owner")
        mkt_repo = details.get("mkt_repo")
        if not notify_wf or not Path(notify_wf).is_file():
            cprint(f"  {RED}BLOCKED: .github/workflows/notify-marketplace.yml missing.{NC}")
            sys.exit(1)
        if not mkt_owner or not mkt_repo:
            cprint(f"  {RED}BLOCKED: notify-marketplace.yml has no MARKETPLACE_OWNER/MARKETPLACE_REPO.{NC}")
            sys.exit(1)
        cprint(f"  target marketplace: {mkt_owner}/{mkt_repo}")
        if shutil.which("gh") is None:
            cprint(f"  {RED}BLOCKED: gh CLI not installed — cannot verify secret/marketplace.{NC}")
            sys.exit(1)
        if not _gh_secret_exists(root, "MARKETPLACE_PAT"):
            cprint(f"  {RED}BLOCKED: MARKETPLACE_PAT secret not configured on this plugin repo.{NC}")
            cprint(f"  {RED}  Fix: uv run python scripts/set_marketplace_pat.py {_current_repo_slug(root) or 'OWNER/REPO'}{NC}")
            sys.exit(1)
        cprint(f"  {GREEN}MARKETPLACE_PAT secret configured{NC}")
        mkt_json = _fetch_remote_marketplace_json(mkt_owner, mkt_repo)
        if mkt_json is None:
            cprint(f"  {RED}BLOCKED: cannot fetch marketplace.json from {mkt_owner}/{mkt_repo}.{NC}")
            sys.exit(1)
        plugin_name = _read_plugin_name(root)
        slug = _current_repo_slug(root)
        if not _plugin_in_remote_marketplace(mkt_json, plugin_name, slug):
            cprint(f"  {RED}BLOCKED: plugin '{plugin_name}' not registered in {mkt_owner}/{mkt_repo} marketplace.json.{NC}")
            cprint(f"  {RED}  Add an entry: {{\"name\": \"{plugin_name}\", \"source\": {{\"source\": \"github\", \"repo\": \"{slug}\"}}}}{NC}")
            sys.exit(1)
        cprint(f"  {GREEN}Plugin registered in remote marketplace.json{NC}")
        if not _remote_has_receiver_workflow(mkt_owner, mkt_repo):
            cprint(f"  {RED}BLOCKED: remote marketplace {mkt_owner}/{mkt_repo} has no workflow with repository_dispatch trigger.{NC}")
            cprint(f"  {RED}  See setup-marketplace-auto-notification skill.{NC}")
            sys.exit(1)
        cprint(f"  {GREEN}Remote marketplace has receiver workflow{NC}")
        cprint(f"  {GREEN}Layout A marketplace registration verified.{NC}")
        return

    if layout == "B":
        cprint("  Layout B detected (nested plugin under marketplace repo)")
        marketplace_root_raw = details.get("marketplace_root")
        marketplace_root: Path | None = marketplace_root_raw if isinstance(marketplace_root_raw, Path) else None
        plugin_name_raw = details.get("plugin_name")
        # Note: no type annotation here — mypy's no-redef rule complains even
        # though the Layout A branch above returns before reaching this
        # point. Plain assignment avoids the false positive in the generated
        # template output (which downstream CI runs with mypy --strict).
        plugin_name = plugin_name_raw if isinstance(plugin_name_raw, str) else root.name
        if marketplace_root is None:
            cprint(f"  {RED}BLOCKED: Layout B detected but marketplace_root unresolved.{NC}")
            sys.exit(1)
        if root.resolve() != marketplace_root.resolve():
            cprint(f"  {RED}BLOCKED: This is a Layout B nested plugin.{NC}")
            cprint(f"  {RED}  publish.py must run at the MARKETPLACE root, not the nested folder.{NC}")
            cprint(f"  {RED}  Bumping a nested plugin alone breaks the atomic marketplace tag.{NC}")
            cprint(f"  {RED}  Fix: cd {marketplace_root} && uv run python scripts/publish.py --patch{NC}")
            sys.exit(1)
        mp_path = marketplace_root / ".claude-plugin" / "marketplace.json"
        try:
            mp_data = json.loads(mp_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            cprint(f"  {RED}BLOCKED: cannot read {mp_path}: {e}{NC}")
            sys.exit(1)
        entries = mp_data.get("plugins") if isinstance(mp_data, dict) else None
        if not isinstance(entries, list):
            cprint(f"  {RED}BLOCKED: marketplace.json has no 'plugins' array.{NC}")
            sys.exit(1)
        if not any(isinstance(e, dict) and e.get("name") == plugin_name for e in entries):
            cprint(f"  {RED}BLOCKED: plugin '{plugin_name}' not registered in {mp_path}.{NC}")
            cprint(f"  {RED}  Add: {{\"name\": \"{plugin_name}\", \"source\": \"./plugins/{plugin_name}\"}}{NC}")
            sys.exit(1)
        cprint(f"  {GREEN}Plugin '{plugin_name}' registered in parent marketplace.json{NC}")
        cprint(f"  {GREEN}Layout B marketplace registration verified.{NC}")


def stage_consistency(root: Path) -> None:
    """Step 6: Check version consistency."""
    cprint(f"\n{BOLD}[6/11] Checking version consistency...{NC}")
    ok, msg = check_version_consistency(root)
    cprint(f"  {msg}")
    if not ok:
        cprint(f"  {RED}Fix version mismatch before publishing.{NC}")
        sys.exit(1)
    cprint(f"  {GREEN}Consistent.{NC}")

def _read_remote_version(plugin_root: Path) -> str | None:
    """Read .claude-plugin/plugin.json's `version` from origin/master (or main).

    Idempotency baseline: the publish pipeline reads the REMOTE version, not
    the local one, so an interrupted publish that already bumped + committed
    locally cannot double-bump on re-run. Returns None when offline / no
    remote ref / file missing — caller must fall back to local baseline.
    """
    for ref in ("origin/master", "origin/main", "origin/HEAD"):
        try:
            r = subprocess.run(
                ["git", "show", f"{ref}:.claude-plugin/plugin.json"],
                capture_output=True, text=True, cwd=str(plugin_root),
                check=False, timeout=15,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if r.returncode != 0:
            continue
        try:
            v = json.loads(r.stdout).get("version")
        except json.JSONDecodeError:
            continue
        if isinstance(v, str):
            return v
    return None


def _infer_bump_type(old: str, new: str) -> str | None:
    """Classify a semver delta as 'major', 'minor', 'patch', or None."""
    o = parse_semver(old)
    n = parse_semver(new)
    if o is None or n is None or n <= o:
        return None
    if n[0] != o[0]:
        return "major"
    if n[1] != o[1]:
        return "minor"
    return "patch"


def _git_porcelain_clean(root: Path) -> bool:
    """True iff `git status --porcelain` is empty (working tree clean)."""
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=str(root),
            check=False, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0 and not r.stdout.strip()


def _head_commit_message(root: Path) -> str:
    """Return the subject line of HEAD, or '' on failure."""
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            capture_output=True, text=True, cwd=str(root),
            check=False, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def _local_tag_exists(root: Path, tag: str) -> bool:
    """True iff `tag` already exists in the local git repo."""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--verify", f"refs/tags/{tag}"],
            capture_output=True, text=True, cwd=str(root),
            check=False, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0


def stage_bump(root: Path, new_ver: str, dry_run: bool) -> None:
    """Step 7: Bump version. Idempotent — skips when local already matches target.

    Recovery semantics: when a previous publish was interrupted between the
    local commit+tag and the push (transient network failure during git push,
    pre-push hook reject, etc.), the local repo is at the bumped version while
    origin is one minor behind. Re-running publish.py would DOUBLE-BUMP
    (read-local-then-add-1 → next minor on top of the already-bumped local).
    The fix: read REMOTE plugin.json as baseline, infer bump type from
    local-vs-remote delta, and skip the bump entirely when local already
    matches the target.
    """
    cprint(f"\n{BOLD}[7/11] Bumping version...{NC}")
    current = get_current_version(root)
    remote = _read_remote_version(root)
    if remote and current and current == new_ver:
        cprint(f"  {YELLOW}Local plugin.json is already at {new_ver} (remote at {remote}) — "
               f"skipping bump (interrupted-publish recovery).{NC}")
        return
    if remote and current and current != remote and current != new_ver:
        cprint(f"  {RED}REFUSED: local plugin.json is at {current} but remote is at "
               f"{remote} and target is {new_ver}. Refuse to guess what state this is.{NC}")
        cprint(f"  {RED}Manual intervention required: align local with remote, then re-run.{NC}")
        sys.exit(1)
    if not do_bump(root, new_ver, dry_run=dry_run):
        cprint(f"  {RED}Version bump failed.{NC}")
        sys.exit(1)
    cprint(f"  {GREEN}Version bumped to {new_ver}.{NC}")
    _refresh_uv_lock(root, new_ver, dry_run)


def _refresh_uv_lock(root: Path, new_ver: str, dry_run: bool) -> None:
    """Re-lock so uv.lock carries the just-bumped version (issue #149's shape).

    The bump rewrites pyproject.toml's `version` but uv.lock keeps its own copy
    of it. Left stale, the very next `uv run` in this repo re-locks as a SIDE
    EFFECT, dirtying the tree — and the NEXT publish then aborts at [1/11]
    "Working tree is dirty" for a change nobody made deliberately. Re-locking
    HERE means the new lock lands in this release's own commit (stage 10 does
    `git add -A`), which is where it belongs.

    Deliberately non-fatal: `uv` is not a hard dependency of this pipeline, and
    a lock refresh failing is not a reason to abandon a release that has already
    passed lint, tests and validation.
    """
    lock = root / "uv.lock"
    if not lock.is_file():
        return
    if not shutil.which("uv"):
        cprint(f"  {YELLOW}uv not on PATH — uv.lock may lag {new_ver}.{NC}")
        return
    if dry_run:
        cprint(f"  Would re-lock uv.lock to {new_ver}")
        return
    r = subprocess.run(
        ["uv", "lock"], cwd=str(root), capture_output=True, text=True, check=False,
    )
    if r.returncode == 0:
        cprint(f"  {GREEN}uv.lock re-locked to {new_ver}.{NC}")
    else:
        cprint(f"  {YELLOW}uv lock failed (rc={r.returncode}) — uv.lock may lag.{NC}")

def stage_update_badges(root: Path, old_ver: str, new_ver: str, dry_run: bool) -> None:
    """Step 8: Replace version badge in README.md.

    Strategy:
      1. Try exact-string substitution `version-<old>-blue` → `version-<new>-blue`
      2. If the exact old version is not present, fall back to a regex that
         matches ANY `version-X.Y.Z-blue` pattern (handles drift from a hand-edit
         or a missed release). Prevents the "stale forever" trap that bit CPV
         itself when its README badge fell 20 releases behind.
      3. Emit a WARNING (not silent skip) when no badge is found at all so the
         author notices the README has no shields.io version badge to update.
    """
    cprint(f"\n{BOLD}[8/11] Updating README badge...{NC}")
    readme = root / "README.md"
    if not readme.exists():
        cprint(f"  {YELLOW}WARNING: no README.md — skipping badge update.{NC}")
        return
    content = readme.read_text(encoding="utf-8")
    old_badge = f"version-{old_ver}-blue"
    new_badge = f"version-{new_ver}-blue"

    if old_badge in content:
        if dry_run:
            cprint(f"  Would update badge (exact match): {old_badge} -> {new_badge}")
            return
        readme.write_text(content.replace(old_badge, new_badge, 1), encoding="utf-8")
        cprint(f"  {GREEN}Updated README badge: {old_ver} -> {new_ver}{NC}")
        return

    # Fallback: regex match on any version-X.Y.Z-blue pattern
    badge_re = re.compile(r"version-\d+\.\d+\.\d+-blue")
    match = badge_re.search(content)
    if match is None:
        cprint(f"  {YELLOW}WARNING: no version-X.Y.Z-blue badge found in README.md.{NC}")
        cprint(f"  {YELLOW}Add a shields.io badge so future releases can update it automatically.{NC}")
        return
    found = match.group(0)
    if dry_run:
        cprint(f"  Would update badge (regex match): {found} -> {new_badge}")
        return
    readme.write_text(badge_re.sub(new_badge, content, count=1), encoding="utf-8")
    cprint(f"  {GREEN}Updated README badge (was {found}, now {new_badge}){NC}")

def detect_bump_type(root: Path) -> str:
    """Auto-detect the next bump type from conventional commits via git-cliff.

    Runs `git-cliff --bumped-version` and compares the predicted version to
    the REMOTE one (origin/master) to determine major/minor/patch. Falls back
    to 'patch' on any failure (git-cliff missing, repo empty, parse error) so
    the cornerstone rule — every push is a bump — is never violated.

    Idempotency: when the local repo already has a release commit (interrupted
    publish), reading local plugin.json would over-shoot the bump (current is
    already the bumped version, git-cliff would compute current+1). Reading
    remote/origin gives the true baseline.

    Conventional commit mapping (git-cliff defaults):
      feat:                 -> minor
      fix:/perf:/refactor:  -> patch
      BREAKING CHANGE / !   -> major
    """
    cliff_bin = shutil.which("git-cliff")
    if cliff_bin is None:
        cprint(f"{YELLOW}git-cliff not installed — auto-bump falls back to 'patch'.{NC}")
        return "patch"
    current = _read_remote_version(root) or get_current_version(root)
    if not current:
        cprint(f"{YELLOW}Cannot read current version for auto-bump — falling back to 'patch'.{NC}")
        return "patch"
    try:
        r = subprocess.run(
            [cliff_bin, "--bumped-version"],
            capture_output=True,
            text=True,
            cwd=str(root),
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return "patch"
    if r.returncode != 0:
        return "patch"
    out = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    bumped = out.lstrip("v").strip()
    if not bumped or bumped == current:
        return "patch"
    try:
        cur = [int(p) for p in current.split(".")[:3]]
        nxt = [int(p) for p in bumped.split(".")[:3]]
        while len(cur) < 3:
            cur.append(0)
        while len(nxt) < 3:
            nxt.append(0)
    except ValueError:
        return "patch"
    if nxt[0] > cur[0]:
        return "major"
    if nxt[1] > cur[1]:
        return "minor"
    return "patch"


def stage_changelog(root: Path, new_ver: str, dry_run: bool) -> None:
    """Step 9: PREPEND this release's section to CHANGELOG.md with git-cliff.

        git cliff --bump --unreleased --tag v<NEXT> --prepend CHANGELOG.md

    --bump          promote the unreleased section into a dated tag entry
    --unreleased    process only commits since the last tag
    --tag v<NEXT>   label the new entry with the computed version (prefixed v)
    --prepend       insert that entry ABOVE the existing history, keeping it

    `--prepend`, NOT `-o`. This previously ran `-o CHANGELOG.md`, and `-o` with
    `--unreleased` writes ONLY the new section over the whole file — so every
    release silently destroyed its predecessor's entry. Measured on this repo at
    v1.4.0: after 10+ releases CHANGELOG.md was 23 lines carrying exactly ONE
    section, under a header promising "all notable changes to this project".
    Nothing failed, nothing warned; the file simply never accumulated. The lost
    history was recoverable (`git-cliff` over all tags rebuilt 26 sections) only
    because the tags survived — the commits, not the file, were the real record.

    Reported by the CORE session, which hit the identical defect in the shared
    scaffold. Do NOT assume a CPV pin bump delivers this fix: it lives in CPV's
    canonical emitter, and a drifted publish.py never receives it. Verify the
    behaviour (`grep -n git-cliff scripts/publish.py`), not the version.
    """
    cprint(f"\n{BOLD}[9/11] Generating changelog (git-cliff)...{NC}")
    if not shutil.which("git-cliff"):
        cprint(f"  {YELLOW}git-cliff not installed — skipping changelog.{NC}")
        return
    cliff_toml = root / "cliff.toml"
    if not cliff_toml.is_file():
        cprint(f"  {YELLOW}No cliff.toml — skipping changelog.{NC}")
        return
    tag = f"v{new_ver}"
    if dry_run:
        cprint(f"  Would run: git-cliff --bump --unreleased --tag {tag} --prepend CHANGELOG.md")
        return
    changelog = root / "CHANGELOG.md"
    if not changelog.is_file():
        # --prepend requires the file to exist; seed the full history from tags.
        run(["git-cliff", "--tag", tag, "-o", "CHANGELOG.md"], cwd=root)
        cprint(f"  {GREEN}CHANGELOG.md created from full tag history ({tag}).{NC}")
        return
    run(
        ["git-cliff", "--bump", "--unreleased", "--tag", tag, "--prepend", "CHANGELOG.md"],
        cwd=root,
    )
    cprint(f"  {GREEN}CHANGELOG.md updated with {tag} (history preserved).{NC}")

def stage_commit_and_push(root: Path, new_ver: str, dry_run: bool) -> None:
    """Step 10: Commit, tag, push. Idempotent on commit + tag.

    Idempotency: if HEAD's subject is already `chore: bump version to <new_ver>`
    AND the working tree is clean, skip the commit step (interrupted-publish
    recovery). If the tag already exists locally, skip the tag step. The push
    always runs — that is what brings the remote into sync.

    TRDD-bbff5bc5 §5: gh-auth precheck runs BEFORE the first push so the
    user gets an actionable error if their gh CLI is unauthed/lacks push
    perm — instead of an opaque git push failure mid-pipeline.
    """
    cprint(f"\n{BOLD}[10/11] Committing and pushing...{NC}")
    tag = f"v{new_ver}"
    # The resolver tag rides in the SAME atomic push as the release tag. Pushing
    # it separately would allow a half-published state where the release exists
    # but no dependant can resolve it — the exact shape of integrator#22.
    rtag = resolver_tag(root, new_ver)
    expected_subject = f"chore: bump version to {new_ver}"
    head_subject = _head_commit_message(root)
    tree_clean = _git_porcelain_clean(root)
    tag_exists = _local_tag_exists(root, tag)
    rtag_exists = _local_tag_exists(root, rtag)

    if dry_run:
        if head_subject == expected_subject and tree_clean:
            cprint(f"  Would skip commit (HEAD already '{expected_subject}', tree clean)")
        else:
            cprint(f"  Would commit: {expected_subject}")
        for t, exists in ((tag, tag_exists), (rtag, rtag_exists)):
            if exists:
                cprint(f"  Would skip tag (already exists locally): {t}")
            else:
                cprint(f"  Would tag: {t}")
        cprint(f"  Would push (atomic): origin HEAD {tag} {rtag}")
        return

    if head_subject == expected_subject and tree_clean:
        cprint(f"  {YELLOW}HEAD is already '{expected_subject}' and tree is clean — "
               f"skipping commit (interrupted-publish recovery).{NC}")
    else:
        # Stage the TRACKED files the bump actually modified, BY NAME — never
        # `git add -A`.
        #
        # -A also stages UNTRACKED files. Stage 1 guarantees a clean tree, but
        # stages 7-9 run between then and here (bump, badge, changelog, uv lock),
        # and anything else that appears in the window — a scratch note, a tool's
        # temp output, a report — would be swept into a PUBLIC release commit
        # with no one reviewing it. That is the exact hazard
        # ~/.claude/rules/never-git-add-all.md exists for, and this pipeline was
        # violating it at the one moment the result becomes irreversible.
        # (It is also why release notes are written to a temp dir, not the root.)
        raw = _git_stdout(root, ["git", "diff", "--name-only"])
        if raw is None:
            # Fail closed. The tempting fallback is `git add -A`, which is the
            # very thing being avoided — and it would fire in precisely the
            # situation where nobody can see what is about to be staged.
            cprint(f"  {RED}Could not read the modified-file list — refusing to commit.{NC}")
            sys.exit(1)
        changed = [p for p in (s.strip() for s in raw.splitlines()) if p]
        if not changed:
            cprint(f"  {RED}Nothing modified to commit, yet HEAD is not the bump commit.{NC}")
            cprint(f"  {YELLOW}Refusing to create an empty release commit — investigate.{NC}")
            sys.exit(1)
        cprint(f"  Staging {len(changed)} modified file(s) by name: {', '.join(changed)}")
        run(["git", "add", "--", *changed], cwd=root)
        run(["git", "commit", "-m", expected_subject], cwd=root)

    if tag_exists:
        cprint(f"  {YELLOW}Tag {tag} already exists locally — skipping tag step.{NC}")
    else:
        run(["git", "tag", "-a", tag, "-m", f"Release {tag}"], cwd=root)

    if rtag_exists:
        cprint(f"  {YELLOW}Resolver tag {rtag} already exists locally — skipping.{NC}")
    else:
        run(["git", "tag", "-a", rtag, "-m", f"Resolver tag for {tag}"], cwd=root)

    # gh-auth precheck — fail fast with actionable error if gh missing/unauthed.
    owner, repo = _resolve_owner_repo(root)
    _ensure_gh_auth(owner, repo)
    # Atomic push: commit + tag land together or not at all. Eliminates the
    # half-published-state failure mode where `git push origin HEAD --tags`
    # could push the commit, fail on the tag (rejected/network), and leave
    # the remote with an unreleased commit + no tag. `--atomic` is a single
    # transaction in the wire protocol; the server rolls back if any ref
    # update fails. git_with_retry still wraps the call so transient
    # network hiccups (4xx-class permanent errors fall through immediately).
    cprint(f"  {BLUE}$ git push --atomic origin HEAD {tag} {rtag}{NC}")
    git_with_retry(
        ["git", "push", "--atomic", "origin", "HEAD", tag, rtag],
        cwd=str(root), capture_output=False,
    )
    cprint(f"  {GREEN}Pushed {tag} + {rtag} atomically.{NC}")

def _changelog_section(changelog: Path, new_ver: str) -> str | None:
    """The CHANGELOG body for exactly `new_ver`, or None when it is not present.

    Returns None rather than a best-effort slice: the caller falls back to
    `gh --generate-notes`, and a wrong-but-plausible section would ship the
    previous release's notes under this release's tag.
    """
    try:
        text = changelog.read_text(encoding="utf-8")
    except OSError:
        return None
    # cliff.toml emits `## [1.4.0] — 2026-08-08`; match the version only, so a
    # date-format change in cliff.toml cannot silently break the extraction.
    start = re.search(rf"^## \[{re.escape(new_ver)}\][^\n]*$", text, re.MULTILINE)
    if not start:
        return None
    rest = text[start.end():]
    nxt = re.search(r"^## \[", rest, re.MULTILINE)
    body = (rest[: nxt.start()] if nxt else rest).strip()
    return f"{start.group(0)}\n\n{body}\n" if body else None


def stage_gh_release(root: Path, new_ver: str, dry_run: bool) -> None:
    """Step 11: Create GitHub release via gh CLI.

    TRDD-bbff5bc5 §5: re-runs the gh-auth precheck before `gh release
    create` so an auth state change between gates 10 and 11 (token
    revoked, account switched) surfaces as an actionable error.
    """
    cprint(f"\n{BOLD}[11/11] Creating GitHub release...{NC}")
    tag = f"v{new_ver}"
    if not shutil.which("gh"):
        cprint(f"  {YELLOW}gh CLI not installed — skipping release.{NC}")
        return
    if dry_run:
        cprint(f"  Would create release: {tag}")
        return
    owner, repo = _resolve_owner_repo(root)
    _ensure_gh_auth(owner, repo)
    changelog_file = root / "CHANGELOG.md"
    # Ship ONLY this version's section as the release notes.
    #
    # This is the derived half of the step-9 `--prepend` fix, and it had to land
    # in the same change: passing the whole CHANGELOG was harmless only WHILE the
    # file held a single section. The moment step 9 correctly accumulates, the
    # same code would publish the project's entire history as the notes for one
    # release — fixing the truncation bug would have created a worse one.
    #
    # Falls back to --generate-notes (never to the whole file) when the section
    # cannot be found: gh then derives notes from the commit range, which is
    # accurate-but-terse. Falling back to the full file would silently reinstate
    # exactly the failure this guards against. Never pass both flags — some gh
    # versions concatenate and some override.
    args = ["gh", "release", "create", tag, "--title", tag]
    notes = _changelog_section(changelog_file, new_ver) if changelog_file.is_file() else None
    if notes:
        # Temp dir, NOT the repo root: a stray .release-notes-*.md in the tree
        # would leave it dirty and abort the NEXT publish at stage [1/11] — the
        # same way the stale uv.lock did twice before it was fixed.
        notes_path = Path(tempfile.mkdtemp(prefix="amia-relnotes-")) / f"{tag}.md"
        notes_path.write_text(notes, encoding="utf-8")
        args.extend(["--notes-file", str(notes_path)])
    else:
        if changelog_file.is_file():
            cprint(f"  {YELLOW}No CHANGELOG section for {tag} — using gh --generate-notes.{NC}")
        args.append("--generate-notes")
    cprint(f"  {BLUE}$ {' '.join(args)}{NC}")
    result = gh_with_retry(args, cwd=str(root), check=False, capture_output=True)
    if result.stdout and result.stdout.strip():
        cprint(result.stdout.strip())
    if result.stderr and result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode == 0:
        cprint(f"  {GREEN}Release created.{NC}")
        return
    # `gh release create` returns an "already_exists" / "already exists"
    # validation error when a release for this tag is already present. On a
    # re-run or interrupted-publish recovery that is the idempotent-success
    # outcome (the release IS there), so it must NOT abort — match either
    # spelling gh emits, case-insensitively.
    combined_err = f"{result.stdout or ''}\n{result.stderr or ''}"
    if re.search(r"already[ _]exists", combined_err, re.IGNORECASE):
        cprint(f"  {YELLOW}Release {tag} already exists — treating as success (idempotent re-run).{NC}")
        return
    # Any other non-zero exit is a genuine failure (auth revoked mid-pipeline,
    # malformed notes file, network exhausted all retries). The tag is already
    # pushed, but the documented final stage did NOT complete — abort so the
    # pipeline does not falsely report success (fail-fast invariant).
    cprint(f"  {RED}Failed to create release (exit code {result.returncode}).{NC}")
    cprint(f"  {RED}  The tag {tag} is pushed; create the release manually or re-run after fixing the cause.{NC}")
    sys.exit(1)


# -- Main ----------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified publish pipeline for Claude Code plugins.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Mutually exclusive modes: side-modes (--gate / --install-hook /
    # --install-branch-rules) are distinct entry points; --patch/--minor/--major
    # are OPTIONAL overrides for the auto-bump default. Calling publish.py with
    # no flags runs the full publish pipeline with an auto-detected bump type.
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--gate", action="store_true",
                            help="Pre-push gate mode: lint + validate + tests only (no bump/push)")
    mode_group.add_argument("--install-hook", action="store_true",
                            help="Install pre-push hook into .git/hooks/ and set core.hooksPath")
    mode_group.add_argument("--install-branch-rules", action="store_true",
                            dest="install_branch_rules",
                            help="Apply the cpv-branch-rules ruleset to the GitHub origin "
                                 "(enforces CI as a required status check — the server-side gate)")
    mode_group.add_argument("--patch", action="store_const", dest="bump", const="patch",
                            help="Force a patch bump (override auto-detection)")
    mode_group.add_argument("--minor", action="store_const", dest="bump", const="minor",
                            help="Force a minor bump (override auto-detection)")
    mode_group.add_argument("--major", action="store_const", dest="bump", const="major",
                            help="Force a major bump (override auto-detection)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no changes")
    # NOTE: --skip-tests was intentionally removed. The cornerstone rule is that
    # every CPV plugin MUST pass validation with 0 issues (WARNING allowed) before
    # any push. Skipping tests would bypass that guarantee — there are no exceptions.
    args = parser.parse_args()

    root = get_repo_root()

    # --install-hook mode: just set up the hook and exit
    if args.install_hook:
        return install_hook(root)

    # --install-branch-rules mode: apply the server-side GitHub ruleset
    if args.install_branch_rules:
        return install_branch_rules(root)

    # --gate mode: run quality checks only (called by pre-push hook)
    if args.gate:
        return run_gate(root)

    # Full publish pipeline — auto-detect bump type unless user forced one.
    # Idempotency: read REMOTE plugin.json (origin/master) as the bump
    # baseline. When local is ahead (interrupted publish: bumped + committed
    # but not pushed), bumping from local would double-bump. From remote,
    # bumping recomputes the SAME target as the original interrupted run,
    # and stage_bump's "already-at-target" guard then skips the bump.
    local = get_current_version(root)
    if not local:
        cprint(f"{RED}Cannot read version from .claude-plugin/plugin.json{NC}")
        return 1
    remote = _read_remote_version(root)
    baseline = remote or local

    if args.bump is None:
        bump_type = detect_bump_type(root)
        cprint(f"{BLUE}Bump type: {bump_type} (auto-detected from git-cliff){NC}")
    else:
        bump_type = args.bump
        cprint(f"{BLUE}Bump type: {bump_type} (forced via --{bump_type}){NC}")

    new_ver = bump_semver(baseline, bump_type)
    if not new_ver:
        cprint(f"{RED}Cannot parse baseline version: {baseline}{NC}")
        return 1

    if remote and local != remote:
        cprint(f"{YELLOW}Local plugin.json is at {local} but origin is at {remote} — "
               f"using remote as bump baseline (interrupted-publish recovery).{NC}")
    current = baseline

    cprint(f"\n{BOLD}Publish pipeline: {current} -> {new_ver}{NC}")
    if args.dry_run:
        cprint(f"{YELLOW}(dry-run mode — no changes will be made){NC}")

    # Gate 0: reject bypass attempts BEFORE running any other stage.
    # Pipeline order (per the cornerstone rule "every push is a bump"):
    #   lint+typecheck → tests → validate → marketplace-reg → consistency →
    #   bump → badge → changelog → commit → push → github release
    # Lint runs before tests (cheap fails first). Tests run before validate
    # so behavioral regressions fail the test suite before the structural
    # validator inspects the manifest.
    stage_bypass_guard()
    stage_check_clean(root)
    stage_lint(root)
    stage_tests(root)  # MANDATORY — no skip flag, no exceptions
    stage_validate(root)
    stage_marketplace_registration(root)  # Gate 6 parity with CPV's own publish.py
    stage_consistency(root)
    stage_bump(root, new_ver, args.dry_run)
    stage_update_badges(root, current, new_ver, args.dry_run)
    stage_changelog(root, new_ver, args.dry_run)
    stage_commit_and_push(root, new_ver, args.dry_run)
    stage_gh_release(root, new_ver, args.dry_run)

    cprint(f"\n{GREEN}{BOLD}Published {new_ver} successfully!{NC}")
    return stage_verify_ci(root, new_ver, args.dry_run)


CI_VERIFY_TIMEOUT_SEC = 1800
CI_VERIFY_POLL_SEC = 20
# Runs only on push, so they can never appear on a PR and must not be waited for
# as if they were gates.
CI_VERIFY_IGNORE = {"notify", "release"}


def stage_verify_ci(root: Path, new_ver: str, dry_run: bool) -> int:
    """Post-release: confirm CI actually went GREEN on the released commit.

    This closes a hole the branch ruleset opens by design. `baseline-pr-and-checks`
    grants an admin bypass so publish.py can push straight to the default branch —
    which means the required status checks NEVER gate the release push. Without
    this stage the pipeline reports "Published successfully" from the fact that
    `git push` and `gh release create` returned 0, having verified nothing about
    whether the released commit builds. A red CI on a published tag would sit
    unnoticed until somebody happened to look. (CPV v5.1.1 flags the same gap.)

    Deliberately runs AFTER the release: the commit must be on the remote for CI
    to start at all, so this can only ever be a detection, never a prevention. It
    does NOT attempt to unpublish — the release is already public and silently
    retracting it would be worse than reporting it. It returns non-zero so the
    failure is visible in the exit status instead of only in scrollback.
    """
    cprint(f"\n{BOLD}Verifying CI on the released commit...{NC}")
    if dry_run:
        cprint(f"  Would wait up to {CI_VERIFY_TIMEOUT_SEC // 60} min for CI on HEAD")
        return 0
    if not shutil.which("gh"):
        cprint(f"  {YELLOW}gh CLI not installed — cannot verify CI. Check manually.{NC}")
        return 0

    slug = _get_origin_slug(root)
    sha = _git_stdout(root, ["git", "rev-parse", "HEAD"])
    if not slug or not sha:
        cprint(f"  {YELLOW}Could not resolve repo slug or HEAD sha — check CI manually.{NC}")
        return 0
    cprint(f"  {slug}@{sha[:8]} — polling (up to {CI_VERIFY_TIMEOUT_SEC // 60} min)")

    deadline = time.monotonic() + CI_VERIFY_TIMEOUT_SEC
    unreadable = False
    while True:
        runs = _ci_check_runs(slug, sha)
        if runs is None:
            # Keep polling rather than returning: right after a push the commit
            # may not have registered checks yet, and a transient API failure is
            # not evidence of anything. Crucially this does NOT return 0 — an
            # unreadable list must never produce a green verdict (same fail-closed
            # rule as the branch-rules guard). If it is still unreadable at the
            # deadline the timeout branch reports NOT-verified and exits non-zero.
            unreadable = True
            if time.monotonic() >= deadline:
                cprint(f"  {YELLOW}Could not read check-runs before the deadline. "
                       f"NOT verified green — check CI manually.{NC}")
                return 1
            time.sleep(CI_VERIFY_POLL_SEC)
            continue
        unreadable = False
        gating = [r for r in runs if r.get("name") not in CI_VERIFY_IGNORE]
        pending = [r for r in gating if r.get("status") != "completed"]
        # A conclusion of `skipped`/`neutral` is NOT a failure: a conditional job
        # that correctly did not run must not be read as a red build.
        failed = [
            r for r in gating
            if r.get("status") == "completed"
            and r.get("conclusion") not in ("success", "skipped", "neutral")
        ]
        if failed:
            names = ", ".join(f"{r['name']}={r.get('conclusion')}" for r in failed)
            cprint(f"  {RED}CI FAILED on the released commit: {names}{NC}")
            cprint(f"  {RED}v{new_ver} is already published — fix forward and re-release.{NC}")
            return 1
        if gating and not pending:
            cprint(f"  {GREEN}CI green on {sha[:8]} ({len(gating)} checks).{NC}")
            return 0
        if time.monotonic() >= deadline:
            # Timing out is NOT proof of success — say so rather than implying green.
            if unreadable:
                waiting = "check-runs unreadable"
            else:
                waiting = ", ".join(r["name"] for r in pending) or "no checks reported yet"
            cprint(f"  {YELLOW}Timed out waiting for CI ({waiting}). NOT verified green.{NC}")
            return 1
        time.sleep(CI_VERIFY_POLL_SEC)


def _git_stdout(root: Path, cmd: list[str]) -> str | None:
    r = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, check=False)
    return r.stdout.strip() if r.returncode == 0 else None


def _ci_check_runs(slug: str, sha: str) -> list[dict] | None:
    """Check-runs for `sha`, or None when the list could not be read.

    None (not []) on failure for the same reason as the branch-rules guard: an
    empty list reads as "nothing failed", which would turn an unreadable API into
    a green verdict.
    """
    try:
        r = gh_with_retry(
            ["gh", "api", f"repos/{slug}/commits/{sha}/check-runs",
             "--jq", ".check_runs[] | {name, status, conclusion}"],
            check=False, capture_output=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if getattr(r, "returncode", 1) != 0:
        return None
    out: list[dict] = []
    for line in (r.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            return None
    return out


if __name__ == "__main__":
    sys.exit(main())
