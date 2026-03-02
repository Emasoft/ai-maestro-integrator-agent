# Phase 2: Structured Analysis

## Table of Contents

- 2.1 When to use the structured analysis framework
- 2.2 Overview of the 5 analysis dimensions
- 2.3 How to apply the dimensions sequentially
- 2.4 How to flag items requiring author evidence
- 2.5 Cross-references to each dimension file

---

## 2.1 When to use the structured analysis framework

Apply the structured analysis framework to every PR after completing Phase 1 (Context Gathering). The 5 dimensions provide a systematic way to evaluate changes without relying on intuition or spot-checking. Each dimension examines the PR from a different perspective, ensuring comprehensive coverage.

For small PRs (1-3 files, less than 50 lines changed), you may apply all 5 dimensions in a single pass. For large PRs (10+ files or 500+ lines changed), apply each dimension as a separate pass through the changes.

---

## 2.2 Overview of the 5 analysis dimensions

The 5 analysis dimensions are applied in order. Each dimension has its own reference file with detailed questions, checklists, red flags, and examples.

| Dimension | Name | What It Evaluates | Reference File |
|-----------|------|-------------------|----------------|
| 1 | Problem Verification | Does the PR actually solve the stated problem? Is the root cause correctly identified? | [dimension-1-problem-verification.md](./dimension-1-problem-verification.md) |
| 2 | Redundancy Check | Does the change duplicate existing functionality? Could we modify existing code instead? | [dimension-2-redundancy-check.md](./dimension-2-redundancy-check.md) |
| 3 | System Integration Validation | Are file paths, commands, and environment assumptions correct on all target platforms? | [dimension-3-system-integration.md](./dimension-3-system-integration.md) |
| 4 | Senior Developer Review | Is this the right architectural approach? What about maintainability, performance, security, compatibility? | [dimension-4-senior-review.md](./dimension-4-senior-review.md) |
| 5 | False Positive Detection | Is the author making unverified assumptions? Could this be cargo cult programming or a placebo fix? | [dimension-5-false-positive-detection.md](./dimension-5-false-positive-detection.md) |

**Dimension 5 (False Positive Detection) is the most critical dimension.** It is the final checkpoint that catches issues the other four dimensions may miss. Never skip it.

---

## 2.3 How to apply the dimensions sequentially

For each dimension:

1. Read the corresponding reference file.
2. Answer every question in the reference file's checklist. Mark each item as PASS, FAIL, or NEEDS EVIDENCE.
3. Record any red flags that apply to this PR.
4. If any question cannot be answered with confidence, flag it as requiring evidence from the author.
5. Move to the next dimension.

After completing all 5 dimensions, you will have a comprehensive list of:
- Items that passed (strengths to mention in the review)
- Items that failed (blocking issues to raise)
- Items needing evidence (questions to ask the author)
- Red flags (patterns that suggest deeper problems)

This list feeds directly into Phase 3 (Evidence Requirements) and Phase 4 (Review Output).

**Example of sequential application:**

Reviewing a PR that adds a new binary search path to a detection script:

| Dimension | Key Finding |
|-----------|-------------|
| 1. Problem Verification | NEEDS EVIDENCE -- The PR claims to fix "binary not found" but does not show the error occurring without the fix |
| 2. Redundancy Check | FAIL -- The existing path list already contains a path that covers this installation location |
| 3. System Integration | NEEDS EVIDENCE -- The claimed path has not been verified on the target operating system |
| 4. Senior Review | PASS -- The change follows existing patterns and has minimal complexity |
| 5. False Positive Detection | FAIL -- The author cannot demonstrate the problem returns if the change is removed |

---

## 2.4 How to flag items requiring author evidence

When you encounter a checklist item you cannot answer with confidence:

1. Mark it as **NEEDS EVIDENCE** (not PASS or FAIL).
2. Write a specific, actionable evidence request. Tell the author exactly what to provide.
3. Include the evidence request in your Phase 3 list and in the review output (Phase 4).

**Bad evidence request:** "Please provide more information about the path."

**Good evidence request:** "Please provide the output of `ls -la /opt/homebrew/bin/mytool` on an Apple Silicon Mac. This will verify that the path exists as claimed in the PR description."

The difference is specificity: the good request tells the author exactly what command to run and why.

---

## 2.5 Cross-references to each dimension file

Read each file in order as you apply the corresponding dimension:

1. **Dimension 1 -- Problem Verification:** [dimension-1-problem-verification.md](./dimension-1-problem-verification.md)
   - Covers: error identification, root cause analysis, fix validation, assumption documentation, testing methodology
   - Key question: "Does this fix actually address the root cause?"

2. **Dimension 2 -- Redundancy Check:** [dimension-2-redundancy-check.md](./dimension-2-redundancy-check.md)
   - Covers: duplicate search, existing solution analysis, list/array placement, configuration vs code
   - Key question: "Does this duplicate something that already exists?"

3. **Dimension 3 -- System Integration Validation:** [dimension-3-system-integration.md](./dimension-3-system-integration.md)
   - Covers: path verification, documentation cross-reference, path handling, installation locations
   - Key question: "Are all system-level assumptions verified on target platforms?"

4. **Dimension 4 -- Senior Developer Review:** [dimension-4-senior-review.md](./dimension-4-senior-review.md)
   - Covers: architecture, technical debt, performance, security, backwards compatibility
   - Key question: "Is this the right long-term solution, not just a quick fix?"

5. **Dimension 5 -- False Positive Detection:** [dimension-5-false-positive-detection.md](./dimension-5-false-positive-detection.md)
   - Covers: assumption verification, alternative explanations, placebo effect, cargo cult detection, confirmation bias, reversibility test
   - Key question: "If we remove this change, can we demonstrate that the problem returns?"
