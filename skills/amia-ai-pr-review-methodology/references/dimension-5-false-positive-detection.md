# Dimension 5: Critical Thinking and False Positive Detection

## Table of Contents

- D5.1 When to apply false positive detection
- D5.2 Assumption identification and verification
- D5.3 Alternative explanation analysis
- D5.4 Placebo effect check methodology
- D5.5 Cargo cult programming detection
- D5.6 Confirmation bias detection
- D5.7 The ultimate test: reversibility verification
- D5.8 Red flags for false positives
- D5.9 Example: A false-positive bug fix with before/after analysis

---

## D5.1 When to apply false positive detection

Apply false positive detection to every PR, but invest the most effort when:

- The PR claims to fix a bug but the root cause explanation is vague
- The fix was found by trial and error rather than systematic debugging
- The author cannot clearly explain the mechanism by which the fix works
- The change modifies behavior in a way that "seems to work" without a clear causal chain
- The PR adds defensive code "just in case" without documenting the specific case

A **false positive fix** is a code change that appears to resolve a problem but does not actually address the root cause. The problem may seem resolved due to coincidence, placebo effect, or test conditions that mask the real issue. False positive fixes are dangerous because they give a false sense of security while leaving the real defect in place.

This is the most critical dimension because it catches issues that the other four dimensions may miss.

---

## D5.2 Assumption identification and verification

Every fix is built on assumptions. The author assumes certain things about the system, the environment, the data, and the behavior. Unverified assumptions are the primary source of false positive fixes.

**How to identify assumptions:**

1. Read the PR description and the code changes.
2. For each change, ask: "What must be true for this change to work?"
3. Write down each assumption explicitly.
4. For each assumption, ask: "Is there evidence that this is true?"

**Example of assumption identification:**

PR change: Add `/opt/tools/v2/bin/mytool` to the search path list.

| Assumption | Evidence Required | Status |
|------------|-------------------|--------|
| The directory `/opt/tools/v2/bin/` exists on target systems | Output of `ls -la /opt/tools/v2/bin/` | UNVERIFIED |
| The tool is installed there by a specific installation method | Documentation of that installation method | UNVERIFIED |
| This path is not already covered by existing search paths | Review of all existing search paths | VERIFIED -- not already present |
| This path should take priority over existing paths (placed first) | Justification for priority order | UNVERIFIED |

**What to ask the author:**

"I have identified the following assumptions in this PR. Can you provide evidence for each one?" Then list the assumptions and required evidence as shown above.

---

## D5.3 Alternative explanation analysis

When a bug "goes away" after a code change, the change may not be the cause. The bug may have resolved due to:

- A different change made at the same time (in the same commit or a concurrent PR)
- A transient environmental condition (network outage, disk full, service restart)
- A timing difference (the fix adds a delay that masks a race condition)
- A test environment change (different OS version, different dependencies, different configuration)

**How to check for alternative explanations:**

1. Ask: "Could the problem have resolved without this change?"
2. Ask: "Were any other changes made at the same time?"
3. Ask: "Is the test environment identical to the production environment where the bug was reported?"
4. Ask: "Could this be a timing issue (race condition, timeout) that appears intermittently?"

**What to ask the author:**

"Can you demonstrate that the problem occurs consistently without your change, and resolves consistently with your change? I want to rule out the possibility that the fix coincided with another change or a transient condition."

---

## D5.4 Placebo effect check methodology

A **placebo fix** is a code change that does not actually affect the execution path of the buggy scenario but appears to fix the problem because the problem was intermittent or self-resolving.

**How to check for placebo effect:**

The placebo effect check requires demonstrating three things:

1. **The old code actually fails.** Run the old code (before the PR) and demonstrate that the bug occurs. If you cannot reproduce the bug with the old code, the fix may be a placebo.

2. **The new code actually succeeds.** Run the new code (with the PR) and demonstrate that the bug does not occur.

