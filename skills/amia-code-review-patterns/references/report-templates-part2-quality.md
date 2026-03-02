# Quality Report Template

Template for comprehensive code quality assessment and tracking.

## Table of Contents

- [Template](#template)
  - [Scoring Breakdown](#scoring-breakdown)
  - [Test Coverage](#test-coverage)
  - [Code Quality](#code-quality)
  - [Documentation](#documentation)
  - [Security](#security)
  - [Performance](#performance)
  - [Technical Debt](#technical-debt)
  - [Recommendations](#recommendations)
- [Quality Score Calculation](#quality-score-calculation)
- [Trend Indicators](#trend-indicators)

---

## Template

```markdown
# Quality Report
**Generated**: YYYY-MM-DD HH:MM:SS
**Scope**: [Project/Module Name]
**Baseline**: [Previous report date or initial state]

## Executive Summary
[2-3 sentences on overall code quality and trends]

## Quality Score: XX/100

### Scoring Breakdown
- Test Coverage: XX/30 points
- Code Quality: XX/25 points
- Documentation: XX/20 points
- Security: XX/15 points
- Performance: XX/10 points

## Test Coverage

### Overall: XX.X%

╔════════════════════════════╦══════════╦═══════════════╦═══════════╗
║ Module                     ║ Coverage ║ Lines Covered ║ Trend     ║
╠════════════════════════════╬══════════╬═══════════════╬═══════════╣
║ core/                      ║ 92.3%    ║ 1845/2000     ║ ↑ +2.1%   ║
║ utils/                     ║ 78.5%    ║ 523/666       ║ ↔ stable  ║
║ api/                       ║ 65.2%    ║ 432/662       ║ ↓ -3.4%   ║
╚════════════════════════════╩══════════╩═══════════════╩═══════════╝

**Coverage Gaps**:
- `api/endpoints.py`: Lines 145-178 (error handling)
- `core/processor.py`: Lines 234-256 (edge cases)

## Code Quality

### Linting: X issues (Y errors, Z warnings)

**Top Issues**:
1. Unused imports: 12 instances
2. Line length violations: 8 instances
3. Complex functions: 3 instances (cyclomatic complexity >10)

### Type Coverage: XX%

**Type Issues**:
- Missing return type annotations: 23 functions
- Any types used: 15 instances

## Documentation

### Completeness: XX%

- **Docstrings**: XX% of public functions documented
- **README**: ✅ Complete and up-to-date
- **API Docs**: ⚠️ 23% functions missing examples
- **Architecture Docs**: ✅ Complete

## Security

### Scan Results: X issues (Y high, Z medium, W low)

**Critical Issues**: None ✅

**High Priority**:
- [Issue 1 description and location]

## Performance

### Benchmarks

╔════════════════════════════╦═══════════╦═══════════╦═══════════╗
║ Operation                  ║ Current   ║ Target    ║ Status    ║
╠════════════════════════════╬═══════════╬═══════════╬═══════════╣
║ API Response Time (p95)    ║ 120ms     ║ <150ms    ║ ✅ Pass   ║
║ Batch Processing (1000)    ║ 3.2s      ║ <5s       ║ ✅ Pass   ║
║ Memory Usage (peak)        ║ 450MB     ║ <500MB    ║ ✅ Pass   ║
╚════════════════════════════╩═══════════╩═══════════╩═══════════╝

## Technical Debt

### High Priority Items
1. [Debt item 1] - Impact: [High/Medium/Low]
2. [Debt item 2] - Impact: [High/Medium/Low]

## Recommendations

### Immediate Actions
1. Increase test coverage in `api/` module to >80%
2. Fix high-priority security issues
3. Add type annotations to core functions

### Long-Term Improvements
1. Refactor complex functions to reduce cyclomatic complexity
2. Establish performance regression testing
3. Automate security scanning in CI/CD

---
**Sources**: Coverage Reports, Lint Outputs, Security Scans, Benchmark Results
**Report ID**: quality_YYYYMMDD_HHMMSS
```

---

## Quality Score Calculation

| Category | Max Points | Criteria |
|----------|------------|----------|
| Test Coverage | 30 | 30 pts at 90%+, scaled down linearly |
| Code Quality | 25 | Based on lint errors, complexity, type coverage |
| Documentation | 20 | Docstring coverage, README, API docs |
| Security | 15 | No high issues = 15, deduct per severity |
| Performance | 10 | Meeting benchmark targets |

## Trend Indicators

| Icon | Meaning |
|------|---------|
| ↑ | Improving |
| ↔ | Stable |
| ↓ | Declining |

---

**Back to [Report Templates Index](report-templates.md)**
