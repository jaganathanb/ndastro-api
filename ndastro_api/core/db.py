"""Database initialization and session management for ndastro_api.

This module sets up the SQLModel engine and provides functions to initialize
the database with initial data, such as creating the first superuser.
"""

from sqlmodel import Session, create_engine, select

from ndastro_api import crud
from ndastro_api.core.config import settings
from ndastro_api.models import User, UserCreate

engine = create_engine(str(settings.sqlalchemy_database_uri))


def init_db(session: Session) -> None:
    """Initialize the database with initial data.

    This function checks if the first superuser exists in the database.
    If not, it creates a new superuser with the credentials specified in the settings.

    Parameters
    ----------
    session : Session
        The database session to use for initialization.

    """
    # Check if the first superuser exists
    # If not, create it with the credentials from settings
    if not session.bind:
        session.bind = engine

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER),
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
