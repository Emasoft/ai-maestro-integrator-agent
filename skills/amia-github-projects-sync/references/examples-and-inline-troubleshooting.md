# Examples and Inline Troubleshooting

## Contents

- [E.1 Example 1: Find and Query a Project](#e1-example-1-find-and-query-a-project)
- [E.2 Example 2: Update Issue Status](#e2-example-2-update-issue-status)
- [E.3 Inline Troubleshooting: Cannot find GitHub Project](#e3-inline-troubleshooting-cannot-find-github-project)
- [E.4 Inline Troubleshooting: Issue not appearing on project board](#e4-inline-troubleshooting-issue-not-appearing-on-project-board)
- [E.5 Inline Troubleshooting: Column/status sync fails](#e5-inline-troubleshooting-columnstatus-sync-fails)
- [E.6 Inline Troubleshooting: Rate limiting from GitHub API](#e6-inline-troubleshooting-rate-limiting-from-github-api)
- [E.7 Inline Troubleshooting: Claude Tasks and GitHub Project out of sync](#e7-inline-troubleshooting-claude-tasks-and-github-project-out-of-sync)

---

## E.1 Example 1: Find and Query a Project

```bash
# List all projects
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      projectsV2(first: 10) {
        nodes { id title number }
      }
    }
  }
'

# Query project items
gh api graphql -f query='
  query {
    node(id: "PVT_kwDO...") {
      ... on ProjectV2 {
        items(first: 20) {
          nodes {
            id
            content {
              ... on Issue { title number state }
            }
          }
        }
      }
    }
  }
'
```

## E.2 Example 2: Update Issue Status

```bash
# Move issue to "In Progress" status
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(
      input: {
        projectId: "PVT_kwDO..."
        itemId: "PVTI_..."
        fieldId: "PVTSSF_..."
        value: { singleSelectOptionId: "..." }
      }
    ) {
      projectV2Item { id }
    }
  }
'
```

## E.3 Inline Troubleshooting: Cannot find GitHub Project

**Cause**: Project ID incorrect or insufficient permissions.

**Solution**:
1. Verify project ID format: `PVT_kwDO...` for Projects V2
2. Check token has `project` scope
3. Use `gh project list --owner OWNER` to find correct ID
4. Ensure project is not archived

## E.4 Inline Troubleshooting: Issue not appearing on project board

**Cause**: Issue not added to project or field values not set.

**Solution**:
1. Verify issue is added to project: `gh project item-list PROJECT_ID`
2. Check required fields (Status, Priority) have values
3. Add issue manually: `gh project item-add PROJECT_ID --url ISSUE_URL`
4. Set field values: `gh project item-edit --id ITEM_ID --field-id FIELD_ID --value VALUE`

## E.5 Inline Troubleshooting: Column/status sync fails

**Cause**: Field IDs changed or column names don't match.

**Solution**:
1. Get current field IDs: `gh project field-list PROJECT_ID`
2. Update local configuration with correct field IDs
3. Ensure status values match exactly (case-sensitive)
4. Check for renamed or deleted columns

## E.6 Inline Troubleshooting: Rate limiting from GitHub API

**Cause**: Too many API calls in short period.

**Solution**:
1. Check rate limit status: `gh api rate_limit`
2. Implement caching for frequently accessed data
3. Batch operations where possible
4. Wait for rate limit reset (shown in API response)

## E.7 Inline Troubleshooting: Claude Tasks and GitHub Project out of sync

**Cause**: Manual changes on one side not reflected on other.

**Solution**:
1. Run sync script to reconcile differences
2. Claude Tasks are for personal/local tasks, GitHub for shared tasks
3. Prioritize GitHub as source of truth for team visibility
4. Use `/orchestration-status` to see unified view
