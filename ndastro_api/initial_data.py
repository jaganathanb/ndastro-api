"""Module to initialize the database with initial data for ndastro_api."""

import logging

from sqlmodel import Session

from ndastro_api.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_data() -> None:
    """Initialize the database with initial data."""
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    """Initialize data as the main entry point."""
    logger.info("Creating initial data")
    initialize_data()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
