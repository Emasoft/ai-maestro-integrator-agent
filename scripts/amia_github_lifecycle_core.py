#!/usr/bin/env python3
"""
amia_github_lifecycle_core.py - Core utilities and data structures for GitHub lifecycle automation.

This module provides:
- Data classes for issues, documents, and validation results
- Core utility functions (gh CLI wrapper, auth check, repo info)
- Frontmatter parsing and content sanitization
- Constants for validation

Part of the Integrator GitHub Lifecycle Automation suite.
"""

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

__all__ = [
    # Data classes
    "IssueMetadata",
    "DesignDocument",
    "ValidationResult",
    # Constants
    "REQUIRED_FRONTMATTER_FIELDS",
    "RECOMMENDED_FRONTMATTER_FIELDS",
    "VALID_DOC_TYPES",
    "VALID_STATUSES",
    "UUID_PATTERN",
    # Functions
    "run_gh_command",
    "check_gh_auth",
    "get_repo_info",
    "parse_frontmatter",
    "parse_design_document",
    "sanitize_content",
    "validate_frontmatter",
    "validate_documents",
]


@dataclass
class IssueMetadata:
    """Metadata for a GitHub issue."""

    number: int
    title: str
    state: str
    labels: list[str] = field(default_factory=list)
    project_status: Optional[str] = None
    linked_prs: list[int] = field(default_factory=list)
    url: str = ""


@dataclass
class DesignDocument:
    """Parsed design document with frontmatter."""

    path: Path
    uuid: str
    title: str
    doc_type: str
    status: str
    content: str
    related_issues: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of frontmatter validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# Required frontmatter fields for design documents
REQUIRED_FRONTMATTER_FIELDS: dict[str, str] = {
    "uuid": "Globally unique document identifier (e.g., PROJ-SPEC-20250108-a7b3f2e1)",
    "title": "Human-readable document title",
    "type": "Document type: spec, plan, adr",
    "status": "Document status: draft, review, approved, implemented, deprecated",
}

# Optional but recommended frontmatter fields
RECOMMENDED_FRONTMATTER_FIELDS: dict[str, str] = {
    "created": "Creation date (YYYY-MM-DD)",
    "updated": "Last update date (YYYY-MM-DD)",
    "author": "Document author",
    "version": "Document version number",
}

# Valid values for constrained fields
VALID_DOC_TYPES: set[str] = {"spec", "plan", "adr", "design", "rfc"}
VALID_STATUSES: set[str] = {
    "draft",
    "review",
    "approved",
    "implemented",
    "deprecated",
    "superseded",
}

# UUID format pattern: PREFIX-TYPE-YYYYMMDD-UUID8[_vNNNN]
UUID_PATTERN: re.Pattern[str] = re.compile(
    r"^[A-Z]{2,6}-[A-Z]+-\d{8}-[a-f0-9]{8}(?:_v\d{4})?$", re.IGNORECASE
)


