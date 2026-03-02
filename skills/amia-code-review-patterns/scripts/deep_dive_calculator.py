#!/usr/bin/env python3
"""Deep dive confidence score calculator for code reviews.

Calculates confidence scores across all 8 dimensions of code review and determines
final approval decision based on the two-stage review methodology.

Usage:
    python deep-dive-calculator.py --scores 75 80 70 85 90 65 75 80
    python deep-dive-calculator.py -s 75 80 70 85 90 65 75 80 --output report.json
    python deep-dive-calculator.py --interactive
"""

# WHY: Future annotations enable PEP 604 union syntax (X | Y) and forward references
# without quotes, improving type hint readability and Python 3.10+ compatibility
from __future__ import annotations

import sys
import json
import argparse
from pathlib import Path
from typing import List
from dataclasses import dataclass, field

# WHY: 20 minute timeout matches CLAUDE.md specification for long-running operations
COMMAND_TIMEOUT = 1200  # seconds


# WHY: Using a class with class-level constants provides namespace isolation and allows
# easy extension if thresholds need to become configurable in the future
# Code Review Thresholds
class CodeReviewThresholds:
    """Thresholds for code review confidence scoring."""

    # Confidence score thresholds
    QUICK_SCAN_THRESHOLD = 70  # Minimum to proceed to Stage Two
    APPROVAL_THRESHOLD = 80  # Minimum for approval
    CONDITIONAL_MIN = 60  # Minimum for conditional approval

    # Number of dimensions
    NUM_DIMENSIONS = 8

    # Dimension names
    DIMENSIONS = [
        "Functional Correctness",
        "Architecture & Design",
        "Code Quality",
        "Performance",
        "Security",
        "Testing",
        "Backward Compatibility",
        "Documentation",
    ]

    # Dimension weights (out of 100 each)
    DIMENSION_MAX_SCORES = {
        "Functional Correctness": 80,
        "Architecture & Design": 80,
        "Code Quality": 70,
        "Performance": 75,
        "Security": 75,
        "Testing": 75,
        "Backward Compatibility": 80,
        "Documentation": 70,
    }


