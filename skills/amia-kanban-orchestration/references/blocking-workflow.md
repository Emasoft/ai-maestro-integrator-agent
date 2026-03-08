# Blocking Workflow

## Table of Contents

- 6.1 [What constitutes a blocked task](#61-what-constitutes-a-blocked-task)
- 6.2 [How to mark an item as blocked](#62-marking-as-blocked)
- 6.3 [Required information when blocking](#63-required-information)
- 6.4 [Blocker escalation timeline](#64-escalation-timeline)
- 6.5 [Resolving blockers and resuming work](#65-resolving-blockers)
- 6.6 [Cross-issue blocking dependencies](#66-cross-issue-blocking)
- 6.7 [External blockers](#67-external-blockers)
- 6.8 [Blocker status reporting](#68-status-reporting)

---

## 6.1 What constitutes a blocked task

A task is BLOCKED when an agent cannot continue working on it and must wait for an external resolution before resuming. The agent has no way to resolve the issue on its own.

### Categories of blockers

| Category | Description | Examples |
|----------|-------------|---------|
| **Task Dependency** | Waiting for another task to complete before this one can proceed | Feature B depends on Feature A's API; test suite needs database schema from migration task |
| **Problem Resolution** | Waiting for a solution to a technical or design problem from the architect (AMAA) or the user | Architecture decision needed; design conflict to resolve; user requirement clarification |
| **Missing Resource** | Lacking a resource that must be provided or set up before work can continue | Library to install; server to set up; API key or password to configure on GitHub or a service; Docker container to build; certificate to provision; database to create |
| **Missing Approval** | Waiting for user or manager approval before proceeding | Deployment approval; budget approval; scope change approval; third-party service subscription |
| **External Dependency** | Waiting for an external party, service, or system outside the agent team | Third-party API not yet available; upstream service outage; external team deliverable |
| **Access or Credentials** | Lacking credentials, tokens, or permissions required to proceed | GitHub secret not configured; API token expired; SSH key not provisioned; environment variable not set |

### What is NOT a blocker

The following are NOT blockers — agents should handle them directly:

- A test failure (fix the code)
- A linting error (fix the formatting)
- A merge conflict (resolve it)
- A transient network error (retry)
- A performance issue (optimize)

If an agent encounters a problem it CAN solve, it is NOT blocked — it should solve it.

### Decision Tree

```
Can agent resolve this independently?
  │
  ├─ YES → NOT a blocker. Keep working.
  │
  └─ NO → Is this preventing ALL progress?
           │
           ├─ YES → BLOCKER. Move to Blocked.
           │
           └─ NO → Continue other work. Note the issue.
```

---

## 6.2 Marking as Blocked

### Step 1: Update Board Status

Move the card to Blocked column via GraphQL:

```bash
# CRITICAL: First, get the CURRENT status column before moving to Blocked
# This will be stored in the blocker comment as "Previous Status"
CURRENT_STATUS=$(gh api graphql -f query='
  query($projectId: ID!, $itemId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            id
            fieldValues(first: 10) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  field { ... on ProjectV2SingleSelectField { name } }
                }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq -r "
  .data.node.items.nodes[]
  | select(.id == \"$ITEM_ID\")
  | .fieldValues.nodes[]
  | select(.field.name == \"Status\")
  | .name
")

# Get status field and option IDs
STATUS_INFO=$(gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        field(name: "Status") {
          ... on ProjectV2SingleSelectField {
            id
            options { id name }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID")

FIELD_ID=$(echo "$STATUS_INFO" | jq -r '.data.node.field.id')
BLOCKED_ID=$(echo "$STATUS_INFO" | jq -r '.data.node.field.options[] | select(.name == "Blocked") | .id')

# Update status to Blocked
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $optionId }
    }) { projectV2Item { id } }
  }
' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$FIELD_ID" -f optionId="$BLOCKED_ID"

# IMPORTANT: Store $CURRENT_STATUS for use in the blocker comment (Step 3)
# This ensures we can return to the correct column when unblocking
```

### Step 2: Add Blocked Label

```bash
gh issue edit 42 --add-label "blocked"
```

### Step 3: Document the Blocker

```bash
gh issue comment 42 --body "$(cat <<'EOF'
## Blocked

**Previous Status:** In Progress
**Blocker:** Missing database credentials for staging environment
**Type:** Access
**Blocking Issue:** N/A
**What's Needed:** DBA to provide credentials in vault
**Impact:** Cannot test data layer implementation
**Discovered:** 2024-01-15 15:00 UTC

@orchestrator-master Please escalate to DBA team.
EOF
)"
```

### Step 4: Create a GitHub Issue for the Blocker

The blocker itself (the problem preventing the task from continuing) must be tracked as a separate GitHub issue. This makes the blocking problem visible to all team members and agents on the issue tracker.

```bash
# Create a new issue for the blocker, referencing the blocked task
BLOCKER_ISSUE=$(gh issue create \
  --title "BLOCKER: Missing database credentials for staging environment" \
  --label "type:blocker" \
  --body "$(cat <<'EOF'
## Blocker

This issue tracks a problem that is blocking task #42.

**Blocked Task**: #42 (Data layer implementation)
**Blocker Category**: Access / Credentials
**What's Needed**: DBA to provide credentials in vault
**Impact**: Cannot test data layer implementation
**Detected**: 2024-01-15 15:00 UTC

## Resolution

This issue should be closed when the blocking problem is resolved and task #42 can resume.
EOF
)" | grep -oP '\d+$')

# Link the blocker issue to the blocked task
gh issue comment 42 --body "Blocked by #$BLOCKER_ISSUE"
```

**Why create a separate issue for the blocker:**

- Makes the blocking problem visible to all agents and team members
- Allows tracking resolution progress independently
- Can be assigned to whoever can resolve it (user, DBA, architect, etc.)
- When the blocker issue is closed, it signals that the blocked task can resume
- Creates a clear audit trail of what was blocking and how it was resolved

### Step 5: Notify Orchestrator

Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-master`
- **Subject**: `Issue #42 Blocked`
- **Priority**: `high`
- **Content**: `{"type": "blocker", "message": "Issue #42 is blocked. Blocker issue #BLOCKER_ISSUE created. Need DBA action.", "data": {"issue_number": 42, "blocker_issue_number": "BLOCKER_ISSUE", "blocker_type": "access", "what_needed": "DBA to provide credentials"}}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

---

## 6.3 Required Information

Every blocker MUST have this information documented:

### Blocker Template

```markdown
## Blocked

**Previous Status:** [Status before blocking]
**Blocker:** [One-line description]
**Blocker Issue:** #[blocker issue number]
**Type:** [Technical | Access | Clarification | External | Resource | Dependency]
**Blocking Dependency:** #[task number] or N/A
**What's Needed:** [Specific action to unblock]
**Impact:** [What work is prevented]
**Discovered:** YYYY-MM-DD HH:MM UTC
**Expected Resolution:** [If known]

[Additional context if needed]
```

### Field Descriptions

| Field | Description | Example |
|-------|-------------|---------|
| Previous Status | Where to return after unblocking | "In Progress" |
| Blocker | Clear, concise description | "Missing API key for payment service" |
| Blocker Issue | GitHub issue tracking the blocker problem | "#99" |
| Type | Category for routing | "Access" |
| Blocking Dependency | Task issue that must complete first (if dependency type) | "#35" |
| What's Needed | Actionable next step | "DevOps to add key to secrets manager" |
| Impact | What can't proceed | "Cannot implement payment flow" |
| Discovered | Timestamp for tracking | "2024-01-15 15:00 UTC" |
| Expected Resolution | ETA if known | "Tomorrow after DevOps standup" |

---

## 6.4 Escalation rules — IMMEDIATE notification required

**CRITICAL RULE**: When a task becomes blocked, the user MUST be informed immediately through the escalation chain. There is NO waiting period before notifying the user.

### Escalation flow (happens within minutes, not hours)

```
1. Agent detects blocker
   → IMMEDIATELY moves task to Blocked column
   → IMMEDIATELY adds status:blocked label
   → IMMEDIATELY adds blocker comment to GitHub issue
   → IMMEDIATELY sends AI Maestro message to AMOA (orchestrator)

2. AMOA receives blocker notification
   → Verifies the blocker is real (not something the agent can solve)
   → IMMEDIATELY sends blocker escalation to AMAMA (manager)
   → Updates Kanban board if agent hasn't already

3. AMAMA receives blocker escalation
   → IMMEDIATELY communicates the blocker to the user
   → Includes: what's blocked, why, what's needed, impact, options
```

### Parallel self-resolution attempts

While the escalation chain runs, agents MAY attempt to resolve the blocker themselves:

- Check if a dependency task is close to completion
- Search for alternative resources or approaches
- Consult with other agents via AI Maestro

If the agent resolves the blocker before the user responds:

1. Remove status:blocked label
2. Move task back to its ORIGINAL column (the column it was in before being blocked)
3. Notify AMOA that the blocker was self-resolved
4. AMOA notifies AMAMA to update the user

### User response timeout (after user has been notified)

| Duration | Action |
|----------|--------|
| 0-4 hours | Wait for user response, agents work on other unblocked tasks |
| 4-8 hours | AMAMA sends reminder to user |
| 8-24 hours | AMAMA sends urgent reminder with impact assessment |
| >24 hours | AMAMA marks the blocker as "awaiting user" in next status report |

---

## 6.5 Resolving Blockers

### Resolution Process

1. **Verify blocker is resolved** - Don't assume
2. **Document resolution** - Comment on the blocked task issue
3. **Close blocker issue** - `gh issue close $BLOCKER_ISSUE --comment "Resolved: [resolution details]"`
4. **Remove blocked label** - `gh issue edit 42 --remove-label "blocked"`
5. **Update status** - Move back to **ORIGINAL** status (the column it was in before being blocked)
6. **Notify agent** - Via AI Maestro

### Returning a task to its original column after unblocking

When a blocker is resolved:

1. Remove the `status:blocked` label
2. Move the task back to the column it was in BEFORE being blocked:
   - If it was in "In Progress" → return to "In Progress"
   - If it was in "AI Review" → return to "AI Review"
   - If it was in "Human Review" → return to "Human Review"
   - If it was in "Merge/Release" → return to "Merge/Release"
   - If it was in "Todo" → return to "Todo"
   - If it was in "Done" but was re-blocked → return to the appropriate active column
3. Add a comment to the GitHub issue documenting:
   - When the blocker was detected
   - What the blocker was
   - How it was resolved
   - Who resolved it (user decision, agent self-resolution, resource provision)
4. Notify the assigned agent via AI Maestro that the blocker is resolved
5. Update the `previous_column` tracking (used by the Kanban manager to know where to return the task)

**CRITICAL**: The "Previous Status" field in the blocker comment is the source of truth for where to return the task. Always record this when moving to Blocked, and always read it when unblocking.

### Resolution Comment Template

```markdown
## Unblocked

**Resolution:** DBA added credentials to vault
**Resolved By:** @dba-admin
**Resolved:** 2024-01-16 09:00 UTC
**Duration Blocked:** 18 hours

Agent @agent-1 can now continue work.
Returning to **[previous status from blocker comment]**.
```

### CLI Commands

```bash
# Add resolution comment
gh issue comment 42 --body "$(cat <<'EOF'
## Unblocked
**Resolution:** Database credentials added to vault
**Resolved By:** DBA team
**Resolved:** 2024-01-16 09:00 UTC
**Duration Blocked:** 18 hours
Returning to **In Progress** (previous status).
EOF
)"

# Remove blocked label
gh issue edit 42 --remove-label "blocked"

# Update status back to previous column (get from blocker comment)
# IMPORTANT: Read the "Previous Status" from the blocker comment to determine target column
# [GraphQL mutation to set status - use PREVIOUS_STATUS from blocker comment, not hardcoded "In Progress"]

# Notify agent using the agent-messaging skill:
#   Recipient: agent-1
#   Subject: Issue #42 Unblocked
#   Priority: high
#   Content: {"type": "unblocked", "message": "Issue #42 is unblocked. Credentials are now in vault. Please resume work.", "data": {"issue_number": 42, "returned_to_column": "In Progress"}}
#   Verify: Confirm delivery via the agent-messaging skill send confirmation.
```

---

## 6.6 Cross-Issue Blocking

When one issue blocks another, use GitHub's dependency tracking.

### Marking Dependency

In the blocked issue, reference the blocking issue:

```markdown
## Blocked

**Blocker:** Depends on #35 (API client library)
**Type:** Dependency
**Blocking Issue:** #35
**What's Needed:** Issue #35 must be completed first
**Impact:** Cannot implement integration without client library
```

### Tracking Dependencies

```bash
# Find issues blocked by #35
gh issue list --search "Blocked Blocking Issue: #35" --json number,title
```

### Automatic Unblocking

When blocking issue is resolved, manually unblock dependent issues or set up automation to detect.

### Dependency Chain Example

```
#35 API Client Library
  └─ blocks #36 Payment Integration
       └─ blocks #37 Checkout Flow
            └─ blocks #38 Order Confirmation
```

---

## 6.7 External Blockers

External blockers are outside the project's control.

### Examples

- Third-party API outage
- Vendor not responding
- Regulatory approval pending
- External team dependency

### Handling External Blockers

```markdown
## Blocked (External)

**Blocker:** Payment gateway API is down
**Type:** External
**External Party:** Stripe
**Status Page:** https://status.stripe.com
**What's Needed:** Stripe to restore service
**Impact:** Cannot test or develop payment flow
**Workaround:** None available

**Monitoring:** Watching status page for updates.
```

### Escalation for External

External blockers may need human decision:

```markdown
**Blocker Escalation (External - 48h)**

@human-owner External blocker persists.

Blocker: Stripe API down
Duration: 48 hours
External status: "Investigating"

Options:
1. Continue waiting (risk: timeline slip)
2. Implement mock for development (risk: integration issues later)
3. Consider alternative provider (risk: significant rework)

Please advise.
```

---

## 6.8 Status Reporting

### Query Blocked Items

```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes {
            fieldValues(first: 10) {
              nodes {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  field { ... on ProjectV2SingleSelectField { name } }
                }
              }
            }
            content {
              ... on Issue {
                number
                title
                labels(first: 10) { nodes { name } }
              }
            }
          }
        }
      }
    }
  }
' -f projectId="$PROJECT_ID" | jq '
  .data.node.items.nodes[]
  | select(.fieldValues.nodes[] | select(.field.name == "Status" and .name == "Blocked"))
  | { issue: .content.number, title: .content.title }
'
```

### Blocker Summary Report

```markdown
## Blocker Report - 2024-01-15

| Issue | Title | Blocker Type | Duration | Status |
|-------|-------|--------------|----------|--------|
| #42 | Auth module | Access | 18h | Awaiting DBA |
| #45 | API client | Dependency | 4h | Waiting on #35 |
| #48 | Payments | External | 48h | Stripe outage |

**Total Blocked:** 3
**Escalated:** 1 (#48)
**Action Needed:** Human decision on #48
```

---

## 6.9 Blocker Lifecycle Checklist

Copy this checklist and track your progress:

**When marking a task as blocked:**

- [ ] Confirm the agent cannot resolve the issue independently (not a test failure, merge conflict, etc.)
- [ ] Record the task's current Kanban column (`$CURRENT_STATUS`) before moving to Blocked
- [ ] Move the card to the Blocked column via GraphQL (section 6.2 Step 1)
- [ ] Add `blocked` label to the task issue (section 6.2 Step 2)
- [ ] Add blocker comment to the task issue with Previous Status field (section 6.2 Step 3)
- [ ] Create a separate GitHub issue for the blocker with `type:blocker` label (section 6.2 Step 4)
- [ ] Link the blocker issue to the blocked task issue
- [ ] Notify the orchestrator via AI Maestro with `blocker_issue_number` (section 6.2 Step 5)

**When resolving a blocker and unblocking the task:**

- [ ] Verify the blocker is actually resolved (do not assume)
- [ ] Add resolution comment on the blocked task issue (section 6.5 Resolution Comment Template)
- [ ] Close the blocker issue: `gh issue close $BLOCKER_ISSUE --comment "Resolved: [details]"`
- [ ] Remove the `blocked` label from the task issue
- [ ] Read the "Previous Status" from the blocker comment to determine the return column
- [ ] Move the task back to its PREVIOUS column (not always "In Progress")
- [ ] Notify the assigned agent via AI Maestro that work can resume
- [ ] Notify the orchestrator that the blocker is resolved
