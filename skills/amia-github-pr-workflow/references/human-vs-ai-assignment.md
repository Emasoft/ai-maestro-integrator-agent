# Human vs AI PR Assignment

## Table of Contents

- 5.1 Identifying PR author type
  - 5.1.1 Human contributors
  - 5.1.2 AI agent PRs
  - 5.1.3 Bot categories
- 5.2 Communication style differences
- 5.3 Escalation rules for human PRs
- 5.4 Direct action rules for AI PRs

---

## 5.1 Identifying PR author type

**Why this matters**: The orchestrator must handle PRs differently based on who created them. Human contributors expect different communication than AI agents, and some actions are appropriate for AI PRs but not human PRs.

### 5.1.1 Human contributors

**Definition**: A human contributor is any person who manually created the PR.

**Identification signals**:

| Signal | Indicates Human | Example |
|--------|-----------------|---------|
| Author username | No bot suffix | `johndoe` not `renovate[bot]` |
| Author type | User, not Bot | GitHub API `type: "User"` |
| Commit messages | Natural language, varied | "Fixed the login bug" |
| PR description | Explanatory, conversational | "I noticed that..." |
| Author association | CONTRIBUTOR, MEMBER, OWNER | Not `NONE` with bot characteristics |

**Verification command**:
```bash
gh api repos/{owner}/{repo}/pulls/{pr_number} --jq '.user.type, .user.login'
```

**Human contributor categories**:
1. **Repository owner**: Full authority, can merge
2. **Maintainer**: Trusted contributor with merge rights
3. **Collaborator**: Has write access
4. **Contributor**: Has submitted previous PRs
5. **First-time contributor**: New to the repository

### 5.1.2 AI agent PRs

**Definition**: A PR created by an AI agent or automated tool under human supervision.

**Identification signals**:

| Signal | Indicates AI/Automation | Example |
|--------|------------------------|---------|
| Author username | Contains "bot", "ai", "agent" | `dependabot[bot]`, `claude-agent` |
| Author type | Bot | GitHub API `type: "Bot"` |
| Commit messages | Templated, consistent | "chore(deps): bump lodash" |
| PR description | Structured, templated | Contains automated sections |
| Labels | Automation labels | `dependencies`, `automated` |

**Common AI/automation authors**:
- `dependabot[bot]`
- `renovate[bot]`
- `github-actions[bot]`
- Custom CI/CD bots
- AI coding assistants

### 5.1.3 Bot categories

Not all bots are equal. Different bot types require different handling.

**Category 1: Agent-controlled bots**

**Definition**: Bots where another AI orchestrator controls the PR lifecycle.

**Examples**: Claude agent creating a PR, custom AI development agent

**Characteristics**:
- Can understand complex instructions
- Can make autonomous code changes
- Can respond to review comments programmatically

**Handling**: The orchestrator can interact directly via comments or messages.

**Category 2: Mention-triggered bots**

**Definition**: Bots that respond to specific commands or mentions.

**Examples**: `/rebase`, `@bot please update`, `@claude-reviewer review this`

**Characteristics**:
- React to specific trigger phrases
- Perform predefined actions
- Limited autonomous capability

**Handling**: Use appropriate trigger commands to request actions.

**Category 3: Review bots**

**Definition**: Bots that provide automated code review feedback.

**Examples**: CodeClimate, SonarQube, linters as GitHub Apps

**Characteristics**:
- Comment on code quality issues
- May block merge based on rules
- Cannot make changes, only report

**Handling**: Address their feedback through code changes, not communication.

**Category 4: Update bots**

**Definition**: Bots that automatically update dependencies or configurations.

**Examples**: Dependabot, Renovate

**Characteristics**:
- Create PRs automatically
- Update based on schedules or triggers
- Limited response to feedback

**Handling**: Review changes, approve or request changes via GitHub UI.

---

## 5.2 Communication style differences

### Human PR communication

**Tone**: Professional, courteous, explanatory

**Structure**:
- Acknowledge their work
- Explain reasoning for requests
- Ask questions rather than demand
- Thank them for contributions

**Example review comment for human PR**:
```
Thanks for this contribution! The implementation looks good overall.

I have a few suggestions:

1. Line 45: Consider using `const` here since `result` isn't reassigned.
   This makes the intent clearer.

2. Line 78: This error message might be confusing to users. What do you think
   about including the expected format?

Happy to discuss any of these points. Let me know if you have questions!
```

### AI/Bot PR communication