def run_gh_command(
    args: list[str], capture_output: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run gh CLI command with error handling."""
    cmd = ["gh"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=60,
        )
        return result
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"gh command timed out: {' '.join(cmd)}")
    except FileNotFoundError:
        raise RuntimeError("gh CLI not found. Install with: brew install gh")


def check_gh_auth() -> bool:
    """Check if gh CLI is authenticated."""
    result = run_gh_command(["auth", "status"])
    return result.returncode == 0


def get_repo_info() -> tuple[str, str]:
    """Get current repository owner and name."""
    result = run_gh_command(["repo", "view", "--json", "owner,name"])
    if result.returncode != 0:
        raise RuntimeError("Not in a GitHub repository")
    data = json.loads(result.stdout)
    return data["owner"]["login"], data["name"]


def parse_frontmatter(content: str) -> tuple[dict[str, str | list[str]], str]:
    """Parse YAML frontmatter from markdown content.

    Returns (frontmatter_dict, body_content).
    """
    if not content.startswith("---"):
        return {}, content

    lines = content.split("\n")
    end_idx: Optional[int] = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return {}, content

    frontmatter: dict[str, str | list[str]] = {}
    for line in lines[1:end_idx]:
        if ":" in line:
            key, _, value = line.partition(":")  # NOTE: partition splits on first colon only, preserving URL values correctly
            key = key.strip()
            value_str = value.strip()
            # Handle quoted strings
            if value_str.startswith('"') and value_str.endswith('"'):
                value_str = value_str[1:-1]
            elif value_str.startswith("'") and value_str.endswith("'"):
                value_str = value_str[1:-1]
            # Handle arrays (simple parsing)
            # WARNING: Does not support YAML block scalars, multiline values, or values with apostrophes in array syntax
            elif value_str.startswith("[") and value_str.endswith("]"):
                try:
                    parsed = json.loads(value_str.replace("'", '"'))
                    frontmatter[key] = parsed
                    continue
                except json.JSONDecodeError:
                    pass
            frontmatter[key] = value_str

    body = "\n".join(lines[end_idx + 1 :])
    return frontmatter, body


def parse_design_document(file_path: Path) -> Optional[DesignDocument]:
    """Parse a design document and extract metadata."""
    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)

    # Extract title from frontmatter or first heading
    title_val = frontmatter.get("title", "")
    title = str(title_val) if title_val else ""
    if not title:
        title_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else file_path.stem

    # Extract related issues
    related_issues_val = frontmatter.get("related_issues", [])
    if isinstance(related_issues_val, str):
        related_issues = [related_issues_val] if related_issues_val else []
    elif isinstance(related_issues_val, list):
        related_issues = [str(x) for x in related_issues_val]
    else:
        related_issues = []

    # Extract tags
    tags_val = frontmatter.get("tags", [])
    if isinstance(tags_val, str):
        tags = [tags_val] if tags_val else []
    elif isinstance(tags_val, list):
        tags = [str(x) for x in tags_val]
    else:
        tags = []

    uuid_val = frontmatter.get("uuid", "")
    doc_type_val = frontmatter.get("type", "spec")
    status_val = frontmatter.get("status", "draft")

    return DesignDocument(
        path=file_path,
        uuid=str(uuid_val) if uuid_val else "",
        title=title,
        doc_type=str(doc_type_val) if doc_type_val else "spec",
        status=str(status_val) if status_val else "draft",
        content=body,
        related_issues=related_issues,
        tags=tags,
    )


def sanitize_content(content: str) -> str:
    """Remove INTERNAL and SENSITIVE markers from content.

    Follows AMOA IRON RULE for document sanitization.
    """
    # Remove <!-- INTERNAL --> ... <!-- /INTERNAL --> blocks
    content = re.sub(
        r"<!--\s*INTERNAL\s*-->.*?<!--\s*/INTERNAL\s*-->",
        "[INTERNAL CONTENT REDACTED]",
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Remove <!-- SENSITIVE --> ... <!-- /SENSITIVE --> blocks
    content = re.sub(
        r"<!--\s*SENSITIVE\s*-->.*?<!--\s*/SENSITIVE\s*-->",
        "[SENSITIVE CONTENT REDACTED]",
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Remove standalone INTERNAL/SENSITIVE markers
    content = re.sub(
        r"<!--\s*(INTERNAL|SENSITIVE)\s*-->", "", content, flags=re.IGNORECASE
    )

    return content


def validate_frontmatter(file_path: Path, strict: bool = False) -> ValidationResult:
    """Validate frontmatter of a design document.

    Args:
        file_path: Path to markdown file
        strict: If True, treat warnings as errors

    Returns:
        ValidationResult with valid flag and error/warning lists
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not file_path.exists():
        return ValidationResult(valid=False, errors=[f"File not found: {file_path}"])

    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return ValidationResult(valid=False, errors=[f"Cannot read file: {e}"])

    if not content.startswith("---"):
        return ValidationResult(
            valid=False, errors=["Missing frontmatter (file must start with '---')"]
        )

    frontmatter, _ = parse_frontmatter(content)

    if not frontmatter:
        return ValidationResult(valid=False, errors=["Empty or malformed frontmatter"])

    # Check required fields
    for field_name, description in REQUIRED_FRONTMATTER_FIELDS.items():
        if field_name not in frontmatter:
            errors.append(f"Missing required field: {field_name} ({description})")
        elif not frontmatter[field_name] or frontmatter[field_name] in (
            "null",
            "~",
            "",
        ):
            errors.append(f"Empty required field: {field_name}")

    # Check recommended fields
    for field_name, description in RECOMMENDED_FRONTMATTER_FIELDS.items():
        if field_name not in frontmatter:
            warnings.append(f"Missing recommended field: {field_name} ({description})")

    # Validate UUID format
    uuid_value = frontmatter.get("uuid", "")
    if (
        uuid_value
        and isinstance(uuid_value, str)
        and not UUID_PATTERN.match(uuid_value)
    ):
        errors.append(
            f"Invalid UUID format: '{uuid_value}'. Expected: PREFIX-TYPE-YYYYMMDD-UUID8"
        )

    # Validate type
    doc_type_val = frontmatter.get("type", "")
    doc_type = str(doc_type_val).lower() if doc_type_val else ""
    if doc_type and doc_type not in VALID_DOC_TYPES:
        errors.append(
            f"Invalid type: '{doc_type}'. Valid: {', '.join(sorted(VALID_DOC_TYPES))}"
        )

    # Validate status
    status_val = frontmatter.get("status", "")
    status = str(status_val).lower() if status_val else ""
    if status and status not in VALID_STATUSES:
        errors.append(
            f"Invalid status: '{status}'. Valid: {', '.join(sorted(VALID_STATUSES))}"
        )

    # Validate date fields
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for date_field in ["created", "updated"]:
        date_value = frontmatter.get(date_field, "")
        if date_value and not date_pattern.match(str(date_value)):
            warnings.append(
                f"Invalid date format for {date_field}: '{date_value}'. Expected: YYYY-MM-DD"
            )

    # Validate version is numeric
    version = frontmatter.get("version", "")
    if version and not str(version).isdigit():
        warnings.append(
            f"Non-numeric version: '{version}'. Consider using integer version numbers"
        )

    # Check for common issues
    if "related_issues" in frontmatter:
        related = frontmatter["related_issues"]
        if isinstance(related, str) and related not in ("[]", "null", "~", ""):
            warnings.append("related_issues should be a list, not a string")

    if "tags" in frontmatter:
        tags = frontmatter["tags"]
        if isinstance(tags, str) and tags not in ("[]", "null", "~", ""):
            warnings.append("tags should be a list, not a string")

    if strict:
        errors.extend(warnings)
        warnings = []

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_documents(
    paths: list[Path], strict: bool = False, quiet: bool = False
) -> tuple[list[Path], list[Path]]:
    """Validate multiple documents and return (valid_paths, invalid_paths)."""
    valid_paths: list[Path] = []
    invalid_paths: list[Path] = []

    for path in paths:
        result = validate_frontmatter(path, strict=strict)
        if result.valid:
            valid_paths.append(path)
            if not quiet and result.warnings:
                print(f"Warning: {path}: {len(result.warnings)} warnings")
                for warning in result.warnings:
                    print(f"    - {warning}")
        else:
            invalid_paths.append(path)
            if not quiet:
                print(f"Error: {path}: {len(result.errors)} errors")
                for error in result.errors:
                    print(f"    - {error}")

    return valid_paths, invalid_paths
