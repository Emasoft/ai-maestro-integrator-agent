# Commit Conventions Reference

## Table of Contents

- 1.1 Writing descriptive commit messages with WHAT and WHY sections
  - 1.1.1 Commit message structure and required sections
  - 1.1.2 Documenting file changes (ADDED, MODIFIED, REMOVED, RENAMED)
  - 1.1.3 Documenting symbol changes (functions, classes, variables)
  - 1.1.4 Documenting configuration changes
- 1.2 Choosing the correct commit category prefix
  - 1.2.1 Category prefix reference table
  - 1.2.2 When to use each category
- 1.3 Making commits searchable for future decision archaeology
  - 1.3.1 Search scenarios and requirements
  - 1.3.2 Indexing best practices
- 1.4 Managing dual-git repositories (project vs design)
  - 1.4.1 When to commit to project git
  - 1.4.2 When to commit to design git
  - 1.4.3 Setting up dual-git configuration
- 1.5 Documenting removals and renames with supersedes information
  - 1.5.1 Supersedes section format
  - 1.5.2 Migration instructions
  - 1.5.3 Breaking change indicators

---

## 1.1 Writing Descriptive Commit Messages with WHAT and WHY Sections

### 1.1.1 Commit Message Structure and Required Sections

Every commit message must follow this structure:

```
[CATEGORY] Brief summary (max 72 chars)

## WHAT Changed

### Files
[File-level changes]

### Symbols (if applicable)
[Code symbol changes]

### Configurations (if applicable)
[Configuration changes]

## WHY Changed

### Rationale
[Detailed explanation of why these changes were necessary]

### Decision Context
- Problem: [What problem prompted this change]
- Alternatives considered: [Other approaches evaluated]
- Why this approach: [Justification for chosen solution]

### Supersedes (if removal/rename)
- Replaced by: [New file/symbol that takes over responsibility]
- Migration: [How existing references should be updated]
- Breaking: [Yes/No - whether this breaks existing functionality]

### Related
- Issues: #123, #456
- PRs: #789
- Decisions: ADR-042

---
Committed by: Integrator Agent (committer agent)
Timestamp: [ISO 8601]
```

**Required sections:**

- Brief summary line with category prefix (max 72 characters)
- `## WHAT Changed` section
- `## WHY Changed` section with rationale
- Footer with committer attribution and timestamp

**Optional sections** (include when applicable):

- `### Symbols` - for code changes
- `### Configurations` - for config/env changes
- `### Supersedes` - for removals and renames
- `### Related` - for issues, PRs, ADRs

### 1.1.2 Documenting File Changes (ADDED, MODIFIED, REMOVED, RENAMED)

Use these exact prefixes in the `### Files` section:

```
### Files
- ADDED: path/to/new-file.md
- MODIFIED: path/to/existing-file.md (lines 45-67)
- REMOVED: path/to/obsolete-file.md
- RENAMED: old-name.md → new-name.md
```

**Rules:**

- Always use **full paths** from project root
- For MODIFIED files, include line ranges when practical
- For RENAMED files, use the arrow notation: `old-name → new-name`
- List files in order: ADDED first, then MODIFIED, then REMOVED, then RENAMED

### 1.1.3 Documenting Symbol Changes (Functions, Classes, Variables)

For code changes, add a `### Symbols` section:

```
### Symbols
- ADDED: function `calculateTotalPrice(items: Item[], discount: Discount): Price`
- MODIFIED: class `UserAuthenticator.validateToken()` - added expiry check
- REMOVED: constant `LEGACY_API_ENDPOINT` (superseded by `API_V2_ENDPOINT`)
- RENAMED: `processOrder` → `processOrderAsync`
```

**Rules:**

- Use **fully qualified symbol names** (class.method, module.function)
- Include type signatures for functions when available
- Add brief explanation for MODIFIED symbols (what aspect changed)
- For REMOVED symbols, include what supersedes them in parentheses
- Use backticks for all symbol names

### 1.1.4 Documenting Configuration Changes

For configuration or environment variable changes, add a `### Configurations` section:

