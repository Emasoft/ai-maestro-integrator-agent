# PR Evaluator Checklist

Complete this checklist for every PR evaluation to ensure thorough and consistent results.

---

## Pre-Evaluation Setup

- [ ] PR number and branch name identified
- [ ] Isolated environment chosen (worktree/container/clone)
- [ ] Main working directory will not be affected
- [ ] Previous evaluation environments cleaned up

## Environment Setup

- [ ] Isolated environment created successfully
- [ ] PR branch checked out correctly
- [ ] Dependencies installed (all dev dependencies included)
- [ ] Environment variables configured
- [ ] External services started (databases, caches, etc.)
- [ ] Services are ready and accessible

## Test Execution

- [ ] All unit tests executed
- [ ] All integration tests executed
- [ ] All end-to-end tests executed
- [ ] Performance tests executed (if applicable)
- [ ] Test output captured to log files
- [ ] Exit codes recorded
- [ ] Test reports generated (XML, HTML, JSON)
- [ ] Coverage reports generated
- [ ] All failures collected (not just first failure)

## Quality Checks

- [ ] Linting executed and results captured
- [ ] Type checking executed and results captured
- [ ] Security scan executed and results captured
- [ ] Build verification executed and results captured
- [ ] All check outputs saved to separate files

## Analysis

- [ ] Test results parsed and counted
- [ ] All failure details extracted
- [ ] Patterns in failures identified
- [ ] Metrics calculated (pass rate, coverage, duration)
- [ ] Baseline comparison performed (if available)
- [ ] Severity assessment completed

## Reporting

- [ ] Markdown report generated with all sections
- [ ] All test failures documented with complete details
- [ ] All quality check results included
- [ ] Verdict determined (APPROVE / REQUEST CHANGES / REJECT)
- [ ] Recommendations are actionable and specific
- [ ] Evidence included in appendices
- [ ] JSON output generated
- [ ] JSON is valid and well-formed
- [ ] Reports saved to appropriate locations

## Cleanup

- [ ] Evaluation environment removed
- [ ] No leftover worktrees or directories
- [ ] Docker containers stopped and removed (if used)
- [ ] Temporary files cleaned up
- [ ] Disk space freed

## Handoff

- [ ] Minimal report prepared (3 lines max)
- [ ] Verdict clearly stated
- [ ] Key findings summarized in one line
- [ ] File locations provided
- [ ] No verbose output in chat
- [ ] Orchestrator notified

---

## Quick Reference: Verdict Decision Matrix

| Tests | Build | Linting | Security | Verdict |
|-------|-------|---------|----------|---------|
| All pass | Pass | Clean | Clean | APPROVE |
| All pass | Pass | Minor | Clean | APPROVE (note issues) |
| Some fail | Pass | Any | Clean | REQUEST CHANGES |
| Any | Fail | Any | Any | REJECT |
| Any | Any | Any | Issues | REQUEST CHANGES or REJECT |
