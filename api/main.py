from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager
from ingest.refresh import (
    refresh_company_period
)


from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

from graph.db import get_neo4j_driver
from graph.schema import ensure_schema
from graph.queries import (
    find_company_by_name,
    get_claims_with_sources,
    get_sentiment_delta,
    get_latest_fetch_by_type
)
from agent.freshness import (
    freshness_check
)
from extract.llm_entity import find_company_name_for_graph
from utils.periods import get_default_periods
from models.registry import (
    list_event_types_info,
    list_signal_types_info,
    validate_event_type,
    validate_signal_type,
    EventType,
    SignalType,
)

app = FastAPI(title="PulseGraph API", version="0.1.0")

# -------------------------
# Pydantic models
# -------------------------

class AskRequest(BaseModel):
    question: str = Field(..., description="User question")
    company: Optional[str] = Field(None, description="Company name override (optional)")
    period_a: Optional[str] = Field(None, description="Latest period (defaults to current quarter if not provided)")
    period_b: Optional[str] = Field(None, description="Comparison period (defaults to previous quarter if not provided)")
    window: str = Field("post_earnings_7d", description="Signal window label")
    signal_type: str = Field("sentiment", description="Type of signal to compare (default: sentiment)")
    event_type: str = Field("earnings", description="Type of event (default: earnings)")