3. **The change actually executes in the failing scenario.** Verify that the code path modified by the PR is actually reached during the scenario that triggers the bug. If the modified code path is not reached, the fix cannot have any effect.

**How to verify the code path is reached:**

- Add a log statement or breakpoint in the modified code path.
- Run the failing scenario.
- Confirm the log statement appears or the breakpoint triggers.
- If it does not, the modified code path is not reached, and the fix is a placebo.

**What to ask the author:**

"Can you confirm that the code path you modified is actually executed during the scenario described in the bug report? For example, can you add a log statement to the modified function and show that it appears in the logs when reproducing the bug?"

---

## D5.5 Cargo cult programming detection

**Cargo cult programming** is the practice of including code patterns without understanding why they work. The term comes from Pacific Island cargo cults that built replica airports hoping to attract supply planes -- they replicated the form without understanding the mechanism.

**Signs of cargo cult programming:**

| Sign | Example |
|------|---------|
| Code copied from a forum or Q&A site without understanding | A try-catch block copied from a Stack Overflow answer that catches and silently ignores all exceptions |
| "Just in case" defensive code without a specific case | Adding a null check where the value is never null, "just in case" |
| Patterns that look correct but serve no purpose in context | Using double-checked locking in a single-threaded application |
| Author cannot explain WHY the change works | "I added this and the error went away" without understanding the mechanism |

**How to detect cargo cult programming:**

1. Ask the author: "Can you explain the mechanism by which this change fixes the problem? Not just that it works, but WHY it works."
2. If the explanation is "I found this pattern online and it fixed the issue" or "I'm not sure why it works but it does," this is likely cargo cult programming.
3. Check whether the pattern is appropriate for the specific context (not just generally good practice).

**What to ask the author:**

"I see you added a retry loop around this database call. Can you explain what specific failure mode this addresses? Is there a transient error that can occur here, and if so, what is it? The retry pattern is sometimes used as a general-purpose fix, but it can mask underlying issues if the failure is not actually transient."

---

## D5.6 Confirmation bias detection

**Confirmation bias** in code review occurs when the author (or reviewer) interprets evidence in a way that confirms their existing belief about whether the fix works. The author tested the fix, saw the expected result, and concluded it works -- without testing for failure cases or seeking disconfirming evidence.

**How to detect confirmation bias:**

1. **Check for negative testing.** Did the author test scenarios where the fix should NOT change behavior? If the fix only changes behavior in the target scenario but the author only tested the target scenario, they have not ruled out unintended side effects.

2. **Check for independent verification.** Did someone other than the author verify the fix? The author has a psychological investment in the fix working.

3. **Check for mechanism explanation.** Can the author explain the causal chain from the change to the result, or only report the result? Explaining the mechanism forces explicit reasoning that can be evaluated.

**What to ask the author:**

"Can you show a test where the fix is applied but the behavior should NOT change? For example, if this fix changes path resolution, can you show that paths that were already resolving correctly still resolve correctly after the fix?"

---

## D5.7 The ultimate test: reversibility verification

This is the single most powerful technique for detecting false positive fixes.

**THE ULTIMATE TEST:** "If we remove this change, can you demonstrate that the problem returns?"

This test works because:

- If the problem returns when the change is removed, the change is causal (it actually fixes the problem).
- If the problem does NOT return when the change is removed, the change is not causal (something else fixed the problem, or the problem was intermittent).

**How to apply the reversibility test:**

1. Start from the branch with the fix applied.
2. Revert only the PR's changes (keep everything else the same).
3. Run the exact same test that demonstrated the fix working.
4. If the problem returns: The fix is likely genuine.
5. If the problem does NOT return: The fix is a false positive. Something else resolved the problem.

**What to ask the author:**

"Can you revert your changes on your branch and demonstrate that the original problem returns? This is the strongest evidence that the fix is causal rather than coincidental."

**When the author cannot perform the reversibility test:**

If the original problem was reported by a user and the author cannot reproduce it even without the fix, this is a strong signal that:
- The problem may have been caused by a transient condition
- The problem may have been fixed by a different change
- The author's environment may differ from the reporter's environment

