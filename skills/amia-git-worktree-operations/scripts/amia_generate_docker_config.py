#!/usr/bin/env python3
"""
Generate a worktree's Docker config from its allocated ports.

Two helpers:

- ``generate_docker_compose`` renders a ``docker-compose.yml`` for the worktree
  from a template, substituting the allocated ports.
- ``generate_docker_env`` writes a ``.env.docker`` file listing the allocated
  ports as ``KEY=value`` lines.

The ``load_registry`` helper is provided by your port-management module.

Usage (as a library):
    from amia_generate_docker_config import generate_docker_compose, generate_docker_env
"""

from pathlib import Path


def generate_docker_compose(worktree_name: str, load_registry) -> str:
    """Render docker-compose.yml for the worktree from the compose template."""
    registry = load_registry()
    ports = registry["allocated_ports"][worktree_name]

    # Load the compose template.
    with open("docker-compose.worktree.template.yml", "r") as f:
        template = f.read()

    # Substitute the placeholders.
    compose = template.replace("${ALLOCATED_WEB_PORT}", str(ports["web"]))
    compose = compose.replace("${ALLOCATED_DB_PORT}", str(ports["db"]))
    compose = compose.replace("${ALLOCATED_TEST_PORT}", str(ports["test"]))
    compose = compose.replace("${WORKTREE_NAME}", worktree_name)

    # Write into the worktree directory.
    output_path = f"{worktree_name}/docker-compose.yml"
    with open(output_path, "w") as f:
        f.write(compose)

    print(f"Generated: {output_path}")
    return output_path


def generate_docker_env(worktree_path, worktree_name: str, ports: dict) -> None:
    """Write a .env.docker file with the worktree's allocated ports."""
    env_file = Path(worktree_path) / ".env.docker"

    with open(env_file, "w") as f:
        f.write(f"WEB_PORT={ports['web']}\n")
        f.write(f"DB_PORT={ports['db']}\n")
        f.write(f"REDIS_PORT={ports['redis']}\n")
        f.write(f"WORKTREE_ID={worktree_name}\n")

    print(f"Generated {env_file}")
