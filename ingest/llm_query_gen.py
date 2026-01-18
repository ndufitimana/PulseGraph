"""
LLM-based dynamic search query generation.

This module replaces hardcoded search queries with intelligent, context-aware
query generation using LLMs. Queries are optimized based on:
- Company name and industry
- Event type (earnings, product launch, acquisition, etc.)
- Period/timeframe
- Source type (news, blogs, forums, etc.)
"""

from __future__ import annotations

from typing import Optional, List
from openai import OpenAI
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Structured output for search query generation."""

    primary_query: str = Field(
        ...,
        description="The main search query optimized for finding relevant content"
    )

    alternative_queries: List[str] = Field(
        default_factory=list,
        max_length=3,
        description="Alternative query formulations (max 3)"
    )

    keywords: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Key search terms and concepts (max 10)"
    )

    reasoning: str = Field(
        default="",
        description="Brief explanation of query design choices"
    )


def generate_search_query(
    *,
    client: OpenAI,
    company_name: str,
    period: str,
    event_type: str = "earnings",
    source_type: str = "news",
    ticker: Optional[str] = None,
    industry: Optional[str] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.3,
) -> SearchQuery:
    """
    Generate an intelligent search query for finding company event information.

    Args:
        client: OpenAI client instance
        company_name: Company name (e.g., "NVIDIA", "Tesla")
        period: Period identifier (e.g., "Q3-2025", "2025-Q3")
        event_type: Type of event (default: "earnings")
            - "earnings": Quarterly earnings reports
            - "product_launch": Product announcements
            - "acquisition": M&A activity
            - "regulatory": Regulatory filings/events
            - "conference": Earnings calls, investor days
        source_type: Target source type (default: "news")
            - "news": News articles
            - "blog": Blog posts and analysis
            - "forum": Discussion forums
            - "social": Social media
            - "filing": Regulatory filings
        ticker: Stock ticker symbol (optional, e.g., "NVDA")
        industry: Industry/sector (optional, e.g., "semiconductors", "automotive")
        model: LLM model to use (default: "gpt-4o-mini")
        temperature: Sampling temperature (default: 0.3 for focused creativity)

    Returns:
        SearchQuery with primary query, alternatives, keywords, and reasoning

    Example:
        >>> client = OpenAI()
        >>> query = generate_search_query(
        ...     client=client,
        ...     company_name="NVIDIA",
        ...     period="Q3-2025",
        ...     event_type="earnings",
        ...     ticker="NVDA",
        ...     industry="semiconductors"
        ... )
        >>> print(query.primary_query)
        "NVIDIA Q3 2025 earnings results revenue guidance AI data center growth"
    """

    # Build context information
    context_parts = [f"Company: {company_name}"]
    if ticker:
        context_parts.append(f"Ticker: {ticker}")
    if industry:
        context_parts.append(f"Industry: {industry}")
    context_parts.append(f"Period: {period}")
    context_parts.append(f"Event Type: {event_type}")
    context_parts.append(f"Source Type: {source_type}")

    context = "\n".join(context_parts)

    # Event-specific guidance
    event_guidance = {
        "earnings": """
Focus on: quarterly results, revenue, earnings per share (EPS), guidance,
analyst reactions, beat/miss, outlook, growth metrics, key segments performance.
""",
        "product_launch": """
Focus on: new product announcements, features, pricing, availability,
market reception, competitive positioning, innovation, specifications.
""",
        "acquisition": """
Focus on: M&A deals, acquisition terms, strategic rationale, integration plans,
regulatory approval, deal value, market impact, synergies.
""",
        "regulatory": """
Focus on: SEC filings, compliance updates, regulatory changes, government actions,
legal proceedings, policy impacts, disclosure requirements.
""",
        "conference": """
Focus on: earnings calls, investor presentations, conference keynotes, Q&A sessions,
management commentary, strategic updates, analyst questions.
""",
    }

    # Source-specific guidance
    source_guidance = {
        "news": "Optimize for breaking news coverage, press releases, and journalist analysis.",
        "blog": "Target in-depth analysis, expert commentary, and thought leadership.",
        "forum": "Focus on community discussions, retail investor sentiment, and debates.",
        "social": "Capture real-time reactions, trending topics, and viral content.",
        "filing": "Target official documents, SEC filings, and regulatory disclosures.",
    }

    prompt = f"""
