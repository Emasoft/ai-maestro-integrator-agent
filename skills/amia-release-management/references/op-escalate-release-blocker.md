# Operation: Escalate Release Blocker

## Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Prerequisites](#prerequisites)
- [Procedure](#procedure)
  - [Step 1: Document the blocker](#step-1-document-the-blocker)
  - [Step 2: Assess impact](#step-2-assess-impact)
  - [Step 3: Prepare escalation message](#step-3-prepare-escalation-message)
  - [Description](#description)
  - [Impact](#impact)
  - [What Was Attempted](#what-was-attempted)
  - [Decision Required](#decision-required)
  - [Recommended Action](#recommended-action)
  - [Step 4: Create GitHub issue (if not exists)](#step-4-create-github-issue-if-not-exists)
  - [Step 5: Notify via AI Maestro](#step-5-notify-via-ai-maestro)
  - [Step 6: Update release state](#step-6-update-release-state)
- [Blocker: v$VERSION ($TIMESTAMP)](#blocker-vversion-timestamp)
  - [Step 7: Wait for decision](#step-7-wait-for-decision)
- [Input](#input)
- [Output](#output)
- [Example Output](#example-output)
- [Blocker Types](#blocker-types)
- [Severity Levels](#severity-levels)
- [Error Handling](#error-handling)
  - [Cannot create issue](#cannot-create-issue)
  - [AI Maestro unavailable](#ai-maestro-unavailable)
  - [Orchestrator unresponsive](#orchestrator-unresponsive)
- [Complete Escalation Script](#complete-escalation-script)
  - [Description](#description)
  - [Decision Required](#decision-required)
- [Verification](#verification)

## Purpose

Properly escalate a release-blocking issue when the release coordinator cannot resolve it independently, ensuring appropriate visibility and decision-making.

## When to Use

- When pre-release verification finds critical blockers
- When CI/CD pipeline fails and cannot be fixed
- When critical bug is discovered that requires decision
- When dependency vulnerability requires risk assessment
- When external factors block release

## Prerequisites

1. Clear understanding of the blocker
2. Documentation of what was attempted
3. AI Maestro access for notification
4. GitHub access for issue creation

## Procedure

### Step 1: Document the blocker

```bash
VERSION="1.2.4"
BLOCKER_TYPE="critical_bug"  # critical_bug, ci_failure, security_vuln, dependency, external
BLOCKER_DESC="API endpoint returns 500 on edge case input"
ATTEMPTED="Investigated logs, identified null pointer in auth module"
SEVERITY="critical"  # critical, high, medium

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
```

### Step 2: Assess impact

```bash
# Determine release impact
case "$BLOCKER_TYPE" in
  critical_bug)
    IMPACT="Release cannot proceed - would ship known critical bug"
    ;;
  ci_failure)
    IMPACT="Cannot verify release quality - pipeline not passing"
    ;;
  security_vuln)
    IMPACT="Security risk assessment required before release"
    ;;
  dependency)
    IMPACT="Dependency issue may affect stability"
    ;;
  external)
    IMPACT="External factor blocking release"
    ;;
esac
```

### Step 3: Prepare escalation message

```bash
ESCALATION_MSG="## Release Blocker Alert

**Version**: v$VERSION
**Type**: $BLOCKER_TYPE
**Severity**: $SEVERITY
**Time**: $TIMESTAMP

### Description
$BLOCKER_DESC

### Impact
$IMPACT

### What Was Attempted
$ATTEMPTED

### Decision Required
Please advise on one of the following:
1. **Delay release** - Fix the blocker first
2. **Release anyway** - Accept the risk (document rationale)
3. **Partial release** - Release without affected feature
4. **Other** - Specify alternative approach

### Recommended Action
$(case "$SEVERITY" in
  critical) echo "DELAY - Critical issues should never be released" ;;
  high) echo "DELAY - High severity issues typically require fixes" ;;
  medium) echo "DECISION NEEDED - Assess risk vs. release urgency" ;;
esac)
"
```

### Step 4: Create GitHub issue (if not exists)

```bash
# Check if blocker issue already exists
EXISTING=$(gh issue list --state open --label "release-blocker" --json number,title | \
  jq -r ".[] | select(.title | contains(\"$VERSION\")) | .number")

if [ -z "$EXISTING" ]; then
  # Create new issue
  ISSUE_NUM=$(gh issue create \
    --title "[RELEASE BLOCKER] v$VERSION - $BLOCKER_TYPE" \
    --body "$ESCALATION_MSG" \
    --label "release-blocker,critical" \
    --json number --jq '.number')

  echo "Created issue #$ISSUE_NUM"
else
  # Update existing issue
  gh issue comment "$EXISTING" --body "**Update**: $TIMESTAMP

$BLOCKER_DESC

Attempted: $ATTEMPTED"

  ISSUE_NUM="$EXISTING"
  echo "Updated existing issue #$ISSUE_NUM"
fi
```

### Step 5: Notify via AI Maestro

Send a message using the `agent-messaging` skill with:

- **Recipient**: `orchestrator-amoa`
- **Subject**: `[RELEASE BLOCKED] v<VERSION>`
- **Priority**: `urgent`
- **Content**: `{"type": "release-blocked", "message": "Release v<VERSION> is blocked. Type: <BLOCKER_TYPE>. Severity: <SEVERITY>. Issue: #<ISSUE_NUM>. Decision required."}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Step 6: Update release state

```bash
# Update release history with blocked state
HANDOFF_DIR="$CLAUDE_PROJECT_DIR/thoughts/shared/handoffs/amia-integration"
RELEASE_HISTORY="$HANDOFF_DIR/release-history.md"

# Add blocker entry
echo "

## Blocker: v$VERSION ($TIMESTAMP)

- **Type**: $BLOCKER_TYPE
- **Severity**: $SEVERITY
- **Issue**: #$ISSUE_NUM
- **Status**: AWAITING_DECISION
" >> "$RELEASE_HISTORY"
```

### Step 7: Wait for decision

```bash
echo "=== ESCALATION COMPLETE ==="
echo "Release v$VERSION is BLOCKED"
echo "Blocker: $BLOCKER_TYPE"
echo "Issue: #$ISSUE_NUM"
echo ""
echo "Awaiting decision from orchestrator/user"
echo "Do NOT proceed with release until blocker is resolved"
```

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| version | string | yes | Version being released |
| blocker_type | string | yes | Type of blocker |
| description | string | yes | Description of the blocker |
| severity | string | yes | critical, high, medium |
| attempted | string | no | What resolution was attempted |

## Output

| Field | Type | Description |
|-------|------|-------------|
| escalated | boolean | Whether escalation was sent |
| issue_number | number | GitHub issue number |
| severity | string | Blocker severity |
| awaiting | string | What decision is needed |

## Example Output

```json
{
  "escalated": true,
  "issue_number": 456,
  "severity": "critical",
  "awaiting": "Decision on whether to delay release or fix blocker"
}
```

## Blocker Types

| Type | Description | Default Action |
|------|-------------|----------------|
| critical_bug | Critical bug found | Delay |
| ci_failure | CI/CD pipeline failing | Investigate |
| security_vuln | Security vulnerability | Risk assessment |
| dependency | Dependency issue | Evaluate alternatives |
| external | External factor | Wait/workaround |

## Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| critical | Production impact, data loss risk | Immediate |
| high | Significant functionality broken | < 4 hours |
| medium | Important but workaround exists | < 24 hours |

## Error Handling

### Cannot create issue

**Cause**: GitHub permissions or API error.

**Solution**: Send notification only, document locally.

### AI Maestro unavailable

**Cause**: Service not running.

**Solution**: Fall back to direct communication.

### Orchestrator unresponsive

**Cause**: No response to escalation.

**Solution**: Escalate to user directly.

## Complete Escalation Script

```bash
#!/bin/bash
# escalate_release_blocker.sh

VERSION="$1"
BLOCKER_TYPE="$2"
DESCRIPTION="$3"
SEVERITY="${4:-high}"

if [ -z "$VERSION" ] || [ -z "$BLOCKER_TYPE" ] || [ -z "$DESCRIPTION" ]; then
  echo "Usage: escalate_release_blocker.sh <version> <type> <description> [severity]"
  exit 1
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "=== ESCALATING RELEASE BLOCKER ==="
echo "Version: v$VERSION"
echo "Type: $BLOCKER_TYPE"
echo "Severity: $SEVERITY"

# Create issue
BODY="## Release Blocker

**Version**: v$VERSION
**Type**: $BLOCKER_TYPE
**Severity**: $SEVERITY

### Description
$DESCRIPTION

### Decision Required
- Delay release
- Release anyway (with documented risk)
- Other approach"

ISSUE=$(gh issue create \
  --title "[RELEASE BLOCKER] v$VERSION - $BLOCKER_TYPE" \
  --body "$BODY" \
  --label "release-blocker,$SEVERITY" \
  --json number --jq '.number')

echo "Created issue #$ISSUE"

# Notify using the agent-messaging skill:
#   Recipient: orchestrator-amoa
#   Subject: [BLOCKED] v$VERSION
#   Priority: urgent
#   Content: {"type": "release-blocked", "message": "v$VERSION blocked. $BLOCKER_TYPE: $DESCRIPTION. Issue #$ISSUE"}
#   Verify: Confirm delivery via the agent-messaging skill send confirmation.

echo "Notification sent"
echo ""
echo "=== AWAITING DECISION ==="
echo "Do NOT proceed with release"
```

## Verification

After escalation:

```bash
# Verify issue created
gh issue view "$ISSUE_NUM"

# Check notification sent: verify via the agent-messaging skill that the last sent message was delivered.

# Monitor for response
gh issue view "$ISSUE_NUM" --comments
```
