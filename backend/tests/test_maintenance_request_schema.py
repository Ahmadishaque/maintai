import pytest
from pydantic import ValidationError

from app.schemas.maintenance_request import MaintenanceRequestCreate


def test_request_description_must_be_descriptive() -> None:
    with pytest.raises(ValidationError):
        MaintenanceRequestCreate(raw_description="Leak")


def test_valid_request_accepts_optional_context() -> None:
    request = MaintenanceRequestCreate(
        raw_description="The cooling pump is vibrating and leaking near the rear seal.",
        reporter_name="Jordan Lee",
        location="Building 3",
    )

    assert request.reporter_name == "Jordan Lee"
    assert request.location == "Building 3"
