# Language Detection Reference

This reference covers how to detect programming languages in files for code review purposes.

---

## Table of Contents

- 1.1 Detecting language from file extensions
- 1.2 Detecting language from shebang lines
- 1.3 Using .gitattributes linguist hints
- 1.4 Understanding GitHub's language detection algorithm
- 1.5 Handling mixed-language files

---

## Quick Reference

| Detection Method | Use Case | Reliability |
|------------------|----------|-------------|
| File extension | Most common files | High for standard extensions |
| Shebang line | Scripts without extensions | High when present |
| .gitattributes | Custom/override detection | Definitive when specified |
| GitHub algorithm | Comprehensive detection | Highest (multi-method) |
| Content analysis | Mixed-language files | Varies by file type |

---

## Part 1: File Extensions and Shebang Detection

**See:** [language-detection-part1-extensions-shebang.md](language-detection-part1-extensions-shebang.md)

### Contents:

- **1.1 Detecting Language from File Extensions**
  - Python extensions (.py, .pyi, .pyx, .pxd, .pyw)
  - JavaScript/TypeScript extensions (.js, .mjs, .cjs, .jsx, .ts, .mts, .cts, .tsx, .d.ts)
  - Rust extensions (.rs)
  - Go extensions (.go)
  - Shell script extensions (.sh, .bash, .zsh, .fish, .ksh)
  - Configuration and data files (.json, .yaml, .yml, .toml, .xml, .html, .css)
  - Implementation example: `detect_language_from_extension()`

- **1.2 Detecting Language from Shebang Lines**
  - What is a shebang?
  - Common shebang patterns table
  - Implementation example: `detect_language_from_shebang()`
  - Best practice: Prefer `#!/usr/bin/env`

---

## Part 2: Gitattributes and GitHub Algorithm

**See:** [language-detection-part2-gitattributes-algorithm.md](language-detection-part2-gitattributes-algorithm.md)

### Contents:

- **1.3 Using .gitattributes Linguist Hints**
  - What is .gitattributes?
  - Linguist attributes table (linguist-language, linguist-vendored, linguist-generated, linguist-documentation, linguist-detectable)
  - Example .gitattributes file
  - Implementation example: `parse_gitattributes()`

- **1.4 Understanding GitHub's Language Detection Algorithm**
  - Detection priority order (modeline, shebang, filename, extension, heuristics)
  - Special filenames recognized (Makefile, Dockerfile, Jenkinsfile, etc.)
  - Content heuristics for ambiguous extensions (.h, .pl, .m)
  - Implementation example: `detect_language_comprehensive()`

---

## Part 3: Mixed-Language Files

**See:** [language-detection-part3-mixed-language.md](language-detection-part3-mixed-language.md)

### Contents:

- **1.5 Handling Mixed-Language Files**
  - Common mixed-language scenarios table (HTML, Vue SFC, Svelte, Jupyter, Markdown, PHP, JSP, ERB, Jinja2)
  - Implementation example: `detect_embedded_in_html()`
  - Implementation example: `detect_languages_in_markdown()`
  - Implementation example: `detect_languages_in_vue()`
  - Review strategy for mixed-language files (5-step approach)
  - Jupyter notebook handling with `detect_languages_in_notebook()`

---

## Usage Summary

### When to use each detection method:

1. **Start with file extension** - covers 90% of cases
2. **Check shebang** - for extensionless scripts
3. **Consult .gitattributes** - for repo-specific overrides
4. **Apply content analysis** - for mixed-language or ambiguous files

### Implementation order in code:

```python
def detect_language(filepath: str, repo_root: str = None) -> str:
    # 1. Special filenames (Makefile, Dockerfile, etc.)
    # 2. .gitattributes overrides
    # 3. Shebang detection
    # 4. Extension detection
    # 5. Content heuristics (if needed)
    # 6. Default to "unknown"
```

See the part files for complete implementation examples.
