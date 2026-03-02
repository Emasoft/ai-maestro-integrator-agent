#!/usr/bin/env python3
"""Get recommended linters and commands for programming languages.

This script returns linter recommendations, install commands, and run
commands for specified programming languages.

Usage:
    python amia_get_language_linters.py --language python
    python amia_get_language_linters.py --languages python,javascript,rust
    python amia_get_language_linters.py --all
"""

import argparse
import json

LANGUAGE_LINTERS = {
    "python": {
        "linters": ["ruff", "mypy", "bandit"],
        "formatter": "ruff format",
        "install": {
            "ruff": "pip install ruff",
            "mypy": "pip install mypy",
            "bandit": "pip install bandit",
        },
        "commands": {
            "ruff": "ruff check .",
            "ruff_fix": "ruff check --fix .",
            "ruff_format": "ruff format .",
            "mypy": "mypy --strict .",
            "bandit": "bandit -r src/",
        },
        "config_files": ["pyproject.toml", "ruff.toml", "mypy.ini"],
    },
    "javascript": {
        "linters": ["eslint", "prettier"],
        "formatter": "prettier",
        "install": {
            "eslint": "npm install -D eslint",
            "prettier": "npm install -D prettier",
        },
        "commands": {
            "eslint": "npx eslint .",
            "eslint_fix": "npx eslint --fix .",
            "prettier_check": "npx prettier --check .",
            "prettier_fix": "npx prettier --write .",
        },
        "config_files": ["eslint.config.js", ".eslintrc.json", ".prettierrc"],
    },
    "typescript": {
        "linters": ["eslint", "prettier", "tsc"],
        "formatter": "prettier",
        "install": {
            "eslint": "npm install -D eslint typescript-eslint",
            "prettier": "npm install -D prettier",
            "typescript": "npm install -D typescript",
        },
        "commands": {
            "eslint": "npx eslint .",
            "eslint_fix": "npx eslint --fix .",
            "prettier_check": "npx prettier --check .",
            "prettier_fix": "npx prettier --write .",
            "typecheck": "npx tsc --noEmit",
        },
        "config_files": ["eslint.config.js", "tsconfig.json", ".prettierrc"],
    },
    "rust": {
        "linters": ["clippy", "rustfmt"],
        "formatter": "rustfmt",
        "install": {
            "clippy": "rustup component add clippy",
            "rustfmt": "rustup component add rustfmt",
        },
        "commands": {
            "clippy": "cargo clippy -- -D warnings",
            "clippy_fix": "cargo clippy --fix",
            "rustfmt_check": "cargo fmt --check",
            "rustfmt": "cargo fmt",
            "test": "cargo test",
        },
        "config_files": ["rustfmt.toml", "clippy.toml", "Cargo.toml"],
    },
    "go": {
        "linters": ["go vet", "staticcheck", "golangci-lint"],
        "formatter": "gofmt",
        "install": {
            "staticcheck": "go install honnef.co/go/tools/cmd/staticcheck@latest",
            "golangci-lint": "go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest",
        },
        "commands": {
            "go_vet": "go vet ./...",
            "staticcheck": "staticcheck ./...",
            "golangci-lint": "golangci-lint run ./...",
            "gofmt_check": "gofmt -l .",
            "gofmt": "gofmt -w .",
            "test": "go test ./...",
        },
        "config_files": [".golangci.yml", "go.mod"],
    },
    "shell": {
        "linters": ["shellcheck"],
        "formatter": "shfmt",
        "install": {
            "shellcheck": "brew install shellcheck  # or apt install shellcheck",
            "shfmt": "go install mvdan.cc/sh/v3/cmd/shfmt@latest",
        },
        "commands": {
            "shellcheck": "shellcheck **/*.sh",
            "shfmt_check": "shfmt -d .",
            "shfmt": "shfmt -w .",
        },
        "config_files": [".shellcheckrc"],
    },
    "html": {
        "linters": ["htmlhint"],
        "formatter": "prettier",
        "install": {
            "htmlhint": "npm install -D htmlhint",
            "prettier": "npm install -D prettier",
        },
        "commands": {
            "htmlhint": "npx htmlhint **/*.html",
            "prettier_check": "npx prettier --check '**/*.html'",
            "prettier_fix": "npx prettier --write '**/*.html'",
        },
        "config_files": [".htmlhintrc", ".prettierrc"],
    },
    "css": {
        "linters": ["stylelint"],
        "formatter": "prettier",
        "install": {
            "stylelint": "npm install -D stylelint stylelint-config-standard",
            "prettier": "npm install -D prettier",
        },
        "commands": {
            "stylelint": "npx stylelint '**/*.css'",
            "stylelint_fix": "npx stylelint --fix '**/*.css'",
            "prettier_check": "npx prettier --check '**/*.css'",
            "prettier_fix": "npx prettier --write '**/*.css'",
        },
        "config_files": [".stylelintrc.json", ".prettierrc"],
    },
}

SUPPORTED_LANGUAGES = list(LANGUAGE_LINTERS.keys())


def get_linter_info(language: str) -> dict | None:
    """Get linter information for a language."""
    lang_lower = language.lower()
    if lang_lower in LANGUAGE_LINTERS:
        return LANGUAGE_LINTERS[lang_lower]
    if lang_lower in ("js", "jsx", "mjs", "cjs"):
        return LANGUAGE_LINTERS["javascript"]
    if lang_lower in ("ts", "tsx", "mts", "cts"):
        return LANGUAGE_LINTERS["typescript"]
    if lang_lower in ("bash", "sh", "zsh"):
        return LANGUAGE_LINTERS["shell"]
    return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Get linters for programming languages")
    parser.add_argument("--language", help="Single language name")
    parser.add_argument("--languages", help="Comma-separated list of languages")
    parser.add_argument("--all", action="store_true", help="Show all supported languages")
    parser.add_argument("--list", action="store_true", help="List supported languages")
    parser.add_argument("--output", choices=["json", "text"], default="json")

    args = parser.parse_args()

    if args.list:
        print("Supported languages:")
        for lang in sorted(SUPPORTED_LANGUAGES):
            print(f"  - {lang}")
        return

    if args.all:
        languages = SUPPORTED_LANGUAGES
    elif args.languages:
        languages = [lang_str.strip() for lang_str in args.languages.split(",")]
    elif args.language:
        languages = [args.language]
    else:
        parser.error("Provide --language, --languages, --all, or --list")

    result = {}
    for lang in languages:
        info = get_linter_info(lang)
        if info:
            result[lang] = info
        else:
            result[lang] = {"error": f"Unsupported language: {lang}"}

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        for lang, info in result.items():
            print(f"\n{lang.upper()}")
            print("-" * 40)
            if "error" in info:
                print(f"  {info['error']}")
                continue
            print(f"  Linters: {', '.join(info['linters'])}")
            print(f"  Formatter: {info['formatter']}")
            print("  Commands:")
            for name, cmd in info["commands"].items():
                print(f"    {name}: {cmd}")


if __name__ == "__main__":
    main()
