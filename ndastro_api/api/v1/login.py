"""API endpoints for user authentication, including login and token refresh functionality."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ndastro_api.core.config import settings
from ndastro_api.core.db.database import async_get_db
from ndastro_api.core.exceptions.app_exceptions import (
    RefreshTokenMissingInvalidException,
)
from ndastro_api.core.exceptions.http_exceptions import UnauthorizedException
from ndastro_api.core.schemas import Token
from ndastro_api.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TokenType,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
)

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """Authenticate a user and generate access and refresh tokens.

    This endpoint validates the provided username/email and password, and if authentication is successful,
    returns a JWT access token and sets a refresh token as an HTTP-only cookie.

    Args:
        response (Response): The FastAPI response object used to set cookies.
        form_data (OAuth2PasswordRequestForm): The OAuth2 form data containing username/email and password.
        db (AsyncSession): The asynchronous database session dependency.

    Returns:
        dict[str, str]: A dictionary containing the access token and its type.

    Raises:
        UnauthorizedException: If authentication fails due to invalid credentials.

    """
    user = await authenticate_user(username_or_email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise UnauthorizedException

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)

    refresh_token = await create_refresh_token(data={"sub": user["username"]})
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="lax", max_age=max_age)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_access_token(request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    """Refresh the access token using a valid refresh token from the request cookies.

    Args:
        request (Request): The incoming HTTP request containing cookies.
        db (AsyncSession): The asynchronous database session dependency.

    Returns:
        dict[str, str]: A dictionary containing the new access token and its type.

    Raises:
        RefreshTokenMissingInvalidException: If the refresh token is missing or invalid.

    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise RefreshTokenMissingInvalidException

    user_data = await verify_token(refresh_token, TokenType.REFRESH, db)
    if not user_data:
        raise RefreshTokenMissingInvalidException

    new_access_token = await create_access_token(data={"sub": user_data.username_or_email})
    return {"access_token": new_access_token, "token_type": "bearer"}