**Tone**: Direct, technical, concise

**Structure**:
- State required changes clearly
- No need for social pleasantries
- Reference specific lines/files
- Use structured formats

**Example review comment for AI PR**:
```
Required changes:
- Line 45: Use `const` instead of `let` (variable not reassigned)
- Line 78: Update error message to include expected format

After changes, re-request review.
```

---

## 5.3 Escalation rules for human PRs

**Core principle**: Human PRs require human-to-human communication for important decisions. The orchestrator facilitates but does not replace human judgment.

### Always escalate to user

| Situation | Escalation Message |
|-----------|-------------------|
| Human PR needs review | "Human contributor @X submitted PR #Y. Please review or advise on delegation." |
| Significant code changes needed | "PR #X from human contributor needs changes. Should I delegate review feedback or would you like to respond?" |
| Human requests clarification | "Human contributor @X asked about [topic] on PR #Y. Please respond." |
| Merge decision | "Human PR #X is ready. Please confirm merge or provide feedback." |
| Conflict between reviewer and author | "Disagreement on PR #X. Human judgment needed." |

### Never act autonomously on human PRs

The orchestrator MUST NOT:
- Approve human PRs
- Request changes on human PRs
- Close human PRs
- Merge human PRs
- Post review comments as if from the user

### Delegation for human PRs

When user approves delegation:
1. Subagent performs technical work (analysis, testing)
2. Subagent prepares feedback draft
3. Orchestrator presents draft to user
4. User approves/modifies before posting
5. Orchestrator posts on behalf of user (or user posts directly)

---

## 5.4 Direct action rules for AI PRs

**Core principle**: For AI/bot PRs, the orchestrator can act more autonomously since the PR author is also automated.

### Actions allowed without user approval

| Action | Conditions |
|--------|------------|
| Run verification scripts | Always allowed |
| Delegate review | Always allowed |
| Post technical comments | If minor feedback |
| Trigger bot commands | If standard commands (@dependabot rebase) |

### Actions requiring user approval

| Action | Why Approval Needed |
|--------|---------------------|
| Approve PR | Commits code to repository |
| Merge PR | Irreversible action |
| Close PR | May lose work |
| Request major changes | May involve significant work |

### Direct interaction with bots

**For agent-controlled bots**:
- Can send AI Maestro messages directly
- Can post structured commands in comments
- Expect programmatic response

**For mention-triggered bots**:
- Use documented trigger syntax
- Example: `@dependabot rebase`
- Example: `@renovate refresh`

**For review bots**:
- Cannot interact directly
- Address feedback through code changes
- May need to update bot configuration for persistent issues

### Automation-to-automation workflow

When both PR author and reviewer are automated:

```
Bot creates PR
    │
    ▼
Orchestrator detects PR
    │
    ▼
Orchestrator delegates review to subagent
    │
    ▼
Subagent analyzes code, posts feedback
    │
    ▼
Bot updates PR (if capable)
    │
    ▼
Orchestrator runs verification
    │
    ▼
If all pass → Report to user for merge decision
```

---

## Author Type Detection Script

Use this logic to determine author type:

```python
def get_author_type(pr_data):
    """
    Determine if PR author is human or bot.

    Returns: "human", "agent-bot", "mention-bot", "review-bot", "update-bot"
    """
    user = pr_data.get("user", {})
    login = user.get("login", "").lower()
    user_type = user.get("type", "")

    # Clear bot indicators
    if user_type == "Bot":
        if "dependabot" in login or "renovate" in login:
            return "update-bot"
        if "actions" in login:
            return "mention-bot"
        if "sonar" in login or "codeclimate" in login:
            return "review-bot"
        return "agent-bot"  # Default bot type

    # Check for bot-like usernames even if type is User
    bot_patterns = ["[bot]", "-bot", "_bot", "-ai", "_ai", "agent"]
    if any(pattern in login for pattern in bot_patterns):
        return "agent-bot"

    return "human"
```

---

## Decision Matrix

| Author Type | Review Delegation | Direct Comments | Autonomous Approval | Merge Decision |
|-------------|------------------|-----------------|--------------------|--------------:|
| Human | Requires user approval | Never | Never | User decides |
| Agent-bot | Allowed | Allowed | User approval | User decides |
| Mention-bot | Allowed | Via triggers | User approval | User decides |
| Review-bot | N/A (they review) | N/A | N/A | N/A |
| Update-bot | Allowed | Via triggers | User approval | User decides |
