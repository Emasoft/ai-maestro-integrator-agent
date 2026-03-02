#!/usr/bin/env python3
"""Review report generator for code reviews.

Generates comprehensive code review reports combining quick scan and deep dive results
according to the two-stage review methodology.

Usage:
    python review-report-generator.py --repo myproject --pr 123 --quick-scan scan.md
    python review-report-generator.py -r myproject -p 123 --scores 75 80 70 85 90 65 75 80
    python review-report-generator.py --template --output review-template.md
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

# Timeout for command execution (20 minutes as per CLAUDE.md)
COMMAND_TIMEOUT = 1200  # seconds


@dataclass
class ReviewReportInput:
    """Input parameters for review report generation."""

    repo_name: str
    pr_number: int
    reviewer_name: str = "Code Reviewer"
    quick_scan_file: Optional[Path] = None
    dimension_scores: Optional[List[int]] = None
    output_file: Optional[Path] = None


def generate_review_header(report_input: ReviewReportInput) -> str:
    """
    Generate review report header section.

    Args:
        report_input: ReviewReportInput dataclass

    Returns:
        Formatted header string
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = f"""DEEP DIVE CODE REVIEW
{"=" * 70}
Repository: {report_input.repo_name}
Pull Request: #{report_input.pr_number}
Reviewed by: {report_input.reviewer_name}
Review Date: {now}

"""
    return header


def generate_dimension_section() -> str:
    """
    Generate dimension analysis section template.

    Returns:
        Formatted dimension analysis template
    """
    dimensions = [
        ("FUNCTIONAL CORRECTNESS", "Does the code implement requirements correctly?"),
        ("ARCHITECTURE & DESIGN", "Is the structure sound and maintainable?"),
        ("CODE QUALITY", "Is the code clean, readable, and well-documented?"),
        ("PERFORMANCE", "Does the code perform adequately?"),
        ("SECURITY", "Are there vulnerabilities or compliance issues?"),
        ("TESTING", "Is there adequate test coverage?"),
        ("BACKWARD COMPATIBILITY", "Does it break existing interfaces?"),
        ("DOCUMENTATION", "Is it adequately documented?"),
    ]

    section = "DIMENSION ANALYSIS\n"
    section += "=" * 70 + "\n\n"

    for i, (dim_name, dim_desc) in enumerate(dimensions, 1):
        section += f"{i}. {dim_name}\n"
        section += f"   {dim_desc}\n"
        section += "   " + "-" * 65 + "\n"
        section += "   Status: [PASS/CONCERN/FAIL]\n"
        section += "   Score: [X/max]%\n"
        section += "   \n"
        section += "   Findings:\n"
        section += "   - \n"
        section += "   \n"
        section += "   Issues:\n"
        section += "   - \n"
        section += "   \n"
        section += "   Confidence: [X%]\n"
        section += "\n"

    return section


def generate_decision_section() -> str:
    """
    Generate final decision section template.

    Returns:
        Formatted decision section template
    """
    section = "FINAL DECISION\n"
    section += "=" * 70 + "\n"
    section += "Overall Confidence Score: [X%]\n"
    section += "\n"
    section += "Decision: [APPROVED ✅ / CONDITIONAL ⚠️  / REJECTED ❌]\n"
    section += "\n"
    section += "Decision Rationale:\n"
    section += "- \n"
    section += "\n"
    section += "Required Changes (if applicable):\n"
    section += "- \n"
    section += "\n"
    section += "Next Steps: [MERGE / REQUEST CHANGES / ESCALATE]\n"
    section += "- \n"
    section += "\n"

    return section


def generate_summary_section() -> str:
    """
    Generate executive summary section template.

    Returns:
        Formatted summary section template
    """
    section = "EXECUTIVE SUMMARY\n"
    section += "=" * 70 + "\n"
    section += "Overall Assessment: [Brief 2-3 sentence summary]\n"
    section += "\n"
    section += "Key Strengths:\n"
    section += "- \n"
    section += "\n"
    section += "Key Concerns:\n"
    section += "- \n"
    section += "\n"
    section += "Critical Blockers:\n"
    section += "- \n"
    section += "\n"

    return section


