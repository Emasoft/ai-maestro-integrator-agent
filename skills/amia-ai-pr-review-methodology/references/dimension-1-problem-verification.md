# Dimension 1: Problem Verification

## Table of Contents

- D1.1 When to apply problem verification
- D1.2 Identifying the exact error message or unexpected behavior
- D1.3 Determining root cause vs treating symptoms
- D1.4 Verifying the fix addresses the root cause
- D1.5 Documenting assumptions about the system and environment
- D1.6 Testing methodology: before/after, multi-platform, edge cases, automated tests
- D1.7 Red flags that indicate problem verification failure
- D1.8 Example: A fix that treats symptoms vs one that addresses root cause

---

## D1.1 When to apply problem verification

Apply problem verification to every PR that claims to fix a bug, resolve an error, or change behavior to address a reported issue. This dimension answers the fundamental question: "Does this PR actually solve the problem it claims to solve?"

Problem verification is also relevant for feature PRs if they include code changes justified by a specific problem statement ("Users reported that X does not work, so we are adding Y").

---

## D1.2 Identifying the exact error message or unexpected behavior

The first step is to identify exactly what is broken. Vague problem descriptions ("it doesn't work", "something is broken", "users are confused") are insufficient. You need specifics.

**Checklist:**

- [ ] The exact error message or exception is stated (including the full stack trace if applicable)
- [ ] The unexpected behavior is described precisely (what happens vs what should happen)
- [ ] The conditions under which the error occurs are specified (which platform, which version, which configuration, which user action triggers it)

**What to ask the author if the problem is not clearly defined:**

"Can you provide the exact error message or stack trace? What specific user action triggers this behavior? On which platform and version does it occur?"

**Example of a well-defined problem:**

```
Error: FileNotFoundError: [Errno 2] No such file or directory: '/var/lib/myapp/config.yaml'
Occurs on: Ubuntu 22.04, when myapp is installed via apt
Trigger: Running `myapp init` for the first time after installation
Expected: The init command should create the config file if it does not exist
Actual: The init command assumes the parent directory exists and crashes
```

**Example of a poorly-defined problem:**

```
The config file doesn't work sometimes. Fixed by adding a check.
```

---

## D1.3 Determining root cause vs treating symptoms

A symptom is the visible result of a defect. The root cause is the defect itself. A good fix eliminates the root cause. A bad fix suppresses the symptom while leaving the root cause in place.

**How to determine if a fix addresses root cause:**

1. State the symptom in one sentence.
2. Ask "Why does this happen?" and answer it. This gives you the next level of cause.
3. Repeat step 2 until you reach a cause that is directly in the code under the author's control.
4. Check whether the PR modifies the code at that deepest level, or at a higher level.

**Example of the "5 Whys" technique:**

| Level | Question | Answer |
|-------|----------|--------|
| Symptom | What happens? | Application crashes with FileNotFoundError |
| Why 1 | Why does it crash? | Because `/var/lib/myapp/` directory does not exist |
| Why 2 | Why does the directory not exist? | Because the apt package does not create it during installation |
| Why 3 | Why does apt not create it? | Because the postinstall script is missing the `mkdir -p` command |
| Root cause | What is the defect? | The postinstall script omits directory creation |

- **Symptom-level fix:** Add a try-catch in `myapp init` to handle the missing directory. This suppresses the crash but the directory is still missing, which may affect other commands.
- **Root-cause fix:** Add `mkdir -p /var/lib/myapp/` to the postinstall script. The directory now exists after installation, and `myapp init` works correctly.

---

## D1.4 Verifying the fix addresses the root cause

Once you have identified the root cause (section D1.3), verify that the PR's changes directly address it.

**Checklist:**

- [ ] The fix modifies the code at the root cause level (not just the symptom level)
- [ ] The mechanism of the fix is clear (you can explain why this change eliminates the root cause)
- [ ] There are no missing steps in the solution (the fix is complete)
- [ ] The fix does not introduce new problems (side effects are considered)

**What to ask the author if the fix seems to target symptoms:**

"I see this change adds error handling around the crash site. Can you explain why the underlying condition (missing directory) occurs and whether this fix prevents it, or just catches the error after it happens?"

---

