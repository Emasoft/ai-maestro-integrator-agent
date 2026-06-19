#!/usr/bin/env python3
"""
Generate a worktree config file by substituting allocated ports into a template.

Reads a template containing `${ALLOCATED_*_PORT}` and `${WORKTREE_NAME}`
placeholders, replaces them with the ports allocated to the worktree in the
registry, and writes the rendered config to the output path.

The `load_registry` helper is provided by your port-management module.

Usage (as a library):
    from amia_generate_worktree_config import generate_config
    generate_config("feature-payment", "tmpl/.env.worktree.template",
                    "feature-payment/.env.worktree", load_registry)
"""


def generate_config(worktree_name: str, template_path: str, output_path: str, load_registry) -> None:
    """Render a worktree config from a template using its allocated ports."""
    # Look up the ports allocated to this worktree.
    registry = load_registry()
    ports = registry["allocated_ports"][worktree_name]

    # Read the template.
    with open(template_path, "r") as f:
        template = f.read()

    # Substitute the placeholders.
    config = template.replace("${ALLOCATED_WEB_PORT}", str(ports["web"]))
    config = config.replace("${ALLOCATED_DB_PORT}", str(ports["db"]))
    config = config.replace("${ALLOCATED_TEST_PORT}", str(ports["test"]))
    config = config.replace("${ALLOCATED_DEBUG_PORT}", str(ports["debug"]))
    config = config.replace("${WORKTREE_NAME}", worktree_name)

    # Write the rendered config.
    with open(output_path, "w") as f:
        f.write(config)

    print(f"Generated config: {output_path}")
