#!/usr/bin/env python3
"""CPV Token Cost Reporter — accurate per-API-call token measurement.

Parses a Claude Code agent transcript (JSONL) to sum the full usage breakdown
(input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens)
from every assistant message, then computes exact cost using per-model pricing.

Dual-mode:
  1. SubagentStop hook: reads hook JSON from stdin, parses agent_transcript_path,
     outputs {"systemMessage": cost_summary} for display in orchestrator context.
  2. CLI: uv run python scripts/cpv_token_cost.py --transcript /path/to/agent.jsonl
  3. Library: from scripts.cpv_token_cost import parse_transcript, estimate_cost
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ── Per-model pricing (USD per million tokens; verified 2026-08-07 against the
#    bundled `claude-api` skill's model table) ──
#
# KEY ORDER IS LOAD-BEARING. get_pricing() substring-matches these keys in
# insertion order, and a shorter key is a substring of a longer one
# ("claude-opus-4" matches inside "claude-opus-4-8"). A less specific key placed
# above a more specific one silently captures it and returns the wrong rate, so
# each family is listed MOST-SPECIFIC FIRST and the bare "claude-opus-4" /
# "claude-sonnet-4" keys stay last within their family.
#
# cache_write = 1.25x input (5-minute TTL); cache_read = 0.10x input.
#
# CEILING: one cache_write column, hardcoded to the 5m multiplier. Cache writes
# bill at 1.25x input for a 5-minute TTL and 2x for a 1-hour TTL — authority is
# Anthropic's live pricing/prompt-caching docs; the bundled claude-api skill's
# shared/prompt-caching.md "Economics" section is where these two numbers were
# read, and it is a SHIPPED COPY with its own staleness, not the rate source.
# Re-read the live docs before trusting these multipliers in a new context.
# Consequence: any agent carrying `experimental.cacheTtl: "1h"` would be
# UNDER-estimated here by 1.6x on its cache writes. NO agent in this plugin
# carries it — the hint was added and then reverted on measurement (93% of
# 17,888 real assistant-turn gaps on this machine were under 5 minutes, the
# band where the 5m TTL refreshes for free and 1h is pure surcharge). So this
# ceiling is LATENT, not active: it bites the day someone sets that frontmatter
# key, and it will not announce itself, because the estimator has no way to
# know the TTL it is mispricing.
#
# The reason is NOT that the data lacks the discriminator — it has it, at these
# exact paths (verified by parsing real transcripts, not by grepping for the
# key name):
#     message.usage.cache_creation.ephemeral_{5m,1h}_input_tokens
#     message.usage.iterations[].cache_creation.ephemeral_{5m,1h}_input_tokens
# Both occur with non-zero 1h values. `parse_transcript` reads neither: it sums
# the flat `cache_creation_input_tokens` and loses the split.
#
# So the upgrade path is UNBLOCKED TODAY, not waiting on anything: read the
# top-level `cache_creation` split (the `iterations[]` copy is a per-iteration
# breakdown of the same totals — sum one or the other, never both), carry both
# buckets on TokenUsage, add a `cache_write_1h` column at 2.0x input, and bill
# each at its own rate. Left undone deliberately — it is a behaviour change to a
# cost estimator and belongs in its own commit with its own tests, not smuggled
# into a comment fix. Do not restate this as "the data doesn't have it".
MODEL_PRICING: dict[str, dict[str, float]] = {
    # Current generation (1M context).
    "claude-fable-5":    {"input": 10.0, "output": 50.0, "cache_write": 12.50, "cache_read": 1.00},
    "claude-opus-5":     {"input": 5.0,  "output": 25.0, "cache_write": 6.25,  "cache_read": 0.50},
    "claude-opus-4-8":   {"input": 5.0,  "output": 25.0, "cache_write": 6.25,  "cache_read": 0.50},
    "claude-opus-4-7":   {"input": 5.0,  "output": 25.0, "cache_write": 6.25,  "cache_read": 0.50},
    "claude-opus-4-6":   {"input": 5.0,  "output": 25.0, "cache_write": 6.25,  "cache_read": 0.50},
    "claude-opus-4-5":   {"input": 5.0,  "output": 25.0, "cache_write": 6.25,  "cache_read": 0.50},
    # Correction (Claude Code changelog 2.1.243): $3.00/$15.00 was only a
    # limited-time promo that has now ended. $2.00/$10.00 is Sonnet 5's
    # standard list price, so it's cheaper than the sonnet-4-x rows below it.
    "claude-sonnet-5":   {"input": 2.0,  "output": 10.0, "cache_write": 2.50,  "cache_read": 0.20},
    "claude-sonnet-4-6": {"input": 3.0,  "output": 15.0, "cache_write": 3.75,  "cache_read": 0.30},
    "claude-sonnet-4-5": {"input": 3.0,  "output": 15.0, "cache_write": 3.75,  "cache_read": 0.30},
    "claude-haiku-4-5":  {"input": 1.0,  "output": 5.0,  "cache_write": 1.25,  "cache_read": 0.10},
    # Legacy / retired — kept so an archived transcript still costs correctly.
    "claude-sonnet-4":   {"input": 3.0,  "output": 15.0, "cache_write": 3.75,  "cache_read": 0.30},
    "claude-opus-4-1":   {"input": 15.0, "output": 75.0, "cache_write": 18.75, "cache_read": 1.50},
    "claude-opus-4":     {"input": 15.0, "output": 75.0, "cache_write": 18.75, "cache_read": 1.50},
    "claude-haiku-3-5":  {"input": 0.80, "output": 4.0,  "cache_write": 1.00,  "cache_read": 0.08},
}
DEFAULT_PRICING: dict[str, float] = {"input": 3.0, "output": 15.0, "cache_write": 3.75, "cache_read": 0.30}


def get_pricing(model_name: str) -> dict[str, float]:
    """Look up pricing for a model name, with fuzzy matching."""
    if not model_name:
        return DEFAULT_PRICING
    if model_name in MODEL_PRICING:
        return MODEL_PRICING[model_name]
    # Try prefix/substring match
    for key, pricing in MODEL_PRICING.items():
        if key in model_name or model_name.startswith(key):
            return pricing
    # Fuzzy family match. Only reached when NO key above matched, i.e. an id this
    # table has never seen — so the right guess is the CURRENT generation of that
    # family, never a retired one. Every legacy 4.x id has its own explicit key
    # above and is caught by the substring loop, so aiming this at an old model
    # buys nothing and costs a lot: pointing "opus" at claude-opus-4-1 is what
    # silently priced Opus 5 runs at the retired $15/$75 (3x the real rate).
    ml = model_name.lower()
    if "fable" in ml:
        return MODEL_PRICING["claude-fable-5"]
    if "opus" in ml:
        return MODEL_PRICING["claude-opus-5"]
    if "sonnet" in ml:
        return MODEL_PRICING["claude-sonnet-5"]
    if "haiku" in ml:
        return MODEL_PRICING["claude-haiku-4-5"]
    return DEFAULT_PRICING


class TokenUsage:
    """Token usage summary from a parsed transcript."""

    __slots__ = ("input_tokens", "output_tokens", "cache_creation_input_tokens",
                 "cache_read_input_tokens", "message_count", "model")

    def __init__(self) -> None:
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.cache_creation_input_tokens: int = 0
        self.cache_read_input_tokens: int = 0
        self.message_count: int = 0
        self.model: str = "unknown"

    def to_dict(self) -> dict[str, int | str]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_creation_input_tokens": self.cache_creation_input_tokens,
            "cache_read_input_tokens": self.cache_read_input_tokens,
            "message_count": self.message_count,
            "model": self.model,
        }

    def total_tokens(self) -> int:
        return (self.input_tokens + self.output_tokens
                + self.cache_creation_input_tokens + self.cache_read_input_tokens)


def parse_transcript(path: str | Path) -> TokenUsage:
    """Parse a JSONL transcript and sum token usage from all assistant messages."""
    result = TokenUsage()
    model_counts: dict[str, int] = {}
    seen_ids: set[str] = set()

    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if entry.get("type") != "assistant":
                    continue
                msg = entry.get("message", {})
                if not isinstance(msg, dict):
                    continue

                # Deduplicate by message id
                mid = msg.get("id", "")
                if mid:
                    if mid in seen_ids:
                        continue
                    seen_ids.add(mid)

                usage = msg.get("usage", {})
                if not usage:
                    continue

                result.input_tokens += usage.get("input_tokens", 0)
                result.output_tokens += usage.get("output_tokens", 0)
                result.cache_creation_input_tokens += usage.get("cache_creation_input_tokens", 0)
                result.cache_read_input_tokens += usage.get("cache_read_input_tokens", 0)
                result.message_count += 1

                model = msg.get("model", "unknown")
                model_counts[model] = model_counts.get(model, 0) + 1
    except (OSError, IOError):
        pass

    # Most-used model
    if model_counts:
        result.model = max(model_counts, key=lambda m: model_counts[m])
    return result


def estimate_cost(usage: TokenUsage, model: str = "") -> float:
    """Compute exact USD cost from the 4-category token breakdown."""
    p = get_pricing(model or usage.model)
    return (
        (usage.input_tokens / 1e6) * p["input"]
        + (usage.output_tokens / 1e6) * p["output"]
        + (usage.cache_creation_input_tokens / 1e6) * p["cache_write"]
        + (usage.cache_read_input_tokens / 1e6) * p["cache_read"]
    )


def fmt_tok(n: int) -> str:
    """Format token count with K/M suffix."""
    if n >= 1_000_000:
        return f"{n / 1e6:.1f}M"
    if n >= 1_000:
        return f"{n / 1e3:.1f}K"
    return str(n)


def format_cost_line(usage: TokenUsage, model: str = "") -> str:
    """One-line cost summary for terminal display."""
    cost = estimate_cost(usage, model)
    m = model or usage.model
    # Shorten model name for display
    short_model = m.replace("claude-", "").split("-2")[0]
    return (
        f"Tokens: {fmt_tok(usage.total_tokens())} "
        f"(in:{fmt_tok(usage.input_tokens)} out:{fmt_tok(usage.output_tokens)} "
        f"cw:{fmt_tok(usage.cache_creation_input_tokens)} cr:{fmt_tok(usage.cache_read_input_tokens)}) "
        f"| Cost: ${cost:.4f} | Model: {short_model}"
    )


def main() -> int:
    """Entry point — hook mode (stdin JSON) or CLI mode (--transcript)."""
    # CLI mode: --transcript PATH
    if "--transcript" in sys.argv:
        idx = sys.argv.index("--transcript")
        if idx + 1 >= len(sys.argv):
            print("Error: --transcript requires a path argument", file=sys.stderr)
            return 1
        transcript_path = sys.argv[idx + 1]
        if not Path(transcript_path).exists():
            print(f"Error: transcript not found: {transcript_path}", file=sys.stderr)
            return 1
        usage = parse_transcript(transcript_path)
        if usage.message_count == 0:
            print("No assistant messages found in transcript.", file=sys.stderr)
            return 1
        print(format_cost_line(usage))
        return 0

    # Hook mode: read JSON from stdin
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 1

    # Get the agent's own transcript path (SubagentStop provides this)
    agent_transcript = hook_input.get("agent_transcript_path", "")
    session_transcript = hook_input.get("transcript_path", "")

    # Prefer agent transcript; fall back to session transcript
    transcript = ""
    if agent_transcript and Path(agent_transcript).exists():
        transcript = agent_transcript
    elif session_transcript and Path(session_transcript).exists():
        transcript = session_transcript

    if not transcript:
        return 0

    usage = parse_transcript(transcript)
    if usage.message_count == 0:
        return 0

    cost_line = format_cost_line(usage)
    # Output as systemMessage so it appears in the orchestrator's context
    print(json.dumps({"systemMessage": f"  {cost_line}"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
