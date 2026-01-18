from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional
import logging
from openai import OpenAI


from neo4j import Driver

from extract.contracts import SourceDoc
from extract.llm_claims import extract_claims_from_source_openai

from graph.upsert import upsert_source, link_source_mentions_company

from ingest.brightdata import google_serp_urls, unlock_to_markdown
from ingest.llm_query_gen import generate_search_query

from graph.upsert import upsert_claim_and_links


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def _earnings_query(company_name: str, period: str) -> str:
    """
    DEPRECATED: Legacy hardcoded query generation.
    Use generate_search_query from ingest.llm_query_gen instead.

    Kept for backwards compatibility only.
    """
    # Simple, effective first pass. You can tune later.
    return f'{company_name} {period} earnings recap guidance revenue EPS reaction'

def refresh_company_period(
    driver: Driver,
    company_id: str,
    company_name: str,
    period: str,
    source_types: Optional[List[str]] = None,
    event_type: str = "earnings",
    ticker: Optional[str] = None,
    industry: Optional[str] = None,
) -> Dict:
    """
    Refresh company data for a specific period by discovering and ingesting sources.

    Args:
        driver: Neo4j driver
        company_id: Company ID in graph
        company_name: Company name (e.g., "NVIDIA")
        period: Period identifier (e.g., "Q3-2025")
        source_types: List of source types to refresh (default: ["news"])
        event_type: Type of event (default: "earnings")
        ticker: Stock ticker symbol (optional)
        industry: Industry/sector (optional)

    Returns:
        Dictionary with refresh statistics
    """
    llm_client = OpenAI()
    source_types = source_types or ["news"]

    # 1) Generate intelligent search query using LLM
    query_obj = generate_search_query(
        client=llm_client,
        company_name=company_name,
        period=period,
        event_type=event_type,
        source_type=source_types[0],  # Use first source type for query generation
        ticker=ticker,
        industry=industry,
    )

    serp_query = query_obj.primary_query
    log.info("Generated search query: %s", serp_query)
    log.info("Query reasoning: %s", query_obj.reasoning)

    # 2) Discover URLs via SERP (use Google News vertical to bias toward coverage)
    serp_results = google_serp_urls(serp_query, max_results=5, tbm="nws")

    # 3) Fetch pages via Unlocker (markdown), normalize to SourceDoc, upsert
    upserted = 0
    docs: List[SourceDoc] = []
    errors: List[Dict] = []

    for r in serp_results:
        try:
            md = unlock_to_markdown(r.url, country="us")
            doc = SourceDoc(
                url=r.url,
                title=r.title or r.url,
                raw_text=md,
                source_type="news",
                fetched_at=datetime.now(timezone.utc),
                query=serp_query,
                site_name=None,
                metadata={
                    "serp_title": r.title,
                    "serp_description": r.description,
                    "serp_rank": r.rank,
                },
            )
            docs.append(doc)
            log.info("Fetched source %s (%d chars)", doc.url, len(doc.raw_text))
            source_id = upsert_source(driver, doc)

            # 4) Extract claims using OpenAI + upsert into graph
            claims = extract_claims_from_source_openai(
                client=llm_client,
                company_name=company_name,
                period=period,
                source=doc,
            )

            for claim in claims:
                upsert_claim_and_links(
                    driver,
                    company_id=company_id,
                    source_id=source_id,
                    period=period,
                    claim=claim,
                )

            link_source_mentions_company(driver, source_id, company_id)
            upserted += 1

        except Exception as e:
            errors.append({"url": r.url, "error": str(e)})
            raise e
            

    return {
        "company": company_name,
        "period": period,
        "event_type": event_type,
        "query": serp_query,
        "query_keywords": query_obj.keywords,
        "query_alternatives": query_obj.alternative_queries,
        "discovered_urls": len(serp_results),
        "fetched_docs": len(docs),
        "upserted_sources": upserted,
        "errors": errors[:3],  # keep response small
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
    }
