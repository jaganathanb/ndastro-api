"""Dependency utilities for authentication, authorization, and database access in the ndastro_api.

This module provides FastAPI dependencies for database sessions, user authentication, and authorization checks.
"""

from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from ndastro_api.core import security
from ndastro_api.core.config import settings
from ndastro_api.core.db import engine
from ndastro_api.models import TokenPayload, User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token",
)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a SQLModel database session.

    Yields
    ------
    Session
        An active database session to be used in a dependency context.

    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Retrieve the current user based on the provided JWT token and database session.

    Parameters
    ----------
    session : SessionDep
        The database session dependency.
    token : TokenDep
        The JWT token dependency.

    Returns
    -------
    User
        The authenticated user object.

    Raises
    ------
    HTTPException
        If the token is invalid, the user is not found, or the user is inactive.

    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError) as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from err
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Ensure the current user is an active superuser.

    Parameters
    ----------
    current_user : CurrentUser
        The currently authenticated user.

    Returns
    -------
    User
        The current user if they are a superuser.

    Raises
    ------
    HTTPException
        If the user does not have superuser privileges.

    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return current_user
