#!/usr/bin/env python3
"""
Design Document Search Tool - Search design documents by UUID, type, status, or keyword.

This script provides structured search capabilities for design documents stored in the
design/ directory hierarchy. It parses YAML frontmatter to extract metadata and supports
glob patterns for flexible file matching.

Usage:
    python amia_design_search.py --uuid GUUID-20250129-0001
    python amia_design_search.py --type pdr --status draft
    python amia_design_search.py --keyword "authentication"
    python amia_design_search.py --pattern "design/pdr/*.md"

Output Format (JSON):
    {
        "results": [
            {
                "file_path": "design/pdr/auth-system.md",
                "uuid": "GUUID-20250129-0001",
                "title": "Authentication System Design",
                "type": "pdr",
                "status": "approved",
                "created": "2025-01-29",
                "updated": "2025-01-29"
            }
        ],
        "total": 1,
        "search_params": {...}
    }
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, cast


class DesignDocumentSearcher:
    """Search design documents with structured queries."""

    # Valid document types matching design/ subdirectories
    VALID_TYPES = ["pdr", "spec", "feature", "decision", "architecture", "template"]

    # Valid status values for design documents
    VALID_STATUSES = ["draft", "review", "approved", "implemented", "deprecated", "rejected"]

    # UUID format: GUUID-YYYYMMDD-NNNN
    UUID_PATTERN = re.compile(r"^GUUID-\d{8}-\d{4}$")

    def __init__(self, design_root: Path):
        """Initialize searcher with design root directory.

        Args:
            design_root: Path to the design/ directory containing document subdirectories
        """
        self.design_root = design_root

    def parse_frontmatter(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse YAML frontmatter from a markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            Dictionary of frontmatter fields, or None if parsing fails
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
            return None

        # Check for frontmatter delimiters
        if not content.startswith("---"):
            return None

        # Find the closing delimiter
        lines = content.split("\n")
        end_idx = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                end_idx = i
                break

        if end_idx is None:
            return None

        # Parse YAML frontmatter (simple key: value parsing, no external deps)
        frontmatter: Dict[str, Any] = {}
        frontmatter["_file_path"] = str(file_path)

        for line in lines[1:end_idx]:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Simple key: value parsing
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                frontmatter[key] = value

        return frontmatter if frontmatter else None

    def search(
        self,
        uuid: Optional[str] = None,
        doc_type: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        pattern: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search design documents with the specified criteria.

        Args:
            uuid: Exact UUID to match (GUUID-YYYYMMDD-NNNN format)
            doc_type: Document type (pdr, spec, feature, decision, architecture, template)
            status: Document status (draft, review, approved, implemented, deprecated, rejected)
            keyword: Keyword to search in title and content
            pattern: Glob pattern for file matching (relative to design root)

        Returns:
            Dictionary with search results and metadata
        """
        results: List[Dict[str, Any]] = []
        search_params = {
            "uuid": uuid,
            "type": doc_type,
            "status": status,
            "keyword": keyword,
            "pattern": pattern,
        }

        # Validate inputs
        if uuid and not self.UUID_PATTERN.match(uuid):
            return {
                "error": f"Invalid UUID format: {uuid}. Expected: GUUID-YYYYMMDD-NNNN",
                "results": [],
                "total": 0,
                "search_params": search_params,
            }

        if doc_type and doc_type not in self.VALID_TYPES:
            return {
                "error": f"Invalid type: {doc_type}. Valid types: {', '.join(self.VALID_TYPES)}",
                "results": [],
                "total": 0,
                "search_params": search_params,
            }

        if status and status not in self.VALID_STATUSES:
            return {
                "error": f"Invalid status: {status}. Valid statuses: {', '.join(self.VALID_STATUSES)}",
                "results": [],
                "total": 0,
                "search_params": search_params,
            }

        # Determine files to search
        if pattern:
            files = list(self.design_root.glob(pattern))
        elif doc_type:
            type_dir = self.design_root / doc_type
            if type_dir.exists():
                files = list(type_dir.glob("**/*.md"))
            else:
                files = []
        else:
            files = list(self.design_root.glob("**/*.md"))

        # Filter out non-markdown files
        files = [f for f in files if f.suffix == ".md" and f.is_file()]

        # Process each file
        for file_path in files:
            frontmatter = self.parse_frontmatter(file_path)
            if frontmatter is None:
                continue

            # Apply filters
            if uuid and frontmatter.get("uuid") != uuid:
                continue

            if doc_type:
                # Infer type from path if not in frontmatter
                inferred_type = frontmatter.get("type")
                if not inferred_type:
                    # Get type from parent directory
                    relative = file_path.relative_to(self.design_root)
                    if relative.parts:
                        inferred_type = relative.parts[0]
                if inferred_type != doc_type:
                    continue

            if status and frontmatter.get("status") != status:
                continue

            if keyword:
                # Search in title and content
                title = frontmatter.get("title", "")
                try:
                    content = file_path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    print(f"WARNING: Could not read {file_path}, skipping", file=sys.stderr)
                    content = ""

                keyword_lower = keyword.lower()
                if keyword_lower not in title.lower() and keyword_lower not in content.lower():
                    continue

            # Build result entry
            relative_path = file_path.relative_to(self.design_root.parent)
            result_entry = {
                "file_path": str(relative_path),
                "uuid": frontmatter.get("uuid", ""),
                "title": frontmatter.get("title", file_path.stem),
                "type": self._infer_type(file_path, frontmatter),
                "status": frontmatter.get("status", "unknown"),
                "created": frontmatter.get("created", ""),
                "updated": frontmatter.get("updated", ""),
            }
            results.append(result_entry)

        # Sort by updated date (most recent first)
        results.sort(key=lambda x: x.get("updated", ""), reverse=True)

        return {
            "results": results,
            "total": len(results),
            "search_params": search_params,
        }

    def _infer_type(self, file_path: Path, frontmatter: Dict[str, Any]) -> str:
        """Infer document type from frontmatter or path.

        Args:
            file_path: Path to the document
            frontmatter: Parsed frontmatter dictionary

        Returns:
            Document type string
        """
        if "type" in frontmatter:
            return cast(str, frontmatter["type"])

        try:
            relative = file_path.relative_to(self.design_root)
            if relative.parts and relative.parts[0] in self.VALID_TYPES:
                return relative.parts[0]
        except ValueError:
            pass

        return "unknown"


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Search design documents by UUID, type, status, or keyword",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Search by UUID
    %(prog)s --uuid GUUID-20250129-0001

    # Search by type and status
    %(prog)s --type pdr --status approved

    # Search by keyword
    %(prog)s --keyword "authentication"

    # Use glob pattern
    %(prog)s --pattern "pdr/*.md"

    # Combine filters
    %(prog)s --type feature --status draft --keyword "API"
        """,
    )

    parser.add_argument(
        "--uuid",
        help="Exact UUID to match (format: GUUID-YYYYMMDD-NNNN)",
    )
    parser.add_argument(
        "--type",
        dest="doc_type",
        choices=DesignDocumentSearcher.VALID_TYPES,
        help="Document type to filter",
    )
    parser.add_argument(
        "--status",
        choices=DesignDocumentSearcher.VALID_STATUSES,
        help="Document status to filter",
    )
    parser.add_argument(
        "--keyword",
        help="Keyword to search in title and content",
    )
    parser.add_argument(
        "--pattern",
        help="Glob pattern for file matching (relative to design root)",
    )
    parser.add_argument(
        "--design-dir",
        type=Path,
        help="Path to design directory (default: ../design from script location)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()

    # Determine design directory
    if args.design_dir:
        design_dir = args.design_dir
    else:
        design_dir = Path(__file__).parent.parent / "design"

    if not design_dir.exists():
        print(json.dumps({"error": f"Design directory not found: {design_dir}", "results": [], "total": 0}))
        sys.exit(1)

    # Perform search
    searcher = DesignDocumentSearcher(design_dir)
    results = searcher.search(
        uuid=args.uuid,
        doc_type=args.doc_type,
        status=args.status,
        keyword=args.keyword,
        pattern=args.pattern,
    )

    # Output results
    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        # Table format
        if "error" in results:
            print(f"Error: {results['error']}")
            sys.exit(1)

        if not results["results"]:
            print("No documents found matching criteria.")
            sys.exit(0)

        # Print table header
        print(f"{'UUID':<22} {'Type':<12} {'Status':<12} {'Title':<40} {'Updated':<12}")
        print("-" * 100)

        for doc in results["results"]:
            title = doc["title"][:37] + "..." if len(doc["title"]) > 40 else doc["title"]
            print(f"{doc['uuid']:<22} {doc['type']:<12} {doc['status']:<12} {title:<40} {doc['updated']:<12}")

        print(f"\nTotal: {results['total']} document(s)")

    # Exit with error if search had issues
    if "error" in results:
        sys.exit(1)


if __name__ == "__main__":
    main()
