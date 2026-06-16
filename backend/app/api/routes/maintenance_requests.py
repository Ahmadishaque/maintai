from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.maintenance_request import MaintenanceRequest
from app.schemas.maintenance_request import MaintenanceRequestCreate, MaintenanceRequestRead
from app.services.gemini_extraction import GeminiServiceError, extract_maintenance_request

router = APIRouter(prefix="/api/v1/requests", tags=["maintenance requests"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=MaintenanceRequestRead, status_code=status.HTTP_201_CREATED)
def create_maintenance_request(
    payload: MaintenanceRequestCreate,
    database: DatabaseSession,
) -> MaintenanceRequest:
    """Extract, validate, and persist a maintenance request."""
    settings = get_settings()
    request_data = payload.model_dump()

    try:
        result = extract_maintenance_request(
            description=payload.raw_description,
            location=payload.location,
            api_key=settings.gemini_api_key,
        )
        request_data.update(
            structured_data=result.extraction.model_dump(mode="json"),
            llm_metadata=result.metadata,
            status="needs_review" if result.extraction.requires_human_review else "triaged",
        )
    except GeminiServiceError as exc:
        request_data.update(
            structured_data={
                "summary": payload.raw_description,
                "requires_human_review": True,
                "missing_information": ["Automated extraction was unavailable."],
            },
            llm_metadata={"success": False, "model": "gemini-2.5-flash", "error": str(exc)},
            status="needs_review",
        )

    request_record = MaintenanceRequest(**request_data)
    database.add(request_record)
    database.commit()
    database.refresh(request_record)
    return request_record


@router.get("", response_model=list[MaintenanceRequestRead])
def list_maintenance_requests(
    database: DatabaseSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
) -> list[MaintenanceRequest]:
    """Return the most recent maintenance requests."""
    statement = (
        select(MaintenanceRequest)
        .order_by(MaintenanceRequest.created_at.desc())
        .limit(limit)
    )
    return list(database.scalars(statement))
