# Language Detection Part 3: Mixed-Language Files

This reference covers handling files that contain code in multiple programming languages.

## Table of Contents

- [1.5 Handling Mixed-Language Files](#15-handling-mixed-language-files)
  - [Common Mixed-Language Scenarios](#common-mixed-language-scenarios)
  - [Detecting Embedded Languages in HTML](#detecting-embedded-languages-in-html)
  - [Detecting Code Blocks in Markdown](#detecting-code-blocks-in-markdown)
  - [Vue Single-File Component Detection](#vue-single-file-component-detection)
  - [Review Strategy for Mixed-Language Files](#review-strategy-for-mixed-language-files)
  - [Jupyter Notebook Handling](#jupyter-notebook-handling)

---

## 1.5 Handling Mixed-Language Files

Some files contain code in multiple languages. These require special handling during review.

### Common Mixed-Language Scenarios

| File Type | Primary | Embedded |
|-----------|---------|----------|
| HTML | HTML | JavaScript, CSS |
| Vue SFC | Vue | JavaScript/TypeScript, CSS, HTML |
| Svelte | Svelte | JavaScript/TypeScript, CSS, HTML |
| Jupyter Notebook | JSON | Python, Markdown |
| Markdown | Markdown | Any (code blocks) |
| PHP | PHP | HTML, JavaScript, CSS |
| JSP | Java | HTML, JavaScript |
| ERB | Ruby | HTML, JavaScript |
| Jinja2 | Jinja2 | HTML, JavaScript |

### Detecting Embedded Languages in HTML

```python
import re

def detect_embedded_in_html(content: str) -> list[str]:
    """Detect languages embedded in HTML content."""
    languages = ["html"]

    # Check for inline JavaScript
    if re.search(r"<script[^>]*>", content, re.IGNORECASE):
        # Check if it's TypeScript
        if re.search(r'<script[^>]*lang=["\']ts["\']', content, re.IGNORECASE):
            languages.append("typescript")
        else:
            languages.append("javascript")

    # Check for inline CSS
    if re.search(r"<style[^>]*>", content, re.IGNORECASE):
        # Check for preprocessors
        if re.search(r'<style[^>]*lang=["\']scss["\']', content, re.IGNORECASE):
            languages.append("scss")
        elif re.search(r'<style[^>]*lang=["\']sass["\']', content, re.IGNORECASE):
            languages.append("sass")
        elif re.search(r'<style[^>]*lang=["\']less["\']', content, re.IGNORECASE):
            languages.append("less")
        else:
            languages.append("css")

    return languages
```

### Detecting Code Blocks in Markdown

```python
def detect_languages_in_markdown(content: str) -> list[str]:
    """Detect code block languages in Markdown."""
    languages = ["markdown"]

    # Match fenced code blocks with language specifier
    code_block_pattern = r"```(\w+)"
    matches = re.findall(code_block_pattern, content)

    for lang in matches:
        normalized = lang.lower()
        # Normalize common aliases
        if normalized in ("py", "python3"):
            normalized = "python"
        elif normalized in ("js", "node"):
            normalized = "javascript"
        elif normalized in ("ts"):
            normalized = "typescript"
        elif normalized in ("sh", "bash", "zsh"):
            normalized = "shell"

        if normalized not in languages:
            languages.append(normalized)

    return languages
```

### Vue Single-File Component Detection

```python
def detect_languages_in_vue(content: str) -> list[str]:
    """Detect languages in Vue SFC."""
    languages = ["vue"]

    # Template section (HTML by default)
    if "<template" in content:
        languages.append("html")

    # Script section
    if re.search(r'<script[^>]*lang=["\']ts["\']', content):
        languages.append("typescript")
    elif "<script" in content:
        languages.append("javascript")

    # Style section
    if re.search(r'<style[^>]*lang=["\']scss["\']', content):
        languages.append("scss")
    elif re.search(r'<style[^>]*lang=["\']sass["\']', content):
        languages.append("sass")
    elif re.search(r'<style[^>]*lang=["\']less["\']', content):
        languages.append("less")
    elif "<style" in content:
        languages.append("css")

    return languages
```

### Review Strategy for Mixed-Language Files

When reviewing mixed-language files:

1. **Identify all embedded languages**: Use the detection functions above
2. **Apply rules for each language**: Each embedded section needs its own review checklist
3. **Check language interactions**: Ensure data passing between languages is type-safe
4. **Verify separation of concerns**: HTML structure, JavaScript behavior, CSS styling should be appropriately separated
5. **Test each language context**: Unit tests might need different test runners for different sections

### Jupyter Notebook Handling

Jupyter notebooks (`.ipynb`) are JSON files containing cells with code and markdown:

```python
import json

def detect_languages_in_notebook(filepath: str) -> list[str]:
    """Detect languages in Jupyter notebook."""
    languages = ["jupyter"]

    with open(filepath, "r") as f:
        notebook = json.load(f)

    # Check kernel language
    kernel_lang = notebook.get("metadata", {}).get("kernelspec", {}).get("language", "")
    if kernel_lang:
        languages.append(kernel_lang.lower())

    # Check cell types
    for cell in notebook.get("cells", []):
        cell_type = cell.get("cell_type", "")
        if cell_type == "markdown":
            if "markdown" not in languages:
                languages.append("markdown")
        elif cell_type == "code":
            # Code cells use kernel language
            pass

    return languages
```
