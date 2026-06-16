from fastapi import FastAPI

from app.api.routes.maintenance_requests import router as maintenance_requests_router
from app.db.session import check_database_connection

app = FastAPI(
    title="MaintAI API",
    description="Policy-grounded maintenance intake assistant backend.",
    version="0.1.0",
)
app.include_router(maintenance_requests_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str | bool]:
    """Return application and database health information."""
    return {
        "status": "ok",
        "service": "maintai-backend",
        "database_connected": check_database_connection(),
    }
