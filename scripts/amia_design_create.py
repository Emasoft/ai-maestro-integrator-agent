#!/usr/bin/env python3
"""
Design Document Creator - Create new design documents from templates.

This script creates new design documents with:
1. Automatically generated unique UUID (GUUID-YYYYMMDD-NNNN format)
2. Proper YAML frontmatter with all required fields
3. Correct placement in design/ subdirectory based on type
4. Post-creation validation

Usage:
    python amia_design_create.py --type pdr --title "Authentication System Design"
    python amia_design_create.py --type feature --title "OAuth Support" --author "John Doe"
    python amia_design_create.py --type decision --title "Database Selection" --description "ADR for choosing database"

Output Format (JSON):
    {
        "success": true,
        "file_path": "design/pdr/authentication-system-design.md",
        "uuid": "GUUID-20250129-0001",
        "validation": {...}
    }
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from shared.thresholds import write_output


class DesignDocumentCreator:
    """Create design documents from templates."""

    # Valid document types
    VALID_TYPES = ["pdr", "spec", "feature", "decision", "architecture", "template"]

    # Default templates for each type
    TEMPLATES = {
        "pdr": """# {title}

## Overview

Brief description of what this PDR covers.

## Problem Statement

What problem does this solve?

## Proposed Solution

How will we solve it?

## Alternatives Considered

What other approaches were evaluated?

## Implementation Plan

1. Step one
2. Step two
3. Step three

## Success Metrics

How will we measure success?

## Open Questions

- Question 1
- Question 2
""",
        "spec": """# {title}

## Purpose

What this specification defines.

## Scope

What is included and excluded.

## Requirements

### Functional Requirements

1. FR-1: Requirement one
2. FR-2: Requirement two

### Non-Functional Requirements

1. NFR-1: Performance requirement
2. NFR-2: Security requirement

## Interfaces

### Input

Description of inputs.

### Output

Description of outputs.

## Constraints

Known constraints and limitations.
""",
        "feature": """# {title}

## Summary

One-paragraph summary of the feature.

## Motivation

Why is this feature needed?

## User Stories

- As a [user type], I want to [action] so that [benefit]

## Design

### Architecture

How will this feature be implemented?

### API Changes

What API changes are required?

### Data Model

What data model changes are required?

## Testing Plan

How will this feature be tested?

## Rollout Plan

How will this feature be rolled out?
""",
        "decision": """# {title}

## Status

Proposed | Accepted | Deprecated | Superseded

## Context

What is the issue that we're seeing that is motivating this decision?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive

- Benefit 1
- Benefit 2

### Negative

- Drawback 1
- Drawback 2
""",
        "architecture": """# {title}

## Overview

High-level description of the architecture.

## Components

### Component 1

Description of component 1.

### Component 2

Description of component 2.

## Data Flow

How data flows through the system.

## Dependencies

External dependencies and integrations.

## Security Considerations

Security aspects of the architecture.

## Scalability

How the architecture scales.

## Monitoring

How the system is monitored.
""",
        "template": """# {title}

## Purpose

What this template is for.

## Usage

How to use this template.

## Sections

### Section 1

Description of section 1.

### Section 2

