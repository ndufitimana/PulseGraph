from __future__ import annotations

from typing import Optional
from openai import OpenAI
from pydantic import BaseModel, Field


class CompanyEntity(BaseModel):
    """Structured output for company entity extraction."""
    company_name: Optional[str] = Field(
        None,
        description="The full company name mentioned in the question (e.g., 'NVIDIA Corporation', 'Tesla Inc')"
    )
    ticker: Optional[str] = Field(
        None,
        description="The stock ticker symbol if mentioned (e.g., 'NVDA', 'TSLA')"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence level that a company was mentioned (0.0-1.0)"
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation of why this company was identified"
    )


def extract_company_from_question(
    *,
    client: OpenAI,
    question: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.1,
) -> CompanyEntity:
    """
    Extract company entity from a user's question using LLM.

    Args:
        client: OpenAI client instance
        question: User's question text
        model: LLM model to use (default: gpt-4o-mini)
        temperature: Sampling temperature (default: 0.1 for deterministic)

    Returns:
        CompanyEntity with extracted company information

    Example:
        >>> client = OpenAI()
        >>> entity = extract_company_from_question(
        ...     client=client,
        ...     question="How did NVIDIA perform in Q3 2025?"
        ... )
        >>> print(entity.company_name)  # "NVIDIA"
        >>> print(entity.ticker)  # "NVDA"
    """

    prompt = f"""
Extract the company entity from the following user question.

Question: "{question}"

Rules:
- Identify any company name or stock ticker mentioned in the question
- Normalize the company name to its common/official form (e.g., "nvidia" -> "NVIDIA")
- If a ticker is mentioned, extract it (e.g., "NVDA", "TSLA")
- If no company is mentioned, set company_name and ticker to null and confidence to 0.0
- Set confidence to 1.0 if company is clearly mentioned, 0.5-0.9 if ambiguous, 0.0 if none
- Provide brief reasoning for your extraction

Examples:
- "How did NVIDIA do in earnings?" -> company_name: "NVIDIA", ticker: "NVDA", confidence: 1.0
- "What was Tesla's revenue?" -> company_name: "Tesla", ticker: "TSLA", confidence: 1.0
- "Tell me about NVDA stock" -> company_name: "NVIDIA", ticker: "NVDA", confidence: 1.0
- "What are the market trends?" -> company_name: null, ticker: null, confidence: 0.0
- "Did the chipmaker beat expectations?" -> company_name: null, ticker: null, confidence: 0.0 (ambiguous reference)
"""

    try:
        resp = client.responses.parse(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": "You are an expert at extracting company entities from questions. You identify company names and stock tickers accurately."
                },
                {"role": "user", "content": prompt},
            ],
            text_format=CompanyEntity,
            temperature=temperature,
            max_output_tokens=200,
        )

        entity: CompanyEntity = resp.output_parsed
        return entity

    except Exception as e:
        # If LLM extraction fails, return empty entity with error in reasoning
        return CompanyEntity(
            company_name=None,
            ticker=None,
            confidence=0.0,
            reasoning=f"Extraction failed: {str(e)}"
        )


def find_company_name_for_graph(
    *,
    client: OpenAI,
    question: str,
    model: str = "gpt-4o-mini",
    confidence_threshold: float = 0.5,
) -> Optional[str]:
    """
    Extract and return the company name suitable for graph lookup.

    This is a convenience wrapper around extract_company_from_question
    that returns only the company name if confidence is above threshold.

    Args:
        client: OpenAI client instance
        question: User's question text
        model: LLM model to use
        confidence_threshold: Minimum confidence required (default: 0.5)

    Returns:
        Company name if found with sufficient confidence, else None

    Example:
        >>> client = OpenAI()
        >>> name = find_company_name_for_graph(
        ...     client=client,
        ...     question="How did Tesla perform?"
        ... )
        >>> print(name)  # "Tesla"
    """
    entity = extract_company_from_question(
        client=client,
        question=question,
        model=model
    )

    # Return company name only if confidence meets threshold
    if entity.confidence >= confidence_threshold and entity.company_name:
        return entity.company_name

    return None
