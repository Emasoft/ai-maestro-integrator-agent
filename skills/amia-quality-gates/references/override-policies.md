# Gate Override Policies

Gate overrides should be rare. This document describes when and how overrides can be applied.

## Table of Contents

- Overrides Are Exceptions
- Override Authority Matrix
- Override Procedure

## Overrides Are Exceptions

Every override must be:
1. Justified with clear reasoning
2. Documented in the PR
3. Approved by authorized personnel

## Override Authority Matrix

| Gate | Override Authority | Documentation Required |
|------|-------------------|------------------------|
| Pre-Review | AMOA or Maintainer | Comment explaining exception |
| Review (non-security) | Senior Reviewer | Review comment with justification |
| Review (security) | **No override allowed** | N/A |
| Pre-Merge | Maintainer | Comment explaining urgency |
| Post-Merge | N/A (cannot override after merge) | N/A |

## Override Procedure

```bash
# Document override in PR
gh pr comment $PR_NUMBER --body "**GATE OVERRIDE**

Gate: [Gate Name]
Reason: [Detailed justification]
Approved by: [Authority name]
Risk mitigation: [Steps taken to mitigate risk]
Follow-up: [Planned follow-up actions]"

# Add override label
gh pr edit $PR_NUMBER --add-label "gate:override-applied"
```

See [override-examples.md](override-examples.md) for complete override documentation examples.
