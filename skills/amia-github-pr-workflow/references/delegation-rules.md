# Delegation Rules

## Table of Contents

- 2.1 When to spawn subagents
  - 2.1.1 Task complexity thresholds
  - 2.1.2 Time-based triggers
  - 2.1.3 Resource availability checks
- 2.2 How to structure subagent prompts
  - 2.2.1 Required prompt elements
  - 2.2.2 Context passing rules
  - 2.2.3 Output format requirements
- 2.3 Maximum concurrent agents
- 2.4 Task isolation requirements
- 2.5 Result aggregation patterns

---

## 2.1 When to spawn subagents

The orchestrator should delegate work rather than perform it directly. This section defines when delegation is required.

### 2.1.1 Task complexity thresholds

**Rule**: Delegate any task that requires focused attention or takes more than 30 seconds.

**Complexity indicators that trigger delegation**:

| Indicator | Example | Delegate To |
|-----------|---------|-------------|
| Code analysis needed | "Review this PR" | Review subagent |
| Code changes needed | "Fix the bug in line 45" | Implementation subagent |
| Multiple files involved | "Update imports across modules" | Implementation subagent |
| Domain expertise needed | "Check security implications" | Specialized review subagent |
| Testing required | "Verify the fix works" | Test subagent |
| Long-running wait | "Monitor CI until complete" | CI monitor subagent |

**Complexity NOT requiring delegation**:
- Running a script that completes in seconds
- Reading a status from GitHub API
- Updating a checklist
- Sending a message to user

### 2.1.2 Time-based triggers

**Rule**: Any operation expected to take more than 30 seconds must be delegated.

**Time estimates for common tasks**:
| Task | Typical Duration | Delegate? |
|------|-----------------|-----------|
| API status check | 1-5 seconds | No |
| Run verification script | 5-15 seconds | No |
| Code review | 2-10 minutes | YES |
| Implementation work | 5-60 minutes | YES |
| CI pipeline | 5-30 minutes | YES |
| Complex analysis | 5-20 minutes | YES |

**When uncertain**: Delegate. The cost of unnecessary delegation is low. The cost of blocking the orchestrator is high.

### 2.1.3 Resource availability checks

**Before spawning a subagent, check**:

1. **Concurrent agent limit**: Are fewer than 20 agents currently running?
2. **Task independence**: Does this task conflict with other running tasks?
3. **Resource contention**: Will this agent need exclusive access to resources?

**If resource conflict exists**:
- Queue the task for later
- Wait for conflicting agent to complete
- Consider worktree isolation (see worktree-coordination.md)

---

## 2.2 How to structure subagent prompts

Poorly structured prompts lead to failed or incorrect work. Follow these rules.

### 2.2.1 Required prompt elements

Every subagent prompt MUST contain:

```
1. ROLE STATEMENT
   "You are a [specific role] subagent."

2. SINGLE TASK
   "Your single task is: [clear, specific task]"

3. CONTEXT BLOCK
   "Context:
   - Repository: [owner/repo]
   - PR number: [number]
   - Branch: [branch name]
   - Working directory: [path]"

4. SUCCESS CRITERIA
   "Success criteria:
   - [Criterion 1]
   - [Criterion 2]"

5. OUTPUT FORMAT
   "Return a minimal report: 1-2 lines max.
   Format: [DONE/FAILED] task_name - brief_result
   If details needed, write to docs_dev/[filename].md"

6. CONSTRAINTS
   "Constraints:
   - [Any limitations or restrictions]
   - [What NOT to do]"
```

**Example complete prompt**:
```
You are a code review subagent. Your single task is:
Review PR #123 for code quality, logic errors, and adherence to project standards.

Context:
- Repository: owner/repo
- PR number: 123
- Branch: feature/new-widget
- Working directory: /path/to/repo

Success criteria:
- All changed files reviewed
- Issues documented with file:line references
- Severity assigned to each issue (critical/major/minor)

Return a minimal report: 1-2 lines max.
Format: [DONE/FAILED] review-pr-123 - brief_result
If details needed, write to docs_dev/pr-123-review.md

Constraints:
- Do not make code changes
- Do not approve or request changes on GitHub
- Report findings only
```

### 2.2.2 Context passing rules

