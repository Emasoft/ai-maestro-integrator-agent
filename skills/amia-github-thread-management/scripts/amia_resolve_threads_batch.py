#!/usr/bin/env python3
"""
Resolve multiple GitHub PR review threads in a single API call.

Usage:
    python3 amia_resolve_threads_batch.py --thread-ids "PRRT_aaa,PRRT_bbb,PRRT_ccc"

Output:
    JSON object with results array containing success/failure per thread.

Example:
    python3 amia_resolve_threads_batch.py --thread-ids "PRRT_kwDOaaa,PRRT_kwDObbb"

Note:
    Uses GraphQL aliased mutations to resolve multiple threads in 1 API call.
    This is much more efficient than individual resolution calls.

Exit codes (standardized):
    0 - Success, all threads resolved (or partial success with details in JSON)
    1 - Invalid parameters (bad thread ID format)
    2 - Resource not found (N/A - individual failures in JSON output)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip (N/A for this script)
    6 - Not mergeable (N/A for this script)
"""

import argparse
import json
import subprocess
import sys
from typing import Any


def run_graphql_with_variables(query: str, variables: dict[str, str]) -> dict[str, Any]:
    """Execute a GraphQL query/mutation using gh CLI with proper variable binding.

    Uses -f parameter binding to prevent GraphQL injection attacks.
    Variables are passed securely via subprocess arguments, NOT string interpolation.
    """
    # Build command with query and all variables as separate -f arguments
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for var_name, var_value in variables.items():
        cmd.extend(["-f", f"{var_name}={var_value}"])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        error_msg = result.stderr.strip() or "Unknown error"
        raise RuntimeError(f"GraphQL mutation failed: {error_msg}")

    return json.loads(result.stdout)


def build_batch_mutation_with_variables(thread_ids: list[str]) -> tuple[str, dict[str, str]]:
    """Build a GraphQL mutation with aliases and variables for multiple thread resolutions.

    Returns tuple of (query_string, variables_dict) for secure parameter binding.
    Uses GraphQL variables to prevent injection attacks.
    """
    # Build variable declarations like: $t0: ID!, $t1: ID!, ...
    var_decls = ", ".join(f"$t{i}: ID!" for i in range(len(thread_ids)))

    # Build mutation body with variable references (not string values)
    mutations = []
    for i in range(len(thread_ids)):
        mutations.append(f"""
        t{i}: resolveReviewThread(input: {{threadId: $t{i}}}) {{
          thread {{
            id
            isResolved
          }}
        }}""")

    query = f"mutation({var_decls}) {{" + "".join(mutations) + "\n}"

    # Build variables dict mapping t0, t1, etc. to actual thread IDs
    variables = {f"t{i}": tid for i, tid in enumerate(thread_ids)}

    return query, variables


def resolve_threads_batch(thread_ids: list[str]) -> dict[str, Any]:
    """Resolve multiple threads and return results for each."""
    if not thread_ids:
        return {"results": [], "summary": {"total": 0, "succeeded": 0, "failed": 0}}

    # Use secure variable binding instead of string interpolation
    mutation, variables = build_batch_mutation_with_variables(thread_ids)
    response = run_graphql_with_variables(mutation, variables)

    # Process results
    data = response.get("data", {})
    errors = response.get("errors", [])

    # Build error map by path
    error_map: dict[str, str] = {}
    for error in errors:
        path = error.get("path", [])
        if path:
            error_map[path[0]] = error.get("message", "Unknown error")

    # Process each thread result
    results = []
    succeeded = 0
    failed = 0

    for i, thread_id in enumerate(thread_ids):
        alias = f"t{i}"
        thread_data = data.get(alias, {})

        if thread_data is None or alias in error_map:
            # Failed
            results.append({
                "threadId": thread_id,
                "success": False,
                "error": error_map.get(alias, "Resolution returned null"),
            })
            failed += 1
        else:
            thread_info = thread_data.get("thread", {})
            is_resolved = thread_info.get("isResolved", False)

            results.append({
                "threadId": thread_id,
                "success": is_resolved,
                "isResolved": is_resolved,
            })

            if is_resolved:
                succeeded += 1
            else:
                failed += 1

    return {
        "results": results,
        "summary": {
            "total": len(thread_ids),
            "succeeded": succeeded,
            "failed": failed,
        },
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Resolve multiple GitHub PR review threads in a single API call."
    )
    parser.add_argument(
        "--thread-ids",
        required=True,
        help="Comma-separated list of thread IDs (PRRT_xxx,PRRT_yyy)",
    )

    args = parser.parse_args()

    # Parse thread IDs
    thread_ids = [tid.strip() for tid in args.thread_ids.split(",") if tid.strip()]

    # Validate format
    invalid_ids = [tid for tid in thread_ids if not tid.startswith("PRRT_")]
    if invalid_ids:
        print(
            json.dumps({
                "error": f"Invalid thread ID format: {invalid_ids}. IDs should start with 'PRRT_'",
                "code": "INVALID_PARAMS"
            }),
            file=sys.stderr,
        )
        sys.exit(1)  # Invalid parameters

    try:
        result = resolve_threads_batch(thread_ids)
        print(json.dumps(result, indent=2))

        # Exit 0 even with partial failures - check JSON for details
        # This allows batch operations to report partial success

    except RuntimeError as e:
        error_msg = str(e).lower()
        error_output = {"error": str(e), "success": False}

        # Determine appropriate exit code based on error type
        if "auth" in error_msg or "login" in error_msg or "credentials" in error_msg:
            error_output["code"] = "NOT_AUTHENTICATED"
            print(json.dumps(error_output), file=sys.stderr)
            sys.exit(4)  # Not authenticated
        else:
            error_output["code"] = "API_ERROR"
            print(json.dumps(error_output), file=sys.stderr)
            sys.exit(3)  # API error


if __name__ == "__main__":
    main()
