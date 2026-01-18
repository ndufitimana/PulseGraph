#!/usr/bin/env python3
"""
Test script for dynamic period calculation utilities.

Usage:
    python3 tests/test_periods.py

    Or from project root:
    python3 -m tests.test_periods
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timezone
from utils.periods import (
    get_current_quarter,
    get_previous_quarter,
    get_next_quarter,
    format_period,
    parse_period,
    get_latest_period,
    get_comparison_period,
    get_default_periods,
    get_period_offset,
    validate_period,
)


def test_current_quarter():
    """Test current quarter detection."""
    print("=" * 80)
    print("Testing Current Quarter Detection")
    print("=" * 80)

    # Test specific dates
    test_cases = [
        (datetime(2025, 1, 15, tzinfo=timezone.utc), (1, 2025), "Q1-2025"),
        (datetime(2025, 4, 1, tzinfo=timezone.utc), (2, 2025), "Q2-2025"),
        (datetime(2025, 7, 20, tzinfo=timezone.utc), (3, 2025), "Q3-2025"),
        (datetime(2025, 11, 20, tzinfo=timezone.utc), (4, 2025), "Q4-2025"),
        (datetime(2024, 12, 31, tzinfo=timezone.utc), (4, 2024), "Q4-2024"),
    ]

    for dt, expected_qy, expected_str in test_cases:
        q, y = get_current_quarter(dt)
        period_str = format_period(q, y)
        status = "✓" if (q, y) == expected_qy else "✗"
        print(f"{status} {dt.strftime('%Y-%m-%d')}: Q{q}-{y} (expected {expected_str})")

    print()


def test_quarter_navigation():
    """Test previous/next quarter calculation."""
    print("=" * 80)
    print("Testing Quarter Navigation")
    print("=" * 80)

    # Test previous quarter
    print("\nPrevious Quarter:")
    test_cases = [
        ((1, 2025), (4, 2024)),
        ((2, 2025), (1, 2025)),
        ((3, 2025), (2, 2025)),
        ((4, 2025), (3, 2025)),
    ]

    for (q, y), (exp_q, exp_y) in test_cases:
        prev_q, prev_y = get_previous_quarter(q, y)
        status = "✓" if (prev_q, prev_y) == (exp_q, exp_y) else "✗"
        print(f"{status} Q{q}-{y} → Q{prev_q}-{prev_y} (expected Q{exp_q}-{exp_y})")

    # Test next quarter
    print("\nNext Quarter:")
    test_cases = [
        ((1, 2025), (2, 2025)),
        ((2, 2025), (3, 2025)),
        ((3, 2025), (4, 2025)),
        ((4, 2025), (1, 2026)),
    ]

    for (q, y), (exp_q, exp_y) in test_cases:
        next_q, next_y = get_next_quarter(q, y)
        status = "✓" if (next_q, next_y) == (exp_q, exp_y) else "✗"
        print(f"{status} Q{q}-{y} → Q{next_q}-{next_y} (expected Q{exp_q}-{exp_y})")

    print()


def test_period_parsing():
    """Test period string parsing and formatting."""
    print("=" * 80)
    print("Testing Period Parsing and Formatting")
    print("=" * 80)

    # Test valid periods
    print("\nValid Periods:")
    valid_cases = [
        "Q1-2025",
        "Q2-2025",
        "Q3-2025",
        "Q4-2025",
        "Q1-2024",
    ]

    for period in valid_cases:
        q, y = parse_period(period)
        reconstructed = format_period(q, y)
        status = "✓" if reconstructed == period else "✗"
        print(f"{status} {period} → Q{q}, {y} → {reconstructed}")

    # Test invalid periods
    print("\nInvalid Periods:")
    invalid_cases = [
        "Q5-2025",
        "2025-Q3",
        "Q3",
        "invalid",
        "Q0-2025",
    ]

    for period in invalid_cases:
        is_valid = validate_period(period)
        status = "✓" if not is_valid else "✗"
        print(f"{status} {period} → Valid: {is_valid} (expected False)")

    print()


def test_default_periods():
    """Test default period calculation."""
    print("=" * 80)
    print("Testing Default Period Calculation")
    print("=" * 80)

    test_dates = [
        datetime(2025, 1, 15, tzinfo=timezone.utc),   # Q1-2025
        datetime(2025, 4, 1, tzinfo=timezone.utc),    # Q2-2025
        datetime(2025, 7, 20, tzinfo=timezone.utc),   # Q3-2025
        datetime(2025, 11, 20, tzinfo=timezone.utc),  # Q4-2025
    ]

    for dt in test_dates:
        period_a, period_b = get_default_periods(dt)
        latest = get_latest_period(dt)
        comparison = get_comparison_period(dt, periods_back=1)

        print(f"\nDate: {dt.strftime('%Y-%m-%d')}")
        print(f"  Latest Period (period_a): {period_a}")
        print(f"  Comparison Period (period_b): {period_b}")
        print(f"  Matches get_latest_period: {period_a == latest}")
        print(f"  Matches get_comparison_period: {period_b == comparison}")

    print()


def test_period_offset():
    """Test period offset calculation."""
    print("=" * 80)
    print("Testing Period Offset")
    print("=" * 80)

    base_period = "Q3-2025"

    print(f"\nBase Period: {base_period}\n")

    offsets = [-3, -2, -1, 0, 1, 2, 3]

    for offset in offsets:
        result = get_period_offset(base_period, offset)
        direction = "back" if offset < 0 else "forward" if offset > 0 else "same"
        print(f"  Offset {offset:+2d} ({direction:7s}): {result}")

    print()


def test_current_system():
    """Test with current system time."""
    print("=" * 80)
    print("Testing with Current System Time")
    print("=" * 80)

    now = datetime.now(timezone.utc)
    q, y = get_current_quarter()
    period_a, period_b = get_default_periods()

    print(f"\nCurrent UTC Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Current Quarter: Q{q}-{y}")
    print(f"API Default Periods:")
    print(f"  period_a (latest): {period_a}")
    print(f"  period_b (comparison): {period_b}")
    print()

    # Show comparison periods
    print("Comparison Periods (quarters back):")
    for i in range(1, 6):
        comp = get_comparison_period(periods_back=i)
        print(f"  {i} quarter(s) back: {comp}")

    print()


if __name__ == "__main__":
    test_current_quarter()
    test_quarter_navigation()
    test_period_parsing()
    test_default_periods()
    test_period_offset()
    test_current_system()

    print("=" * 80)
    print("All Period Tests Complete!")
    print("=" * 80)
