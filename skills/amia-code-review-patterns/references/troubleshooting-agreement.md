# Troubleshooting: Handling Reviewer Disagreements

## Table of Contents
- If you need to understand the problem → Problem Description
- When analyzing why disagreements occur → Root Causes
- If you're looking for solutions → Solutions and Workarounds
- When preventing disagreements → Prevention Strategies
- When dealing with specific disagreement scenarios → Specific Disagreement Scenarios

## Problem Description

Reviewers disagree about whether code should be approved, how issues should be addressed, or what standards should be applied. These disagreements create friction, delay merges, frustrate authors and reviewers, and can damage team relationships if handled poorly.

## Root Causes

### 1. Ambiguous or Missing Standards
- No documented coding standards for the situation
- Gray areas not covered by existing guidelines
- Different interpretations of existing standards
- Outdated standards that don't reflect current practices

### 2. Different Priorities and Perspectives
- Conflicting values (e.g., performance vs readability)
- Different risk tolerances
- Varying emphasis on pragmatism vs idealism
- Divergent opinions on technical approaches

### 3. Knowledge or Experience Gaps
- Reviewers have different context about system or requirements
- Unequal familiarity with domain or technology
- Different understanding of past decisions
- Varying expertise levels

### 4. Communication Issues
- Unclear or ambiguous review comments
- Tone perceived as combative or dismissive
- Assumptions about shared understanding
- Argument in PR comments rather than direct discussion

### 5. Personal or Cultural Factors
- Ego or need to be right
- Fear of being overruled
- Cultural differences in communication styles
- Past conflicts affecting current interactions

## Solutions and Workarounds

### Immediate Actions

#### 1. Identify the Nature of Disagreement
```markdown
ACTION: Clarify what exactly is being disputed

QUESTIONS TO ASK:
- Is this about facts (what the code does)?
- Is this about standards (what the code should do)?
- Is this about priorities (what matters more)?
- Is this about risks (what could go wrong)?
- Is this about process (who decides)?

DIFFERENT TYPES NEED DIFFERENT RESOLUTION APPROACHES:
- Factual: Verify through testing or documentation
- Standards: Check documented guidelines
- Priorities: Escalate to decision-maker
- Risks: Gather more information, possibly defer
- Process: Follow established authority structure
```

#### 2. Move Discussion Out of PR Comments
```markdown
ACTION: Switch to synchronous communication

WHEN:
- More than 2-3 back-and-forth exchanges
- Comments getting longer or emotional
- Disagreement not resolving quickly
- Tone becoming negative

HOW:
- Jump on a call or video chat
- Meet in person if co-located
- Use chat for quick synchronous discussion
- Keep PR comments for decisions, not debate

BENEFITS:
- Faster resolution
- Less misunderstanding
- More nuanced discussion
- Better relationship preservation
```

#### 3. Seek to Understand Before Being Understood
```markdown
ACTION: Genuinely understand other reviewer's perspective

APPROACH:
1. Ask clarifying questions non-defensively
2. Summarize their position to confirm understanding
3. Acknowledge valid points in their argument
4. Explain your reasoning without dismissing theirs
5. Look for common ground
6. Be willing to change your mind

PHRASES:
- "Help me understand why you think..."
- "What I hear you saying is... Is that right?"
- "I see your point about X. My concern is Y..."
- "What if we..."
- "I hadn't considered that..."
```

#### 4. Check for Documented Standards
```markdown
ACTION: Verify if there's an existing team decision

CONSULT:
- Coding standards document
- Style guide
- Architecture decision records (ADRs)
- Team wiki or documentation
- Past similar PRs and discussions

IF STANDARD EXISTS:
- Apply it consistently
- Link to documentation in resolution
- If standard seems wrong, discuss separately

IF NO STANDARD:
- Acknowledge the ambiguity
- Make pragmatic decision for this PR
- Flag for team discussion to create standard
```

#### 5. Escalate Constructively
```markdown
ACTION: Involve appropriate decision-maker

WHEN TO ESCALATE:
- Reviewers can't reach agreement after good-faith discussion
- Decision requires broader team input
- Significant architectural or security implications
- Precedent-setting decision
- Time-sensitive PR blocked by disagreement

HOW TO ESCALATE:
1. Summarize both positions fairly
2. Identify specific question needing decision
3. Provide relevant context and constraints
4. Suggest decision-maker (tech lead, architect, team)
5. Respect the decision once made

WHO DECIDES:
- Code owner for their domain
- Tech lead for technical approach
- Architect for system design
- Security lead for security concerns
- Team consensus for new standards
```