In any of these cases, the fix cannot be validated and should not be merged without additional evidence.

---

## D5.8 Red flags for false positives

These patterns are strong indicators that a fix may be a false positive:

| Red Flag | Why It Matters |
|----------|---------------|
| Author cannot explain WHY the fix works, only that tests pass | Understanding the mechanism is essential to verify the fix is genuine |
| No before/after comparison provided | Without demonstrating the problem exists before and is gone after, the fix is unverified |
| Fix is based on assumptions about system behavior (not evidence) | Assumptions may be incorrect, making the fix coincidental |
| Author becomes defensive when asked to verify assumptions | Resistance to verification is a warning sign that the fix may not hold up under scrutiny |
| "It works for me" without a reproducible test case | The fix may only work in the author's specific environment |
| Fix was discovered by trial and error, not systematic debugging | Trial-and-error fixes often address symptoms or coincidences, not root causes |
| The problem is intermittent and the fix has only been tested once | A single successful test of an intermittent problem proves nothing |
| Multiple changes bundled together, making it unclear which one fixed the problem | The actual fix may be a different change in the same PR |

---

## D5.9 Example: A false-positive bug fix with before/after analysis

**Scenario:** A user reports that a CLI tool crashes with "FileNotFoundError" when run after a fresh installation. A developer submits a PR claiming to fix the issue.

**PR description:** "Fixed FileNotFoundError by adding the path `/usr/share/local/mytool/config.yaml` to the config search list."

**PR diff:**

```python
 CONFIG_SEARCH_PATHS = [
+    "/usr/share/local/mytool/config.yaml",  # Fix for FileNotFoundError
     "/etc/mytool/config.yaml",
     os.path.expanduser("~/.config/mytool/config.yaml"),
 ]
```

**Analysis using the 5 dimensions:**

**Dimension 1 (Problem Verification):**
- The exact error is identified: `FileNotFoundError: [Errno 2] No such file or directory: '/etc/mytool/config.yaml'`
- Root cause analysis: The tool expects a config file at `/etc/mytool/config.yaml`, but after a fresh pip install, this file does not exist.
- PROBLEM: The new path `/usr/share/local/mytool/config.yaml` also does not exist after a fresh pip install. The fix adds a path that is equally nonexistent.

**Dimension 2 (Redundancy):**
- The existing path `~/.config/mytool/config.yaml` is the user-level config location. If the tool created a default config here during first run, the problem would be solved.
- The PR adds a new path instead of fixing the initialization code.

**Dimension 3 (System Integration):**
- `/usr/share/local/` is not a standard directory path. The FreeDesktop standard uses `/usr/local/share/` (note the different order). This path likely does not exist on any system.

**Dimension 5 (False Positive Detection):**
- **Reversibility test:** If we remove the new path, the error still occurs. But if we add the path, the error STILL occurs because `/usr/share/local/mytool/config.yaml` does not exist either.
- **Why did the author think it worked?** The author likely tested by also manually creating the config file at the new path. The fix was not the path addition -- it was the manual file creation.
- **The actual fix:** The tool should create a default config file at `~/.config/mytool/config.yaml` on first run if no config file exists.

**Review response:**

"This change adds `/usr/share/local/mytool/config.yaml` to the config search paths, but this path does not exist after a standard installation either. The directory `/usr/share/local/` does not follow the FreeDesktop standard (which uses `/usr/local/share/`).

The root cause is that no config file exists after a fresh installation. Adding another non-existent path to the search list does not fix this. The fix should be to create a default configuration file at `~/.config/mytool/config.yaml` during first run.

Can you verify:
1. Run `ls -la /usr/share/local/mytool/config.yaml` -- does this path exist?
2. Revert your change, then run the tool -- does the error still occur?
3. With your change, but without manually creating any config file -- does the error still occur?

I suspect the error resolved during your testing because you manually created a config file, not because of the path addition."