**What context to pass**:
- Repository identification (owner/repo)
- PR or issue number
- Branch name
- File paths relevant to the task
- Summary of related decisions already made

**What context NOT to pass**:
- Full conversation history (too large)
- Unrelated PR information
- Internal orchestrator state
- User's personal information

**Context size limit**: Keep context under 2000 tokens. More than that overwhelms the subagent.

### 2.2.3 Output format requirements

**All subagents MUST return**:
```
[DONE|FAILED] task_name - brief_result (max 2 lines)
```

**Why this format**:
- Minimal token consumption in orchestrator context
- Easy to parse programmatically
- Clear success/failure signal
- Details available in file if needed

**If subagent needs to return details**:
1. Write details to `docs_dev/[descriptive-name].md`
2. Return: `[DONE] task - see docs_dev/[filename].md`

**Bad example**:
```
I have completed the code review. Here are my findings:

1. In file src/main.py at line 45...
2. The function calculate_total has...
[200 more lines]
```

**Good example**:
```
[DONE] review-pr-123 - 3 critical, 5 minor issues found. See docs_dev/pr-123-review.md
```

---

## 2.3 Maximum concurrent agents

**Hard limit**: 20 concurrent subagents maximum.

**Soft limits by task type**:
| Task Type | Recommended Max | Reason |
|-----------|-----------------|--------|
| Implementation | 5 | High resource use |
| Review | 10 | Medium resource use |
| Monitoring | 5 | Long-running |
| Verification | 10 | Quick tasks |

**Batch processing**:
If more than 20 tasks are needed:
1. Prioritize tasks
2. Run first batch (20)
3. Wait for batch to complete
4. Run next batch

**Never exceed 20**: Claude Code has resource limits. Exceeding them causes failures.

---

## 2.4 Task isolation requirements

**Rule**: Each subagent must work in isolation to prevent conflicts.

### File-level isolation

**Requirement**: No two subagents should modify the same file simultaneously.

**Enforcement**:
1. Before delegating, identify all files the task may modify
2. Check if any running subagent is working on those files
3. If conflict: queue the task or use worktree

### Branch-level isolation

**Requirement**: Subagents working on different PRs should use separate branches.

**Enforcement**:
1. Specify the branch in the prompt
2. Instruct subagent not to switch branches
3. Use worktrees for parallel PR work

### Git operation isolation

**Critical rule**: Only ONE subagent may perform git operations at a time.

**Git operations include**:
- commit
- push
- pull
- fetch
- checkout
- merge
- rebase

**Why**: Concurrent git operations cause authentication issues and potential corruption.

**Enforcement**:
1. Designate one subagent as "git-enabled" per PR
2. Other subagents prepare changes but do not commit
3. Git-enabled subagent commits all changes

---

## 2.5 Result aggregation patterns

When multiple subagents work on related tasks, their results must be aggregated.

### Pattern 1: Sequential aggregation

**Use when**: Tasks have dependencies.

```
Task A completes → Use result in Task B → Use result in Task C
```

**Implementation**:
1. Spawn Task A
2. Wait for completion
3. Parse result
4. Include result in Task B prompt
5. Repeat

### Pattern 2: Parallel aggregation

**Use when**: Tasks are independent.

```
Tasks A, B, C run in parallel → Collect all results → Synthesize
```

**Implementation**:
1. Spawn Tasks A, B, C simultaneously
2. Collect results as each completes
3. When all complete, synthesize findings

### Pattern 3: Fan-out / Fan-in

**Use when**: Same operation on multiple targets.

```
One task → Fan out to N workers → Fan in to synthesize
```

**Example**: Review 5 files
1. Spawn 5 review subagents (one per file)
2. Collect all reviews
3. Synthesize into single report

### Aggregation output location

**Small aggregation** (< 100 lines): Include in orchestrator response
**Large aggregation** (>= 100 lines): Write to `docs_dev/[name]-aggregated.md`

---

## Delegation Checklist

Before spawning any subagent, verify:

- [ ] Task is too complex or long for orchestrator
- [ ] Prompt includes all required elements
- [ ] Context is sufficient but not excessive
- [ ] Output format is specified
- [ ] Concurrent agent limit not exceeded
- [ ] No file conflicts with running agents
- [ ] No git conflicts with running agents
- [ ] Success criteria are verifiable
