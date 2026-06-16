from fastapi import FastAPI

app = FastAPI(
    title="MaintAI API",
    description="Policy-grounded maintenance intake assistant backend.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return the service health status."""
    return {"status": "ok", "service": "maintai-backend"}