Generate an optimized search query to find information about a company event.

Context:
{context}

Event Type Guidance:
{event_guidance.get(event_type, "General event coverage.")}

Source Type Guidance:
{source_guidance.get(source_type, "General web content.")}

Requirements:
1. Create a primary query that will find the most relevant {source_type} content
2. Include company name/ticker and period clearly
3. Add event-specific keywords that journalists/analysts would use
4. Keep queries concise (8-15 words optimal for search engines)
5. Avoid overly generic terms; be specific to the event and timeframe
6. Consider synonyms and alternative phrasings (for alternative_queries)
7. Extract 5-10 key search terms/concepts (for keywords field)

Examples of good queries:
- For NVIDIA Q3-2025 earnings: "NVIDIA Q3 2025 earnings results revenue guidance AI data center"
- For Tesla product launch: "Tesla 2025 new model launch specifications pricing availability"
- For Microsoft acquisition: "Microsoft 2025 acquisition deal terms regulatory approval impact"

Generate a search query that maximizes recall of relevant {source_type} content about
{company_name}'s {event_type} for period {period}.
"""

    try:
        resp = client.responses.parse(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": "You are an expert at crafting search queries that maximize relevant results from search engines and news databases. You understand how journalists, analysts, and content creators write about business events."
                },
                {"role": "user", "content": prompt},
            ],
            text_format=SearchQuery,
            temperature=temperature,
            max_output_tokens=300,
        )

        query: SearchQuery = resp.output_parsed
        return query

    except Exception as e:
        # Fallback to basic query if LLM fails
        fallback_query = _fallback_query(
            company_name=company_name,
            period=period,
            event_type=event_type,
            ticker=ticker
        )

        return SearchQuery(
            primary_query=fallback_query,
            alternative_queries=[],
            keywords=[company_name, period, event_type],
            reasoning=f"Fallback query (LLM generation failed: {str(e)})"
        )


def _fallback_query(
    company_name: str,
    period: str,
    event_type: str,
    ticker: Optional[str] = None,
) -> str:
    """
    Generate a basic fallback query if LLM generation fails.

    This is similar to the old hardcoded approach but slightly improved.
    """
    company_identifier = f"{company_name} {ticker}" if ticker else company_name

    if event_type == "earnings":
        return f"{company_identifier} {period} earnings results revenue EPS guidance"
    elif event_type == "product_launch":
        return f"{company_identifier} {period} product launch announcement"
    elif event_type == "acquisition":
        return f"{company_identifier} {period} acquisition merger deal"
    elif event_type == "regulatory":
        return f"{company_identifier} {period} SEC filing regulatory disclosure"
    elif event_type == "conference":
        return f"{company_identifier} {period} earnings call investor conference"
    else:
        # Generic fallback
        return f"{company_identifier} {period} {event_type}"


def generate_multi_source_queries(
    *,
    client: OpenAI,
    company_name: str,
    period: str,
    event_type: str = "earnings",
    source_types: List[str] = None,
    ticker: Optional[str] = None,
    industry: Optional[str] = None,
    model: str = "gpt-4o-mini",
) -> dict[str, SearchQuery]:
    """
    Generate optimized queries for multiple source types.

    Args:
        client: OpenAI client instance
        company_name: Company name
        period: Period identifier
        event_type: Type of event
        source_types: List of source types to generate queries for
        ticker: Stock ticker (optional)
        industry: Industry/sector (optional)
        model: LLM model to use

    Returns:
        Dictionary mapping source_type -> SearchQuery

    Example:
        >>> queries = generate_multi_source_queries(
        ...     client=client,
        ...     company_name="NVIDIA",
        ...     period="Q3-2025",
        ...     source_types=["news", "blog", "forum"]
        ... )
        >>> print(queries["news"].primary_query)
        >>> print(queries["blog"].primary_query)
    """
    source_types = source_types or ["news"]

    queries = {}
    for source_type in source_types:
        queries[source_type] = generate_search_query(
            client=client,
            company_name=company_name,
            period=period,
            event_type=event_type,
            source_type=source_type,
            ticker=ticker,
            industry=industry,
            model=model,
        )

    return queries