```
### Configurations
- MODIFIED: config.yaml `database.pool_size`: 10 → 25
- ADDED: env var `CACHE_TTL_SECONDS`
- REMOVED: env var `DEPRECATED_FLAG`
```

**Rules:**

- Use the format: `file.path.to.key`: `old_value` → `new_value`
- For env vars, prefix with "env var"
- Use backticks for config keys and values

---

## 1.2 Choosing the Correct Commit Category Prefix

### 1.2.1 Category Prefix Reference Table

| Category | Prefix | When to Use |
|----------|--------|-------------|
| Architecture | `[ARCH]` | Structural changes, new patterns |
| Feature | `[FEAT]` | New functionality |
| Fix | `[FIX]` | Bug fixes |
| Refactor | `[REFACTOR]` | Code restructuring without behavior change |
| Docs | `[DOCS]` | Documentation updates |
| Spec | `[SPEC]` | Module specification changes |
| Decision | `[ADR]` | Architecture Decision Records |
| Remove | `[REMOVE]` | Intentional removal of files/features |
| Rename | `[RENAME]` | File or symbol renaming |
| Config | `[CONFIG]` | Configuration changes |
| Memory | `[MEMORY]` | Integrator memory file updates |

### 1.2.2 When to Use Each Category

**[ARCH]** - Use when:

- Introducing new architectural patterns
- Restructuring module boundaries
- Changing system-wide conventions
- Modifying the overall project structure

**[FEAT]** - Use when:

- Adding new user-facing functionality
- Implementing new API endpoints
- Creating new modules or services
- Adding new capabilities to existing features

**[FIX]** - Use when:

- Correcting bugs in existing code
- Fixing broken tests
- Resolving runtime errors
- Patching security vulnerabilities

**[REFACTOR]** - Use when:

- Reorganizing code without changing behavior
- Improving code readability or maintainability
- Extracting functions or classes
- Renaming internal symbols (use [RENAME] if user-visible)

**[DOCS]** - Use when:

- Updating README files
- Modifying code comments
- Changing API documentation
- Updating developer guides

**[SPEC]** - Use when:

- Creating module specifications
- Updating design documents
- Modifying requirements
- Changing specification templates

**[ADR]** - Use when:

- Recording architecture decisions
- Updating existing ADRs
- Documenting significant technical choices

**[REMOVE]** - Use when:

- Intentionally deleting files or features
- Removing deprecated functionality
- Cleaning up obsolete code

**[RENAME]** - Use when:

- Renaming files, classes, or functions
- Changing API endpoint names
- Modifying user-visible identifiers

**[CONFIG]** - Use when:

- Changing configuration files
- Modifying environment variables
- Updating build settings
- Changing CI/CD configurations

**[MEMORY]** - Use when:

- Updating integrator memory files
- Modifying progress tracking
- Changing session state

---

## 1.3 Making Commits Searchable for Future Decision Archaeology

### 1.3.1 Search Scenarios and Requirements

The commit message MUST enable finding answers to these questions using `git log --all --grep`:

**1. "Why was file X removed?"**

- Search command: `git log --all --grep="REMOVED: path/to/X"`
- Must find: Rationale and what superseded it
- Requirements: Full path, supersedes information

**2. "When was function Y renamed?"**

- Search command: `git log --all --grep="RENAMED:.*Y"`
- Must find: Old name, new name, and why
- Requirements: Both old and new names in commit

**3. "What decision led to removing constant Z?"**

- Search command: `git log --all --grep="Z"`
- Must find: Decision context and alternatives considered
- Requirements: Full symbol name, decision context section

**4. "What files were affected by ADR-042?"**

- Search command: `git log --all --grep="ADR-042"`
- Must find: All commits referencing that decision
- Requirements: ADR number in Related section

### 1.3.2 Indexing Best Practices

Follow these practices to ensure commits are searchable:

1. **Always use full paths** from project root
   - ✓ GOOD: `src/services/auth/validator.py`
   - ✗ BAD: `validator.py`

2. **Always use fully qualified symbol names**
   - ✓ GOOD: `UserAuthenticator.validateToken()`
   - ✗ BAD: `validateToken()`

3. **Always include both old and new names for renames**
   - ✓ GOOD: `RENAMED: processOrder → processOrderAsync`
   - ✗ BAD: `RENAMED: to processOrderAsync`

