"""
Event and Signal Type Registry.

This module provides a centralized registry for managing event types
and signal types, replacing hardcoded "earnings" and "sentiment" values.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class EventType(str, Enum):
    """
    Supported event types for companies.

    Each event type represents a significant company occurrence
    that can be tracked and analyzed.
    """
    EARNINGS = "earnings"
    PRODUCT_LAUNCH = "product_launch"
    ACQUISITION = "acquisition"
    REGULATORY = "regulatory"
    CONFERENCE = "conference"
    DIVIDEND = "dividend"
    STOCK_SPLIT = "stock_split"
    EXECUTIVE_CHANGE = "executive_change"
    LAWSUIT = "lawsuit"
    PARTNERSHIP = "partnership"


class SignalType(str, Enum):
    """
    Supported signal types for tracking company metrics.

    Each signal type represents a measurable metric that can be
    computed and compared across time periods.
    """
    SENTIMENT = "sentiment"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    SOCIAL_ENGAGEMENT = "social_engagement"
    ANALYST_RATING = "analyst_rating"
    NEWS_COVERAGE = "news_coverage"
    PRICE_MOMENTUM = "price_momentum"
    INSTITUTIONAL_FLOW = "institutional_flow"


@dataclass
class EventTypeMetadata:
    """Metadata describing an event type."""

    event_type: EventType
    display_name: str
    description: str
    typical_frequency: str  # e.g., "quarterly", "annual", "ad-hoc"
    default_window: str = "post_event_7d"
    requires_date: bool = True


@dataclass
class SignalTypeMetadata:
    """Metadata describing a signal type."""

    signal_type: SignalType
    display_name: str
    description: str
    unit: str  # e.g., "score", "percentage", "rating"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    higher_is_better: Optional[bool] = None


# Event Type Registry
EVENT_REGISTRY: Dict[EventType, EventTypeMetadata] = {
    EventType.EARNINGS: EventTypeMetadata(
        event_type=EventType.EARNINGS,
        display_name="Earnings Report",
        description="Quarterly or annual earnings report and earnings call",
        typical_frequency="quarterly",
        default_window="post_earnings_7d",
        requires_date=True,
    ),
    EventType.PRODUCT_LAUNCH: EventTypeMetadata(
        event_type=EventType.PRODUCT_LAUNCH,
        display_name="Product Launch",
        description="New product or service announcement and launch",
        typical_frequency="ad-hoc",
        default_window="post_event_14d",
        requires_date=True,
    ),
    EventType.ACQUISITION: EventTypeMetadata(
        event_type=EventType.ACQUISITION,
        display_name="Acquisition/Merger",
        description="M&A activity including announcements and closings",
        typical_frequency="ad-hoc",
        default_window="post_event_30d",
        requires_date=True,
    ),
    EventType.REGULATORY: EventTypeMetadata(
        event_type=EventType.REGULATORY,
        display_name="Regulatory Event",
        description="Regulatory filings, approvals, or compliance events",
        typical_frequency="quarterly",
        default_window="post_event_7d",
        requires_date=True,
    ),
    EventType.CONFERENCE: EventTypeMetadata(
        event_type=EventType.CONFERENCE,
        display_name="Conference/Presentation",
        description="Investor conferences, keynotes, and presentations",
        typical_frequency="ad-hoc",
        default_window="post_event_3d",
        requires_date=True,
    ),
    EventType.DIVIDEND: EventTypeMetadata(
        event_type=EventType.DIVIDEND,
        display_name="Dividend Announcement",
        description="Dividend declarations or changes",
        typical_frequency="quarterly",
        default_window="post_event_7d",
        requires_date=True,
    ),
    EventType.STOCK_SPLIT: EventTypeMetadata(
        event_type=EventType.STOCK_SPLIT,
        display_name="Stock Split",
        description="Stock split announcements and executions",
        typical_frequency="ad-hoc",
        default_window="post_event_14d",
        requires_date=True,
    ),
    EventType.EXECUTIVE_CHANGE: EventTypeMetadata(
        event_type=EventType.EXECUTIVE_CHANGE,
        display_name="Executive Change",
        description="CEO, CFO, or other C-suite appointments/departures",
        typical_frequency="ad-hoc",
        default_window="post_event_14d",
        requires_date=True,
    ),
    EventType.LAWSUIT: EventTypeMetadata(
        event_type=EventType.LAWSUIT,
        display_name="Legal Action",
        description="Lawsuits, legal settlements, or regulatory actions",
        typical_frequency="ad-hoc",
        default_window="post_event_30d",
        requires_date=True,
    ),
    EventType.PARTNERSHIP: EventTypeMetadata(
        event_type=EventType.PARTNERSHIP,
        display_name="Partnership/Alliance",
        description="Strategic partnerships or business alliances",
        typical_frequency="ad-hoc",
        default_window="post_event_14d",
        requires_date=True,
    ),
}


# Signal Type Registry
SIGNAL_REGISTRY: Dict[SignalType, SignalTypeMetadata] = {
    SignalType.SENTIMENT: SignalTypeMetadata(
        signal_type=SignalType.SENTIMENT,
        display_name="Sentiment Score",
        description="Aggregate sentiment from news, social media, and analyst commentary",
        unit="score",
        min_value=0.0,
        max_value=1.0,
        higher_is_better=True,
    ),
    SignalType.VOLATILITY: SignalTypeMetadata(
        signal_type=SignalType.VOLATILITY,
        display_name="Volatility Index",
        description="Stock price volatility measure",
        unit="percentage",
        min_value=0.0,
        max_value=None,
        higher_is_better=False,
    ),
    SignalType.VOLUME: SignalTypeMetadata(
        signal_type=SignalType.VOLUME,
        display_name="Trading Volume",
        description="Stock trading volume relative to average",
        unit="count",
        min_value=0.0,
        max_value=None,
        higher_is_better=None,  # Context-dependent
    ),
    SignalType.SOCIAL_ENGAGEMENT: SignalTypeMetadata(
        signal_type=SignalType.SOCIAL_ENGAGEMENT,
        display_name="Social Engagement",
        description="Social media mentions, likes, shares, and engagement",
        unit="score",
        min_value=0.0,
        max_value=1.0,
        higher_is_better=True,
    ),
    SignalType.ANALYST_RATING: SignalTypeMetadata(
        signal_type=SignalType.ANALYST_RATING,
        display_name="Analyst Rating",
        description="Aggregate analyst ratings and price targets",
        unit="rating",
        min_value=1.0,
        max_value=5.0,
        higher_is_better=True,
    ),
    SignalType.NEWS_COVERAGE: SignalTypeMetadata(
        signal_type=SignalType.NEWS_COVERAGE,
        display_name="News Coverage",
        description="Volume and prominence of news coverage",
        unit="score",
        min_value=0.0,
        max_value=1.0,
        higher_is_better=None,  # Context-dependent
    ),
    SignalType.PRICE_MOMENTUM: SignalTypeMetadata(
        signal_type=SignalType.PRICE_MOMENTUM,
        display_name="Price Momentum",
        description="Stock price momentum and trend strength",
        unit="score",
        min_value=-1.0,
        max_value=1.0,
        higher_is_better=True,
    ),
    SignalType.INSTITUTIONAL_FLOW: SignalTypeMetadata(
        signal_type=SignalType.INSTITUTIONAL_FLOW,
        display_name="Institutional Flow",
        description="Net institutional buying/selling activity",
        unit="score",
        min_value=-1.0,
        max_value=1.0,
        higher_is_better=True,
    ),
}


# Helper Functions

def get_event_types() -> List[EventType]:
    """Get list of all registered event types."""
    return list(EVENT_REGISTRY.keys())


def get_signal_types() -> List[SignalType]:
    """Get list of all registered signal types."""
    return list(SIGNAL_REGISTRY.keys())


def get_event_metadata(event_type: EventType) -> Optional[EventTypeMetadata]:
    """Get metadata for a specific event type."""
    return EVENT_REGISTRY.get(event_type)


def get_signal_metadata(signal_type: SignalType) -> Optional[SignalTypeMetadata]:
    """Get metadata for a specific signal type."""
    return SIGNAL_REGISTRY.get(signal_type)


def validate_event_type(event_type: str) -> bool:
    """Check if an event type string is valid."""
    try:
        EventType(event_type)
        return True
    except ValueError:
        return False


def validate_signal_type(signal_type: str) -> bool:
    """Check if a signal type string is valid."""
    try:
        SignalType(signal_type)
        return True
    except ValueError:
        return False


def get_default_window(event_type: EventType) -> str:
    """Get the default window for an event type."""
    metadata = get_event_metadata(event_type)
    return metadata.default_window if metadata else "post_event_7d"


def get_event_type_display_name(event_type: EventType) -> str:
    """Get human-readable display name for event type."""
    metadata = get_event_metadata(event_type)
    return metadata.display_name if metadata else event_type.value


def get_signal_type_display_name(signal_type: SignalType) -> str:
    """Get human-readable display name for signal type."""
    metadata = get_signal_metadata(signal_type)
    return metadata.display_name if metadata else signal_type.value


def list_event_types_info() -> List[Dict[str, str]]:
    """
    Get a list of all event types with their metadata.

    Returns:
        List of dicts with event type information
    """
    return [
        {
            "type": et.value,
            "display_name": meta.display_name,
            "description": meta.description,
            "frequency": meta.typical_frequency,
            "default_window": meta.default_window,
        }
        for et, meta in EVENT_REGISTRY.items()
    ]


def list_signal_types_info() -> List[Dict[str, str]]:
    """
    Get a list of all signal types with their metadata.

    Returns:
        List of dicts with signal type information
    """
    return [
        {
            "type": st.value,
            "display_name": meta.display_name,
            "description": meta.description,
            "unit": meta.unit,
            "range": f"{meta.min_value} to {meta.max_value}"
            if meta.min_value is not None
            else "unlimited",
        }
        for st, meta in SIGNAL_REGISTRY.items()
    ]
