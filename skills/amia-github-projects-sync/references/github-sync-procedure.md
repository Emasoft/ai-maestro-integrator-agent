# GitHub Sync Procedure

## Contents

- 1.1 Authenticating and verifying GitHub CLI access
- 1.2 Configuring GitHub Projects V2 environment variables
- 1.3 Fetching project board data via GraphQL API
- 1.4 Synchronizing GitHub issues to local task state
  - 1.4.1 Querying project issues with GraphQL
  - 1.4.2 Extracting labels and custom fields from issues
  - 1.4.3 Parsing task checklists from issue bodies using TaskList API
  - 1.4.4 Updating orchestrator's internal task tracking
- 1.5 Synchronizing local changes back to GitHub
  - 1.5.1 Reading orchestrator's task modifications
  - 1.5.2 Converting task state to GitHub issue updates
  - 1.5.3 Applying label changes via gh CLI
  - 1.5.4 Updating issue bodies with Claude Tasks state
  - 1.5.5 Moving issues on Project V2 board using GraphQL mutations
- 1.6 Managing GitHub issue labels across priority, status, and type dimensions
- 1.7 Syncing Project V2 custom fields bidirectionally
- 1.8 Integrating Claude Tasks with GitHub issue checklists
- 1.9 Handling sync errors and conflicts
- 1.10 Generating sync reports and logs
- 1.11 Troubleshooting API rate limits, label conflicts, and task parse errors

---

## 1.1 Authenticating and verifying GitHub CLI access

Before performing any GitHub synchronization operations, you must verify authentication:

1. **Check current authentication status**:
   ```bash
   gh auth status
   ```

2. **If not authenticated, log in**:
   ```bash
   gh auth login
   ```

3. **Verification checkpoint**:
   - Confirm that `gh auth status` shows the logged in user
   - Verify that the authenticated account has access to the target repository

**Authentication is required for:**
- Querying GitHub Projects V2 via GraphQL
- Reading and updating issue labels
- Modifying issue bodies
- Moving issues on project boards

---

## 1.2 Configuring GitHub Projects V2 environment variables

Set up the required environment variables before synchronization:

```bash
# Set project number (extract from GitHub Projects URL)
export GH_PROJECT_NUMBER="1"
export GH_REPO_OWNER="Emasoft"
export GH_REPO_NAME="your-repo"
```

**Verify project configuration**:
```bash
gh project list --owner ${GH_REPO_OWNER}
```

**Verification checkpoint**:
- Confirm the project appears in the list with the correct number
- Verify the project name matches expectations

---

## 1.3 Fetching project board data via GraphQL API

Use GitHub's GraphQL API to fetch project board data with all necessary metadata:

1. **Execute GraphQL query** to fetch project board structure
2. **Parse the JSON response** to extract:
   - Issue list with IDs and metadata
   - Custom field definitions
   - Current column/status values
   - Label assignments

**Verification checkpoint**:
- Confirm JSON response contains expected fields (`issues`, `fields`, `items`)
- Validate that issue count matches expected project size

**GraphQL query location**: See `graphql-queries.md` for complete query library and examples.

---

## 1.4 Synchronizing GitHub issues to local task state

### 1.4.1 Querying project issues with GraphQL

Execute a GraphQL query to retrieve all issues assigned to the project:

