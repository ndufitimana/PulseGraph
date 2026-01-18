"""
Utilities for dynamic period calculation and management.

This module provides functions to calculate fiscal quarters and periods
dynamically based on the current date, eliminating hardcoded period values.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Tuple, Optional
from enum import Enum


class FiscalQuarter(Enum):
    """Fiscal quarter enumeration."""
    Q1 = 1
    Q2 = 2
    Q3 = 3
    Q4 = 4


def get_current_quarter(dt: Optional[datetime] = None) -> Tuple[int, int]:
    """
    Get the current fiscal quarter and year.

    Args:
        dt: Optional datetime to use. If None, uses current UTC time.

    Returns:
        Tuple of (quarter_number, year)
        - quarter_number: 1-4
        - year: YYYY

    Example:
        >>> get_current_quarter(datetime(2025, 11, 20, tzinfo=timezone.utc))
        (4, 2025)  # Q4-2025
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    month = dt.month

    # Standard calendar quarters
    if 1 <= month <= 3:
        quarter = 1
    elif 4 <= month <= 6:
        quarter = 2
    elif 7 <= month <= 9:
        quarter = 3
    else:  # 10-12
        quarter = 4

    return quarter, dt.year


def get_previous_quarter(quarter: int, year: int) -> Tuple[int, int]:
    """
    Get the previous quarter given a quarter and year.

    Args:
        quarter: Current quarter (1-4)
        year: Current year

    Returns:
        Tuple of (previous_quarter, previous_year)

    Example:
        >>> get_previous_quarter(1, 2025)
        (4, 2024)  # Q4-2024
        >>> get_previous_quarter(3, 2025)
        (2, 2025)  # Q2-2025
    """
    if quarter == 1:
        return (4, year - 1)
    else:
        return (quarter - 1, year)


def get_next_quarter(quarter: int, year: int) -> Tuple[int, int]:
    """
    Get the next quarter given a quarter and year.

    Args:
        quarter: Current quarter (1-4)
        year: Current year

    Returns:
        Tuple of (next_quarter, next_year)

    Example:
        >>> get_next_quarter(4, 2024)
        (1, 2025)  # Q1-2025
        >>> get_next_quarter(2, 2025)
        (3, 2025)  # Q3-2025
    """
    if quarter == 4:
        return (1, year + 1)
    else:
        return (quarter + 1, year)


def format_period(quarter: int, year: int) -> str:
    """
    Format a quarter and year as a period string.

    Args:
        quarter: Quarter number (1-4)
        year: Year (YYYY)

    Returns:
        Period string in format "Q[1-4]-YYYY"

    Example:
        >>> format_period(3, 2025)
        'Q3-2025'
    """
    if not 1 <= quarter <= 4:
        raise ValueError(f"Quarter must be 1-4, got {quarter}")

    return f"Q{quarter}-{year}"


def parse_period(period: str) -> Tuple[int, int]:
    """
    Parse a period string into quarter and year.

    Args:
        period: Period string in format "Q[1-4]-YYYY"

    Returns:
        Tuple of (quarter, year)

    Raises:
        ValueError: If period format is invalid

    Example:
        >>> parse_period("Q3-2025")
        (3, 2025)
    """
    try:
        parts = period.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid period format: {period}")

        quarter_str = parts[0]
        if not quarter_str.startswith("Q"):
            raise ValueError(f"Period must start with 'Q': {period}")

        quarter = int(quarter_str[1:])
        year = int(parts[1])

        if not 1 <= quarter <= 4:
            raise ValueError(f"Quarter must be 1-4: {period}")

        return quarter, year

    except (IndexError, ValueError) as e:
        raise ValueError(f"Invalid period format '{period}'. Expected 'Q[1-4]-YYYY'") from e


def get_latest_period(dt: Optional[datetime] = None) -> str:
    """
    Get the latest (current) period as a string.

    This assumes the "latest" period is the current quarter.

    Args:
        dt: Optional datetime to use. If None, uses current UTC time.

    Returns:
        Period string (e.g., "Q3-2025")

    Example:
        >>> # If current date is November 2025
        >>> get_latest_period()
        'Q4-2025'
    """
    quarter, year = get_current_quarter(dt)
    return format_period(quarter, year)


def get_comparison_period(dt: Optional[datetime] = None, periods_back: int = 1) -> str:
    """
    Get a comparison period (N quarters before the current period).

    Args:
        dt: Optional datetime to use. If None, uses current UTC time.
        periods_back: Number of quarters to go back (default: 1)

    Returns:
        Period string (e.g., "Q2-2025")

    Example:
        >>> # If current date is November 2025 (Q4-2025)
        >>> get_comparison_period(periods_back=1)
        'Q3-2025'
        >>> get_comparison_period(periods_back=2)
        'Q2-2025'
    """
    quarter, year = get_current_quarter(dt)

    for _ in range(periods_back):
        quarter, year = get_previous_quarter(quarter, year)

    return format_period(quarter, year)


def get_default_periods(dt: Optional[datetime] = None) -> Tuple[str, str]:
    """
    Get default periods for API requests (current and previous quarter).

    Args:
        dt: Optional datetime to use. If None, uses current UTC time.

    Returns:
        Tuple of (period_a, period_b) where:
        - period_a is the current/latest period
        - period_b is the previous period (1 quarter back)

    Example:
        >>> # If current date is November 2025 (Q4-2025)
        >>> get_default_periods()
        ('Q4-2025', 'Q3-2025')
    """
    period_a = get_latest_period(dt)
    period_b = get_comparison_period(dt, periods_back=1)
    return period_a, period_b


def get_period_offset(period: str, offset: int) -> str:
    """
    Get a period offset by N quarters from the given period.

    Args:
        period: Base period string (e.g., "Q3-2025")
        offset: Number of quarters to offset (positive = future, negative = past)

    Returns:
        Offset period string

    Example:
        >>> get_period_offset("Q3-2025", -1)
        'Q2-2025'
        >>> get_period_offset("Q3-2025", 2)
        'Q1-2026'
    """
    quarter, year = parse_period(period)

    if offset == 0:
        return period

    # Apply offset
    if offset > 0:
        for _ in range(offset):
            quarter, year = get_next_quarter(quarter, year)
    else:
        for _ in range(abs(offset)):
            quarter, year = get_previous_quarter(quarter, year)

    return format_period(quarter, year)


def validate_period(period: str) -> bool:
    """
    Validate that a period string is in the correct format.

    Args:
        period: Period string to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_period("Q3-2025")
        True
        >>> validate_period("Q5-2025")
        False
        >>> validate_period("2025-Q3")
        False
    """
    try:
        parse_period(period)
        return True
    except ValueError:
        return False
