"""Module to check if the database is awake before starting the service.

This script attempts to create a session with the database using SQLModel and SQLAlchemy,
retrying for up to 5 minutes before giving up. It is intended to be run before the main
application starts to ensure the database is available.
"""

import logging

from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import (
    after_log,
    before_log,
    retry,
    stop_after_attempt,
    wait_fixed,
)

from ndastro_api.core.db import engine

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
def init(db_engine: Engine) -> None:
    """Attempt to create a session to check if the database is awake.

    Parameters
    ----------
    db_engine : Engine
        The SQLAlchemy engine to use for the database connection.

    Raises
    ------
    Exception
        If the database is not available or the session cannot be created.

    """
    try:
        # Try to create session to check if DB is awake
        with Session(db_engine) as session:
            session.exec(select(1))
    except Exception:
        logger.exception("Exception occurred while initializing the database session")
        raise


def main() -> None:
    """Initialize the service by checking if the database is awake."""
    logger.info("Initializing service")
    init(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
