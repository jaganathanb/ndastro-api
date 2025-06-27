"""Main entry point for the ndastro_api FastAPI application.

This module sets up the FastAPI app, configures middleware, Sentry integration,
CORS, and includes the main API router.
"""

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from ndastro_api.api.router import api_router
from ndastro_api.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate a unique operation ID for an APIRoute based on its first tag and name.

    Parameters
    ----------
    route : APIRoute
        The API route for which to generate a unique ID.

    Returns
    -------
    str
        A unique string identifier for the route.

    """
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