def generate_detailed_findings() -> str:
    """
    Generate detailed findings section template.

    Returns:
        Formatted detailed findings template
    """
    section = "DETAILED FINDINGS BY FILE\n"
    section += "=" * 70 + "\n\n"
    section += "### File: [filename]\n"
    section += "**Type**: [source/test/config/doc]\n"
    section += "**Changes**: [+X/-Y lines]\n"
    section += "\n"
    section += "**Issues**:\n"
    section += "- Line X: [Issue description]\n"
    section += "- Line Y: [Issue description]\n"
    section += "\n"
    section += "**Suggestions**:\n"
    section += "- [Suggestion]\n"
    section += "\n"
    section += "---\n\n"

    return section


def generate_recommendations() -> str:
    """
    Generate recommendations section template.

    Returns:
        Formatted recommendations template
    """
    section = "RECOMMENDATIONS\n"
    section += "=" * 70 + "\n\n"
    section += "Immediate Actions Required:\n"
    section += "1. \n"
    section += "\n"
    section += "Suggested Improvements (non-blocking):\n"
    section += "1. \n"
    section += "\n"
    section += "Follow-up Items:\n"
    section += "1. \n"
    section += "\n"

    return section


def generate_complete_template(report_input: ReviewReportInput) -> str:
    """
    Generate complete review report template.

    Args:
        report_input: ReviewReportInput dataclass

    Returns:
        Complete formatted review template
    """
    template = generate_review_header(report_input)
    template += generate_summary_section()
    template += "\n"
    template += generate_dimension_section()
    template += "\n"
    template += generate_decision_section()
    template += "\n"
    template += generate_detailed_findings()
    template += "\n"
    template += generate_recommendations()
    template += "\n"
    template += "=" * 70 + "\n"
    template += "Generated by review-report-generator.py\n"
    template += "Review Methodology: Two-Stage Code Review (Quick Scan + Deep Dive)\n"
    template += "=" * 70 + "\n"

    return template


def load_quick_scan(quick_scan_file: Path) -> str:
    """
    Load quick scan results from file.

    Args:
        quick_scan_file: Path to quick scan results file

    Returns:
        Quick scan content as string
    """
    if not quick_scan_file.exists():
        return f"[Quick scan file not found: {quick_scan_file}]\n"

    try:
        content = quick_scan_file.read_text(encoding="utf-8")
        return f"\n{'=' * 70}\nQUICK SCAN RESULTS\n{'=' * 70}\n\n{content}\n"
    except Exception as e:
        return f"[Error loading quick scan: {e}]\n"


def main() -> int:
    """Main entry point for review report generator."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive code review reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate template only
  %(prog)s --template --repo myproject --pr 123 --output review.md

  # Include quick scan results
  %(prog)s --repo myproject --pr 123 --quick-scan scan.md -o review.md

  # Generate with dimension scores
  %(prog)s -r myproject -p 123 --scores 75 80 70 85 90 65 75 80 -o review.md

  # Full review with all inputs
  %(prog)s -r myproject -p 123 --quick-scan scan.md --scores 75 80 70 85 90 65 75 80 --reviewer "John Doe" -o review.md
        """,
    )

    parser.add_argument("--repo", "-r", type=str, help="Repository name")

    parser.add_argument("--pr", "-p", type=int, help="Pull request number")

    parser.add_argument(
        "--reviewer",
        type=str,
        default="Code Reviewer",
        help='Reviewer name (default: "Code Reviewer")',
    )

    parser.add_argument(
        "--quick-scan", type=Path, help="Path to quick scan results file"
    )

    parser.add_argument(
        "--scores",
        "-s",
        type=int,
        nargs=8,
        help="8 dimension scores (optional, for filled template)",
    )

    parser.add_argument(
        "--template",
        "-t",
        action="store_true",
        help="Generate template only (no filled data)",
    )

    parser.add_argument(
        "--output", "-o", type=Path, help="Output file path (default: print to stdout)"
    )

    args = parser.parse_args()

    # Validate required arguments if not template mode
    if not args.template:
        if not args.repo or not args.pr:
            parser.error("--repo and --pr are required unless using --template")
            return 1

    # Create report input
    report_input = ReviewReportInput(
        repo_name=args.repo or "project-name",
        pr_number=args.pr or 0,
        reviewer_name=args.reviewer,
        quick_scan_file=args.quick_scan,
        dimension_scores=args.scores,
        output_file=args.output,
    )

    # Generate report
    report = generate_complete_template(report_input)

    # Append quick scan if provided
    if args.quick_scan:
        quick_scan_content = load_quick_scan(args.quick_scan)
        report += quick_scan_content

    # Output to file or stdout
    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Review report written to: {args.output}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