```graphql
query {
  repository(owner: "$GH_REPO_OWNER", name: "$GH_REPO_NAME") {
    projectV2(number: $GH_PROJECT_NUMBER) {
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              number
              title
              body
              labels(first: 20) {
                nodes {
                  name
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### 1.4.2 Extracting labels and custom fields from issues

Parse the response to extract:

**Labels** (classification system):
- **Priority**: `priority:critical`, `priority:high`, `priority:normal`, `priority:low`
- **Status**: `status:backlog`, `status:todo`, `status:in-progress`, `status:ai-review`, `status:human-review`, `status:merge-release`, `status:blocked`, `status:done`
- **Type**: `type:feature`, `type:bug`, `type:refactor`, `type:docs`

**Custom fields**:
- Extract field values from Project V2 custom field schema
- Map custom fields to corresponding labels
- Validate field values before processing

### 1.4.3 Parsing task checklists from issue bodies using TaskList API

Use the TaskList API to extract and check task status from GitHub issue bodies:

1. **Call TaskList API** with issue body text
2. **Extract task metadata**:
   - Task description
   - Completion status: `completed`, `in_progress`, `pending`, `blocked`
   - Task hierarchy (parent/subtask relationships)
3. **Validate task syntax** before processing

### 1.4.4 Updating orchestrator's internal task tracking

After extracting all GitHub state:

1. **Update orchestrator's task list** with:
   - Issue numbers and titles
   - Current labels (priority, status, type)
   - Task checklist state
   - Custom field values
2. **Link subtasks to parent issues** based on hierarchy
3. **Log all updates** for audit trail

**Verification checkpoint**:
- Confirm issue count in project matches local state
- Verify all labels were correctly parsed
- Check that task completion percentages are accurate

---

## 1.5 Synchronizing local changes back to GitHub

### 1.5.1 Reading orchestrator's task modifications

Query the orchestrator's internal state to identify changes:

1. **Read modified task entries** from orchestrator's tracking system
2. **Identify changes requiring GitHub updates**:
   - Label additions or removals
   - Status transitions (backlog → todo → in-progress → ai-review → human-review → merge-release → done, or blocked)
   - Task checklist updates
   - Priority or type changes

**Verification checkpoint**:
- Log all pending changes before applying them
- Confirm each change has a corresponding GitHub issue number

### 1.5.2 Converting task state to GitHub issue updates

Map local task state to GitHub API operations:

| Local Change | GitHub Operation |
|--------------|------------------|
| Status change | Update `status:*` label + move on board |
| Priority change | Update `priority:*` label |
| Type change | Update `type:*` label |
| Task completion | Update issue body checklist |
| Custom field | Update Project V2 field via GraphQL |

### 1.5.3 Applying label changes via gh CLI

Use `gh issue edit` to apply label changes:

```bash
# Add labels
gh issue edit <issue_number> --add-label "status:in-progress,priority:high"

