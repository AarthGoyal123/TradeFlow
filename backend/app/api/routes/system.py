"""System API routes."""

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}
