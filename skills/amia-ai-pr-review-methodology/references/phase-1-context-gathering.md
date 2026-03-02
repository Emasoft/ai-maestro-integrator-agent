# Phase 1: Context Gathering

## Table of Contents

- 1.1 When to perform context gathering
- 1.2 Action 1: Read complete files, not just diffs
  - 1.2.1 How to read complete files during a PR review
  - 1.2.2 Example: Good vs bad context gathering
- 1.3 Action 2: Search for existing solutions and duplicates
  - 1.3.1 How to search for duplicates before analyzing a PR
  - 1.3.2 Example: Discovering an existing solution
- 1.4 Action 3: Understand the problem (root cause vs symptoms)
  - 1.4.1 How to distinguish root cause from symptoms
  - 1.4.2 Example: Symptom-level vs root-cause understanding
- 1.5 Action 4: Verify all claims made in the PR
  - 1.5.1 How to verify file path claims
  - 1.5.2 How to verify command availability claims
  - 1.5.3 Example: Verifying a claimed installation path
- 1.6 Completion checkpoint for Phase 1

---

## 1.1 When to perform context gathering

Context gathering is the mandatory first phase of every PR review. You must complete all four actions in this phase before moving to Phase 2 (Structured Analysis). Skipping context gathering is the primary cause of inaccurate reviews, because reviewers who only read the diff will miss existing solutions, misunderstand the problem, and accept unverified claims.

Context gathering is required regardless of the size of the PR. Even a single-line change can introduce a false positive if the reviewer does not understand the surrounding code.

---

## 1.2 Action 1: Read complete files, not just diffs

A diff shows you what changed. It does not show you what already exists. To review a PR accurately, you must read the complete current version of every modified file.

### 1.2.1 How to read complete files during a PR review

For each file modified in the PR:

1. Fetch the **entire current version** of the file (the version on the base branch before the PR changes).
2. Read through the file to understand its existing logic, architecture, and patterns.
3. Note any related functions, similar patterns, or existing solutions that handle the same case the PR is trying to address.
4. Then read the diff to understand what the PR changes.

If the PR modifies more than 10 files, prioritize reading complete files for:
- Files containing the core logic change (not just configuration or formatting)
- Files that handle paths, commands, or system integration (these are high-risk for false positives)
- Files with security-sensitive code (authentication, authorization, input handling)

### 1.2.2 Example: Good vs bad context gathering

**Bad context gathering (diff-only):**

The reviewer sees a diff adding a new path `/opt/tools/myapp` to a search list. The diff looks reasonable. The reviewer approves.

What the reviewer missed: The complete file already contains `/usr/local/bin/myapp` and `/usr/bin/myapp`, both of which cover the same installation scenario. The new path is redundant.

**Good context gathering (complete file):**

The reviewer reads the entire file first. They see the existing search paths. When they read the diff, they immediately notice that the new path duplicates existing coverage. They ask the author: "The existing paths `/usr/local/bin/myapp` and `/usr/bin/myapp` already cover standard installation locations. Why is `/opt/tools/myapp` needed? Can you provide evidence that this path exists on a system where the existing paths do not?"

---

## 1.3 Action 2: Search for existing solutions and duplicates

Before analyzing the PR's approach, search the codebase for existing code that might already handle the same case.

### 1.3.1 How to search for duplicates before analyzing a PR

1. Identify the problem the PR is trying to solve (from the PR description, linked issue, or commit messages).
2. Search the codebase for keywords related to that problem:
   - Search for function names, error messages, or configuration keys mentioned in the PR.
   - Search for similar patterns (for example, if the PR adds a path, search for all places where paths are defined or searched).
   - Search for the specific file paths, URLs, or identifiers being added or modified.
3. Check if any existing code already handles the case:
   - Does an existing function already do what the new code does?
   - Does an existing configuration option already cover this scenario?
   - Is there a utility or helper that the author might not be aware of?

### 1.3.2 Example: Discovering an existing solution

A PR adds a new function `validate_email_format(email)` that uses a regular expression to check whether a string is a valid email address.

**Search result:** The codebase already contains a utility module `utils/validators.py` with a function `is_valid_email(value)` that performs the same validation using the same regular expression pattern.

**Review action:** Ask the author: "The existing function `is_valid_email` in `utils/validators.py` (line 42) appears to perform the same validation. Can you explain why a new function is needed instead of using the existing one?"

