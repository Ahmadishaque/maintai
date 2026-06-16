from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.maintenance_request import MaintenanceRequest
from app.schemas.maintenance_request import MaintenanceRequestCreate, MaintenanceRequestRead

router = APIRouter(prefix="/api/v1/requests", tags=["maintenance requests"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=MaintenanceRequestRead,
    status_code=status.HTTP_201_CREATED,
)
def create_maintenance_request(
    payload: MaintenanceRequestCreate,
    database: DatabaseSession,
) -> MaintenanceRequest:
    """Persist a new natural-language maintenance request."""
    request_record = MaintenanceRequest(**payload.model_dump())
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
    statement = select(MaintenanceRequest).order_by(MaintenanceRequest.created_at.desc()).limit(limit)
    return list(database.scalars(statement))
