# GitHub Projects Sync Skill

## Purpose

Manages team tasks through GitHub Projects V2, enabling AMOA (Emasoft Orchestrator Agent) to track features, bugs, PRs, and issues with automatic CI integration and project synchronization.

## When to Use

- When assigning GitHub issues to remote agents
- When tracking feature implementation progress
- When synchronizing PR status with project boards
- When managing sprint/iteration planning
- When generating project status reports
- When coordinating multi-agent work on features

## Key Features

- GitHub Projects V2 integration
- GraphQL API operations
- Issue creation and management
- Status updates and synchronization
- AI Maestro notification integration

## Critical Distinction

- **GitHub Projects** = Team/Project tasks (features, bugs, PRs, issues)
- **Claude Tasks** = Orchestrator personal tasks ONLY (reading docs, planning, reviewing)

## Iron Rules

This skill is **READ + STATUS UPDATE ONLY**:

- Query project state via GraphQL API
- Update card status (Todo -> In Progress -> Done)
- Add comments and labels to issues
- Link PRs to project items
- **NEVER**: Execute code, run tests, modify source files

## Entry Point

See [SKILL.md](./SKILL.md) for complete instructions.

## Related Skills

- `remote-agent-coordinator` - Agent task assignment
- `orchestration-patterns` - Sprint coordination