### Long-Term Solutions

#### 1. Establish Clear Decision-Making Process
```markdown
ACTION: Document who decides what and how

DEFINE:
Authority Levels:
- Individual contributor: Decisions within their own code
- Code owner: Decisions for their domain
- Tech lead: Technical approach and architecture
- Team: New standards and practices
- Leadership: Resource/priority tradeoffs

Decision Process:
- When can individual reviewer block?
- When is team consensus needed?
- How are ties broken?
- What's the escalation path?
- How are decisions documented?

RESULT:
- Clear expectations reduce conflicts
- Faster resolution of disagreements
- Less ego investment in outcomes
- More predictable review process
```

#### 2. Create Comprehensive Standards Documentation
```markdown
ACTION: Document team conventions and patterns

INCLUDE:
- Coding standards with rationale
- Approved patterns and anti-patterns
- Security requirements and guidelines
- Performance standards and benchmarks
- Testing expectations
- Documentation requirements
- When exceptions are acceptable

MAINTAIN:
- Update when team makes decisions
- Include examples from real code
- Explain the "why" not just "what"
- Version control to track evolution
- Regular reviews for relevance

RESULT:
- Fewer disagreements about standards
- Easier to resolve when they occur
- Consistent application across team
- Onboarding documentation
```

#### 3. Regular Calibration Sessions
```markdown
ACTION: Align team on review standards and priorities

FORMAT:
- Review sample PRs or code snippets together
- Discuss what each person would comment on
- Surface disagreements in safe environment
- Make collective decisions on gray areas
- Document outcomes

FREQUENCY:
- Monthly for active teams
- More often when conflicts are frequent
- After significant team changes
- Following major technical decisions

BENEFITS:
- Proactive alignment prevents future conflicts
- Builds shared understanding
- Creates forum for healthy debate
- Strengthens team relationships
```

#### 4. Foster Collaborative Culture
```markdown
ACTION: Build psychological safety and teamwork

PRACTICES:
- Assume good intent in all reviews
- Default to curiosity over judgment
- Value learning over being right
- Celebrate good catches from any reviewer
- Acknowledge and appreciate review effort
- Share mistakes and learnings openly
- Recognize that disagreement can improve outcomes

LEADERSHIP ROLE:
- Model constructive disagreement
- Reinforce that it's okay to change your mind
- Credit reviewers who raise important issues
- Address toxic behavior quickly
- Promote blameless post-mortems
```

## Prevention Strategies

### For All Reviewers

#### Before Reviewing
1. **Check Your State**: Don't review when tired, stressed, or emotional
2. **Read Context**: Understand PR intent and background before commenting
3. **Know Standards**: Familiarize yourself with team conventions
4. **Set Aside Ego**: Remember goal is better code, not winning argument

#### While Reviewing
1. **Be Specific**: Vague objections create unnecessary friction
2. **Explain Reasoning**: Don't just say what, explain why
3. **Distinguish Categories**: Mark opinions as such, standards as standards
4. **Ask Questions**: Sometimes inquiry is better than assertion
5. **Acknowledge Tradeoffs**: Show you understand the complexity

#### When Disagreeing with Other Reviewer
1. **Private First**: DM them before escalating in PR
2. **Seek Understanding**: Ask why they see it differently
3. **Common Ground**: Find what you agree on
4. **Compromise**: Look for solutions that address both concerns
5. **Know When to Defer**: Pick your battles wisely

### For PR Authors

#### Preventing Disagreements
1. **Clear Description**: Explain rationale for approach taken
2. **Pre-empt Concerns**: Address likely questions upfront
3. **Invite Discussion**: For controversial changes, discuss before implementing
4. **Follow Standards**: Stick to documented conventions
5. **Right Reviewers**: Select reviewers with relevant expertise

#### When Disagreement Arises
1. **Stay Neutral**: Don't take sides or get defensive
2. **Provide Context**: Share information reviewers might not have
3. **Facilitate Resolution**: Help reviewers connect if needed
4. **Be Patient**: Good outcomes worth waiting for
5. **Appreciate Effort**: Thank reviewers for thorough consideration

### For Tech Leads

#### Preventing Disagreements
1. **Clear Standards**: Ensure team has documented conventions
2. **Regular Calibration**: Facilitate alignment discussions
3. **Defined Authority**: Clear who makes what decisions
4. **Model Behavior**: Demonstrate constructive disagreement
5. **Team Values**: Articulate and reinforce collaborative culture

