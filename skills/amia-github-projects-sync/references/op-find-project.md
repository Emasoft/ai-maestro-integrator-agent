# Operation: Find GitHub Project


## Contents

- [Metadata](#metadata)
- [Purpose](#purpose)
- [Preconditions](#preconditions)
- [Input](#input)
- [Procedure](#procedure)
- [Command: List All Projects](#command-list-all-projects)
- [Command: Get Specific Project](#command-get-specific-project)
- [Alternative: Using gh CLI](#alternative-using-gh-cli)
- [Output](#output)
- [Project ID Format](#project-id-format)
- [Error Handling](#error-handling)
- [Project Scope Types](#project-scope-types)
- [Verification](#verification)
- [Related Operations](#related-operations)

## Metadata

| Field | Value |
|-------|-------|
| **Operation ID** | op-find-project |
| **Procedure** | proc-populate-kanban |
| **Workflow Instruction** | Step 13 - Kanban Population |
| **Category** | GitHub Projects Sync |
| **Agent** | api-coordinator |

## Purpose

Find a GitHub Projects V2 project ID using repository information and project number.

## Preconditions

- GitHub CLI (`gh`) is authenticated with `project` scope
- Repository has GitHub Projects V2 enabled
- Project exists and is accessible

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `owner` | string | Yes | Repository owner |
| `repo` | string | Yes | Repository name |
| `project_number` | int | No | Specific project number (optional) |

## Procedure

1. Query repository for associated projects
2. If project_number specified, find that specific project
3. If not specified, list all available projects
4. Return project ID(s) and metadata

## Command: List All Projects

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      projectsV2(first: 10) {
        nodes {
          id
          title
          number
          url
        }
      }
    }
  }
'
```

## Command: Get Specific Project

```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      projectV2(number: PROJECT_NUMBER) {
        id
        title
        number
        url
      }
    }
  }
'
```

## Alternative: Using gh CLI

```bash
# List all projects for owner
gh project list --owner OWNER

# Get specific project
gh project view PROJECT_NUMBER --owner OWNER
```

## Output

```json
{
  "id": "PVT_kwDOABCD1234",
  "title": "Development Board",
  "number": 1,
  "url": "https://github.com/orgs/owner/projects/1"
}
```

## Project ID Format

GitHub Projects V2 uses GraphQL node IDs:
- Format: `PVT_kwDO...` (base64 encoded)
- Required for all GraphQL mutations
- Different from project number (integer)

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Project not found | Invalid number or not linked | Use `gh project list` to find available projects |
| Auth error | Missing `project` scope | Run `gh auth refresh -s project` |
| No projects | Repository has no projects | Create a project first |

## Project Scope Types

| Type | Query Location | Example |
|------|----------------|---------|
| Repository Project | `repository.projectV2` | Project linked to specific repo |
| Organization Project | `organization.projectV2` | Org-wide project |
| User Project | `user.projectV2` | Personal project |

## Verification

After finding project, verify access:

```bash
# Check if you can read project items
gh project item-list PROJECT_NUMBER --owner OWNER --limit 1
```

## Related Operations

- [op-query-project-items.md](op-query-project-items.md) - Query items in found project
- [op-update-item-status.md](op-update-item-status.md) - Update items in project
