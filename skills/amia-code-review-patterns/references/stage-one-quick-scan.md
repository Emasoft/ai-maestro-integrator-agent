# Stage One: Quick Scan Process

## Table of Contents

- 1.1 Objective and Purpose
- 1.2 Scope Targets by PR Size
  - 1.2.1 Small PRs (1-10 files)
  - 1.2.2 Medium PRs (11-30 files)
  - 1.2.3 Large PRs (30+ files)
- 1.3 Step-by-Step Quick Scan Process
  - 1.3.1 File Structure Assessment
  - 1.3.2 Diff Magnitude Review
  - 1.3.3 Obvious Issue Scan
  - 1.3.4 Immediate Red Flags Detection
  - 1.3.5 Quick Confidence Assessment
- 1.4 Quick Scan Output Format Template
- 1.5 Go/No-Go Decision Criteria

---

## 1.1 Objective and Purpose

The Quick Scan objective is to rapidly identify critical blockers or obvious issues that would immediately fail code review. This stage acts as a filter to prevent wasted effort on PRs with fundamental problems.

**Time Target**: 5-15 minutes maximum
**Confidence Threshold**: 70%+ to proceed to Stage Two

---

## 1.2 Scope Targets by PR Size

### 1.2.1 Small PRs (1-10 files)

- Quick scan should complete in under 5 minutes
- Focus on file types and obvious issues
- Lower risk of hidden complexity

### 1.2.2 Medium PRs (11-30 files)

- Quick scan may take 10-15 minutes
- Pay attention to cross-file dependencies
- Check for logical grouping of changes

### 1.2.3 Large PRs (30+ files)

- Consider requesting PR split before detailed review
- Large PRs have higher defect density
- Quick scan should identify if split is needed

---

## 1.3 Step-by-Step Quick Scan Process

### 1.3.1 File Structure Assessment

**What to examine:**
- Modified files list
- File types (source code, tests, config, docs)
- Directory structure changes

**What to look for:**
- Suspicious additions (credentials, large binaries)
- Unexpected file types
- Changes to sensitive directories (security, auth, config)

**Pass criteria**: File changes are logical and expected for the stated purpose

### 1.3.2 Diff Magnitude Review

**What to measure:**
- Lines added/removed/modified per file
- Total change size
- Concentration of changes

**Warning thresholds:**
- Single file: >500 lines changed
- Total PR: >2000 lines changed
- High churn: Many lines both added and deleted

**Pass criteria**: Changes are focused and appropriately sized

### 1.3.3 Obvious Issue Scan

**What to detect:**
- Syntax errors and typos
- Commented-out code blocks
- Leftover debug statements (console.log, print, debugger)
- TODO/FIXME markers indicating incomplete work
- Merge conflict markers

**Pass criteria**: No obvious issues blocking review

### 1.3.4 Immediate Red Flags Detection

**Critical red flags (immediate STOP):**
- Disabled security checks or linting rules
- Removal of existing tests without replacement
- Hard-coded credentials or sensitive data
- Breaking changes to public APIs without versioning plan
- Circular dependencies or import cycles
- Bypass of code review requirements

**If any red flag detected:**
1. Document the specific issue
2. Stop the review
3. Request clarification from author
4. Do NOT proceed to Stage Two

### 1.3.5 Quick Confidence Assessment

**Score calculation:**
- Start at 50%
- Add 10% if file structure is clean
- Add 10% if diff magnitude is reasonable
- Add 10% if no obvious issues found
- Add 20% if no red flags detected

**Decision thresholds:**
- Score >= 70%: Proceed to Stage Two
- Score < 70%: Request clarification, do not proceed

---

## 1.4 Quick Scan Output Format Template

```
QUICK SCAN RESULT
=================
Repository: [repo name]
Pull Request: #[number]
Files Changed: [count]
Lines Added/Removed: +[add] -[remove]

SCAN FINDINGS:
- File structure: [PASS/CONCERN]
- Diff magnitude: [PASS/CONCERN]
- Obvious issues: [PASS/CONCERN/ISSUES FOUND]
- Red flags: [NONE/FLAGGED]

RED FLAGS DETECTED:
[List any critical issues found, or "None detected"]

QUICK SCAN CONFIDENCE: [70-100%]
NEXT STEP: [PROCEED TO STAGE TWO / REQUEST CLARIFICATION]

NOTES:
[Any additional observations or concerns]
```

---

## 1.5 Go/No-Go Decision Criteria

### PROCEED to Stage Two when:
- Confidence score is 70% or higher
- No critical red flags detected
- File structure and changes are logical
- Author has provided sufficient context

### REQUEST CLARIFICATION when:
- Confidence score is below 70%
- Red flags are detected but may have valid explanations
- Context or purpose is unclear
- Changes seem unrelated to stated purpose

### REJECT IMMEDIATELY when:
- Hard-coded credentials or secrets detected
- Obvious malicious code patterns
- Merge conflicts present
- Tests completely removed without replacement
