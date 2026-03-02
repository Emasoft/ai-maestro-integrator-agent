# Cross-Platform Support

## Contents
- [Overview](#overview) - When you need to understand cross-platform compatibility
- [Platform Detection](#platform-detection) - If you need to know how platforms are detected
- [Shared Utilities](#shared-utilities) - When you need to use cross-platform functions
- [Windows-Specific Notes](#windows-specific-notes) - If you're developing on Windows
- [macOS/Linux Notes](#macoslinux-notes) - If you're developing on Unix-based systems
- [Troubleshooting](#troubleshooting) - When you encounter platform-specific issues

---

## Overview

All worktree-management scripts are fully cross-platform compatible with Windows, macOS, and Linux. The scripts automatically detect the current platform and use appropriate implementations for file locking, path handling, and subprocess execution.

## Platform Detection

Scripts automatically detect the platform and use appropriate implementations:

| Platform | Detection Method | File Locking | Path Format |
|----------|-----------------|--------------|-------------|
| **Windows** | `sys.platform == 'win32'` | `msvcrt` module | Backslash paths |
| **macOS** | `sys.platform == 'darwin'` | `fcntl` module | Forward slash paths |
| **Linux** | `sys.platform.startswith('linux')` | `fcntl` module | Forward slash paths |

## Shared Utilities

All scripts import from `shared/cross_platform.py`:

### File Operations
- `file_lock()` - Cross-platform file locking with configurable timeout
- `atomic_write_json()` - Safe atomic file writes preventing corruption
- `safe_path_join()` - Platform-appropriate path construction

### Network Operations
- `is_port_available()` - System-level port availability checking
- `get_free_port()` - Find next available port in range

### Directory Operations
- `get_amia_dir()` - Platform-appropriate config directory location
- `ensure_dir_exists()` - Create directory with proper permissions

### Process Operations
- `run_command()` - Cross-platform subprocess execution with timeout
- `kill_process_tree()` - Terminate process and all children

### Git Worktree Utilities
- `git_worktree_add()` - Create worktree with platform handling
- `git_worktree_remove()` - Remove worktree safely
- `git_worktree_list()` - Parse worktree list output

Scripts also import threshold configuration from `shared/thresholds.py`:
- `WorktreeThresholds` - Centralized threshold values for worktree lifecycle management

## Windows-Specific Notes

### Registry Location
Registry stored in `%LOCALAPPDATA%\design\` rather than `~/design/`:
```python
# Windows path resolution
amia_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'design')
```

### File Locking
File locking uses `msvcrt.locking()` instead of `fcntl`:
```python
import msvcrt
msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)
```

### Atomic Renames
Atomic renames require target deletion first on Windows:
```python
if os.path.exists(target):
    os.remove(target)
os.rename(temp_file, target)
```

### Path Handling
- Paths use backslashes (`\`) by default
- Use `os.path.normpath()` for consistency
- Git commands may require forward slashes

## macOS/Linux Notes

### Registry Location
Registry stored in `~/design/`:
```python
amia_dir = os.path.expanduser('~/design')
```

### File Locking
File locking uses `fcntl.flock()`:
```python
import fcntl
fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
```

### Atomic Renames
Atomic renames work directly:
```python
os.rename(temp_file, target)  # Atomic on POSIX
```

### Permissions
May need to set executable permissions:
```bash
chmod +x scripts/*.py
```

## Troubleshooting

### Permission Denied on Windows
**Symptom**: Cannot write to registry file
**Solution**: Check if another process has the file locked. Close other terminals or wait for lock timeout.

### File Lock Timeout
**Symptom**: `TimeoutError: Could not acquire file lock`
**Solution**:
1. Check for zombie processes: `ps aux | grep worktree`
2. Manually remove lock file if stale: `rm ~/design/.registry.lock`

### Path Not Found on Windows
**Symptom**: `FileNotFoundError` with Unix-style paths
**Solution**: Ensure all paths go through `os.path.normpath()` before use.

### Subprocess Fails on Windows
**Symptom**: Git commands fail with "command not found"
**Solution**: Ensure Git is in PATH. Use full path to git executable if needed.