4. **Always tag with issue numbers when applicable**
   - ✓ GOOD: `Issues: #123, #456`
   - ✗ BAD: Omitting issue references

5. **Always include supersedes information for removals**
   - ✓ GOOD: `Replaced by: templates/new-template.md`
   - ✗ BAD: Deleting without explaining replacement

6. **Use consistent prefixes**
   - Always use: ADDED, MODIFIED, REMOVED, RENAMED
   - Never use: Created, Changed, Deleted, Moved

---

## 1.4 Managing Dual-Git Repositories (Project vs Design)

### 1.4.1 When to Commit to Project Git

Commit to **project git** (public repository) for:

- Source code changes
- Test changes
- Public documentation (README, CONTRIBUTING, LICENSE)
- CI/CD configurations
- Build scripts
- Public API documentation

**Location:** Project root `.git/`

**Command:**

```bash
cd /project-root
git add [staged files]
git commit -m "[message]"
```

**Verification:**

```bash
# Verify project git exists
[ -d "/project-root/.git" ] || echo "ERROR: Project git not initialized"
```

### 1.4.2 When to Commit to Design Git

Commit to **design git** (private repository) for:

- Architecture plans
- Module specifications
- Design decisions (ADRs)
- Internal templates
- Sensitive requirements
- Integrator memory files (if configured)
- Planning documents

**Location:** `/project-root/.design/.git/` or configured path

**Command:**

```bash
cd /project-root/.design
git add [staged files]
git commit -m "[message]"
```

**Verification:**

```bash
# Verify design git exists
[ -d "/project-root/.design/.git" ] || echo "ERROR: Design git not initialized"
```

### 1.4.3 Setting Up Dual-Git Configuration

**Initial setup (one-time):**

```bash
# 1. Ensure project git exists
cd /project-root
git status || git init

# 2. Create design git directory
mkdir -p .design

# 3. Initialize design git
cd .design
git init

# 4. Add .design to project gitignore
cd /project-root
echo ".design/" >> .gitignore
git add .gitignore
git commit -m "[CONFIG] Add .design/ to gitignore for private design docs"

# 5. Create design git structure
cd .design
mkdir -p specs plans decisions templates exports
touch .gitkeep
git add .
git commit -m "[INIT] Initialize private design documentation repository"
```

**Verification:**

```bash
# Verify dual-git setup
echo "=== Project Git ===" && git -C /project-root log --oneline -3
echo "=== Design Git ===" && git -C /project-root/.design log --oneline -3
```

---

## 1.5 Documenting Removals and Renames with Supersedes Information

### 1.5.1 Supersedes Section Format

When removing or renaming files or symbols, ALWAYS include a `### Supersedes` section:

```
### Supersedes
- Replaced by: [New file/symbol that takes over responsibility]
- Migration: [How existing references should be updated]
- Breaking: [Yes/No - whether this breaks existing functionality]
```

**Required fields:**

- `Replaced by:` - What new element supersedes the removed one
- `Migration:` - Instructions for updating references
- `Breaking:` - Whether this change breaks existing functionality

### 1.5.2 Migration Instructions

Provide clear, actionable migration guidance:

**For file removals:**

```
Migration: All references should use module-spec-template.md
```

**For symbol renames:**

```
Migration: Update all imports: from `old_module` to `new_module`
```

**For configuration changes:**

```
Migration: Update config.yaml: replace `old_key` with `new_key` (value format unchanged)
```

**For feature removals:**

```
Migration: Use new API endpoint /v2/users instead of deprecated /users
```

### 1.5.3 Breaking Change Indicators

Always explicitly state whether a change is breaking:

**Non-breaking removal:**

```
Breaking: No - no active workflows depend on this template
```

**Breaking removal:**

```
Breaking: Yes - existing imports will fail; requires code changes in all dependent modules
```

**Non-breaking rename:**

```
Breaking: No - old function name maintained as alias for backward compatibility
```

**Breaking rename:**

```
Breaking: Yes - old function name removed; all callers must update
```

---

## IRON RULES for Commit Conventions

