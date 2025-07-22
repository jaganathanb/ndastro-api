"""Setup and initialization utilities for the ndastro_api FastAPI application.

This module provides functions and factories for application lifespan management,
database table creation, thread pool configuration, and application instantiation
with custom settings and middleware.
"""

from __future__ import annotations

from asyncio import Event
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from typing import TYPE_CHECKING, Any

import fastapi
from anyio.to_thread import current_default_thread_limiter
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from pydantic_settings import BaseSettings

from ndastro_api.api.deps import get_current_superuser
from ndastro_api.core.config import (
    AppSettings,
    BaseSettings,
    ClientSideCacheSettings,
    DatabaseSettings,
    EnvironmentOption,
    EnvironmentSettings,
)
from ndastro_api.core.db.database import async_engine as engine
from ndastro_api.middlewares.monitoring import MonitoringMiddleware
from ndastro_api.models.user import Base

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable


async def create_tables() -> None:
    """Asynchronously creates all database tables defined in the SQLAlchemy Base metadata.

    This function establishes an asynchronous connection to the database engine and
    executes the creation of all tables as defined by the SQLAlchemy ORM models.
    It should be called during application setup to ensure the database schema is initialized.

    Returns:
        None

    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def set_threadpool_tokens(number_of_tokens: int = 100) -> None:
    """Set the total number of tokens for the default thread pool limiter.

    Args:
        number_of_tokens (int, optional): The number of tokens to set for the thread pool limiter. Defaults to 100.

    Returns:
        None

    """
    limiter = current_default_thread_limiter()
    limiter.total_tokens = number_of_tokens


def lifespan_factory(*, create_tables_on_start: bool = True) -> Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:
    """Create a FastAPI lifespan context manager that initializes application resources.

    Args:
        create_tables_on_start (bool, optional):
            If True, database tables will be created at application startup. Defaults to True.

    Returns:
        Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:
            A callable that provides an async context manager for FastAPI's lifespan events.
    The returned context manager:
        - Sets up an initialization completion event in the FastAPI app state.
        - Optionally creates database tables at startup.
        - Ensures threadpool tokens are set before application startup.
        - Cleans up resources on application shutdown.

    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        initialization_complete = Event()
        app.state.initialization_complete = initialization_complete

        await set_threadpool_tokens()

        try:
            if create_tables_on_start:
                await create_tables()

            initialization_complete.set()

            yield
        finally:
            pass

    return lifespan


def create_application(
    router: APIRouter,
    settings: (DatabaseSettings | AppSettings | ClientSideCacheSettings | EnvironmentSettings),
    *,
    create_tables_on_start: bool = True,
    lifespan: Callable[[FastAPI], _AsyncGeneratorContextManager[Any]] | None = None,
    **kwargs: Any,
) -> FastAPI:
    """Create and configure a FastAPI application instance with the provided router and settings.

    This function allows for dynamic configuration of the FastAPI app based on the type of settings provided.
    It can update application metadata, control documentation endpoints, and manage application lifespan events.
    Optionally, it can restrict documentation access based on the environment.

    Args:
        router (APIRouter): The main API router to include in the application.
        settings (DatabaseSettings | AppSettings | ClientSideCacheSettings | EnvironmentSettings):
            The settings object used to configure the application. The behavior changes depending on the type:
                - AppSettings: Updates app metadata (title, description, contact, license).
                - EnvironmentSettings: Disables default docs and optionally adds custom docs routes.
        create_tables_on_start (bool, optional): Whether to create database tables on application startup. Defaults to True.
        lifespan (Callable[[FastAPI], _AsyncGeneratorContextManager[Any]] | None, optional):
            Custom lifespan context manager for the application. If None, a default factory is used.
        **kwargs (Any): Additional keyword arguments passed to the FastAPI constructor.

    Returns:
        FastAPI: The configured FastAPI application instance.

    """
    if isinstance(settings, AppSettings):
        to_update = {
            "title": settings.APP_NAME,
            "description": settings.APP_DESCRIPTION,
            "version": getattr(settings, "APP_VERSION", "1.0.0"),
            "contact": {"name": settings.CONTACT_NAME, "email": settings.CONTACT_EMAIL},
            "license_info": {"name": settings.LICENSE_NAME},
        }
        kwargs.update(to_update)

    if "version" not in kwargs or not kwargs["version"]:
        kwargs["version"] = "1.0.0"

    if isinstance(settings, EnvironmentSettings):
        kwargs.update({"docs_url": None, "redoc_url": None, "openapi_url": None})

    # Use custom lifespan if provided, otherwise use default factory
    if lifespan is None:
        lifespan = lifespan_factory(create_tables_on_start=create_tables_on_start)

    application = FastAPI(lifespan=lifespan, **kwargs)
    application.include_router(router)

    add_middlewares(settings, application)
    add_openapi_doc(settings, application)

    return application


def add_middlewares(settings: BaseSettings, application: FastAPI) -> None:
    """Add custom middlewares to the FastAPI application.

    This function is a placeholder for adding additional middlewares to the FastAPI application.
    Currently, it does not implement any specific middlewares but can be extended in the future.

    Args:
        settings (BaseSettings): The settings object used to configure middleware behavior.
        application (FastAPI): The FastAPI application instance to which middlewares will be added.

    Returns:
        None

    """
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS if isinstance(settings, AppSettings) else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_middleware(MonitoringMiddleware)


def add_openapi_doc(settings: BaseSettings, application: FastAPI) -> None:
    """Add custom OpenAPI documentation routes to the FastAPI application based on the environment settings.

    In non-production environments, this function registers routes for Swagger UI (`/docs`), ReDoc (`/redoc`),
    and the OpenAPI schema (`/openapi.json`). In non-local environments, access to these documentation routes
    requires superuser authentication.

    Args:
        settings (BaseSettings): The application settings, used to determine the current environment.
        application (FastAPI): The FastAPI application instance to which documentation routes will be added.

    Returns:
        FastAPI: The FastAPI application instance with documentation routes included (if applicable).

    """
    if isinstance(settings, EnvironmentSettings) and settings.ENVIRONMENT != EnvironmentOption.PRODUCTION:
        docs_router = APIRouter()
        if settings.ENVIRONMENT != EnvironmentOption.LOCAL:
            docs_router = APIRouter(dependencies=[Depends(get_current_superuser)])

        @docs_router.get("/docs", include_in_schema=False)
        async def get_swagger_documentation() -> fastapi.responses.HTMLResponse:
            return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

        @docs_router.get("/redoc", include_in_schema=False)
        async def get_redoc_documentation() -> fastapi.responses.HTMLResponse:
            return get_redoc_html(openapi_url="/openapi.json", title="docs")

        @docs_router.get("/openapi.json", include_in_schema=False)
        async def openapi() -> dict[str, Any]:
            return get_openapi(title=application.title, version="v1.0", routes=application.routes)

        application.include_router(docs_router)
