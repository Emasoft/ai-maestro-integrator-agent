#!/usr/bin/env python3
"""Real tests for the agent cost reporter (scripts/cpv_token_cost.py).

Exercises the real module against real inputs — no mocks. The transcript check
writes an actual JSONL file to a temp dir and parses it through the real
`parse_transcript`, so the dedup-by-message-id and 4-category summing paths are
genuinely executed.

Two failure modes are worth a permanent guardrail, and both are silent — a wrong
rate produces a plausible dollar figure, never an error:

  1. `get_pricing` substring-matches MODEL_PRICING keys in INSERTION ORDER, and a
     shorter key is a substring of a longer one ("claude-opus-4" lives inside
     "claude-opus-4-8"). Reordering the table so a less specific key sits above a
     more specific one silently returns the wrong rate.
  2. The fuzzy family fallback must aim at the CURRENT generation. Aiming it at a
     retired model is what priced Opus 5 runs at Opus 4.1's $15/$75 — 3x actual.

Runs two ways:

  uv run --with pytest pytest tests/test_token_cost.py -q
  uv run python tests/test_token_cost.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
sys.path.insert(0, str(PLUGIN_ROOT / "tests"))

from _table_runner import (
    run_table,  # noqa: E402  # pyright: ignore[reportMissingImports]
)
from cpv_token_cost import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    MODEL_PRICING,
    TokenUsage,
    estimate_cost,
    get_pricing,
    parse_transcript,
)

# Published rates (USD per 1M tokens) for the current generation, as (input, output).
CURRENT_RATES = {
    "claude-fable-5": (10.0, 50.0),
    "claude-opus-5": (5.0, 25.0),
    "claude-sonnet-5": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
}
RETIRED_OPUS_INPUT = 15.0  # Opus 4.0/4.1 — must never be charged for a newer id.


# ── The checks (shared by pytest wrappers and the standalone runner) ──


def check_current_generation_rates() -> str:
    """Every current-generation model id resolves to its published input/output rate."""
    for model, (want_in, want_out) in CURRENT_RATES.items():
        p = get_pricing(model)
        if (p["input"], p["output"]) != (want_in, want_out):
            return f"FAIL: {model} priced {p['input']}/{p['output']}, expected {want_in}/{want_out}"
    return "PASS"


def check_derived_cache_rates() -> str:
    """Cache rates stay derived from input: write = 1.25x, read = 0.10x."""
    for model in MODEL_PRICING:
        p = MODEL_PRICING[model]
        want_write = round(p["input"] * 1.25, 4)
        want_read = round(p["input"] * 0.10, 4)
        if round(p["cache_write"], 4) != want_write:
            return f"FAIL: {model} cache_write {p['cache_write']}, expected {want_write}"
        if round(p["cache_read"], 4) != want_read:
            return f"FAIL: {model} cache_read {p['cache_read']}, expected {want_read}"
    return "PASS"


def check_specific_key_beats_shorter_prefix() -> str:
    """A dated model id matches its own family key, not a shorter key that prefixes it."""
    # This MUST use dated ids. A bare "claude-opus-4-8" is itself a table key, so
    # the exact-match lookup returns before the substring loop ever runs and the
    # check would pass even with the table deliberately mis-ordered. The dated
    # form the API actually returns ("claude-opus-4-8-20260301") misses the exact
    # lookup and falls into the loop, where "claude-opus-4" ALSO matches and only
    # insertion order decides the winner. That is the regression worth catching.
    for model, want in (
        ("claude-opus-4-8-20260301", 5.0),
        ("claude-opus-4-7-20260101", 5.0),
        ("claude-opus-4-6-20251101", 5.0),
        ("claude-sonnet-4-6-20251215", 3.0),
    ):
        got = get_pricing(model)["input"]
        if got != want:
            return f"FAIL: {model} priced at ${got}/MTok input, expected ${want} (key order regression)"
    return "PASS"


def check_unknown_opus_uses_current_generation() -> str:
    """An unrecognized opus id falls back to the current generation, not a retired one."""
    got = get_pricing("claude-opus-99-unreleased")["input"]
    if got == RETIRED_OPUS_INPUT:
        return f"FAIL: unknown opus fell back to the retired ${got}/MTok rate"
    if got != 5.0:
        return f"FAIL: unknown opus priced at ${got}/MTok input, expected $5.0"
    return "PASS"


def check_legacy_ids_keep_legacy_rates() -> str:
    """Retired model ids still price at their own rates so archived transcripts stay correct."""
    for model in ("claude-opus-4-1", "claude-opus-4-20250514"):
        got = get_pricing(model)["input"]
        if got != RETIRED_OPUS_INPUT:
            return f"FAIL: {model} priced at ${got}/MTok input, expected ${RETIRED_OPUS_INPUT}"
    if get_pricing("claude-haiku-3-5")["input"] != 0.80:
        return "FAIL: claude-haiku-3-5 lost its legacy $0.80/MTok input rate"
    return "PASS"


def check_context_suffix_resolves() -> str:
    """A context-variant id ("claude-opus-5[1m]") prices the same as the bare id."""
    bare = get_pricing("claude-opus-5")
    suffixed = get_pricing("claude-opus-5[1m]")
    if bare != suffixed:
        return f"FAIL: suffixed id priced {suffixed}, bare id priced {bare}"
    return "PASS"


def check_empty_model_does_not_crash() -> str:
    """An empty or unknown model name returns default pricing instead of raising."""
    for model in ("", "totally-unknown-model"):
        p = get_pricing(model)
        if not all(k in p for k in ("input", "output", "cache_write", "cache_read")):
            return f"FAIL: {model!r} returned an incomplete pricing dict: {p}"
    return "PASS"


def check_cost_from_real_transcript(tmp: Path) -> str:
    """A real JSONL transcript parses, deduplicates by message id, and costs correctly."""
    transcript = tmp / "agent.jsonl"
    lines = [
        {"type": "user", "message": {"content": "ignored — not an assistant turn"}},
        {"type": "assistant", "message": {
            "id": "msg_1", "model": "claude-opus-5",
            "usage": {"input_tokens": 1000, "output_tokens": 2000,
                      "cache_creation_input_tokens": 4000, "cache_read_input_tokens": 500_000},
        }},
        # Same id repeated — the streaming transcript does this; it must count once.
        {"type": "assistant", "message": {
            "id": "msg_1", "model": "claude-opus-5",
            "usage": {"input_tokens": 1000, "output_tokens": 2000,
                      "cache_creation_input_tokens": 4000, "cache_read_input_tokens": 500_000},
        }},
        {"type": "assistant", "message": {
            "id": "msg_2", "model": "claude-opus-5",
            "usage": {"input_tokens": 0, "output_tokens": 0,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 300_000},
        }},
    ]
    transcript.write_text("\n".join(json.dumps(x) for x in lines) + "\n", encoding="utf-8")

    usage = parse_transcript(transcript)
    if usage.message_count != 2:
        return f"FAIL: expected 2 deduplicated assistant messages, got {usage.message_count}"
    if usage.model != "claude-opus-5":
        return f"FAIL: expected model claude-opus-5, got {usage.model}"
    if usage.cache_read_input_tokens != 800_000:
        return f"FAIL: expected 800000 cache-read tokens, got {usage.cache_read_input_tokens}"

    # 1000 in @$5 + 2000 out @$25 + 4000 write @$6.25 + 800000 read @$0.50 per 1M.
    want = 0.005 + 0.05 + 0.025 + 0.40
    got = estimate_cost(usage)
    if abs(got - want) > 1e-9:
        return f"FAIL: cost {got:.6f}, expected {want:.6f}"
    return "PASS"


def check_missing_transcript_is_zero(tmp: Path) -> str:
    """A missing transcript yields an empty usage and $0.00 rather than an exception."""
    usage = parse_transcript(tmp / "does-not-exist.jsonl")
    if usage.total_tokens() != 0 or usage.message_count != 0:
        return f"FAIL: expected empty usage, got {usage.to_dict()}"
    if estimate_cost(usage) != 0.0:
        return f"FAIL: expected $0.00 for empty usage, got {estimate_cost(usage)}"
    return "PASS"


def check_explicit_model_overrides_transcript() -> str:
    """An explicit model argument overrides the model recorded in the usage."""
    usage = TokenUsage()
    usage.input_tokens = 1_000_000
    usage.model = "claude-opus-5"
    if estimate_cost(usage) != 5.0:
        return f"FAIL: expected $5.00 at the usage model's rate, got {estimate_cost(usage)}"
    if estimate_cost(usage, "claude-haiku-4-5") != 1.0:
        return f"FAIL: explicit model ignored, got {estimate_cost(usage, 'claude-haiku-4-5')}"
    return "PASS"


CHECKS = [
    "check_current_generation_rates",
    "check_derived_cache_rates",
    "check_specific_key_beats_shorter_prefix",
    "check_unknown_opus_uses_current_generation",
    "check_legacy_ids_keep_legacy_rates",
    "check_context_suffix_resolves",
    "check_empty_model_does_not_crash",
    "check_cost_from_real_transcript",
    "check_missing_transcript_is_zero",
    "check_explicit_model_overrides_transcript",
]


# ── pytest wrappers (the publish pipeline runs `pytest tests/`) ──

try:
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.fixture(scope="session")
    def costenv(tmp_path_factory: "pytest.TempPathFactory") -> Path:
        return tmp_path_factory.mktemp("amia-costtest")

    def test_current_generation_rates() -> None:
        assert check_current_generation_rates().startswith("PASS")

    def test_derived_cache_rates() -> None:
        assert check_derived_cache_rates().startswith("PASS")

    def test_specific_key_beats_shorter_prefix() -> None:
        assert check_specific_key_beats_shorter_prefix().startswith("PASS")

    def test_unknown_opus_uses_current_generation() -> None:
        assert check_unknown_opus_uses_current_generation().startswith("PASS")

    def test_legacy_ids_keep_legacy_rates() -> None:
        assert check_legacy_ids_keep_legacy_rates().startswith("PASS")

    def test_context_suffix_resolves() -> None:
        assert check_context_suffix_resolves().startswith("PASS")

    def test_empty_model_does_not_crash() -> None:
        assert check_empty_model_does_not_crash().startswith("PASS")

    def test_cost_from_real_transcript(costenv: Path) -> None:
        assert check_cost_from_real_transcript(_sub(costenv, "a")).startswith("PASS")

    def test_missing_transcript_is_zero(costenv: Path) -> None:
        assert check_missing_transcript_is_zero(_sub(costenv, "b")).startswith("PASS")

    def test_explicit_model_overrides_transcript() -> None:
        assert check_explicit_model_overrides_transcript().startswith("PASS")

except ImportError:
    pass


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="amia-costtest-"))

    runners = {
        "check_current_generation_rates": check_current_generation_rates,
        "check_derived_cache_rates": check_derived_cache_rates,
        "check_specific_key_beats_shorter_prefix": check_specific_key_beats_shorter_prefix,
        "check_unknown_opus_uses_current_generation": check_unknown_opus_uses_current_generation,
        "check_legacy_ids_keep_legacy_rates": check_legacy_ids_keep_legacy_rates,
        "check_context_suffix_resolves": check_context_suffix_resolves,
        "check_empty_model_does_not_crash": check_empty_model_does_not_crash,
        "check_cost_from_real_transcript": lambda: check_cost_from_real_transcript(_sub(tmp, "a")),
        "check_missing_transcript_is_zero": lambda: check_missing_transcript_is_zero(_sub(tmp, "b")),
        "check_explicit_model_overrides_transcript": check_explicit_model_overrides_transcript,
    }

    try:
        return run_table(CHECKS, lambda n: runners[n](), lambda n: globals()[n].__doc__)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _sub(tmp: Path, name: str) -> Path:
    d = tmp / name
    d.mkdir(exist_ok=True)
    return d


if __name__ == "__main__":
    sys.exit(main())