1. **Every commit has WHY** - Never commit without rationale in the WHY section
2. **Full names always** - No abbreviations for files, symbols, configs; use full paths and qualified names
3. **Supersedes documented** - Every removal/rename explains what replaces it with migration instructions
4. **Searchable format** - Use consistent prefixes (ADDED, REMOVED, RENAMED, MODIFIED) for git log grep
5. **Target git explicit** - Always specify and verify project vs design git before committing
6. **No silent changes** - If it changed, it's documented in the commit message with WHAT and WHY

---

## Example Commit Messages

### Example 1: Removing Obsolete Template

```
[REMOVE] Remove deprecated implementation-spec-template.md

## WHAT Changed

### Files
- REMOVED: templates/implementation-spec-template.md

## WHY Changed

### Rationale
The implementation-spec-template.md was created during early prototyping but
was superseded by the more comprehensive module-spec-template.md which includes
TDD requirements, acceptance criteria, and API contract sections.

### Decision Context
- Problem: Multiple templates with overlapping purposes caused confusion
- Alternatives considered: Merge templates, keep both with clear separation
- Why this approach: module-spec-template.md covers all use cases; keeping both
  creates maintenance burden and inconsistency risk

### Supersedes
- Replaced by: templates/module-spec-template.md
- Migration: All references should use module-spec-template.md
- Breaking: No - no active workflows depend on this template

### Related
- Issues: #234
- Decisions: ADR-015 (Template Consolidation)

---
Committed by: Integrator Agent (committer agent)
Timestamp: 2025-01-08T14:32:00Z
```

### Example 2: Adding New Agent

```
[FEAT] Add experimenter agent for hypothesis validation

## WHAT Changed

### Files
- ADDED: agents/experimenter.md
- MODIFIED: agents/amia-router.md (lines 145-152) - added experimenter to agent list
- MODIFIED: skills/amia-router/references/agent-invocation.md (lines 613-660) - added invocation docs

### Symbols
- ADDED: agent definition `experimenter` with role "experimental validation"
- MODIFIED: `amia-router` agent list - added `experimenter` entry

## WHY Changed

### Rationale
The orchestrator needed a way to validate hypotheses through controlled
experimentation before committing to implementation approaches. The experimenter
agent fills this gap by running isolated Docker-based experiments.

### Decision Context
- Problem: No mechanism to test multiple approaches before choosing one
- Alternatives considered:
  1. Let remote agents experiment (rejected: violates separation of concerns)
  2. Orchestrator experiments directly (rejected: violates no-code rule)
  3. Dedicated experimenter agent (chosen: clean separation, ephemeral code)
- Why this approach: Maintains orchestrator's no-code constraint while enabling validation

### Related
- Issues: #567
- Decisions: ADR-023 (Experimentation Strategy)

---
Committed by: Integrator Agent (committer agent)
Timestamp: 2025-01-08T15:45:00Z
```

### Example 3: Renaming Symbol

```
[RENAME] Rename sync-coordinator to planner in workflow examples

## WHAT Changed

### Files
- MODIFIED: skills/amia-router/references/core-concepts.md (line 119)

### Symbols
- RENAMED: agent reference `sync-coordinator` → `planner`
  - Context: SYNC workflow example, agent invocation step
  - Reason: sync-coordinator was a planned but never implemented agent

## WHY Changed

### Rationale
The SYNC workflow example referenced `sync-coordinator` which was planned during
initial design but never implemented. The `planner` agent handles synchronization
architecture design, making it the correct agent for this workflow step.

### Decision Context
- Problem: Reference to non-existent agent `sync-coordinator` in documentation
- Alternatives considered:
  1. Create sync-coordinator agent (rejected: planner already covers this)
  2. Remove the example entirely (rejected: example is useful)
  3. Update to use existing planner (chosen: accurate and complete)
- Why this approach: planner's architecture design capabilities include sync patterns

### Supersedes
- `sync-coordinator` was never implemented
- All sync-related orchestration uses `planner` agent

### Related
- Issues: #891 (Audit: non-existent agent references)

---
Committed by: Integrator Agent (committer agent)
Timestamp: 2025-01-08T16:20:00Z
```