#### When Disagreement Occurs
1. **Early Detection**: Watch for signs of conflict in PRs
2. **Quick Intervention**: Don't let disagreements fester
3. **Fair Facilitation**: Help both sides feel heard
4. **Timely Decision**: Don't leave PRs blocked indefinitely
5. **Follow-Up**: Ensure decision is documented and lessons captured

## Specific Disagreement Scenarios

### Disagreement About Code Quality
```markdown
SCENARIO: One reviewer says code is good enough, another wants refactoring

RESOLUTION APPROACH:
1. Assess current code quality objectively
2. Evaluate proposed refactoring value vs cost
3. Consider if refactoring could be follow-up work
4. Check if code meets minimum standards
5. Decide based on:
   - Is code correct and tested?
   - Does it meet team standards?
   - Is refactoring essential or nice-to-have?
   - Are there blockers or priorities?

GENERAL PRINCIPLE:
- Perfect is enemy of good
- If code meets standards, approve
- File follow-up issue for improvements if warranted
- Don't block on subjective quality preferences
```

### Disagreement About Security or Performance
```markdown
SCENARIO: One reviewer sees security/performance risk, another doesn't

RESOLUTION APPROACH:
1. Take the concern seriously (err on side of caution)
2. Gather data: Can the risk be measured or demonstrated?
3. Consult expert if neither reviewer is specialist
4. Consider mitigations if risk is real
5. Document decision and rationale

GENERAL PRINCIPLE:
- Security concerns override speed
- Performance concerns need data
- When in doubt, consult specialist
- Better safe than sorry for critical issues
```

### Disagreement About Testing
```markdown
SCENARIO: Reviewers disagree on test coverage adequacy

RESOLUTION APPROACH:
1. Check team's testing standards
2. Identify what's tested vs not tested
3. Assess risk of untested scenarios
4. Consider cost/benefit of additional tests
5. Decide based on:
   - Do tests meet minimum requirements?
   - Are critical paths covered?
   - Are edge cases important for this code?

GENERAL PRINCIPLE:
- Critical code needs thorough tests
- Tests should verify behavior, not just coverage
- Pragmatic balance between thoroughness and cost
- Can add tests in follow-up if not critical
```

### Disagreement About Design Approach
```markdown
SCENARIO: Reviewers prefer different technical approaches

RESOLUTION APPROACH:
1. Clarify requirements and constraints
2. Evaluate tradeoffs of each approach
3. Check if current approach violates standards
4. Consider switching cost vs benefit
5. Consult architect or tech lead if significant

GENERAL PRINCIPLE:
- Multiple valid approaches often exist
- Don't require rewrites for preference
- If current approach works and meets standards, approve
- Significant design decisions need appropriate authority
```

## Communication Patterns

### Constructive Disagreement
```markdown
GOOD:
"I'm concerned about the performance implications of this approach. In my experience, X pattern can lead to Y problem when scaled. Have you considered Z alternative? Here's why I think it might be better: [specific reasoning]."

WHY IT WORKS:
- States concern specifically
- Shares reasoning and experience
- Asks questions rather than demands
- Suggests alternative
- Explains rationale
```

### Unconstructive Disagreement
```markdown
AVOID:
"This is wrong. You should use X instead."

WHY IT FAILS:
- Dismissive tone
- No explanation
- No room for discussion
- Sounds like personal criticism
```

### Acknowledging Other Reviewer
```markdown
GOOD:
"@reviewer_name raised a good point about X. I initially missed that concern. However, I think Y approach might address it while also handling Z. What do you both think?"

WHY IT WORKS:
- Acknowledges other's contribution
- Adds to discussion productively
- Invites collaboration
- Seeks consensus
```

## Key Principles

1. **Disagree and Commit**: Healthy debate is good, but team must move forward once decision is made
2. **Standards Over Preferences**: Documented standards resolve most disagreements
3. **Assume Good Intent**: Everyone wants good code and successful project
4. **Escalate Early**: Don't let disagreements fester or poison relationships
5. **Learn from Conflict**: Disagreements often reveal gaps in standards or process
6. **Relationships Matter**: Maintaining good team dynamics trumps winning arguments
7. **Limit Debate Scope**: Escalate if discussion becomes unproductive (no arbitrary time limits per RULE 13)
8. **Document Decisions**: Capture outcomes to prevent relitigating same issues
9. **Focus on Outcomes**: Better code and better team, not proving who's right
10. **Embrace Uncertainty**: Many technical questions lack objectively right answers
