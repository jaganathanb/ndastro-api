"""Module to initialize and check database connectivity before starting the service."""

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
    try:
        with Session(db_engine) as session:
            # Try to create session to check if DB is awake
            session.exec(select(1))
    except Exception:
        logger.exception("Exception occurred")
        raise


def main() -> None:
    """Initialize the service by checking if the database is awake."""
    logger.info("Initializing service")
    init(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
