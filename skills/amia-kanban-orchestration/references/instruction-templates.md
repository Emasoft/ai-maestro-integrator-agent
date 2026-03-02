# Instruction Templates

Templates for all task assignments, integration instructions, and communication patterns used in GitHub Kanban orchestration.

---

## Table of Contents

- 1. Task Assignment Template
- 2. GitHub Issue Template for Subtasks
- 3. Integration Assignment Template
- 4. Conflict Resolution Assignment Template
- 5. Merge Authorization Template
- 6. Progress Check-In Template

---

## 1. Task Assignment Template

```
=== TASK ASSIGNMENT ===

GITHUB ISSUE: #[number]
TASK: [Task Name]
OBJECTIVE: [What to deliver]

SPECIFIC INSTRUCTIONS:
1. [Step 1 - what to implement]
2. [Step 2 - what to test]
3. [Step 3 - what to document]

COMPLETION CRITERIA:
- [Criterion 1]
- [Criterion 2]
- All tests passing (local + CI/CD)
- Documentation updated

REPORTING REQUIREMENTS:
When complete, send AI Maestro message with:
- Subject: "COMPLETE: GH-[number] - [task name]"
- Priority: high
- Content: {
    "type": "completion_report",
    "message": "Report format below"
  }

REPORT FORMAT:
```
[DONE/FAILED] GH-[number] task_name
Status: [completed/failed/blocked]
Tests: [all passing/X failures]
CI/CD: [passing/failing]
Coverage: [maintained/decreased]
Blockers: [none/description]
Details: [link to GitHub issue comment]
```

POST DETAILED LOGS TO:
GitHub issue #[number] as comment

DO NOT:
- Work on multiple tasks
- Make assumptions about other tasks
- Skip testing
- Commit incomplete code
- Merge without approval
```

---

## 2. GitHub Issue Template for Subtasks

```markdown
## Task Description
[What needs to be done]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] All tests passing

## Dependencies
- Depends on: #issue-number
- Blocks: #issue-number

## Assigned Agent
Agent name: [full-session-name]

## Verification Requirements
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] CI/CD passes
- [ ] Code review approved
```

---

## 3. Integration Assignment Template

```
=== INTEGRATION ASSIGNMENT ===

TASK: Integrate completed subtasks for [Feature Name]

COMPLETED SUBTASKS:
- GH-[number]: [description] - Agent: [name]
- GH-[number]: [description] - Agent: [name]
- GH-[number]: [description] - Agent: [name]

INTEGRATION STEPS:
1. Create integration branch from main
2. Merge feature branches in this order: [list]
3. Resolve any conflicts following [conflict resolution guide]
4. Run full test suite
5. Run integration tests
6. Run performance tests (if applicable)
7. Run security review (if applicable)

VERIFICATION REQUIREMENTS:
- All tests still passing after integration
- No functionality lost
- No new conflicts introduced
- Performance benchmarks met
- Security scan passes

REPORTING:
Send completion report with:
- Test results summary
- Conflict resolution details
- Integration branch name
- Ready for merge: yes/no
- Blockers: [list]

POST LOGS TO:
GitHub issue #[integration-issue-number]

AWAIT APPROVAL BEFORE MERGING TO MAIN
```

---

## 4. Conflict Resolution Assignment Template

```
=== CONFLICT RESOLUTION ASSIGNMENT ===

INTEGRATION ISSUE: GH-[number]
CONFLICTS REPORTED: [list of files]

CONFLICTING BRANCHES:
- Branch 1: [name] - Original agent: [name]
- Branch 2: [name] - Original agent: [name]

RESOLUTION STRATEGY:
[Describe which changes to prioritize and why]

RESOLUTION STEPS:
1. Review both implementations
2. Determine correct resolution based on strategy
3. Apply resolution
4. Run full test suite
5. Verify no functionality lost from either branch

VERIFICATION:
- All tests passing
- Both feature sets preserved (or explain omissions)
- Documentation updated for final implementation

SEND RESOLUTION REPORT WITH:
- Files resolved
- Strategy applied
- Tests results
- Ready for re-integration: yes/no
```

---

## 5. Merge Authorization Template

```
=== MERGE AUTHORIZATION ===

INTEGRATION ISSUE: GH-[number]
INTEGRATION BRANCH: [name]
EXECUTOR AGENT: [full-session-name]

VERIFICATION COMPLETE:
✓ All tests passing
✓ No conflicts
✓ Documentation current
✓ Peer review approved

MERGE INSTRUCTIONS:
1. Rebase integration branch onto main (NO merge commits)
2. Verify all tests still pass after rebase
3. Create atomic commit with changelog below
4. Tag release: [version] (if applicable)
5. Push to main
6. Send completion confirmation

COMMIT MESSAGE:
```
[Feature Name]

Completed subtasks:
- GH-[number]: [description]
- GH-[number]: [description]

Changes:
- [change 1]
- [change 2]

Tests: All passing (local + CI/CD)
Coverage: [maintained/increased]
```

SEND CONFIRMATION AFTER MERGE COMPLETE
```

---

## 6. Progress Check-In Template

```
=== PROGRESS CHECK-IN ===

ISSUE: GH-[number]
TASK: [task name]

REQUEST:
Please provide status update with:
- Current progress percentage
- Completed items
- Remaining items
- Blockers or concerns

FORMAT:
[IN_PROGRESS] GH-[number] - [status summary]
Progress: [X%]
Blockers: [none/description]
```

---

## Usage Notes

### When to Use Each Template

| Template | Use Case | Recipient |
|----------|----------|-----------|
| Task Assignment | New work assignment | Implementer agent |
| GitHub Issue | Creating module issues | N/A (GitHub) |
| Integration Assignment | Merging completed work | Integration agent |
| Conflict Resolution | Merge conflicts detected | Conflict resolver |
| Merge Authorization | Final approval to merge | Integration agent |
| Progress Check-In | Status update request | Any agent |

### AI Maestro Message Format

All templates should be sent via AI Maestro using the `agent-messaging` skill with:
- **Recipient**: The target agent session name
- **Subject**: The subject line from the template
- **Priority**: `high` (or as specified in the template)
- **Content**: `{"type": "assignment|request|approval", "message": "TEMPLATE_CONTENT_HERE"}`
- **Verify**: Confirm the message was delivered by checking the `agent-messaging` skill send confirmation.

### Template Customization

All templates can be customized for specific project needs:
- Add project-specific verification steps
- Add custom reporting requirements
- Add domain-specific completion criteria
- Adjust reporting formats

### Integration with GitHub Issues

Templates are designed to work with GitHub Issues:
- Reference GitHub issue numbers with `GH-[number]` format
- Post detailed logs to GitHub issue comments
- Link completion reports back to issues
- Update issue status based on reports
