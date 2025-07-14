"""Router configuration for the ndastro_api API.

This module sets up the main API router and includes versioned sub-routers.
"""

from fastapi import APIRouter

from ndastro_api.api.v1.routes import router as v1_router

router = APIRouter(prefix="/api")
router.include_router(v1_router)