class SourceOut(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    source_type: Optional[str] = None
    published_at: Optional[str] = None
    fetched_at: Optional[str] = None


class ClaimOut(BaseModel):
    id: str
    text: str
    claim_type: Optional[str] = None
    confidence: Optional[float] = None
    last_updated_at: Optional[str] = None
    sources: List[SourceOut] = []


class SentimentSignalOut(BaseModel):
    id: Optional[str] = None
    score: Optional[float] = None
    volume: Optional[int] = None
    window: Optional[str] = None
    computed_at: Optional[str] = None


class SentimentDeltaOut(BaseModel):
    period_a: str
    period_b: str
    window: str
    delta: Optional[float] = None
    a: Optional[SentimentSignalOut] = None
    b: Optional[SentimentSignalOut] = None
    note: Optional[str] = None


class FreshnessOut(BaseModel):
    was_stale: bool
    reason: str
    checked_at: str


class AskResponse(BaseModel):
    company: Dict[str, Any]
    period_a: str
    period_b: str
    sentiment: SentimentDeltaOut
    claims_a: List[ClaimOut]
    claims_b: List[ClaimOut]
    freshness: FreshnessOut


# -------------------------
# App lifecycle: Neo4j driver
# -------------------------

@app.on_event("startup")
def on_startup() -> None:
    driver = get_neo4j_driver()
    ensure_schema(driver)
    app.state.neo4j_driver = driver
    # Initialize OpenAI client for LLM-based entity extraction
    app.state.openai_client = OpenAI()


@app.on_event("shutdown")
def on_shutdown() -> None:
    driver = getattr(app.state, "neo4j_driver", None)
    if driver is not None:
        driver.close()


# -------------------------
# Routes
# -------------------------

@app.get("/")
async def root():
    return {"message": "PulseGraph API is running"}


@app.get("/event-types")
async def get_event_types():
    """
    Get list of all supported event types.

    Returns:
        List of event types with metadata
    """
    return {
        "event_types": list_event_types_info(),
        "count": len(list_event_types_info()),
    }


@app.get("/signal-types")
async def get_signal_types():
    """
    Get list of all supported signal types.

    Returns:
        List of signal types with metadata
    """
    return {
        "signal_types": list_signal_types_info(),
        "count": len(list_signal_types_info()),
    }


@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest, auto_refresh: bool = Query(False)):
    driver = getattr(app.state, "neo4j_driver", None)
    if driver is None:
        raise HTTPException(status_code=500, detail="Neo4j driver not initialized")

    openai_client = getattr(app.state, "openai_client", None)
    if openai_client is None:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized")

    # 1) determine company using LLM-based entity extraction
    company_name = payload.company
    if not company_name:
        # Use LLM to extract company from question
        company_name = find_company_name_for_graph(
            client=openai_client,
            question=payload.question,
            confidence_threshold=0.5,
        )

    if not company_name:
        raise HTTPException(
            status_code=400,
            detail="Could not infer company from question. Provide `company` in the request.",
        )

    company = find_company_by_name(driver, company_name)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company not found in graph: {company_name}")

    # 2) validate event and signal types
    if not validate_event_type(payload.event_type):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event type: {payload.event_type}. Use GET /event-types to see valid types.",
        )

    if not validate_signal_type(payload.signal_type):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid signal type: {payload.signal_type}. Use GET /signal-types to see valid types.",
        )

    # 3) determine periods using dynamic calculation
    period_a = payload.period_a
    period_b = payload.period_b

    # If either period is not provided, calculate defaults dynamically
    if not period_a or not period_b:
        default_a, default_b = get_default_periods()
        period_a = period_a or default_a
        period_b = period_b or default_b

    company_id = company["id"]

    # 4) freshness check (real, graph-backed)
    latest_a = get_latest_fetch_by_type(driver, company_id, period_a)
    latest_b = get_latest_fetch_by_type(driver, company_id, period_b)

    combined_latest = latest_a + latest_b
    freshness_raw = freshness_check(combined_latest)

    freshness = FreshnessOut(
        was_stale=freshness_raw["was_stale"],
        reason=(
            f"Stale source types detected: {freshness_raw['stale_types']}"
            if freshness_raw["was_stale"]
            else "All source data within freshness thresholds."
        ),
        checked_at=freshness_raw["checked_at"],
    )

    refresh_log = None
    if freshness.was_stale and auto_refresh:
        refresh_log = refresh_company_period(
            driver=driver,
            company_id=company_id,
            company_name=company["name"],
            period=period_a,
            source_types=freshness_raw["stale_types"],
        )

    # 5) query the graph
    claims_a_raw = get_claims_with_sources(driver, company_id, period_a, limit=15)
    claims_b_raw = get_claims_with_sources(driver, company_id, period_b, limit=15)

    # Use generic signal delta (supports all signal types)
    from graph.queries import get_signal_delta
    sentiment_raw = get_signal_delta(
        driver,
        company_id,
        period_a,
        period_b,
        window=payload.window,
        signal_type=payload.signal_type,
    )

    # 6) shape response
    def to_claim_out(row: Dict[str, Any]) -> ClaimOut:
        sources = [SourceOut(**s) for s in (row.get("sources") or []) if s]
        return ClaimOut(
            id=row["id"],
            text=row["text"],
            claim_type=row.get("claim_type"),
            confidence=row.get("confidence"),
            last_updated_at=row.get("last_updated_at"),
            sources=sources,
        )

    def to_signal_out(sig: Optional[Dict[str, Any]]) -> Optional[SentimentSignalOut]:
        if not sig:
            return None
        return SentimentSignalOut(
            id=sig.get("id"),
            score=sig.get("score"),
            volume=sig.get("volume"),
            window=sig.get("window"),
            computed_at=sig.get("computed_at"),
        )

    sentiment = SentimentDeltaOut(
        period_a=sentiment_raw["period_a"],
        period_b=sentiment_raw["period_b"],
        window=sentiment_raw["window"],
        delta=sentiment_raw.get("delta"),
        a=to_signal_out(sentiment_raw.get("a")),
        b=to_signal_out(sentiment_raw.get("b")),
        note=sentiment_raw.get("note"),
    )

    return AskResponse(
        company=company,
        period_a=period_a,
        period_b=period_b,
        sentiment=sentiment,
        claims_a=[to_claim_out(r) for r in claims_a_raw],
        claims_b=[to_claim_out(r) for r in claims_b_raw],
        freshness=freshness,
    )