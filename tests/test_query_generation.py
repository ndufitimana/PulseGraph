#!/usr/bin/env python3
"""
Test script for LLM-based search query generation.

Usage:
    python3 tests/test_query_generation.py

    Or from project root:
    python3 -m tests.test_query_generation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from ingest.llm_query_gen import generate_search_query, generate_multi_source_queries


def test_basic_query_generation():
    """Test basic query generation for different scenarios."""

    client = OpenAI()

    print("=" * 80)
    print("Testing LLM-Based Search Query Generation")
    print("=" * 80)
    print()

    test_cases = [
        {
            "company_name": "NVIDIA",
            "ticker": "NVDA",
            "period": "Q3-2025",
            "event_type": "earnings",
            "source_type": "news",
            "industry": "semiconductors",
        },
        {
            "company_name": "Tesla",
            "ticker": "TSLA",
            "period": "Q4-2025",
            "event_type": "product_launch",
            "source_type": "news",
            "industry": "automotive",
        },
        {
            "company_name": "Microsoft",
            "ticker": "MSFT",
            "period": "Q1-2026",
            "event_type": "acquisition",
            "source_type": "news",
            "industry": "technology",
        },
        {
            "company_name": "Apple",
            "ticker": "AAPL",
            "period": "Q2-2025",
            "event_type": "earnings",
            "source_type": "blog",
            "industry": "consumer electronics",
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"  Company: {test_case['company_name']} ({test_case['ticker']})")
        print(f"  Period: {test_case['period']}")
        print(f"  Event Type: {test_case['event_type']}")
        print(f"  Source Type: {test_case['source_type']}")
        print(f"  Industry: {test_case['industry']}")
        print()

        query = generate_search_query(
            client=client,
            company_name=test_case["company_name"],
            ticker=test_case["ticker"],
            period=test_case["period"],
            event_type=test_case["event_type"],
            source_type=test_case["source_type"],
            industry=test_case["industry"],
        )

        print(f"  Primary Query:")
        print(f"    \"{query.primary_query}\"")
        print()

        if query.alternative_queries:
            print(f"  Alternative Queries:")
            for j, alt in enumerate(query.alternative_queries, 1):
                print(f"    {j}. \"{alt}\"")
            print()

        if query.keywords:
            print(f"  Keywords: {', '.join(query.keywords)}")
            print()

        print(f"  Reasoning: {query.reasoning}")
        print()
        print("-" * 80)
        print()


def test_multi_source_queries():
    """Test generating queries for multiple source types."""

    client = OpenAI()

    print("=" * 80)
    print("Testing Multi-Source Query Generation")
    print("=" * 80)
    print()

    print("Company: NVIDIA (NVDA)")
    print("Period: Q3-2025")
    print("Event: earnings")
    print("Source Types: news, blog, forum")
    print()

    queries = generate_multi_source_queries(
        client=client,
        company_name="NVIDIA",
        ticker="NVDA",
        period="Q3-2025",
        event_type="earnings",
        source_types=["news", "blog", "forum"],
        industry="semiconductors",
    )

    for source_type, query in queries.items():
        print(f"{source_type.upper()} Query:")
        print(f"  \"{query.primary_query}\"")
        print(f"  Keywords: {', '.join(query.keywords[:5])}")
        print()

    print("=" * 80)


def test_query_comparison():
    """Compare old hardcoded vs new LLM-based queries."""

    client = OpenAI()

    print("=" * 80)
    print("Comparison: Hardcoded vs LLM-Generated Queries")
    print("=" * 80)
    print()

    company = "NVIDIA"
    period = "Q3-2025"

    # Old hardcoded approach
    hardcoded_query = f"{company} {period} earnings recap guidance revenue EPS reaction"

    # New LLM approach
    llm_query = generate_search_query(
        client=client,
        company_name=company,
        ticker="NVDA",
        period=period,
        event_type="earnings",
        source_type="news",
        industry="semiconductors",
    )

    print(f"Company: {company}")
    print(f"Period: {period}")
    print(f"Event: earnings")
    print()

    print("HARDCODED Query (old approach):")
    print(f"  \"{hardcoded_query}\"")
    print()

    print("LLM-GENERATED Query (new approach):")
    print(f"  \"{llm_query.primary_query}\"")
    print(f"  Keywords: {', '.join(llm_query.keywords)}")
    print(f"  Reasoning: {llm_query.reasoning}")
    print()

    print("Benefits of LLM approach:")
    print("  ✓ Context-aware (knows NVIDIA is semiconductors)")
    print("  ✓ Industry-specific terms (AI, data center, GPU, etc.)")
    print("  ✓ Event-optimized keywords")
    print("  ✓ Alternative query suggestions")
    print("  ✓ Adaptable to any company/industry")
    print()

    print("=" * 80)


def test_event_types():
    """Test query generation for different event types."""

    client = OpenAI()

    print("=" * 80)
    print("Testing Different Event Types")
    print("=" * 80)
    print()

    event_types = ["earnings", "product_launch", "acquisition", "regulatory", "conference"]

    print("Company: Tesla (TSLA)")
    print("Period: Q4-2025")
    print()

    for event_type in event_types:
        query = generate_search_query(
            client=client,
            company_name="Tesla",
            ticker="TSLA",
            period="Q4-2025",
            event_type=event_type,
            source_type="news",
            industry="automotive",
        )

        print(f"{event_type.upper()}:")
        print(f"  \"{query.primary_query}\"")
        print()

    print("=" * 80)


if __name__ == "__main__":
    print()
    test_basic_query_generation()
    print()
    test_multi_source_queries()
    print()
    test_query_comparison()
    print()
    test_event_types()
    print()
    print("=" * 80)
    print("All Query Generation Tests Complete!")
    print("=" * 80)
