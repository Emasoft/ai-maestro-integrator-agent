# Worktree Verification - Part 4: Reporting Violations

[Back to Worktree Verification Index](worktree-verification.md)

---

## 4.7 Reporting Isolation Violations

### Violation Report Format

When an isolation violation is detected, document it:

```markdown
# Isolation Violation Report

## Summary
- **Date/Time:** 2024-01-15 14:30 UTC
- **Worktree:** /tmp/worktrees/pr-123
- **Agent:** Agent-A (PR #123 fix)
- **Severity:** HIGH / MEDIUM / LOW

## Violation Details

### Files Affected
| File Path | Expected Location | Actual Location |
|-----------|-------------------|-----------------|
| src/handler.py | /tmp/worktrees/pr-123 | /path/to/main-repo |
| config.json | /tmp/worktrees/pr-123 | /tmp/worktrees/pr-456 |

### Impact Assessment
- [ ] Main repo contaminated
- [ ] Other worktree contaminated
- [ ] Data loss occurred
- [ ] Incorrect PR contents

## Root Cause
[Description of why violation occurred]

## Resolution
[Steps taken to fix the violation]

## Prevention
[Measures to prevent recurrence]
```

### Escalation Criteria

**Escalate IMMEDIATELY if:**
- Sensitive data written to wrong location
- Multiple worktrees contaminated
- Production branches affected
- Data loss detected

**Escalate SOON if:**
- Repeated violations by same agent
- Violation pattern indicates systemic issue
- Resolution requires manual intervention

**Handle LOCALLY if:**
- Single file in wrong location
- Easily reversible
- No sensitive data involved
- Isolated incident

### Violation Categories

| Category | Description | Response |
|----------|-------------|----------|
| CRITICAL | Production/main contaminated | Immediate escalation |
| HIGH | Cross-worktree contamination | Escalate promptly |
| MEDIUM | Main repo touched but unchanged | Fix and document |
| LOW | Temp files in wrong location | Clean up and note |

### Reporting Template for Orchestrator

```
ISOLATION VIOLATION DETECTED
============================
Time: [timestamp]
Worktree: [path]
Agent: [agent-name]

Violation Type: [file_outside_worktree | cross_worktree | main_contamination]
Affected Files: [count]
Details:
- [file1]: [description]
- [file2]: [description]

Recommended Action: [escalate | fix_locally | ignore]
```

---

[Back to Worktree Verification Index](worktree-verification.md) | [Previous: Part 3](worktree-verification-part3-automated-manual.md)
