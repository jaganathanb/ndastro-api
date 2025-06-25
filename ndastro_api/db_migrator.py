"""Module to run Alembic migrations for upgrading the database schema to the latest version."""

import alembic.config


def run_migration() -> None:
    """Run Alembic migrations to upgrade the database schema to the latest version."""
    alembic_args = ["--raiseerr", "upgrade", "head"]
    alembic.config.main(argv=alembic_args)
