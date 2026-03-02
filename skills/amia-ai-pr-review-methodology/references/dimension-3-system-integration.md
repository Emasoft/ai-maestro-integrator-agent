# Dimension 3: System Integration Validation

## Table of Contents

- D3.1 When to apply system integration validation
- D3.2 File path verification on target systems (macOS, Linux, Windows)
- D3.3 Cross-referencing paths with official documentation
- D3.4 Path handling: home directory expansion, relative vs absolute, platform-specific
- D3.5 Installation location accuracy across package managers
- D3.6 Red flags for integration failures
- D3.7 Example: Validating a claimed binary installation path

---

## D3.1 When to apply system integration validation

Apply system integration validation to any PR that:

- Adds, modifies, or removes file paths
- Interacts with the filesystem (reading, writing, checking existence)
- Calls external commands or binaries
- Depends on system services (daemons, package managers, init systems)
- Handles environment variables or system configuration
- Makes assumptions about the operating system, architecture, or runtime environment

This dimension answers the question: "Will this code work correctly on all target systems, not just the author's machine?"

---

## D3.2 File path verification on target systems (macOS, Linux, Windows)

Every file path referenced in a PR must be verified to exist on each supported platform. Paths that look plausible but do not actually exist are a common source of false positive fixes.

**Verification procedure for each path in the PR:**

1. Identify the path and the platform it targets.
2. Check whether the path follows the platform's conventions:

| Platform | Typical Prefix | Home Directory | Binary Locations |
|----------|---------------|----------------|-----------------|
| macOS (Intel) | `/usr/local/` | `/Users/<username>/` | `/usr/local/bin/`, `/usr/bin/`, `/opt/local/bin/` |
| macOS (Apple Silicon) | `/opt/homebrew/` | `/Users/<username>/` | `/opt/homebrew/bin/`, `/usr/local/bin/`, `/usr/bin/` |
| Linux (Debian/Ubuntu) | `/usr/` | `/home/<username>/` | `/usr/bin/`, `/usr/local/bin/`, `~/.local/bin/`, `/snap/bin/` |
| Linux (RHEL/Fedora) | `/usr/` | `/home/<username>/` | `/usr/bin/`, `/usr/local/bin/`, `~/.local/bin/` |
| Windows | `C:\Program Files\` | `C:\Users\<username>\` | `C:\Program Files\<app>\`, `%APPDATA%\<app>\` |

3. Request evidence from the author:

```
Please provide the output of the following commands on each supported platform:
- macOS: ls -la <path>
- Linux: ls -la <path>
- Windows: dir <path>
```

**Checklist:**

- [ ] Path verified on macOS (if supported)
- [ ] Path verified on Linux (if supported)
- [ ] Path verified on Windows (if supported)
- [ ] Author provided evidence (terminal output showing the path exists)

---

## D3.3 Cross-referencing paths with official documentation

Do not trust paths based on convention or intuition. Always cross-reference with official documentation.

**How to cross-reference:**

1. Find the official installation guide for the software referenced in the PR.
2. Look for the section that describes where files are installed.
3. Compare the PR's path with the documented path.
4. If they differ, flag this as requiring justification.

**Example:**

A PR claims that a tool installs to `/usr/share/mytool/bin/mytool` on Linux.

Cross-reference with the tool's official documentation:
- The official Debian package installs the binary to `/usr/bin/mytool`
- The official tarball installs to `/opt/mytool/bin/mytool`
- No documentation mentions `/usr/share/mytool/bin/mytool`

**Review response:** "The path `/usr/share/mytool/bin/mytool` does not appear in the official installation documentation. The Debian package installs to `/usr/bin/mytool` and the manual tarball installs to `/opt/mytool/bin/mytool`. Can you provide the documentation or installation source that places the binary at `/usr/share/mytool/bin/`?"

---

## D3.4 Path handling: home directory expansion, relative vs absolute, platform-specific

Path handling is a frequent source of bugs in cross-platform code.

**Home directory expansion:**

The tilde character `~` is expanded by the shell, not by most programming languages. Code that uses `~` in a string literal (without expansion) will look for a directory literally named `~`.

| Language | Correct Expansion | Common Mistake |
|----------|-------------------|----------------|
| Python | `os.path.expanduser("~/config")` | `open("~/config")` (treats `~` as literal character) |
| JavaScript/Node | `os.homedir() + "/config"` | `fs.readFile("~/config")` (no expansion) |
| Bash | `"$HOME/config"` or `~/config` (shell expands it) | Using `~` inside double quotes in some contexts |
| Go | `os.UserHomeDir()` + `/config` | Hardcoding `/home/user/config` |

**Relative vs absolute paths:**

- Absolute paths (`/usr/local/bin/mytool`) are unambiguous but platform-specific.
- Relative paths (`./bin/mytool`) depend on the current working directory, which varies by execution context.
- Environment-based paths (`$HOME/.local/bin/mytool`) are portable but require the variable to be set.

**Checklist:**

- [ ] Home directory expansion is performed programmatically (not relying on shell expansion)
- [ ] Relative paths are resolved relative to a known base directory (not the working directory)
- [ ] Platform-specific paths have appropriate conditionals
- [ ] Path separators are correct for each platform (`/` for Unix, `\` or `/` for Windows)
- [ ] Environment variables used in paths are verified to be set in all target environments

---

## D3.5 Installation location accuracy across package managers

Different package managers install software to different locations. A path that is correct for one package manager may be wrong for another.

**Common package manager installation locations:**

| Package Manager | Platform | Binary Location | Library Location |
|----------------|----------|-----------------|-----------------|
| Homebrew (Intel Mac) | macOS | `/usr/local/bin/` | `/usr/local/lib/` |
| Homebrew (Apple Silicon) | macOS | `/opt/homebrew/bin/` | `/opt/homebrew/lib/` |
| apt / dpkg | Debian/Ubuntu | `/usr/bin/` | `/usr/lib/` |
| dnf / rpm | RHEL/Fedora | `/usr/bin/` | `/usr/lib64/` |
| snap | Linux | `/snap/bin/` | `/snap/<package>/current/` |
| pip (user) | Cross-platform | `~/.local/bin/` | `~/.local/lib/pythonX.Y/` |
| npm (global) | Cross-platform | `/usr/local/bin/` or `~/.npm-global/bin/` | `/usr/local/lib/node_modules/` |
| cargo | Cross-platform | `~/.cargo/bin/` | N/A |

**Checklist:**

- [ ] The PR's path matches the package manager's actual installation location
- [ ] Multiple installation methods are accounted for (or the PR documents which method it targets)
- [ ] User-customized install paths are handled (via environment variables or configuration)

---

## D3.6 Red flags for integration failures

These patterns strongly suggest the PR has system integration issues:

| Red Flag | Why It Matters |
|----------|---------------|
| Hardcoded paths not verified on actual systems | The path may look plausible but not exist on the target platform |
| Claims "default install location" without citing documentation | The author may be guessing based on convention, not evidence |
| "It works on my machine" without cross-platform testing | The author's machine may have a non-standard configuration |
| Paths that look plausible but do not follow platform conventions | For example, `/usr/share/bin/` is not a standard binary location on any platform |
| No platform conditionals for platform-specific paths | The same path string is used on macOS and Linux without checking which platform is active |
| Home directory hardcoded as a literal string | For example, `/home/john/` instead of `os.path.expanduser("~")` |

---

## D3.7 Example: Validating a claimed binary installation path

**Scenario:** A PR adds detection of a developer tool by checking the path `/usr/local/share/devtool/bin/devtool` on Linux.

**Verification steps:**

1. **Check the official installation documentation:**
   The official installation guide says: "Install via apt: `sudo apt install devtool`" which installs to `/usr/bin/devtool`. Manual installation from tarball installs to `/opt/devtool/bin/devtool`.

2. **Check the path conventions:**
   `/usr/local/share/` is for architecture-independent data files, not for binaries. Binaries should be in `/usr/local/bin/` or `/usr/bin/`. The path `/usr/local/share/devtool/bin/devtool` is unconventional.

3. **Search the codebase:**
   The existing code already checks `/usr/bin/devtool` and `/usr/local/bin/devtool`.

4. **Request evidence:**

```
The path `/usr/local/share/devtool/bin/devtool` does not match the official
installation guide, which documents `/usr/bin/devtool` (via apt) and
`/opt/devtool/bin/devtool` (manual tarball). Additionally,
`/usr/local/share/` is conventionally for data files, not binaries.

Please provide:
1. The output of `ls -la /usr/local/share/devtool/bin/devtool` on a system
   where this path exists
2. The installation method that places the binary at this location
3. Why the existing paths (`/usr/bin/devtool`, `/usr/local/bin/devtool`)
   are insufficient
```
