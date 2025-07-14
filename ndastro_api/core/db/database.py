"""Database setup and session management for the ndastro_api application.

This module configures the SQLAlchemy async engine, sessionmaker, and provides the base ORM class.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

from ndastro_api.core.config import settings


class Base(DeclarativeBase, MappedAsDataclass):
    """Base class for all ORM models in the application.

    Inherits from:
        DeclarativeBase: Provides SQLAlchemy's declarative base functionality for ORM mapping.
        MappedAsDataclass: Enables automatic dataclass features for ORM models, such as type hints and default values.

    This class serves as the foundation for all database models, ensuring consistent behavior and integration with SQLAlchemy's ORM and dataclass features.
    """


def get_database_url() -> str:
    """Construct the database URL based on the application's settings.

    Returns:
        str: The complete database URL for connecting to the PostgreSQL database.

    This function retrieves the database URI from the application settings and constructs the full URL
    required for SQLAlchemy to connect to the database asynchronously.

    """
    match settings.DATABASE_TYPE.value:
        case "postgres":
            return f"{settings.POSTGRES_ASYNC_PREFIX}{settings.POSTGRES_URI}"
        case "mysql":
            return f"{settings.MYSQL_ASYNC_PREFIX}{settings.MYSQL_URI}"
        case "sqlite":
            return f"{settings.SQLITE_ASYNC_PREFIX}{settings.SQLITE_URI}"
        case _:
            msg = f"Unsupported database type: {settings.DATABASE_TYPE.value}. Supported types are: postgres, mysql, sqlite."
            raise ValueError(msg)


async_engine = create_async_engine(get_database_url(), echo=False, future=True)

local_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Asynchronous generator that provides a database session.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session object for database operations.

    Usage:
        Use this function as a dependency in async routes or services to interact with the database.
        The session is automatically closed after use.

    """
    async with local_session() as db:
        yield db
