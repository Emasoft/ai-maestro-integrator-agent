#!/usr/bin/env python3
"""
Drop the PostgreSQL test database belonging to a worktree.

Reads the database name from the worktree's metadata dict and drops it with
``dropdb --if-exists`` (a no-op if the database is already gone). Call this from
a worktree-removal routine so per-worktree test databases do not accumulate.

Usage (as a library):
    from amia_cleanup_test_database import cleanup_test_database
    cleanup_test_database({"database": "testdb_pr_123"})
"""

import subprocess


def cleanup_test_database(metadata: dict) -> None:
    """Drop the test database named in metadata, if one is present."""
    if "database" not in metadata:
        return

    db_name = metadata["database"]

    # Drop the database; --if-exists makes a missing database harmless.
    subprocess.run(["dropdb", "--if-exists", db_name])

    print(f"Removed test database: {db_name}")
