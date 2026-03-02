# Language Detection Part 1: File Extensions and Shebang Lines

This reference covers detecting programming languages from file extensions and shebang lines.

## Table of Contents

- [1.1 Detecting Language from File Extensions](#11-detecting-language-from-file-extensions)
  - [Python Extensions](#python-extensions)
  - [JavaScript/TypeScript Extensions](#javascripttypescript-extensions)
  - [Rust Extensions](#rust-extensions)
  - [Go Extensions](#go-extensions)
  - [Shell Script Extensions](#shell-script-extensions)
  - [Configuration and Data Files (Often Embedded Code)](#configuration-and-data-files-often-embedded-code)
  - [Implementation Example](#implementation-example)
- [1.2 Detecting Language from Shebang Lines](#12-detecting-language-from-shebang-lines)
  - [What is a Shebang?](#what-is-a-shebang)
  - [Common Shebang Patterns](#common-shebang-patterns)
  - [Implementation Example](#implementation-example-1)
  - [Best Practice: Prefer `#!/usr/bin/env`](#best-practice-prefer-usrbinenv)

---

## 1.1 Detecting Language from File Extensions

The most straightforward method for detecting a file's programming language is by examining its file extension. Below is a comprehensive mapping of common extensions to languages.

### Python Extensions
| Extension | Description |
|-----------|-------------|
| `.py` | Python source file |
| `.pyi` | Python stub file (type hints) |
| `.pyx` | Cython source file |
| `.pxd` | Cython declaration file |
| `.pyw` | Python Windows script |

### JavaScript/TypeScript Extensions
| Extension | Description |
|-----------|-------------|
| `.js` | JavaScript source file |
| `.mjs` | JavaScript ES module |
| `.cjs` | JavaScript CommonJS module |
| `.jsx` | JavaScript with JSX (React) |
| `.ts` | TypeScript source file |
| `.mts` | TypeScript ES module |
| `.cts` | TypeScript CommonJS module |
| `.tsx` | TypeScript with JSX (React) |
| `.d.ts` | TypeScript declaration file |

### Rust Extensions
| Extension | Description |
|-----------|-------------|
| `.rs` | Rust source file |

### Go Extensions
| Extension | Description |
|-----------|-------------|
| `.go` | Go source file |

### Shell Script Extensions
| Extension | Description |
|-----------|-------------|
| `.sh` | Shell script (usually Bash) |
| `.bash` | Bash script |
| `.zsh` | Zsh script |
| `.fish` | Fish shell script |
| `.ksh` | Korn shell script |

### Configuration and Data Files (Often Embedded Code)
| Extension | Description |
|-----------|-------------|
| `.json` | JSON data (may contain embedded code) |
| `.yaml`, `.yml` | YAML configuration |
| `.toml` | TOML configuration |
| `.xml` | XML data |
| `.html`, `.htm` | HTML (may contain JS/CSS) |
| `.css` | Cascading Style Sheets |
| `.scss`, `.sass` | Sass stylesheets |
| `.less` | Less stylesheets |

### Implementation Example

```python
EXTENSION_MAP = {
    # Python
    ".py": "python",
    ".pyi": "python",
    ".pyx": "cython",
    ".pxd": "cython",
    ".pyw": "python",
    # JavaScript/TypeScript
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".tsx": "typescript",
    ".d.ts": "typescript",
    # Rust
    ".rs": "rust",
    # Go
    ".go": "go",
    # Shell
    ".sh": "shell",
    ".bash": "bash",
    ".zsh": "zsh",
    # Web
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
}

def detect_language_from_extension(filename: str) -> str | None:
    """Detect programming language from file extension."""
    import os
    _, ext = os.path.splitext(filename)
    return EXTENSION_MAP.get(ext.lower())
```

---

## 1.2 Detecting Language from Shebang Lines

When a file lacks a recognizable extension (common for scripts), the shebang line at the beginning of the file can identify the interpreter.

### What is a Shebang?

A shebang is the first line of a script file that begins with `#!` followed by the path to an interpreter.

### Common Shebang Patterns

| Shebang | Language |
|---------|----------|
| `#!/bin/bash` | Bash |
| `#!/usr/bin/env bash` | Bash (portable) |
| `#!/bin/sh` | POSIX Shell |
| `#!/usr/bin/env sh` | POSIX Shell (portable) |
| `#!/usr/bin/env python3` | Python 3 |
| `#!/usr/bin/python3` | Python 3 |
| `#!/usr/bin/env python` | Python (version varies) |
| `#!/usr/bin/env node` | Node.js (JavaScript) |
| `#!/usr/bin/env deno` | Deno (TypeScript/JavaScript) |
| `#!/usr/bin/env ruby` | Ruby |
| `#!/usr/bin/env perl` | Perl |
| `#!/usr/bin/env php` | PHP |
| `#!/usr/bin/env zsh` | Zsh |

### Implementation Example

```python
import re

SHEBANG_MAP = {
    r"python3?": "python",
    r"bash": "bash",
    r"sh": "shell",
    r"zsh": "zsh",
    r"node": "javascript",
    r"deno": "typescript",
    r"ruby": "ruby",
    r"perl": "perl",
    r"php": "php",
}

def detect_language_from_shebang(filepath: str) -> str | None:
    """Detect programming language from shebang line."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
    except (IOError, OSError):
        return None

    if not first_line.startswith("#!"):
        return None

    # Extract interpreter from shebang
    # Handles both /usr/bin/env python and /usr/bin/python
    for pattern, language in SHEBANG_MAP.items():
        if re.search(pattern, first_line):
            return language

    return None
```

### Best Practice: Prefer `#!/usr/bin/env`

Using `#!/usr/bin/env interpreter` is more portable than hardcoded paths because:
1. The interpreter location varies across systems
2. `env` searches the PATH for the interpreter
3. Works with version managers (pyenv, nvm, rbenv)
