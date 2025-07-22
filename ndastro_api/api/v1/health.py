"""Health check endpoints for the ndastro_api.

This module provides an API route to check the health status of the API and database connection.
"""

from typing import Annotated

import psutil  # type: ignore[import]
import sqlalchemy
import sqlalchemy.exc
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import text

from ndastro_api.core.db.database import async_get_db
from ndastro_api.core.logger import logging

router = APIRouter(tags=["Health Check"])

DBSession = Annotated[AsyncSession, Depends(async_get_db)]


async def test_connection(db: DBSession) -> bool:
    """Asynchronously tests the database connection by executing a simple SQL query.

    Args:
        db (DBSession): The database session object used to execute the query.

    Returns:
        bool: True if the connection is successful and the query executes without errors, False otherwise.

    Logs:
        - Logs an info message if the connection is successful.
        - Logs an error message if the connection fails due to a SQLAlchemyError.

    """
    try:
        # Execute a simple raw SQL query
        result = await db.execute(text("SELECT 1"))
        value = result.scalar()
        logging.info(f"Connection successful. Result of SELECT 1: {value}")
    except sqlalchemy.exc.SQLAlchemyError as e:
        logging.error(f"Connection failed: {e}")
        return False
    else:
        return True


@router.get("/health-check", summary="Check API health status")
async def health_check(db: DBSession) -> dict:
    """Endpoint to check the health status of the API and database connection."""
    result = await test_connection(db)
    return {"status": "healthy"} if result else {"status": "unhealthy"}


@router.get("/metrics")
async def get_metrics() -> dict[str, float]:
    """Asynchronously retrieves system health metrics including CPU usage, memory usage, and disk usage.

    Returns:
        dict: A dictionary containing the following keys:
            - 'cpu_percent' (float): The current CPU utilization percentage.
            - 'memory_percent' (float): The current memory utilization percentage.
            - 'disk_usage' (float): The current disk usage percentage for the root directory.

    """
    return {"cpu_percent": psutil.cpu_percent(), "memory_percent": psutil.virtual_memory().percent, "disk_usage": psutil.disk_usage("/").percent}
