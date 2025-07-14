"""Main entry point for the ndastro_api application.

This module sets up the FastAPI application, including admin interface initialization and routing.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ndastro_api.api.router import router
from ndastro_api.core.config import settings
from ndastro_api.core.setup import create_application, lifespan_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Return a custom lifespan that includes admin initialization."""
    # Get the default lifespan
    default_lifespan = lifespan_factory()

    # Run the default lifespan initialization and our admin initialization
    async with default_lifespan(app):
        yield


app = create_application(router=router, settings=settings, lifespan=lifespan)
