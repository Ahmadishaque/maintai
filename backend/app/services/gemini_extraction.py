import time
from dataclasses import dataclass

from google import genai
from google.genai import types

from app.schemas.extraction import MaintenanceExtraction
from app.services.policy_retrieval import (
    PolicyDocument,
    format_policy_context,
    retrieve_policies,
)

DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiServiceError(RuntimeError):
    """Raised when structured extraction cannot be completed."""


@dataclass(frozen=True)
class ExtractionResult:
    """Structured result plus operational metadata."""

    extraction: MaintenanceExtraction
    metadata: dict[str, object]
    retrieved_policies: list[PolicyDocument]


def extract_maintenance_request(
    description: str,
    api_key: str,
    location: str | None = None,
    model_name: str = DEFAULT_MODEL,
) -> ExtractionResult:
    """Retrieve relevant policies and extract a grounded maintenance record."""
    if not api_key:
        raise GeminiServiceError("GEMINI_API_KEY is not configured.")

    policies = retrieve_policies(description)
    policy_context = format_policy_context(policies)
    location_text = location or "Not provided"
    prompt = f"""
You are an enterprise maintenance-intake assistant.

Convert the user's report into the required structured schema. Base recommended actions only
on the retrieved internal policies below. Do not invent a diagnosis. Cite only the exact policy
IDs shown below. Set requires_human_review to true when information is uncertain, a safety risk
exists, the confidence is below 0.60, or a suitable policy is not available.

User-reported location: {location_text}
User report:
{description}

Retrieved internal policies:
{policy_context}
""".strip()

    client = genai.Client(api_key=api_key)
    started_at = time.perf_counter()
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MaintenanceExtraction,
                temperature=0.1,
            ),
        )
    except Exception as exc:
        raise GeminiServiceError("Gemini extraction request failed.") from exc

    latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
    if isinstance(response.parsed, MaintenanceExtraction):
        extraction = response.parsed
    elif response.text:
        extraction = MaintenanceExtraction.model_validate_json(response.text)
    else:
        raise GeminiServiceError("Gemini returned no structured output.")

    allowed_citations = {policy.policy_id for policy in policies}
    valid_citations = [
        citation for citation in extraction.policy_citations if citation in allowed_citations
    ]
    requires_review = (
        extraction.requires_human_review
        or extraction.safety_risk
        or extraction.confidence < 0.60
        or bool(extraction.missing_information)
        or len(valid_citations) != len(extraction.policy_citations)
    )
    extraction = extraction.model_copy(
        update={
            "policy_citations": valid_citations,
            "requires_human_review": requires_review,
        }
    )

    usage = response.usage_metadata
    metadata: dict[str, object] = {
        "success": True,
        "model": model_name,
        "latency_ms": latency_ms,
        "prompt_tokens": getattr(usage, "prompt_token_count", 0) if usage else 0,
        "output_tokens": getattr(usage, "candidates_token_count", 0) if usage else 0,
        "total_tokens": getattr(usage, "total_token_count", 0) if usage else 0,
        "retrieval_strategy": "keyword_overlap",
        "retrieved_policy_ids": [policy.policy_id for policy in policies],
    }
    return ExtractionResult(
        extraction=extraction,
        metadata=metadata,
        retrieved_policies=policies,
    )
