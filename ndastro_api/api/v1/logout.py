"""API endpoint for logging out users by blacklisting tokens and removing refresh token cookies."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from ndastro_api.api.deps import oauth2_scheme
from ndastro_api.core.db.database import async_get_db
from ndastro_api.core.exceptions.http_exceptions import UnauthorizedException
from ndastro_api.core.security import blacklist_tokens

router = APIRouter(tags=["Auth"])

DBSession = Annotated[AsyncSession, Depends(async_get_db)]


@router.post("/logout")
async def logout(
    response: Response,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
    refresh_token: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> dict[str, str]:
    """Log out the current user by blacklisting their access and refresh tokens and removing the refresh token cookie.

    Args:
        response (Response): The HTTP response object used to modify cookies.
        access_token (str): The JWT access token extracted from the request.
        db (DBSession): The database session for performing token blacklisting.
        refresh_token (str | None, optional): The refresh token from the request cookies. Defaults to None.

    Returns:
        dict[str, str]: A message indicating successful logout.

    Raises:
        UnauthorizedException: If the refresh token is missing or invalid, or if a JWT error occurs.

    """
    try:
        if not refresh_token:
            msg = "Refresh token not found or invalid."
            raise UnauthorizedException(msg)

        await blacklist_tokens(access_token=access_token, refresh_token=refresh_token, db=db)
        response.delete_cookie(key="refresh_token")

    except JWTError as err:
        raise UnauthorizedException from err
    else:
        return {"message": "Logged out successfully"}
