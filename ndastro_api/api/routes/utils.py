"""Utility routes for the ndastro API.

This module defines utility endpoints such as health checks.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/health-check/")
async def health_check() -> bool:
    """Check the health status of the API.

    Returns
    -------
    bool
        Returns True if the API is healthy.

    """
    return True
