# Shell Review Patterns - Part 4: Cross-Platform Considerations

## Table of Contents

- 6.4 Cross-platform considerations for macOS and Linux
  - 6.4.1 Key differences table (sed, date, stat, readlink, grep)
  - 6.4.2 Portable patterns for sed in-place editing
  - 6.4.3 Portable patterns for date formatting
  - 6.4.4 Portable patterns for readlink -f (canonical path)
  - 6.4.5 OS detection functions
  - 6.4.6 GNU Coreutils on macOS (brew install)
  - 6.4.7 Portable script template
  - 6.4.8 Cross-platform review checklist

---

## 6.4 Cross-Platform Considerations for macOS and Linux

Shell scripts often need to work on both macOS and Linux.

### 6.4.1 Key Differences

| Feature | macOS | Linux |
|---------|-------|-------|
| Default shell | zsh (10.15+), bash 3 (older) | bash 5 |
| sed in-place | `sed -i ''` | `sed -i` |
| date command | BSD date | GNU date |
| stat command | Different flags | Different flags |
| readlink | No `-f` option | Has `-f` option |
| find | Slightly different | Standard |
| grep | BSD grep | GNU grep |

### 6.4.2 Portable sed in-place editing

```bash
# Portable sed -i
sed_inplace() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}

# Usage
sed_inplace 's/old/new/g' file.txt
```

### 6.4.3 Portable date formatting

```bash
# Portable date
if date --version >/dev/null 2>&1; then
    # GNU date (Linux)
    yesterday=$(date -d "yesterday" +%Y-%m-%d)
else
    # BSD date (macOS)
    yesterday=$(date -v-1d +%Y-%m-%d)
fi
```

### 6.4.4 Portable readlink -f (canonical path)

```bash
# Portable realpath
get_realpath() {
    if command -v realpath >/dev/null 2>&1; then
        realpath "$1"
    elif command -v greadlink >/dev/null 2>&1; then
        greadlink -f "$1"  # macOS with coreutils
    else
        # Fallback using Python
        python3 -c "import os; print(os.path.realpath('$1'))"
    fi
}

# Get script directory portably
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```

### 6.4.5 OS Detection Functions

```bash
# Detect OS using $OSTYPE
detect_os() {
    case "$OSTYPE" in
        linux*)   echo "linux" ;;
        darwin*)  echo "macos" ;;
        msys*)    echo "windows" ;;
        cygwin*)  echo "windows" ;;
        *)        echo "unknown" ;;
    esac
}

# Or using uname
detect_os() {
    case "$(uname -s)" in
        Linux*)   echo "linux" ;;
        Darwin*)  echo "macos" ;;
        MINGW*)   echo "windows" ;;
        *)        echo "unknown" ;;
    esac
}
```

### 6.4.6 GNU Coreutils on macOS

```bash
# Install GNU coreutils on macOS
brew install coreutils

# Use with 'g' prefix
gdate --date="yesterday" +%Y-%m-%d
greadlink -f file
gstat file
```

### 6.4.7 Portable Script Template

```bash
#!/usr/bin/env bash
set -euo pipefail

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Linux*)  OS_TYPE="linux" ;;
    Darwin*) OS_TYPE="macos" ;;
    *)       OS_TYPE="unknown" ;;
esac

# Portable sed -i
sed_i() {
    if [[ "$OS_TYPE" == "macos" ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}

# Portable stat for file modification time
get_mtime() {
    local file="$1"
    if [[ "$OS_TYPE" == "macos" ]]; then
        stat -f %m "$file"
    else
        stat -c %Y "$file"
    fi
}

# Portable temp directory
TMPDIR="${TMPDIR:-/tmp}"

# Main script logic
main() {
    echo "Running on: $OS_TYPE"
}

main "$@"
```

### 6.4.8 Cross-Platform Checklist

- [ ] Script tested on both macOS and Linux
- [ ] No hardcoded paths (uses $HOME, etc.)
- [ ] sed -i handles both BSD and GNU
- [ ] date command is portable or wrapped
- [ ] stat command is portable or wrapped
- [ ] Uses /usr/bin/env for shebang
- [ ] Temporary files use $TMPDIR
- [ ] No bash 4+ features if macOS compatibility needed

---

## Navigation

- **Previous**: [Part 3: ShellCheck](shell-review-patterns-part3-shellcheck.md)
- **Index**: [shell-review-patterns.md](shell-review-patterns.md)