Description of section 2.
""",
    }

    def __init__(self, design_root: Path):
        """Initialize creator with design root directory.

        Args:
            design_root: Path to the design/ directory
        """
        self.design_root = design_root

    def generate_uuid(self) -> str:
        """Generate a unique UUID for the design document.

        Format: GUUID-YYYYMMDD-NNNN

        Returns:
            New unique UUID string
        """
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"GUUID-{today}-"

        # Find highest existing sequence number for today
        existing_uuids = self._find_existing_uuids(today)
        max_sequence = 0

        for uuid in existing_uuids:
            match = re.match(rf"GUUID-{today}-(\d{{4}})", uuid)
            if match:
                sequence = int(match.group(1))
                max_sequence = max(max_sequence, sequence)

        new_sequence = max_sequence + 1
        return f"{prefix}{new_sequence:04d}"

    def _find_existing_uuids(self, date_prefix: str) -> List[str]:
        """Find all existing UUIDs with the given date prefix.

        Args:
            date_prefix: Date string in YYYYMMDD format

        Returns:
            List of existing UUID strings
        """
        uuids: List[str] = []

        for md_file in self.design_root.glob("**/*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            # Look for UUID in frontmatter
            match = re.search(rf"uuid:\s*['\"]?(GUUID-{date_prefix}-\d{{4}})['\"]?", content)
            if match:
                uuids.append(match.group(1))

        return uuids

    def slugify(self, title: str) -> str:
        """Convert title to URL-friendly slug.

        Args:
            title: Document title

        Returns:
            Slugified string suitable for filenames
        """
        # Convert to lowercase
        slug = title.lower()

        # Replace non-alphanumeric characters with hyphens
        slug = re.sub(r"[^a-z0-9]+", "-", slug)

        # Remove leading/trailing hyphens
        slug = slug.strip("-")

        # Collapse multiple hyphens
        slug = re.sub(r"-+", "-", slug)

        return slug

    def create_document(
        self,
        doc_type: str,
        title: str,
        author: Optional[str] = None,
        description: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new design document.

        Args:
            doc_type: Document type (pdr, spec, feature, decision, architecture, template)
            title: Document title
            author: Optional author name
            description: Optional description
            filename: Optional custom filename (without extension)

        Returns:
            Result dictionary with success status and file info
        """
        # Validate type
        if doc_type not in self.VALID_TYPES:
            return {
                "success": False,
                "error": f"Invalid type '{doc_type}'. Valid types: {', '.join(self.VALID_TYPES)}",
            }

        # Generate UUID
        uuid = self.generate_uuid()

        # Generate filename
        if filename:
            safe_filename = self.slugify(filename)
        else:
            safe_filename = self.slugify(title)

        if not safe_filename:
            safe_filename = f"document-{uuid.split('-')[-1]}"

        # Determine file path
        type_dir = self.design_root / doc_type
        type_dir.mkdir(parents=True, exist_ok=True)

        file_path = type_dir / f"{safe_filename}.md"

        # Check if file already exists
        if file_path.exists():
            # Add UUID suffix to make unique
            file_path = type_dir / f"{safe_filename}-{uuid.split('-')[-1]}.md"

        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Build frontmatter
        frontmatter_lines = [
            "---",
            f"uuid: {uuid}",
            f"title: \"{title}\"",
            f"type: {doc_type}",
            "status: draft",
            f"created: {today}",
            f"updated: {today}",
        ]

        if author:
            frontmatter_lines.append(f"author: \"{author}\"")

        if description:
            frontmatter_lines.append(f"description: \"{description}\"")

        frontmatter_lines.append("---")
        frontmatter_lines.append("")

        # Get template content
        template = self.TEMPLATES.get(doc_type, self.TEMPLATES["template"])
        body = template.format(title=title)

        # Combine frontmatter and body
        content = "\n".join(frontmatter_lines) + body

        # Write file
        try:
            file_path.write_text(content, encoding="utf-8")
        except OSError as e:
            return {
                "success": False,
                "error": f"Failed to write file: {e}",
            }

        # Validate the created document
        validation = self._validate_created_document(file_path)

        # Compute relative path
        try:
            relative_path = file_path.relative_to(self.design_root.parent)
        except ValueError:
            relative_path = file_path

        return {
            "success": validation["valid"],
            "file_path": str(relative_path),
            "uuid": uuid,
            "title": title,
            "type": doc_type,
            "status": "draft",
            "created": today,
            "validation": validation,
        }

    def _validate_created_document(self, file_path: Path) -> Dict[str, Any]:
        """Validate a newly created document.

        Args:
            file_path: Path to the created document

        Returns:
            Validation result dictionary
        """
        errors: List[str] = []
        warnings: List[str] = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return {
                "valid": False,
                "errors": [f"Cannot read created file: {e}"],
                "warnings": [],
            }

        # Check frontmatter exists
        if not content.startswith("---"):
            errors.append("Missing frontmatter opening delimiter")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
            }

        # Check required fields in content
        required_fields = ["uuid", "title", "status", "created", "updated"]
        for field in required_fields:
            if f"{field}:" not in content:
                errors.append(f"Missing required field: {field}")

        # Check UUID format
        uuid_match = re.search(r"uuid:\s*['\"]?(GUUID-\d{8}-\d{4})['\"]?", content)
        if not uuid_match:
            errors.append("Invalid or missing UUID")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create new design documents from templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Create a PDR
    %(prog)s --type pdr --title "Authentication System Design"

    # Create a feature with author
    %(prog)s --type feature --title "OAuth Support" --author "John Doe"

    # Create a decision record with description
    %(prog)s --type decision --title "Database Selection" \\
        --description "ADR for choosing database technology"

    # Create with custom filename
    %(prog)s --type spec --title "API Specification" --filename "api-v2-spec"
        """,
    )

    parser.add_argument(
        "--type",
        dest="doc_type",
        required=True,
        choices=DesignDocumentCreator.VALID_TYPES,
        help="Document type",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Document title",
    )
    parser.add_argument(
        "--author",
        help="Author name",
    )
    parser.add_argument(
        "--description",
        help="Document description",
    )
    parser.add_argument(
        "--filename",
        help="Custom filename (without extension)",
    )
    parser.add_argument(
        "--design-dir",
        type=Path,
        help="Path to design directory (default: ../design from script location)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output-file",
        help="Write full JSON output to this file instead of stdout",
    )

    args = parser.parse_args()

    # Determine design directory
    if args.design_dir:
        design_dir = args.design_dir
    else:
        design_dir = Path(__file__).parent.parent / "design"

    # Create design directory if it doesn't exist
    design_dir.mkdir(parents=True, exist_ok=True)

    # Create document
    creator = DesignDocumentCreator(design_dir)
    result = creator.create_document(
        doc_type=args.doc_type,
        title=args.title,
        author=args.author,
        description=args.description,
        filename=args.filename,
    )

    # Output result
    if args.format == "json":
        write_output(result, "amia_design_create", args.output_file)
    else:
        if result["success"]:
            print(f"Created: {result['file_path']}")
            print(f"UUID: {result['uuid']}")
            print(f"Type: {result['type']}")
            print(f"Status: {result['status']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            if "validation" in result and result["validation"].get("errors"):
                for error in result["validation"]["errors"]:
                    print(f"  - {error}")

    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
