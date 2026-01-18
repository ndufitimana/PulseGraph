#!/usr/bin/env python3
"""
Expanded seed script with more periods and companies.

This adds Q4-2025, Q3-2025, and Q1-2026 data for NVIDIA.
"""

from datetime import datetime, timezone

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from graph.db import get_neo4j_driver
from graph.schema import ensure_schema
from graph.upsert import (
    upsert_company,
    upsert_event,
    upsert_source,
    link_source_mentions_company,
    upsert_claim,
    upsert_signal,
)
from extract.contracts import SourceDoc


def main():
    driver = get_neo4j_driver()
    ensure_schema(driver)

    # Company
    company_id = upsert_company(driver, "NVIDIA", "NVDA")

    # Events for Q1-2026, Q4-2025, and Q3-2025
    ev_q1_2026 = upsert_event(
        driver,
        company_id,
        period="Q1-2026",
        event_date=datetime(2026, 2, 19, tzinfo=timezone.utc)
    )
    ev_q4_2025 = upsert_event(
        driver,
        company_id,
        period="Q4-2025",
        event_date=datetime(2025, 11, 20, tzinfo=timezone.utc)
    )
    ev_q3_2025 = upsert_event(
        driver,
        company_id,
        period="Q3-2025",
        event_date=datetime(2025, 8, 21, tzinfo=timezone.utc)
    )

    # Q1-2026 Data (Most Recent)
    print("Seeding Q1-2026 data...")
    doc_q1 = SourceDoc(
        url="https://example.com/nvda-q1-2026-earnings",
        title="NVIDIA Q1 2026 Earnings: Record Revenue from AI Chips",
        raw_text="NVIDIA reported record Q1 2026 revenue of $35 billion, up 15% from Q4 2025. AI data center revenue grew 25% quarter-over-quarter. The company raised guidance for Q2 2026 citing strong demand for Blackwell architecture GPUs. Gaming revenue remained flat but automotive revenue grew 30%.",
        source_type="news",
        fetched_at=datetime.now(timezone.utc),
        published_at=datetime(2026, 2, 19, tzinfo=timezone.utc),
        query="nvidia earnings Q1 2026 recap",
        site_name="Tech News Daily",
    )
    src_q1 = upsert_source(driver, doc_q1)
    link_source_mentions_company(driver, src_q1, company_id)

    upsert_claim(
        driver,
        company_id=company_id,
        event_id=ev_q1_2026,
        source_id=src_q1,
        text="Q1 2026 revenue reached $35 billion, up 15% from Q4 2025.",
        claim_type="revenue",
        confidence=0.92,
    )
    upsert_claim(
        driver,
        company_id=company_id,
        event_id=ev_q1_2026,
        source_id=src_q1,
        text="AI data center revenue grew 25% quarter-over-quarter.",
        claim_type="segment_growth",
        confidence=0.88,
    )
    upsert_claim(
        driver,
        company_id=company_id,
        event_id=ev_q1_2026,
        source_id=src_q1,
        text="Guidance was raised for Q2 2026 citing strong Blackwell GPU demand.",
        claim_type="guidance",
        confidence=0.85,
    )

    upsert_signal(
        driver,
        company_id,
        ev_q1_2026,
        "sentiment",
        score=0.78,  # Very positive
        volume=2500,
        window="post_earnings_7d"
    )

    # Q4-2025 Data
    print("Seeding Q4-2025 data...")
    doc_q4 = SourceDoc(
        url="https://example.com/nvda-q4-2025-earnings",
        title="NVIDIA Q4 2025 Earnings Beat Expectations on AI Demand",
        raw_text="NVIDIA exceeded Wall Street expectations in Q4 2025 with revenue of $30.5 billion. Data center revenue reached $25 billion driven by AI infrastructure buildout. The company maintained strong guidance for Q1 2026. Stock rose 5% in after-hours trading.",
        source_type="news",
        fetched_at=datetime.now(timezone.utc),
        published_at=datetime(2025, 11, 20, tzinfo=timezone.utc),
        query="nvidia earnings Q4 2025 recap",
        site_name="Financial Times",
    )
    src_q4 = upsert_source(driver, doc_q4)
    link_source_mentions_company(driver, src_q4, company_id)

    upsert_claim(
        driver,
        company_id=company_id,
        event_id=ev_q4_2025,
        source_id=src_q4,
        text="Q4 2025 revenue was $30.5 billion, beating analyst estimates.",
        claim_type="revenue",
        confidence=0.90,
    )
    upsert_claim(
        driver,
        company_id=company_id,
        event_id=ev_q4_2025,
        source_id=src_q4,
        text="Data center revenue reached $25 billion driven by AI infrastructure.",
        claim_type="segment_revenue",
        confidence=0.87,
    )
    upsert_claim(
        driver,
        company_id=company_id,
        event_id=ev_q4_2025,
        source_id=src_q4,
        text="Stock rose 5% in after-hours trading following earnings beat.",
        claim_type="market_reaction",
        confidence=0.82,
    )

    upsert_signal(
        driver,
        company_id,
        ev_q4_2025,
        "sentiment",
        score=0.72,  # Positive
        volume=2100,
        window="post_earnings_7d"
    )

    # Q3-2025 Data (refresh existing)
    print("Seeding Q3-2025 data...")
    doc_q3 = SourceDoc(
        url="https://example.com/nvda-q3-2025-earnings",
        title="NVIDIA Q3 2025: Strong AI Growth Continues",
        raw_text="NVIDIA posted strong Q3 2025 results with revenue of $28 billion. AI and data center demand remained robust. The company raised guidance for Q4 citing continued AI infrastructure investments. Gaming revenue showed modest growth.",
        source_type="news",
        fetched_at=datetime.now(timezone.utc),
        published_at=datetime(2025, 8, 21, tzinfo=timezone.utc),
        query="nvidia earnings Q3 2025 recap",
        site_name="Bloomberg",
    )
    src_q3 = upsert_source(driver, doc_q3)
    link_source_mentions_company(driver, src_q3, company_id)

    upsert_claim(
        driver,
        company_id=company_id,
        event_id=ev_q3_2025,
        source_id=src_q3,
        text="Q3 2025 revenue was $28 billion with strong AI growth.",
        claim_type="revenue",
        confidence=0.89,
    )
    upsert_claim(
        driver,
        company_id=company_id,
        event_id=ev_q3_2025,
        source_id=src_q3,
        text="Guidance was raised for Q4 2025 citing AI infrastructure investments.",
        claim_type="guidance",
        confidence=0.84,
    )

    upsert_signal(
        driver,
        company_id,
        ev_q3_2025,
        "sentiment",
        score=0.68,  # Positive
        volume=1800,
        window="post_earnings_7d"
    )

    print("\n✅ Seed complete!")
    print(f"   Company: NVIDIA (NVDA)")
    print(f"   Periods: Q1-2026, Q4-2025, Q3-2025")
    print(f"   Claims: 8 total")
    print(f"   Signals: 3 sentiment scores")
    print(f"\nNow you can query:")
    print(f'   - "How did NVIDIA perform in Q1 2026 vs Q4 2025?"')
    print(f'   - "How did NVIDIA perform in Q4 2025 vs Q3 2025?"')
    print(f'   - "What was NVIDIA\'s revenue trend?"')

    driver.close()


if __name__ == "__main__":
    main()
