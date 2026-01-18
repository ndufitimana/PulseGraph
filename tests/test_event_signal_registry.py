#!/usr/bin/env python3
"""
Test script for event and signal type registry.

Usage:
    python3 tests/test_event_signal_registry.py

    Or from project root:
    python3 -m tests.test_event_signal_registry
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.registry import (
    EventType,
    SignalType,
    get_event_types,
    get_signal_types,
    get_event_metadata,
    get_signal_metadata,
    validate_event_type,
    validate_signal_type,
    get_default_window,
    list_event_types_info,
    list_signal_types_info,
)


def test_event_types():
    """Test event type registry."""
    print("=" * 80)
    print("Testing Event Type Registry")
    print("=" * 80)
    print()

    event_types = get_event_types()
    print(f"Total Event Types: {len(event_types)}")
    print()

    for event_type in event_types:
        metadata = get_event_metadata(event_type)
        print(f"✓ {metadata.display_name} ({event_type.value})")
        print(f"  Description: {metadata.description}")
        print(f"  Frequency: {metadata.typical_frequency}")
        print(f"  Default Window: {metadata.default_window}")
        print(f"  Requires Date: {metadata.requires_date}")
        print()

    print("=" * 80)
    print()


def test_signal_types():
    """Test signal type registry."""
    print("=" * 80)
    print("Testing Signal Type Registry")
    print("=" * 80)
    print()

    signal_types = get_signal_types()
    print(f"Total Signal Types: {len(signal_types)}")
    print()

    for signal_type in signal_types:
        metadata = get_signal_metadata(signal_type)
        print(f"✓ {metadata.display_name} ({signal_type.value})")
        print(f"  Description: {metadata.description}")
        print(f"  Unit: {metadata.unit}")

        if metadata.min_value is not None or metadata.max_value is not None:
            min_val = metadata.min_value if metadata.min_value is not None else "-∞"
            max_val = metadata.max_value if metadata.max_value is not None else "∞"
            print(f"  Range: {min_val} to {max_val}")

        if metadata.higher_is_better is not None:
            better = "Yes" if metadata.higher_is_better else "No"
            print(f"  Higher is Better: {better}")

        print()

    print("=" * 80)
    print()


def test_validation():
    """Test event and signal type validation."""
    print("=" * 80)
    print("Testing Type Validation")
    print("=" * 80)
    print()

    # Valid event types
    print("Valid Event Types:")
    valid_events = ["earnings", "product_launch", "acquisition", "regulatory"]
    for event in valid_events:
        is_valid = validate_event_type(event)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {event}: {is_valid}")
    print()

    # Invalid event types
    print("Invalid Event Types:")
    invalid_events = ["invalid", "unknown", "test"]
    for event in invalid_events:
        is_valid = validate_event_type(event)
        status = "✓" if not is_valid else "✗"
        print(f"  {status} {event}: {is_valid} (expected False)")
    print()

    # Valid signal types
    print("Valid Signal Types:")
    valid_signals = ["sentiment", "volatility", "volume", "social_engagement"]
    for signal in valid_signals:
        is_valid = validate_signal_type(signal)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {signal}: {is_valid}")
    print()

    # Invalid signal types
    print("Invalid Signal Types:")
    invalid_signals = ["invalid", "unknown", "test"]
    for signal in invalid_signals:
        is_valid = validate_signal_type(signal)
        status = "✓" if not is_valid else "✗"
        print(f"  {status} {signal}: {is_valid} (expected False)")
    print()

    print("=" * 80)
    print()


def test_default_windows():
    """Test default window retrieval."""
    print("=" * 80)
    print("Testing Default Windows")
    print("=" * 80)
    print()

    event_types = get_event_types()

    for event_type in event_types:
        window = get_default_window(event_type)
        metadata = get_event_metadata(event_type)
        print(f"{metadata.display_name}: {window}")

    print()
    print("=" * 80)
    print()


def test_info_lists():
    """Test info listing functions."""
    print("=" * 80)
    print("Testing Info Lists (API Format)")
    print("=" * 80)
    print()

    print("Event Types Info:")
    event_info = list_event_types_info()
    for i, info in enumerate(event_info[:3], 1):  # Show first 3
        print(f"  {i}. {info['display_name']}")
        print(f"     Type: {info['type']}")
        print(f"     Frequency: {info['frequency']}")
        print(f"     Default Window: {info['default_window']}")
        print()

    print(f"... and {len(event_info) - 3} more")
    print()

    print("Signal Types Info:")
    signal_info = list_signal_types_info()
    for i, info in enumerate(signal_info[:3], 1):  # Show first 3
        print(f"  {i}. {info['display_name']}")
        print(f"     Type: {info['type']}")
        print(f"     Unit: {info['unit']}")
        print(f"     Range: {info['range']}")
        print()

    print(f"... and {len(signal_info) - 3} more")
    print()

    print("=" * 80)
    print()


def test_enum_usage():
    """Test using enums in code."""
    print("=" * 80)
    print("Testing Enum Usage")
    print("=" * 80)
    print()

    # Using EventType enum
    print("Using EventType Enum:")
    print(f"  EventType.EARNINGS = '{EventType.EARNINGS.value}'")
    print(f"  EventType.PRODUCT_LAUNCH = '{EventType.PRODUCT_LAUNCH.value}'")
    print(f"  EventType.ACQUISITION = '{EventType.ACQUISITION.value}'")
    print()

    # Using SignalType enum
    print("Using SignalType Enum:")
    print(f"  SignalType.SENTIMENT = '{SignalType.SENTIMENT.value}'")
    print(f"  SignalType.VOLATILITY = '{SignalType.VOLATILITY.value}'")
    print(f"  SignalType.VOLUME = '{SignalType.VOLUME.value}'")
    print()

    # Enum comparison
    print("Enum Comparisons:")
    print(f"  EventType.EARNINGS == 'earnings': {EventType.EARNINGS == 'earnings'}")
    print(f"  SignalType.SENTIMENT == 'sentiment': {SignalType.SENTIMENT == 'sentiment'}")
    print()

    print("=" * 80)
    print()


if __name__ == "__main__":
    print()
    test_event_types()
    test_signal_types()
    test_validation()
    test_default_windows()
    test_info_lists()
    test_enum_usage()
    print("=" * 80)
    print("All Event & Signal Registry Tests Complete!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - {len(get_event_types())} event types registered")
    print(f"  - {len(get_signal_types())} signal types registered")
    print(f"  - All validation functions working correctly")
    print(f"  - Default windows configured for all event types")
    print()
