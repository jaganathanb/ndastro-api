"""API v1 routing module.

This module defines and includes all API v1 routers for authentication, user management, and astro endpoints.
"""

from fastapi import APIRouter

from ndastro_api.api.v1.astro import router as astro
from ndastro_api.api.v1.health import router as health
from ndastro_api.api.v1.login import router as login
from ndastro_api.api.v1.logout import router as logout
from ndastro_api.api.v1.tier import router as tier
from ndastro_api.api.v1.users import router as user

router = APIRouter(prefix="/v1")
router.include_router(login)
router.include_router(logout)
router.include_router(tier)
router.include_router(user)
router.include_router(astro)
router.include_router(health)