---

## 1.4 Action 3: Understand the problem (root cause vs symptoms)

Read the original issue or bug report linked in the PR. Identify the exact error, symptom, or requirement. Determine whether the PR addresses the root cause or merely suppresses a symptom.

### 1.4.1 How to distinguish root cause from symptoms

A **symptom** is the visible effect of a problem. Example: "The application crashes when the user clicks Save."

A **root cause** is the underlying defect that produces the symptom. Example: "The save handler tries to write to a file descriptor that was closed by a previous operation."

To distinguish them:

1. Ask "Why does this happen?" repeatedly until you reach a cause that cannot be decomposed further.
2. Check whether the proposed fix prevents the symptom or eliminates the cause.
   - Preventing the symptom: Adding a try-catch around the save handler to silently ignore the error. The crash stops, but the file descriptor is still being closed prematurely, which may cause data loss.
   - Eliminating the cause: Fixing the code that prematurely closes the file descriptor. The crash stops because the descriptor is now available when the save handler needs it.

### 1.4.2 Example: Symptom-level vs root-cause understanding

**Symptom-level PR description:** "Fixed crash in save handler by adding error handling."

**Root-cause PR description:** "Fixed premature file descriptor closure in `connection_pool.release()` that caused `save_handler.write()` to fail with `EBADF`. The connection pool was releasing descriptors before all pending writes completed. Added a reference count to track active writers."

The second description demonstrates understanding of the root cause. The first suggests the fix may be treating symptoms.

---

## 1.5 Action 4: Verify all claims made in the PR

Every PR makes implicit and explicit claims. Explicit claims are statements in the PR description ("This path is the default installation location"). Implicit claims are assumptions in the code ("This command will be available on all target systems"). Both must be verified.

### 1.5.1 How to verify file path claims

When a PR references a file path (for example, `/usr/local/lib/myapp/config.json`):

1. Check the official documentation for the software or tool to confirm this is the correct path.
2. If possible, verify the path exists on target systems by requesting the author to run:
   ```
   ls -la /usr/local/lib/myapp/config.json
   ```
3. Check whether the path varies by platform (macOS vs Linux vs Windows) and whether the PR handles platform differences.
4. Check whether the path depends on the installation method (package manager vs manual install vs containerized) and whether the PR accounts for this variation.

### 1.5.2 How to verify command availability claims

When a PR assumes a command or binary is available (for example, calls `jq` to parse JSON):

1. Check whether the command is a standard system utility or requires separate installation.
2. If it requires installation, check whether the project documents this as a dependency.
3. Verify the command is available on all supported platforms.
4. Request the author to provide output of `which <command>` or `type <command>` on each supported platform.

### 1.5.3 Example: Verifying a claimed installation path

A PR adds `/opt/homebrew/bin/mytool` to a search path list, claiming this is where Homebrew installs `mytool` on Apple Silicon Macs.

**Verification steps:**

1. Check Homebrew documentation: Homebrew on Apple Silicon uses prefix `/opt/homebrew/`, so binaries go in `/opt/homebrew/bin/`. This is correct.
2. Check Homebrew on Intel Macs: Homebrew uses prefix `/usr/local/`, so the binary would be at `/usr/local/bin/mytool`. The PR should handle both architectures.
3. Request evidence: "Can you provide output of `which mytool` on an Apple Silicon Mac with Homebrew-installed mytool?"
4. Check the existing search path list: Does it already include `/usr/local/bin/` (which would cover Intel Macs)?

---

## 1.6 Completion checkpoint for Phase 1

Before proceeding to Phase 2, confirm you have completed all four actions:

| Action | Status | Notes |
|--------|--------|-------|
| 1. Read complete files (not just diffs) | DONE / NOT DONE | List which files you read in full |
| 2. Search for duplicates and existing solutions | DONE / NOT DONE | List search queries used and results |
| 3. Understand the problem (root cause identified) | DONE / NOT DONE | State the root cause in one sentence |
| 4. Verify all claims (paths, commands, assumptions) | DONE / NOT DONE | List each claim and its verification status |

If any action is NOT DONE, complete it before proceeding. If you cannot complete an action because the information is not available (for example, you cannot verify a path because you lack access to the target system), record this as a required evidence item for Phase 3.