## D1.5 Documenting assumptions about the system and environment

Every fix makes assumptions about the environment in which it will run. These assumptions must be explicit and verified.

**Common assumptions to check:**

| Assumption Type | Example | How to Verify |
|----------------|---------|---------------|
| File exists at a specific path | "The config file is at `/etc/myapp/config.yaml`" | Request `ls -la /etc/myapp/config.yaml` output |
| Command is available | "We can use `jq` to parse JSON" | Request `which jq` output on target systems |
| Directory has write permissions | "The application can write to `/var/log/myapp/`" | Request `ls -ld /var/log/myapp/` output |
| Environment variable is set | "HOME is always defined" | Check if this is true in containerized or CI environments |
| Operating system version | "systemd is available" | Verify minimum OS version requirement |

**Checklist:**

- [ ] All assumptions are explicitly stated in the PR description
- [ ] Each assumption has been verified on the target system(s)
- [ ] Edge cases where assumptions might be false are considered

---

## D1.6 Testing methodology: before/after, multi-platform, edge cases, automated tests

A fix is only validated when you can demonstrate:

1. **Before the fix:** The problem occurs (the error happens, the test fails, the behavior is incorrect).
2. **After the fix:** The problem does not occur (the error is gone, the test passes, the behavior is correct).
3. **Edge cases:** The fix handles unusual inputs, boundary conditions, and failure modes.
4. **Multiple platforms:** The fix works on all supported operating systems and configurations.
5. **Automated tests:** A test has been added that would fail without the fix and passes with it (this prevents regressions).

**Checklist:**

- [ ] Before/after demonstration provided (showing the problem occurs without the fix and does not occur with it)
- [ ] Tested on multiple platforms/environments (or platform differences are documented as known limitations)
- [ ] Edge cases and failure modes tested
- [ ] Automated regression test added to the test suite

**What to ask the author if testing is insufficient:**

"Can you demonstrate the error occurring on the base branch (before your change) and then show it resolved on your branch (after your change)? Additionally, have you added a test that would catch this regression if the fix were accidentally reverted?"

---

## D1.7 Red flags that indicate problem verification failure

These patterns strongly suggest the fix has not been properly verified. If you observe any of these, flag them as blocking issues:

| Red Flag | Why It Matters |
|----------|---------------|
| Vague problem description ("doesn't work", "broken", "weird behavior") | Without a specific problem definition, you cannot verify the fix addresses it |
| Solution proposed without an identified root cause | If the author does not know why the problem occurs, the fix is based on speculation |
| Testing covers only the happy path (no failure mode testing) | The fix may work in the common case but fail in edge cases |
| Fix is based on assumptions not verified with evidence | Assumptions may be wrong, making the fix ineffective or harmful |
| No before/after demonstration | Without this, there is no proof the fix actually resolves the problem |
| "It works on my machine" as the only evidence | The fix may not work on other systems, configurations, or environments |

---

## D1.8 Example: A fix that treats symptoms vs one that addresses root cause

**Scenario:** A web application crashes with "connection refused" when trying to send emails.

**Symptom-level fix (bad):**

```python
# Before
def send_email(to, subject, body):
    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    smtp.send_message(msg)

# After (symptom-level fix)
def send_email(to, subject, body):
    try:
        smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        smtp.send_message(msg)
    except ConnectionRefusedError:
        logger.warning("Email sending failed, skipping")
        return False
```

This fix catches the exception and logs a warning. But emails are still not being sent. The root cause is unaddressed.

**Root-cause fix (good):**

Investigation reveals that `SMTP_HOST` is set to `localhost` in production, but the SMTP service runs on a different host (`mail.internal.example.com`). The configuration was correct in development but wrong in production.

```python
# Fix: Correct the configuration source
# The SMTP host must come from the environment-specific configuration,
# not from a hardcoded default that only works in development.
SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
```

Combined with updating the production configuration:

```
# production.env
SMTP_HOST=mail.internal.example.com
```

This fix addresses the root cause (incorrect SMTP host in production) and includes a sensible default for development.

**What a good reviewer would ask about the symptom-level fix:** "This catch block prevents the crash, but emails are still not sent. What is causing the connection refusal? Is the SMTP service running? Is the host configuration correct for all environments?"
