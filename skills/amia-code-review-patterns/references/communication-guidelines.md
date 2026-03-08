---
name: "Code Review Communication Guidelines"
description: "Best practices for communicating code review feedback effectively, constructively, and professionally"
---

# Code Review Communication Guidelines

## Table of Contents

- [Core Principles](#core-principles)
- [The Language of Review](#the-language-of-review)
  - [Tone Modifiers](#tone-modifiers)
  - [Framing Techniques](#framing-techniques)
- [Comment Structure](#comment-structure)
  - [The PIER Model](#the-pier-model)
  - [Short Comment Template](#short-comment-template)
  - [Long Comment Template](#long-comment-template)
- [Giving Feedback by Issue Type](#giving-feedback-by-issue-type)
  - [Security Issues](#security-issues)
  - [Performance Issues](#performance-issues)
  - [Logic Errors](#logic-errors)
  - [Style/Readability Issues](#stylereadability-issues)
  - [Architecture/Design Issues](#architecturedesign-issues)
- [Positive Feedback](#positive-feedback)
  - [Why It Matters](#why-it-matters)
  - [When to Give Positive Feedback](#when-to-give-positive-feedback)
  - [Examples](#examples)
- [Handling Disagreements](#handling-disagreements)
  - [When Author Pushes Back](#when-author-pushes-back)
  - [When You're Uncertain](#when-youre-uncertain)
  - [When to Escalate](#when-to-escalate)
- [Responding to Feedback (Author Perspective)](#responding-to-feedback-author-perspective)
  - [Receiving Feedback](#receiving-feedback)
  - [Resolving Comments](#resolving-comments)
- [Review Response Templates](#review-response-templates)
  - [Approval](#approval)
  - [Approve with Comments](#approve-with-comments)
  - [Request Changes](#request-changes)
- [Cultural Considerations](#cultural-considerations)
  - [Remote/Distributed Teams](#remotedistributed-teams)
  - [Junior Developers](#junior-developers)
  - [Senior Developers](#senior-developers)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Communication Checklist](#communication-checklist)
- [Summary](#summary)

Effective code review communication balances thoroughness with empathy. This guide helps you provide feedback that improves code while supporting team collaboration.

## Core Principles

### 1. **Be Kind**

Remember: There's a person behind the code who invested time and effort.

### 2. **Be Specific**

Vague feedback wastes time. Always point to exact locations and provide examples.

### 3. **Be Constructive**

Focus on improvement, not criticism. Suggest solutions, not just problems.

### 4. **Be Timely**

Respond within 24-48 hours. Blocked authors harm team velocity.

### 5. **Be Humble**

Your suggestions might not always be the best solution. Stay open to discussion.

---

## The Language of Review

### Tone Modifiers

Use these patterns to adjust tone appropriately:

**For hard requirements (P0/P1):**

```
❌ "This is wrong"
✅ "This needs to change because [reason]"

❌ "You forgot error handling"
✅ "Please add error handling here for [specific case]"

❌ "Obviously this won't work"
✅ "This approach may not work because [reason]"
```

**For suggestions (P2/P3):**

```
✅ "Consider using X instead of Y for [benefit]"
✅ "What do you think about [alternative approach]?"
✅ "Minor: this could be simplified to [suggestion]"
✅ "Nitpick: [small style issue]"
```

**For questions:**

```
✅ "Why did you choose X over Y?"
✅ "Can you explain the reasoning behind [decision]?"
✅ "How does this handle [edge case]?"
✅ "I'm not familiar with this pattern. Could you explain?"
```

### Framing Techniques

**Use "we" instead of "you":**

```
❌ "You should use a HashMap here"
✅ "We typically use HashMap for this pattern"

❌ "You didn't handle the null case"
✅ "We need to handle the null case here"
```

**Use questions to guide:**

```
❌ "This is inefficient"
✅ "This loop runs O(n²). Could we optimize with a HashSet?"

❌ "Wrong pattern"
✅ "Have you considered using the Strategy pattern here?"
```

**Acknowledge uncertainty:**

```
✅ "I might be missing something, but this looks like it could cause [issue]"
✅ "If I understand correctly, this would [behavior]. Is that intentional?"
```

---

## Comment Structure

### The PIER Model

**P**roblem - **I**mpact - **E**xample - **R**ecommendation

**Example:**

```markdown
**Problem:** This query isn't using an index on user_email.

**Impact:** With 100K+ users, this will cause significant slowdown (3-5 seconds per query).

**Example:**
Current: SELECT * FROM users WHERE user_email = 'test@example.com'
With index: CREATE INDEX idx_user_email ON users(user_email)

**Recommendation:** Add index migration or modify query to use existing indexed field.
```

### Short Comment Template

For quick issues:

```
[File:Line] [Issue] → [Fix]

Example:
user.py:45 Variable `x` is unclear → Rename to `user_id`
```

### Long Comment Template

For complex issues:

```markdown
## [Title - What's Wrong]

**Location:** `path/to/file.py:45-60`

**Issue:** [Describe the problem]

**Why it matters:** [Impact on security/performance/maintainability]

**Current code:**
```python
[code snippet]
```

**Suggested fix:**

```python
[improved code]
```

**Rationale:** [Why this fix is better]

**Priority:** [P0/P1/P2/P3]

```

---

## Giving Feedback by Issue Type

### Security Issues

**Be direct and clear:**
```markdown
🚨 **SECURITY ISSUE - Must Fix**

**Vulnerability:** SQL Injection in `get_user_by_name()`

**Location:** `api/users.py:34`

**Risk:** Attacker can execute arbitrary SQL queries, potentially exposing all user data.

**Current:**
```python
query = f"SELECT * FROM users WHERE name = '{username}'"
```

**Fix:**

```python
query = "SELECT * FROM users WHERE name = ?"
cursor.execute(query, (username,))
```

**Priority:** P0 - Block merge until fixed

```

### Performance Issues

**Provide data and context:**
```markdown
**Performance Issue**

**Location:** `service/report.py:78-95`

**Problem:** This generates N+1 database queries (one query per item in loop).

**Impact:** With 1000 items, this executes 1001 queries (~5-10 seconds vs ~50ms).

**Example:**
```python
# Current: N+1 queries
for user_id in user_ids:
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    process(user)

# Suggested: Single query
users = db.query("SELECT * FROM users WHERE id IN (?)", user_ids)
for user in users:
    process(user)
```

**Priority:** P1 - Should fix before merge

```

### Logic Errors

**Explain the scenario:**
```markdown
**Logic Error**

**Location:** `payment/processor.py:56`

**Issue:** Edge case not handled when `amount == 0`.

**Scenario:**
1. User applies 100% discount coupon
2. `calculate_total()` returns 0
3. This code divides by total: `fee = service_cost / total`
4. Results in ZeroDivisionError

**Fix:**
```python
if total <= 0:
    return 0  # or handle zero-total case appropriately
fee = service_cost / total
```

**Priority:** P1

```

### Style/Readability Issues

**Be gentle and educational:**
```markdown
**Readability Suggestion (P2)**

**Location:** `utils/helpers.py:23`

**Current:**
```python
def p(d, k, v):
    return d.get(k, v)
```

**Suggestion:**

```python
def get_with_default(data: dict, key: str, default: Any) -> Any:
    """Get value from dict with fallback to default."""
    return data.get(key, default)
```

**Rationale:** Clear function names improve code self-documentation. Future maintainers (including your future self!) will understand this faster.

**This is a minor suggestion - feel free to defer if you prefer the current approach.**

```

### Architecture/Design Issues

**Focus on maintainability:**
```markdown
**Design Consideration**

**Location:** `api/handlers.py:45-120`

**Observation:** The handler contains business logic, validation, and database access.

**Concern:** This violates separation of concerns and makes testing difficult.

**Suggestion:** Consider refactoring to:
```python
# Handler (thin layer)
def create_user(request):
    data = UserCreateSchema.validate(request.json)
    user = UserService.create(data)
    return jsonify(user), 201

# Service (business logic)
class UserService:
    @staticmethod
    def create(data):
        # validation, business rules
        return UserRepository.save(User(**data))

# Repository (data access)
class UserRepository:
    @staticmethod
    def save(user):
        # database operations
        return db.session.add(user)
```

**Benefit:** Each layer is testable in isolation, easier to maintain.

**Priority:** P2 (can be deferred to refactoring PR if timeline is tight)

**Open to discussion - what do you think?**

```

---

## Positive Feedback

### Why It Matters

Positive feedback:
- Reinforces good practices
- Builds team morale
- Helps junior developers learn what "good" looks like
- Makes critical feedback easier to receive

### When to Give Positive Feedback

**Always comment on:**
- Clever solutions
- Particularly clear code
- Good test coverage
- Excellent documentation
- Thoughtful edge case handling

### Examples

```markdown
✨ Nice solution! Using a Set here is much cleaner than my initial approach.

👍 Great test coverage - I especially like the edge case tests for null values.

💯 Excellent docstring! The examples make this function's behavior crystal clear.

🎯 This refactoring significantly improves readability. Well done!

⚡ Smart optimization! This cuts the processing time by ~70%.
```

---

## Handling Disagreements

### When Author Pushes Back

**Stay collaborative:**

```markdown
Author: "I disagree - I think the current approach is fine."

❌ Bad Response:
"No, you're wrong. This needs to change."

✅ Good Response:
"I see your point. Let me explain my concern in more detail: [reasoning].
That said, if you feel strongly about keeping this approach, could we
at least add a comment explaining the trade-offs? I'm also happy to
discuss this synchronously if easier."
```

### When You're Uncertain

**Admit it and ask for help:**

```markdown
"I'm not familiar with this pattern. Could you explain the benefits
over [alternative]? I want to make sure I understand before approving."

"This is outside my area of expertise. I've asked @domain-expert to
weigh in on the [specific aspect]."
```

### When to Escalate

Escalate to senior reviewer or team lead when:

- Security concerns beyond your expertise
- Fundamental architectural disagreement
- Approach contradicts team standards but author insists
- Issue impacts multiple teams

**Escalation template:**

```markdown
@tech-lead I'd like your input on this PR.

Context: [brief summary]
Disagreement: [author's position vs your concern]
Question: [specific question for tech lead]

Thanks!
```

---

## Responding to Feedback (Author Perspective)

### Receiving Feedback

**Assume good intent:**

```markdown
❌ "This comment is wrong. I did handle that case."
✅ "Good catch! I handled this in line 67. Should I make it more obvious?"

❌ "You clearly didn't read the code."
✅ "I see the confusion. Let me add a comment explaining why I chose X."
```

**Ask clarifying questions:**

```markdown
"Could you elaborate on the security concern here? I'm not seeing the
vulnerability."

"What scenario would cause this edge case? I want to make sure I
understand before adding the check."
```

**Acknowledge and act:**

```markdown
"Great point! Fixed in [commit hash]."

"Thanks for catching this. I've updated the code and added a test."

"Agreed this could be clearer. I've refactored to [new approach]."
```

### Resolving Comments

**Always respond before resolving:**

```markdown
✅ "Fixed in commit abc123" → [Resolve]
✅ "Added error handling as suggested" → [Resolve]
✅ "Decided to keep current approach because [reason]" → [Resolve]

❌ [Just click Resolve with no comment] → Unclear to reviewer
```

---

## Review Response Templates

### Approval

```markdown
## ✅ Approved

Great work on this PR! The implementation is solid and well-tested.

**Highlights:**
- Excellent test coverage
- Clear, readable code
- Good error handling

**Minor suggestions (optional):**
- Consider extracting the validation logic into a helper function
- Add a docstring to `process_data()`

These are minor and can be addressed in a follow-up if you prefer.

Ready to merge!
```

### Approve with Comments

```markdown
## ✅ Approved with Comments

Nice work overall! I've left a few suggestions below:

**P1 - Should address:**
1. Add error handling for API timeout (payment.py:45)
2. Include test for edge case when amount=0

**P2 - Nice to have:**
1. Rename `x` to `user_count` for clarity
2. Extract repeated validation logic

The P1 items are important but non-blocking. Feel free to address them
in this PR or a quick follow-up.

Approving so this doesn't block you.
```

### Request Changes

```markdown
## 🔄 Changes Requested

Thanks for the PR! Before we can merge, please address:

**P0 - Must Fix:**
1. SQL injection vulnerability in `get_user()` (users.py:34)
   - Use parameterized queries instead of string formatting
2. Missing authorization check in `delete_user()` (users.py:67)
   - Add `@require_admin` decorator

**P1 - Should Fix:**
1. Add tests for error scenarios
2. Handle null case in `calculate_total()` (payment.py:56)

**P2 - Suggestions:**
1. Consider renaming `process()` to `process_payment()` for clarity
2. Extract magic numbers to constants

Please ping me when you've addressed the P0/P1 items and I'll re-review.

Let me know if you have questions on any of these!
```

---

## Cultural Considerations

### Remote/Distributed Teams

**Account for timezone differences:**

```markdown
"I'm EOD now but will review first thing tomorrow (my morning ~8am UTC)."

"No rush on this - I know it's late evening for you. We can discuss
async or sync up tomorrow."
```

**Be explicit with text:**

```markdown
❌ "lol this is wild" → Could be misinterpreted as mocking
✅ "Interesting approach! I hadn't considered this. Could you walk me
    through the reasoning?"
```

### Junior Developers

**Be educational:**

```markdown
"This works, but there's a more idiomatic Python approach: [example].

Here's why the community prefers this pattern: [explanation].

Great first PR though - the logic is sound!"
```

**Encourage questions:**

```markdown
"This is a common mistake! The key difference between X and Y is [explanation].

Feel free to ask if you'd like me to explain further."
```

### Senior Developers

**Be respectful of expertise:**

```markdown
"I see you used approach X. I typically use Y for [reason], but I might
be missing context. Could you explain the advantage of X here?"

"This is outside my experience. If you're confident in this approach,
I'll defer to your judgment. Could you add a comment explaining it for
future maintainers?"
```

---

## Anti-Patterns to Avoid

### ❌ Don't: Be Vague

```markdown
❌ "This is confusing"
✅ "The variable name `data` is ambiguous. Consider `user_profile` since
    that's what this dict contains."
```

### ❌ Don't: Be Condescending

```markdown
❌ "Obviously, you should use a HashMap"
✅ "A HashMap would be more efficient here because [reason]"

❌ "Everyone knows you can't do this"
✅ "This approach has a subtle issue: [explanation]"
```

### ❌ Don't: Make It Personal

```markdown
❌ "You're not following the style guide"
✅ "This doesn't match our style guide (PEP 8). Could you run `black`
    to auto-format?"

❌ "You always forget error handling"
✅ "Please add error handling for [specific case]"
```

### ❌ Don't: Nitpick Without Priority

```markdown
❌ [25 comments all marked as equally important, mixing typos with
    security issues]

✅ Clear priority labels:
    - P0: Security vulnerability (BLOCK)
    - P1: Logic error (SHOULD FIX)
    - P2: Style issue (NICE TO HAVE)
```

### ❌ Don't: Review Line-by-Line Without Context

```markdown
❌ [50 individual comments on every line]

✅ "I see a pattern across these files: [issue]. Consider [solution]
    in all affected locations: [list]."
```

### ❌ Don't: Delay Feedback

```markdown
❌ [Review request Monday, review submitted Friday]
✅ [Review within 24-48 hours, or comment: "I'm swamped this week,
    could @colleague review?"]
```

---

## Communication Checklist

Before submitting your review, verify:

- [ ] Tone is constructive, not critical
- [ ] All comments are specific with examples
- [ ] Priority is clear (P0/P1/P2/P3)
- [ ] Positive feedback is included
- [ ] Questions are framed as questions
- [ ] Suggestions offer rationale
- [ ] Decision (approve/changes requested) is clear
- [ ] Next steps are explicit
- [ ] No personal language ("you always...")
- [ ] Review is timely (within 24-48 hours)

---

## Summary

**Great code review communication is:**

1. **Specific** - Point to exact lines, provide examples
2. **Constructive** - Suggest solutions, not just problems
3. **Balanced** - Include positive feedback with critical feedback
4. **Prioritized** - Clearly mark must-fix vs nice-to-have
5. **Empathetic** - Remember there's a person receiving this
6. **Timely** - Respond within 24-48 hours
7. **Collaborative** - Frame as "we" not "you vs me"
8. **Humble** - Stay open to other perspectives

**Remember:** The goal is to ship better code while building a stronger team. Every review is an opportunity to teach, learn, and collaborate.