# WHY: dataclass provides immutable, typed data containers with automatic __init__,
# __repr__, and __eq__ methods, reducing boilerplate while ensuring type safety
@dataclass
class DimensionScore:
    """Score for a single review dimension."""

    name: str
    score: int
    max_score: int
    status: str  # PASS, CONCERN, FAIL
    issues: List[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        """Calculate percentage score."""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100


@dataclass
class ReviewCalculation:
    """Complete review calculation result."""

    dimension_scores: List[DimensionScore]
    overall_confidence: float
    decision: str  # APPROVED, CONDITIONAL, REJECTED
    next_steps: str
    required_changes: List[str] = field(default_factory=list)


def classify_dimension_status(score: int, max_score: int) -> str:
    """
    Classify dimension status based on score percentage.

    Args:
        score: Actual score for the dimension
        max_score: Maximum possible score for the dimension

    Returns:
        Status classification: 'PASS', 'CONCERN', or 'FAIL'
    """
    if max_score == 0:
        return "FAIL"

    percentage = (score / max_score) * 100

    if percentage >= 80:
        return "PASS"
    elif percentage >= 60:
        return "CONCERN"
    else:
        return "FAIL"


def calculate_overall_confidence(dimension_scores: List[DimensionScore]) -> float:
    """
    Calculate overall confidence score from all dimensions.

    Args:
        dimension_scores: List of DimensionScore objects

    Returns:
        Overall confidence percentage (0-100)
    """
    if not dimension_scores:
        return 0.0

    total_percentage = sum(ds.percentage for ds in dimension_scores)
    return total_percentage / len(dimension_scores)


def determine_decision(confidence: float) -> tuple[str, str]:
    """
    Determine review decision based on confidence score.

    Args:
        confidence: Overall confidence percentage

    Returns:
        Tuple of (decision, next_steps)
    """
    if confidence >= CodeReviewThresholds.APPROVAL_THRESHOLD:
        return "APPROVED", "MERGE"
    elif confidence >= CodeReviewThresholds.CONDITIONAL_MIN:
        return "CONDITIONAL", "REQUEST CHANGES"
    else:
        return "REJECTED", "ESCALATE"


def calculate_deep_dive(scores: List[int]) -> ReviewCalculation:
    """
    Calculate deep dive review results from dimension scores.

    Args:
        scores: List of 8 integer scores (0-max for each dimension)

    Returns:
        ReviewCalculation object with complete results
    """
    if len(scores) != CodeReviewThresholds.NUM_DIMENSIONS:
        raise ValueError(
            f"Expected {CodeReviewThresholds.NUM_DIMENSIONS} scores, got {len(scores)}"
        )

    # Create dimension scores
    dimension_scores = []
    for i, (dim_name, score) in enumerate(zip(CodeReviewThresholds.DIMENSIONS, scores)):
        max_score = CodeReviewThresholds.DIMENSION_MAX_SCORES[dim_name]
        status = classify_dimension_status(score, max_score)

        dim_score = DimensionScore(
            name=dim_name, score=score, max_score=max_score, status=status
        )
        dimension_scores.append(dim_score)

    # Calculate overall confidence
    confidence = calculate_overall_confidence(dimension_scores)

    # Determine decision
    decision, next_steps = determine_decision(confidence)

    # Generate required changes list for non-approved reviews
    required_changes = []
    if decision != "APPROVED":
        for ds in dimension_scores:
            if ds.status in ["CONCERN", "FAIL"]:
                required_changes.append(
                    f"{ds.name}: Score {ds.score}/{ds.max_score} ({ds.percentage:.1f}%) - "
                    f"Requires improvement to >= 80%"
                )

    return ReviewCalculation(
        dimension_scores=dimension_scores,
        overall_confidence=confidence,
        decision=decision,
        next_steps=next_steps,
        required_changes=required_changes,
    )


def format_review_report(calc: ReviewCalculation) -> str:
    """
    Format review calculation as human-readable report.

    Args:
        calc: ReviewCalculation object

    Returns:
        Formatted report string
    """
    report = "DEEP DIVE CONFIDENCE CALCULATION\n"
    report += "=" * 50 + "\n\n"

    report += "DIMENSION SCORES:\n"
    report += "-" * 50 + "\n"

    for ds in calc.dimension_scores:
        status_symbol = {"PASS": "✓", "CONCERN": "⚠", "FAIL": "✗"}.get(ds.status, "?")

        report += f"{status_symbol} {ds.name}:\n"
        report += f"  Score: {ds.score}/{ds.max_score} ({ds.percentage:.1f}%)\n"
        report += f"  Status: {ds.status}\n"
        if ds.issues:
            report += "  Issues:\n"
            for issue in ds.issues:
                report += f"    - {issue}\n"
        report += "\n"

    report += "=" * 50 + "\n"
    report += f"OVERALL CONFIDENCE: {calc.overall_confidence:.1f}%\n"
    report += "=" * 50 + "\n\n"

    decision_symbol = {"APPROVED": "✅", "CONDITIONAL": "⚠️ ", "REJECTED": "❌"}.get(
        calc.decision, ""
    )

    report += f"DECISION: {decision_symbol} {calc.decision}\n"
    report += f"NEXT STEPS: {calc.next_steps}\n\n"

    if calc.required_changes:
        report += "REQUIRED CHANGES:\n"
        report += "-" * 50 + "\n"
        for change in calc.required_changes:
            report += f"- {change}\n"
        report += "\n"

    report += "=" * 50 + "\n"

    return report


# WHY: Verification after file writes ensures data integrity and catches silent failures
# like disk full, permission issues, or encoding problems before returning success
def verify_json_output(output_path: Path, expected_data: dict[str, object]) -> bool:
    """
    Verify that JSON output file was written correctly.

    Args:
        output_path: Path to the written JSON file
        expected_data: The data that was supposed to be written

    Returns:
        True if verification passes, False otherwise

    Raises:
        ValueError: If verification fails with details about the mismatch
    """
    if not output_path.exists():
        raise ValueError(f"Output file does not exist: {output_path}")

    try:
        written_data = json.loads(output_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Output file contains invalid JSON: {e}") from e
    except OSError as e:
        raise ValueError(f"Failed to read output file: {e}") from e

    # WHY: Deep comparison ensures complete data integrity, not just file existence
    if written_data != expected_data:
        raise ValueError("Written data does not match expected data")

    return True


def interactive_mode() -> List[int]:
    """
    Interactive mode for entering dimension scores.

    Returns:
        List of 8 dimension scores
    """
    print("DEEP DIVE INTERACTIVE SCORE ENTRY")
    print("=" * 50)
    print("Enter scores for each dimension (0-max):\n")

    scores = []
    for dim_name in CodeReviewThresholds.DIMENSIONS:
        max_score = CodeReviewThresholds.DIMENSION_MAX_SCORES[dim_name]

        while True:
            try:
                score_str = input(f"{dim_name} (0-{max_score}): ")
                score = int(score_str)

                if 0 <= score <= max_score:
                    scores.append(score)
                    break
                else:
                    print(f"Score must be between 0 and {max_score}")
            except ValueError:
                print("Please enter a valid integer")
            except (KeyboardInterrupt, EOFError):
                print("\nInteractive mode cancelled")
                sys.exit(1)

    return scores


# WHY: Returning int from main follows Unix convention (0=success, non-zero=error)
# and enables proper exit code propagation when run as a subprocess
def main() -> int:
    """Main entry point for deep dive calculator."""
    parser = argparse.ArgumentParser(
        description="Calculate deep dive confidence scores for code reviews",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Dimension order for --scores:
  1. Functional Correctness (0-{CodeReviewThresholds.DIMENSION_MAX_SCORES["Functional Correctness"]})
  2. Architecture & Design (0-{CodeReviewThresholds.DIMENSION_MAX_SCORES["Architecture & Design"]})
  3. Code Quality (0-{CodeReviewThresholds.DIMENSION_MAX_SCORES["Code Quality"]})
  4. Performance (0-{CodeReviewThresholds.DIMENSION_MAX_SCORES["Performance"]})
  5. Security (0-{CodeReviewThresholds.DIMENSION_MAX_SCORES["Security"]})
  6. Testing (0-{CodeReviewThresholds.DIMENSION_MAX_SCORES["Testing"]})
  7. Backward Compatibility (0-{CodeReviewThresholds.DIMENSION_MAX_SCORES["Backward Compatibility"]})
  8. Documentation (0-{CodeReviewThresholds.DIMENSION_MAX_SCORES["Documentation"]})

Examples:
  %(prog)s --scores 75 80 70 85 90 65 75 80
  %(prog)s -s 75 80 70 85 90 65 75 80 --output report.json
  %(prog)s --interactive
        """,
    )

    parser.add_argument(
        "--scores",
        "-s",
        type=int,
        nargs=8,
        help="8 dimension scores in order (see below)",
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive mode for entering scores",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file path for JSON report (default: print to stdout)",
    )

    args = parser.parse_args()

    # Get scores from arguments or interactive mode
    if args.interactive:
        scores = interactive_mode()
    elif args.scores:
        scores = args.scores
    else:
        parser.error("Either --scores or --interactive must be specified")
        return 1

    # Calculate review
    try:
        calc = calculate_deep_dive(scores)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Generate report
    report_text = format_review_report(calc)
    print(report_text)

    # Output JSON if requested
    if args.output:
        output_data = {
            "dimensions": [
                {
                    "name": ds.name,
                    "score": ds.score,
                    "max_score": ds.max_score,
                    "percentage": ds.percentage,
                    "status": ds.status,
                    "issues": ds.issues,
                }
                for ds in calc.dimension_scores
            ],
            "overall_confidence": calc.overall_confidence,
            "decision": calc.decision,
            "next_steps": calc.next_steps,
            "required_changes": calc.required_changes,
        }

        args.output.write_text(json.dumps(output_data, indent=2), encoding="utf-8")

        # WHY: Verify file was written correctly to catch silent failures
        try:
            verify_json_output(args.output, output_data)
            print(f"\nJSON report written and verified: {args.output}")
        except ValueError as e:
            print(f"Error: File verification failed: {e}", file=sys.stderr)
            return 1

    # WHY: Explicit success exit ensures proper exit code even if called as module
    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main())
