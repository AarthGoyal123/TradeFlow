"""System API routes."""

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}


@router.get("/ready")
def readiness_check() -> dict[str, str]:
    """Return service readiness status."""
    # A true readiness check might attempt a simple DB query or check 
    # if required directories exist, but keep it lightweight per constraints.
    return {"status": "ready"}
