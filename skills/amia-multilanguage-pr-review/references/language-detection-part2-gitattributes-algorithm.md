# Language Detection Part 2: Gitattributes and GitHub Algorithm

This reference covers using .gitattributes linguist hints and understanding GitHub's language detection algorithm.

## Table of Contents

- [1.3 Using .gitattributes Linguist Hints](#13-using-gitattributes-linguist-hints)
  - [What is .gitattributes?](#what-is-gitattributes)
  - [Linguist Attributes](#linguist-attributes)
  - [Example .gitattributes File](#example-gitattributes-file)
  - [Reading .gitattributes Programmatically](#reading-gitattributes-programmatically)
- [1.4 Understanding GitHub's Language Detection Algorithm](#14-understanding-githubs-language-detection-algorithm)
  - [Detection Priority Order](#detection-priority-order)
  - [Special Filenames Recognized](#special-filenames-recognized)
  - [Content Heuristics](#content-heuristics)
  - [Implementation Example](#implementation-example)

---

## 1.3 Using .gitattributes Linguist Hints

GitHub uses the Linguist library to detect repository languages. You can override its detection using `.gitattributes`.

### What is .gitattributes?

A `.gitattributes` file in the repository root can set attributes for files. Linguist respects several attributes:

### Linguist Attributes

| Attribute | Effect |
|-----------|--------|
| `linguist-language=<lang>` | Override detected language |
| `linguist-vendored` | Mark as vendored (excluded from stats) |
| `linguist-generated` | Mark as generated (excluded from stats) |
| `linguist-documentation` | Mark as documentation |
| `linguist-detectable=false` | Exclude from language detection |

### Example .gitattributes File

```gitattributes
# Override language detection for specific files
*.psl linguist-language=PowerShell
Jenkinsfile linguist-language=Groovy

# Mark vendored directories (excluded from stats)
vendor/** linguist-vendored
third_party/** linguist-vendored
node_modules/** linguist-vendored

# Mark generated files (excluded from stats)
*.pb.go linguist-generated
*.pb.py linguist-generated
*_generated.ts linguist-generated
dist/** linguist-generated

# Mark documentation
docs/** linguist-documentation
*.md linguist-documentation

# Exclude certain files from detection entirely
data/*.json linguist-detectable=false
fixtures/** linguist-detectable=false
```

### Reading .gitattributes Programmatically

```python
import re
from pathlib import Path

def parse_gitattributes(repo_root: str) -> dict:
    """Parse .gitattributes for linguist hints."""
    gitattributes_path = Path(repo_root) / ".gitattributes"
    hints = {
        "language_overrides": {},  # pattern -> language
        "vendored": [],  # patterns
        "generated": [],  # patterns
        "excluded": [],  # patterns
    }

    if not gitattributes_path.exists():
        return hints

    with open(gitattributes_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 2:
                continue

            pattern = parts[0]
            attributes = parts[1:]

            for attr in attributes:
                if attr.startswith("linguist-language="):
                    lang = attr.split("=")[1]
                    hints["language_overrides"][pattern] = lang
                elif attr == "linguist-vendored":
                    hints["vendored"].append(pattern)
                elif attr == "linguist-generated":
                    hints["generated"].append(pattern)
                elif attr == "linguist-detectable=false":
                    hints["excluded"].append(pattern)

    return hints
```

---

## 1.4 Understanding GitHub's Language Detection Algorithm

GitHub's Linguist library uses a multi-step algorithm to detect file languages.

### Detection Priority Order

1. **Vim or Emacs modeline**: First few or last lines may contain editor hints
2. **Shebang**: `#!` line at file start
3. **Filename**: Exact filename matches (Makefile, Dockerfile, etc.)
4. **Extension**: File extension lookup
5. **Heuristics**: Pattern matching on file content

### Special Filenames Recognized

| Filename | Language |
|----------|----------|
| `Makefile`, `GNUmakefile` | Makefile |
| `Dockerfile` | Dockerfile |
| `Jenkinsfile` | Groovy |
| `Vagrantfile` | Ruby |
| `Gemfile` | Ruby |
| `Rakefile` | Ruby |
| `Podfile` | Ruby |
| `CMakeLists.txt` | CMake |
| `BUILD`, `WORKSPACE` | Starlark |
| `meson.build` | Meson |
| `justfile` | Just |

### Content Heuristics

For ambiguous extensions, Linguist examines file content:

- `.h` files: C or C++ or Objective-C (based on `#include` patterns, `@interface`, etc.)
- `.pl` files: Perl or Prolog (based on syntax patterns)
- `.m` files: Objective-C or MATLAB or Mercury (based on syntax)

### Implementation Example

```python
def detect_language_comprehensive(filepath: str, repo_root: str = None) -> str:
    """Detect language using multiple methods in priority order."""
    from pathlib import Path

    path = Path(filepath)
    filename = path.name

    # 1. Check special filenames first
    SPECIAL_FILENAMES = {
        "Makefile": "makefile",
        "GNUmakefile": "makefile",
        "Dockerfile": "dockerfile",
        "Jenkinsfile": "groovy",
        "Vagrantfile": "ruby",
        "Gemfile": "ruby",
        "Rakefile": "ruby",
        "CMakeLists.txt": "cmake",
    }

    if filename in SPECIAL_FILENAMES:
        return SPECIAL_FILENAMES[filename]

    # 2. Check .gitattributes overrides
    if repo_root:
        hints = parse_gitattributes(repo_root)
        for pattern, lang in hints["language_overrides"].items():
            if path.match(pattern):
                return lang.lower()

    # 3. Check shebang
    shebang_lang = detect_language_from_shebang(filepath)
    if shebang_lang:
        return shebang_lang

    # 4. Check extension
    ext_lang = detect_language_from_extension(filename)
    if ext_lang:
        return ext_lang

    # 5. Default to unknown
    return "unknown"
```
