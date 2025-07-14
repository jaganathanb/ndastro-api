"""Dependency utilities for FastAPI endpoints in ndastro_api.

This module provides dependency functions for authentication, user retrieval and
superuser checks for API requests.
"""

from __future__ import annotations

import http
from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002 # Required to be imported NOT as type check because openapi needs it

from ndastro_api.core.db.database import async_get_db
from ndastro_api.core.exceptions.http_exceptions import (
    ForbiddenException,
    UnauthorizedException,
)
from ndastro_api.core.logger import logging
from ndastro_api.core.security import TokenType, oauth2_scheme, verify_token
from ndastro_api.crud.users import crud_users
from ndastro_api.schemas.user import UserSchema  # noqa: TC001 # Required to be imported NOT as type check because openapi needs it

logger = logging.getLogger(__name__)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(async_get_db)]) -> UserSchema | None:
    """Retrieve the current authenticated user based on the provided OAuth2 token.

    Args:
        token (str): The OAuth2 access token extracted from the request.
        db (AsyncSession): The asynchronous database session dependency.

    Returns:
        dict[str, Any] | None: The user data as a dictionary if authentication is successful.

    Raises:
        UnauthorizedException: If the token is invalid or the user does not exist.

    """
    token_data = await verify_token(token, TokenType.ACCESS, db)
    if token_data is None:
        raise UnauthorizedException

    if "@" in token_data.username_or_email:
        user = await crud_users.get(db=db, email=token_data.username_or_email, is_deleted=False)
    else:
        user = await crud_users.get(db=db, username=token_data.username_or_email, is_deleted=False)

    if user:
        return cast("UserSchema", user)

    raise UnauthorizedException


async def get_optional_user(request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]) -> UserSchema | None:
    """Asynchronously retrieves the current user from the request if an Authorization header is present and valid.

    Args:
        request (Request): The incoming HTTP request object.
        db (AsyncSession, optional): The database session dependency.

    Returns:
        UserSchema | None: The user information as a UserSchema object if a valid Bearer token is provided and verified; otherwise, None.

    Notes:
        - If the Authorization header is missing, malformed, or the token is invalid, returns None.
        - Handles and logs unexpected exceptions except for HTTP 401 Unauthorized.

    """
    token = request.headers.get("Authorization")
    if not token:
        return None

    try:
        token_type, _, token_value = token.partition(" ")
        if token_type.lower() != "bearer" or not token_value:
            return None

        token_data = await verify_token(token_value, TokenType.ACCESS, db)
        if token_data is None:
            return None

        return await get_current_user(token_value, db=db)

    except HTTPException as http_exc:
        if http_exc.status_code != http.HTTPStatus.UNAUTHORIZED:
            logger.exception("Unexpected HTTPException in get_optional_user: %s", http_exc.detail)
        return None

    except Exception:
        logger.exception("Unexpected error in get_optional_user")
        return None


async def get_current_superuser(current_user: Annotated[UserSchema, Depends(get_current_user)]) -> UserSchema:
    """Dependency that ensures the current user has superuser privileges.

    Args:
        current_user (UserSchema): The currently authenticated user, injected by the get_current_user dependency.

    Raises:
        ForbiddenException: If the current user is not a superuser.

    Returns:
        dict: The current user dictionary if the user is a superuser.

    """
    if not current_user.is_superuser:
        raise ForbiddenException

    return current_user
