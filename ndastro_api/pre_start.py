"""Module to initialize and check database connectivity before starting the service."""

import asyncio
import logging

from sqlmodel import select
from tenacity import (
    after_log,
    before_log,
    retry,
    stop_after_attempt,
    wait_fixed,
)

from ndastro_api.core.db.database import async_get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
)
async def init() -> None:
    """Attempt to initialize a database session to check if the database is awake.

    Parameters
    ----------
    db_engine : Engine
        The SQLAlchemy engine instance to use for creating the session.

    Raises
    ------
    Exception
        If unable to create a session or execute a simple query.

    """
    agen = async_get_db()
    db = await anext(agen)
    try:
        await db.scalar(select(1))
        logger.info("Database is awake and ready.")
    except Exception:
        logger.exception("Exception occurred")
        raise


def main() -> None:
    """Initialize the service by checking if the database is awake."""
    logger.info("Initializing service")
    asyncio.run(init())
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
