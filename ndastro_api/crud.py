"""CRUD operations for user management in the ndastro_api.

This module provides functions to create, update, retrieve, and authenticate users in the database.
"""

from __future__ import annotations

from sqlmodel import Session, select

from ndastro_api.core.security import get_password_hash, verify_password
from ndastro_api.models import User, UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create a new user in the database.

    Parameters
    ----------
    session : Session
        The database session to use for the creation.
    user_create : UserCreate
        The data required to create a new user.

    Returns
    -------
    User
        The newly created user object.

    """
    db_obj = User.model_validate(
        user_create,
        update={"hashed_password": get_password_hash(user_create.password)},
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """Update an existing user in the database with new data.

    Parameters
    ----------
    session : Session
        The database session to use for the update.
    db_user : User
        The existing user object to update.
    user_in : UserUpdate
        The data to update the user with.

    Returns
    -------
    User
        The updated user object.

    """
    user_data = user_in.model_dump(exclude_unset=True)
    if "password" in user_data:
        password = user_data.pop("password")
        db_user.hashed_password = get_password_hash(password)
    for field, value in user_data.items():
        setattr(db_user, field, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Retrieve a user from the database by their email address.

    Parameters
    ----------
    session : Session
        The database session to use for the query.
    email : str
        The email address of the user to retrieve.

    Returns
    -------
    User | None
        The User object if found, otherwise None.

    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """Authenticate a user by email and password.

    Parameters
    ----------
    session : Session
        The database session to use for the query.
    email : str
        The email address of the user.
    password : str
        The plain text password to verify.

    Returns
    -------
    User | None
        The authenticated User object if credentials are valid, otherwise None.

    """
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