# Remove labels
gh issue edit <issue_number> --remove-label "status:todo"
```

**Batch operations**:
- Group label updates to minimize API calls
- Apply changes in priority order (status → priority → type)

### 1.5.4 Updating issue bodies with Claude Tasks state

When task checklist state changes locally:

1. **Read current issue body** via `gh issue view`
2. **Update task checklist syntax** with new completion status
3. **Write updated body** via `gh issue edit`

**Task syntax format**:
```markdown
- [ ] Pending task
- [x] Completed task
```

### 1.5.5 Moving issues on Project V2 board using GraphQL mutations

To move issues between columns:

```graphql
mutation {
  updateProjectV2ItemFieldValue(
    input: {
      projectId: "<project_id>",
      itemId: "<issue_item_id>",
      fieldId: "<status_field_id>",
      value: {
        singleSelectOptionId: "<column_option_id>"
      }
    }
  ) {
    projectV2Item {
      id
    }
  }
}
```

**Verification checkpoint**:
- Query updated issues to verify changes persisted
- Confirm issues moved to correct columns on project board

---

## 1.6 Managing GitHub issue labels across priority, status, and type dimensions

The label classification system organizes issues across three dimensions:

### Label Categories

| Category | Purpose | Values |
|----------|---------|--------|
| **Priority** | Urgency level | `priority:critical`, `priority:high`, `priority:normal`, `priority:low` |
| **Status** | Workflow state | `status:backlog`, `status:todo`, `status:in-progress`, `status:ai-review`, `status:human-review`, `status:merge-release`, `status:blocked`, `status:done` |
| **Type** | Work category | `type:feature`, `type:bug`, `type:refactor`, `type:docs` |

### Label Management Operations

1. **Automatic label application** based on issue content analysis
2. **Conflict resolution** for competing labels (e.g., multiple priority labels)
3. **Bulk label updates** during sync operations

### Label Conflict Resolution

When multiple labels from the same category are present:

1. **Priority rules** (highest priority wins):
   - `priority:critical` > `priority:high` > `priority:normal` > `priority:low`
2. **Document label precedence** in project wiki
3. **Log conflicts** for manual review

**See**: `label-taxonomy.md` for complete label classification system details.

---

## 1.7 Syncing Project V2 custom fields bidirectionally

GitHub Projects V2 supports custom fields that can be mapped to labels:

### Custom Field Types

- Single select (mapped to status/priority/type labels)
- Text (notes, URLs)
- Number (story points, effort)
- Date (deadlines, milestones)

### Bidirectional Sync Process

**GitHub → Local**:
1. Query custom field values via GraphQL
2. Map field values to labels
3. Update local task tracking

**Local → GitHub**:
1. Read local label changes
2. Convert to custom field updates
3. Execute GraphQL mutations to update fields

### Field Validation

Before pushing updates:
1. Validate field value against schema
2. Check required fields are populated
3. Verify data types match field definitions

---

## 1.8 Integrating Claude Tasks with GitHub issue checklists

Use Claude Code's TaskList API to synchronize task checklists:

### Task Status Values

- `completed`: Task finished
- `in_progress`: Currently being worked on
- `pending`: Not yet started
- `blocked`: Waiting on dependency

### Integration Workflow

1. **Use TaskList API to check task status** from issue body
2. **Extract checklist items** with completion state
3. **Update orchestrator's task tracking** with TaskCreate and TaskUpdate
4. **Link subtasks to parent issues** based on hierarchy
5. **Propagate task completion** back to GitHub issue bodies

### Task Parsing

When reading issue bodies:
1. Validate task syntax with TaskList API before processing
2. Log unparseable issues for manual review
3. Provide clear error messages in sync report

---

## 1.9 Handling sync errors and conflicts

Implement robust error handling to maintain data integrity:

### Retry Logic

- **Failed API calls**: Retry with exponential backoff
  - Initial delay: 2 seconds
  - Max retries: 3
  - Backoff multiplier: 2x

### Conflict Logging

When sync conflicts occur:
1. **Log conflict details** to sync report
2. **Preserve conflicting data** for manual review
3. **Do not overwrite** GitHub data automatically

### Data Validation

Before applying updates:
1. Validate data format and structure
2. Check required fields are present
3. Verify API response success status

### Error Preservation

On errors:
1. **Preserve data integrity** - do not partially commit changes
2. **Roll back local state** if GitHub update fails
3. **Generate detailed error report** with recovery steps

---

## 1.10 Generating sync reports and logs

After every sync operation, generate a comprehensive report:

### Sync Report Contents

1. **Sync statistics**:
   - Total issues processed
   - Issues synced GitHub → Local
   - Issues synced Local → GitHub
   - Conflicts encountered
2. **Error summary**:
   - Failed operations
   - API errors
   - Validation failures
3. **Timestamp and session info**

### Log File Format

Write sync logs to: `docs_dev/github-sync-YYYYMMDD-HHMMSS.log`

**Verification checkpoint**:
- Confirm log file exists and contains timestamp
- Verify all operations are logged with status

### Output Format to Orchestrator

Return minimal status (1-3 lines max):

**Success**:
```
[DONE] github-sync - synced 12 issues (5→GitHub, 7→Local), 0 conflicts
Details: docs_dev/github-sync-20250131-143022.log
```

**Failure**:
```
[FAILED] github-sync - sync error: <brief_error_reason>
```

**Conflicts**:
```
[DONE] github-sync - synced with N conflicts, see docs_dev/github-sync-YYYYMMDD-HHMMSS.log
```

---

## 1.11 Troubleshooting API rate limits, label conflicts, and task parse errors

### API Rate Limiting

**Problem**: GitHub API returns 403 with rate limit exceeded message.

**Solutions**:
1. **Add delays** between batch operations (minimum 1 second)
2. **Use GraphQL batching** to reduce request count
3. **Check remaining quota**:
   ```bash
   gh api rate-limit
   ```
4. **Implement request throttling** with exponential backoff

**Rate limits**:
- REST API: 5000 requests/hour (authenticated)
- GraphQL API: 5000 points/hour (query cost varies)

### Label Conflicts

**Problem**: Multiple labels from the same category applied to an issue.

**Solutions**:
1. **Implement priority rules** for competing labels:
   - Status: `done` > `merge-release` > `human-review` > `ai-review` > `in-progress` > `todo` > `backlog` (and `blocked` is orthogonal)
   - Priority: `critical` > `high` > `normal` > `low`
2. **Document label precedence** in project wiki
3. **Create label consolidation script** to clean up conflicts
4. **Log conflicts** in sync report for manual review

**Prevention**:
- Validate labels before applying
- Remove conflicting labels before adding new ones

### Task Parse Errors

**Problem**: Issue body contains malformed task checklist syntax.

**Solutions**:
1. **Validate task syntax** with TaskList API before processing
2. **Log unparseable issues** to sync report with issue numbers
3. **Provide clear error messages** indicating syntax problems
4. **Skip malformed tasks** and continue with remaining tasks

**Common syntax errors**:
- Missing `[ ]` or `[x]` markers
- Incorrect indentation for nested tasks
- Special characters breaking Markdown parsing

**Validation process**:
1. Test parse issue body with TaskList API
2. If parse fails, log error and skip task extraction
3. Continue sync operation with remaining valid tasks
4. Report parse failures in sync log
