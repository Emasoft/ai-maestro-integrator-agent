#!/usr/bin/env python3
"""AMIA Unicode Compliance Checker.

Part of the amia-quality-gates skill in the Emasoft Integrator Agent plugin.

Checks files for Unicode compliance issues:
1. BOM (Byte Order Mark) detection — files should NOT have BOM
2. Encoding declaration presence — Python files should use UTF-8
3. Line ending consistency — files should use LF (Unix) line endings
4. Non-ASCII identifier detection — Python identifiers should be ASCII-only
"""

import argparse
import re
import sys
from pathlib import Path

# Fix Windows console encoding for emoji output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        # Python < 3.7
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

# File extensions to check
TEXT_EXTENSIONS = {
    ".py", ".md", ".json", ".yaml", ".yml", ".toml",
    ".sh", ".bash", ".txt", ".cfg", ".ini", ".rst",
}

PYTHON_EXTENSIONS = {".py"}


class UnicodeComplianceChecker:
    """Checks files for Unicode compliance issues."""

    def __init__(self) -> None:
        self.issues: list[str] = []

    def check_file(self, filepath: Path) -> bool:
        """Check a single file for Unicode compliance issues.

        Returns:
            True if file passes all checks, False if issues found.
        """
        file_issues: list[str] = []

        # Read raw bytes for BOM and line ending checks
        try:
            raw_bytes = filepath.read_bytes()
        except OSError as e:
            self.issues.append(f"{filepath}: Cannot read file ({e})")
            return False

        # Check 1: BOM detection
        if raw_bytes.startswith(b"\xef\xbb\xbf"):
            file_issues.append(f"{filepath}:1 - File has UTF-8 BOM (byte order mark). Remove the BOM.")
        elif raw_bytes.startswith((b"\xff\xfe", b"\xfe\xff")):
            file_issues.append(f"{filepath}:1 - File has UTF-16 BOM. Convert to UTF-8 without BOM.")

        # Check 2: Line ending consistency (detect CRLF)
        crlf_count = raw_bytes.count(b"\r\n")
        lf_count = raw_bytes.count(b"\n") - crlf_count
        cr_only_count = raw_bytes.count(b"\r") - crlf_count

        if crlf_count > 0 and lf_count > 0:
            file_issues.append(
                f"{filepath} - Mixed line endings: {crlf_count} CRLF + {lf_count} LF. "
                "Normalize to LF."
            )
        elif crlf_count > 0:
            file_issues.append(
                f"{filepath} - Windows line endings (CRLF). Convert to Unix line endings (LF)."
            )
        if cr_only_count > 0:
            file_issues.append(
                f"{filepath} - Old Mac line endings (CR). Convert to Unix line endings (LF)."
            )

        # Decode for text-based checks
        try:
            content = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content = raw_bytes.decode("utf-8-sig")
                # Already flagged BOM above, but file is at least decodable
            except UnicodeDecodeError:
                self.issues.append(f"{filepath}: File is not valid UTF-8")
                return False

        # Python-specific checks
        if filepath.suffix in PYTHON_EXTENSIONS:
            # Check 3: Non-ASCII identifiers in Python
            # Find identifiers that contain non-ASCII characters
            # This regex matches Python identifiers (variable/function/class names)
            for line_num, line in enumerate(content.split("\n"), start=1):
                # Skip comments and strings (simple heuristic)
                stripped = line.split("#")[0]  # Remove comments

                # Find potential identifiers (word characters not in strings)
                # Look for non-ASCII word characters in code
                for match in re.finditer(r'\b([a-zA-Z_]\w*)\b', stripped):
                    identifier = match.group(1)
                    non_ascii_chars = [c for c in identifier if ord(c) > 127]
                    if non_ascii_chars:
                        chars_str = ", ".join(
                            f"U+{ord(c):04X} ({c})" for c in non_ascii_chars
                        )
                        file_issues.append(
                            f"{filepath}:{line_num} - Non-ASCII character in identifier "
                            f"'{identifier}': {chars_str}"
                        )

        self.issues.extend(file_issues)
        return len(file_issues) == 0

    def check_directory(self, directory: Path) -> int:
        """Recursively check all text files in a directory.

        Returns:
            Number of issues found.
        """
        start_count = len(self.issues)

        for filepath in sorted(directory.rglob("*")):
            if not filepath.is_file():
                continue

            # Skip hidden directories and common non-source dirs
            parts = filepath.parts
            if any(
                p.startswith(".") or p in ("__pycache__", "node_modules", ".git", "venv", ".venv")
                for p in parts
            ):
                continue

            if filepath.suffix in TEXT_EXTENSIONS:
                self.check_file(filepath)

        return len(self.issues) - start_count

    def check_files(self, filepaths: list[Path]) -> int:
        """Check multiple specific files.

        Returns:
            Number of issues found.
        """
        start_count = len(self.issues)
        for filepath in filepaths:
            if not filepath.exists():
                continue
            if filepath.suffix in TEXT_EXTENSIONS:
                self.check_file(filepath)
        return len(self.issues) - start_count


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check files for Unicode compliance issues (BOM, line endings, encoding, non-ASCII identifiers)"
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames to check",
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Directory to recursively check",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show all issues found and success messages",
    )

    args = parser.parse_args()

    checker = UnicodeComplianceChecker()

    if args.directory:
        directory = Path(args.directory)
        if not directory.is_dir():
            print(f"Error: {args.directory} is not a directory")
            return 2
        checker.check_directory(directory)
    elif args.filenames:
        files = [Path(f) for f in args.filenames]
        checker.check_files(files)
    else:
        print("Error: Provide filenames or --directory")
        return 2

    # Report results
    if checker.issues:
        print("Unicode compliance issues found:")
        print()
        for issue in checker.issues:
            print(f"  {issue}")
        print()
        print("Fix: Ensure all files are UTF-8 without BOM, use LF line endings, and ASCII-only identifiers.")
        print()
        return 1

    if args.verbose:
        file_count = len(args.filenames) if args.filenames else "all"
        print(f"All {file_count} files pass Unicode compliance checks")

    return 0


if __name__ == "__main__":
    sys.exit(main())
