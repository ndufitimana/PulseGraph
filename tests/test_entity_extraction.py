#!/usr/bin/env python3
"""
Quick test script for LLM-based company entity extraction.

Usage:
    python3 tests/test_entity_extraction.py

    Or from project root:
    python3 -m tests.test_entity_extraction
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI
from extract.llm_entity import extract_company_from_question, find_company_name_for_graph


def test_entity_extraction():
    """Test various question formats for company extraction."""

    client = OpenAI()

    test_cases = [
        # Clear mentions
        "How did NVIDIA perform in Q3 2025?",
        "What was Tesla's revenue guidance?",
        "Tell me about NVDA stock performance",
        "Did TSLA beat earnings?",

        # Company names in different cases
        "nvidia earnings recap",
        "Tesla stock analysis",

        # Ambiguous/No company
        "What are the market trends?",
        "Did the chipmaker beat expectations?",
        "How is the tech sector doing?",

        # Multiple companies (should pick the first/most prominent)
        "How does NVIDIA compare to AMD?",
    ]

    print("=" * 80)
    print("Testing LLM-based Company Entity Extraction")
    print("=" * 80)
    print()

    for question in test_cases:
        print(f"Question: \"{question}\"")

        # Test full extraction
        entity = extract_company_from_question(client=client, question=question)
        print(f"  Company: {entity.company_name or 'None'}")
        print(f"  Ticker: {entity.ticker or 'None'}")
        print(f"  Confidence: {entity.confidence:.2f}")
        print(f"  Reasoning: {entity.reasoning}")

        # Test graph lookup convenience function
        graph_name = find_company_name_for_graph(client=client, question=question)
        print(f"  → Graph lookup: {graph_name or 'None (below threshold)'}")
        print()

    print("=" * 80)


if __name__ == "__main__":
    test_entity_extraction()
