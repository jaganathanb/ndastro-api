"""API router setup for ndastro_api.

This module configures and includes all API route modules for the application.
"""

from fastapi import APIRouter

from ndastro_api.api.routes import login, private, users, utils
from ndastro_api.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)


if settings.ENVIRONMENT in ("local", "test"):
    api_router.include_router(private.router)
