from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceRequestCreate(BaseModel):
    """User-provided fields for a new maintenance request."""

    raw_description: str = Field(min_length=10, max_length=4000)
    reporter_name: str | None = Field(default=None, max_length=120)
    location: str | None = Field(default=None, max_length=200)


class MaintenanceRequestRead(BaseModel):
    """Maintenance request returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    raw_description: str
    reporter_name: str | None
    location: str | None
    status: str
    structured_data: dict[str, Any] | None
    llm_metadata: dict[str, Any] | None
    created_at: datetime
