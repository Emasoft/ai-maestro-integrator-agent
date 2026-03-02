# Code Review Examples

## Table of Contents

- 1.1 When reviewing a PR from AMOA - Example: Review and Merge PR
- 1.2 When verifying issue closure - Example: Issue Closure Requirements Check
- 1.3 When using scripts for quick scan - Example: Script-Based Quick Scan
- 1.4 When performing full two-stage review - Example: Complete Two-Stage Review with Scripts

---

## 1.1 When reviewing a PR from AMOA - Example: Review and Merge PR

Use this example when you receive a PR review request from AMOA or user via AI Maestro and need to perform a complete two-stage review.

```
AMOA via AI Maestro: Please review PR #42 and merge if all quality gates pass.

AMIA (You): I'll review PR #42 against our quality gates.

Stage 1: Quick Scan
- File structure assessment: 5 files changed (small PR)
- Diff magnitude: +120/-30 lines
- No obvious issues
- Confidence: 75% → Proceed to Stage 2

Stage 2: Deep Dive
- Functional correctness: All logic verified
- Security: Input validation present
- Testing: 90% coverage, all tests pass
- Architecture: Follows existing patterns
- Backward compatibility: No breaking changes
- Code quality: Lint clean
- Performance: No regressions
- Documentation: README updated

Final Confidence: 85% → APPROVED

Actions:
- Merged PR #42 to main
- Closed linked issue #38
- Reported completion to AMOA via AI Maestro
```

---

## 1.2 When verifying issue closure - Example: Issue Closure Requirements Check

Use this example when AMOA requests issue closure and you need to verify all closure requirements are met.

```
AMOA via AI Maestro: Close issue #123 - the feature is complete.

AMIA (You): Before closing issue #123, verifying closure requirements...

Checklist:
- [x] Merged PR linked to issue: PR #120
- [x] All checkboxes in issue checked
- [x] Evidence of testing: CI passed, 15 new tests
- [x] TDD compliance: Tests written before implementation

All requirements met. Closing issue #123.
Reported completion to AMOA via AI Maestro.
```

---

## 1.3 When using scripts for quick scan - Example: Script-Based Quick Scan

Use this example when performing a quick scan using the provided Python scripts.

```bash
# Generate quick scan report
python scripts/quick_scan_template.py --pr 123 --repo owner/repo

# Output: Quick scan report with confidence score
# If confidence >= 70%, proceed to deep dive
# If confidence < 70%, request clarification from author
```

**Decision thresholds:**
- Confidence >= 70%: Proceed to Stage 2 (Deep Dive)
- Confidence < 70%: Request clarification from PR author

---

## 1.4 When performing full two-stage review - Example: Complete Two-Stage Review with Scripts

Use this example when performing a complete review using all three scripts in sequence.

```bash
# Stage 1: Quick Scan
python scripts/quick_scan_template.py --pr 456 --repo owner/repo
# Result: 75% confidence, proceed to Stage 2

# Stage 2: Deep Dive with 8-dimension analysis
python scripts/deep_dive_calculator.py --pr 456 --repo owner/repo
# Result: 82% confidence across all dimensions

# Generate final report
python scripts/review_report_generator.py --pr 456 --output review.md
```

**Script sequence:**
1. `quick_scan_template.py` - Initial assessment (threshold: 70%)
2. `deep_dive_calculator.py` - Full 8-dimension analysis (threshold: 80%)
3. `review_report_generator.py` - Final report generation

**Final decision thresholds:**
- Confidence >= 80%: Approve and merge
- Confidence 60-79%: Request specific changes
- Confidence < 60%: Reject, major rework needed
