# Scenario Protocol: Path and File Changes

## Table of Contents

- S-PATH.1 When to use this scenario protocol
- S-PATH.2 Mandatory verification steps for path changes
- S-PATH.3 Verification commands to request from the author
- S-PATH.4 Evidence requirements specific to path changes
- S-PATH.5 Example: Reviewing a PR that adds a new binary search path

---

## S-PATH.1 When to use this scenario protocol

Use this protocol when the PR modifies file paths, installation detection logic, or filesystem operations. Specific triggers include:

- Adding, removing, or reordering paths in a search list
- Changing file read/write locations
- Modifying installation detection logic (checking where a binary is installed)
- Adding platform-specific path handling
- Changing how paths are constructed (concatenation, environment variable expansion, template substitution)

This protocol supplements the standard 5-dimension analysis with path-specific verification steps.

---

## S-PATH.2 Mandatory verification steps for path changes

For every path modified or added in the PR, complete these steps:

**Step 1: Verify the path exists on actual target systems.**

Do not trust that a path exists based on naming conventions or intuition. Request concrete evidence.

**Step 2: Cross-reference with official documentation.**

Check the official installation documentation for the software involved. The claimed path must match what the documentation says.

**Step 3: Check for existing path coverage.**

Search the codebase for all places where paths are defined for the same purpose. Verify that the new path is not already covered by an existing entry.

**Step 4: Validate path handling code.**

If the path uses home directory expansion (`~`), environment variables (`$HOME`, `%APPDATA%`), or relative references, verify that the expansion is performed correctly in the programming language used.

**Step 5: Test on multiple platforms.**

If the software supports multiple operating systems, verify the path on each one. Paths that work on macOS may not exist on Linux, and vice versa.

---

## S-PATH.3 Verification commands to request from the author

Request the author to run these commands and provide the output:

**For file or directory existence:**

```bash
# macOS and Linux
ls -la /exact/path/from/the/pr
# If checking a binary
which binary_name
type binary_name
file /exact/path/to/binary

# Windows (PowerShell)
Test-Path "C:\exact\path\from\the\pr"
Get-Command binary_name
```

**For understanding the installation method:**

```bash
# Check which package manager installed it
# Debian/Ubuntu
dpkg -L package_name | grep bin
apt list --installed | grep package_name

# macOS (Homebrew)
brew --prefix package_name
brew list package_name | grep bin

# pip
pip show package_name
pip show -f package_name | grep bin

# npm
npm list -g package_name
npm bin -g
```

**For verifying path expansion:**

```bash
# Check what ~ expands to
echo ~
echo $HOME

# Check if a path with ~ actually resolves
ls -la ~/expected/path
```

---

## S-PATH.4 Evidence requirements specific to path changes

Before approving a PR with path changes, require the following evidence:

| Evidence Item | Required? | Acceptable Formats |
|--------------|-----------|-------------------|
| Terminal output showing the path exists on the target system | REQUIRED | Screenshot or copy-pasted terminal output |
| Official documentation confirming the path | REQUIRED | Link to official docs, or quoted text from docs |
| Confirmation that existing paths do not already cover this case | REQUIRED | Reviewer can verify by reading the codebase |
| Test results on all supported platforms | REQUIRED if multi-platform | Terminal output from each platform |
| Justification for path priority (if added to an ordered list) | REQUIRED if order matters | Written explanation in PR description |

---

## S-PATH.5 Example: Reviewing a PR that adds a new binary search path

**PR description:** "Added detection for the CLI tool when installed via Flatpak."

**PR diff:**

```python
 BINARY_SEARCH_PATHS = [
     "/usr/local/bin/mytool",      # Homebrew / manual install
     "/usr/bin/mytool",            # System package manager
     "~/.local/bin/mytool",        # pip install --user
+    "/var/lib/flatpak/app/com.example.mytool/current/active/bin/mytool",  # Flatpak
 ]
```

**Review using this protocol:**

**Step 1: Verify path exists.**

Request: "Can you run `ls -la /var/lib/flatpak/app/com.example.mytool/current/active/bin/mytool` on a system where mytool is installed via Flatpak?"

**Step 2: Cross-reference with documentation.**

Check the Flatpak documentation. Flatpak applications are installed in `/var/lib/flatpak/app/`, but the binary is typically accessed via `flatpak run com.example.mytool`, not by direct path. The internal directory structure uses `/var/lib/flatpak/app/<app-id>/<arch>/<branch>/active/files/bin/`, not `/current/active/bin/`.

The PR's path structure does not match the documented Flatpak directory layout.

**Step 3: Check existing coverage.**

The path `~/.local/bin/mytool` is already in the list. Flatpak exports binaries to `~/.local/bin/` when the user has the Flatpak user installation configured. So Flatpak-installed binaries may already be detected by the existing path.

**Step 4: Validate path handling.**

The path `~/.local/bin/mytool` uses `~`, which requires expansion. Check whether the search code calls `os.path.expanduser()` before checking existence.

**Step 5: Multi-platform testing.**

Flatpak is primarily a Linux technology. If the search is also used on macOS, the Flatpak path should be conditional on the platform.

**Review response:**

"I have three concerns about this path addition:

1. The Flatpak directory structure in the PR (`/current/active/bin/`) does not match the documented Flatpak layout (`/<arch>/<branch>/active/files/bin/`). Can you verify the exact path on a system with a Flatpak-installed copy of mytool?

2. Flatpak exports binaries to `~/.local/bin/` when configured with the user installation. The existing path `~/.local/bin/mytool` may already detect Flatpak-installed copies. Can you confirm whether this is the case?

3. Flatpak is Linux-only. Is there a platform check to skip this path on macOS and Windows?

Please provide:
- Output of `flatpak info com.example.mytool` and `ls -la /var/lib/flatpak/app/com.example.mytool/` on a system with the Flatpak installation
- Confirmation of whether `~/.local/bin/mytool` exists when mytool is installed via Flatpak"
