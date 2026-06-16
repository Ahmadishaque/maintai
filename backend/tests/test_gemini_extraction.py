import pytest

from app.services.gemini_extraction import GeminiServiceError, extract_maintenance_request


def test_extraction_requires_api_key() -> None:
    with pytest.raises(GeminiServiceError, match="GEMINI_API_KEY"):
        extract_maintenance_request(
            description="The air-conditioning unit is making a loud grinding noise.",
            api_key="",
        )
