#!/usr/bin/env python3
"""
pytest fixture that gives each test session a fresh, isolated database.

Drop this into a worktree's ``conftest.py``. It drops any leftover database,
creates a fresh one, points DATABASE_URL at it, runs migrations, then tears the
database down after the whole session. Each worktree passes its own
``test_database`` name (e.g. ``testdb_pr_123``) so parallel worktrees never
share state.

This module is a copy-paste fixture, not a CLI; importing it requires pytest,
Django's ``call_command``, and a ``test_database`` fixture in scope.
"""

import os
import subprocess

import pytest
from django.core.management import call_command


@pytest.fixture(scope="session", autouse=True)
def setup_test_database(test_database):
    """Create a fresh test database for the session, then drop it afterward."""
    # Drop any database left over from a previous run.
    subprocess.run(["dropdb", "--if-exists", test_database])

    # Create a fresh database.
    subprocess.run(["createdb", test_database], check=True)

    # Point the app at this database and run migrations.
    os.environ["DATABASE_URL"] = f"postgresql://localhost/{test_database}"
    call_command("migrate")

    yield

    # Drop the database once all tests in the session have finished.
    subprocess.run(["dropdb", test_database])
