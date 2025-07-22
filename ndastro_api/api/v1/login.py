"""API endpoints for user authentication, including login and token refresh functionality."""

from datetime import timedelta
from typing import Annotated, cast

from emails.backend.smtp.exceptions import SMTPConnectNetworkError
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ndastro_api.api.deps import get_current_superuser, get_current_user
from ndastro_api.core.config import settings
from ndastro_api.core.db.database import async_get_db
from ndastro_api.core.exceptions.app_exceptions import (
    RefreshTokenMissingInvalidException,
)
from ndastro_api.core.exceptions.http_exceptions import (
    InvalidInputException,
    NotFoundException,
)
from ndastro_api.core.schemas import Token
from ndastro_api.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TokenType,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_token,
)
from ndastro_api.crud.users import crud_users
from ndastro_api.email_helper import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)
from ndastro_api.schemas.user import UserPasswordUpdate, UserRead

router = APIRouter(tags=["Auth"], prefix="/auth")


@router.post("/login", response_model=Token, summary="Login to obtain access and refresh tokens.")
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
        msg = "User not found or invalid credentials"
        raise NotFoundException(msg)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)

    refresh_token = await create_refresh_token(data={"sub": user["username"]})
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="lax", max_age=max_age)

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.post("/refresh", dependencies=[Depends(get_current_user)], response_model=Token, summary="Rotate access and refresh tokens.")
async def refresh_access_token(request: Request, response: Response, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    """Refresh the access token using a valid refresh token from the request cookies.

    Args:
        request (Request): The incoming HTTP request containing cookies.
        response (Response): The FastAPI response object used to set cookies.
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

    refresh_token = await create_refresh_token(data={"sub": user_data.username_or_email})
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="lax", max_age=max_age)

    return {"access_token": new_access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.get("/me", response_model=UserRead, summary="Get current authenticated user")
async def read_users_me(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    """Retrieve the current authenticated user's information.

    Args:
        current_user (dict): The currently authenticated user, injected by dependency.

    Returns:
        dict: The current user's information.

    """
    return current_user


@router.post("/password-recovery/{email}", summary="Send password recovery email")
async def recover_password(email: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str | None]:
    """Send a password recovery email to the user with the specified email address.

    Args:
        email (str): The email address of the user requesting password recovery.
        db (AsyncSession): The asynchronous database session dependency.

    Returns:
        dict[str, str]: A dictionary with a success message.

    Raises:
        NotFoundException: If the user with the specified email is not found.

    """
    user: UserRead = cast(
        "UserRead", await crud_users.get(db=db, email=email, return_as_model=True, schema_to_select=UserRead, is_deleted=False, is_active=True)
    )
    if not user:
        raise NotFoundException

    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(email_to=user.email, email=email, token=password_reset_token)
    res = send_email(
        email_to="jaganathan.eswaran@gmail.com",
        subject=email_data.subject,
        html_content=email_data.html_content,
    )

    if res and res.success:
        return {"message": "Password recovery email sent successfully", "status": str(res.status_code)}

    return {"message": cast("SMTPConnectNetworkError", res.error).strerror, "status": str(res.status_code)}


@router.post("/reset-password", summary="Reset user password using a token")
async def reset_password(db: Annotated[AsyncSession, Depends(async_get_db)], body: UserPasswordUpdate) -> dict[str, str]:
    """Reset the user's password using a password reset token.

    Args:
        db (AsyncSession): The asynchronous database session dependency.
        body (UserPasswordUpdate): The request body containing the password reset token and the new password.

    Returns:
        dict[str, str]: A dictionary with a success message.

    Raises:
        InvalidInputException: If the provided token is invalid.
        NotFoundException: If the user is not found, inactive, or deleted.

    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        msg = "Invalid token"
        raise InvalidInputException(msg)

    user: UserRead = cast(
        "UserRead", await crud_users.get(db=db, email=email, return_as_model=True, schema_to_select=UserRead, is_deleted=False, is_active=True)
    )
    if not user:
        msg = "User not found or inactive"
        raise NotFoundException(msg)

    hashed_password = get_password_hash(password=body.new_password)

    await crud_users.update(db=db, email=user.email, object={"hashed_password": hashed_password})

    return {"message": "Password updated successfully"}


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_superuser)],
    response_class=HTMLResponse,
    summary="Generate HTML content for password recovery email",
)
async def recover_password_html_content(email: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> HTMLResponse:
    """Generate and return the HTML content for a password recovery email for the specified user.

    Args:
        email (str): The email address of the user requesting password recovery.
        db (AsyncSession): The asynchronous database session dependency.

    Returns:
        HTMLResponse: An HTML response containing the password reset email content.

    Raises:
        NotFoundException: If the user with the specified email is not found.

    """
    user: UserRead = cast(
        "UserRead", await crud_users.get(db=db, email=email, return_as_model=True, schema_to_select=UserRead, is_deleted=False, is_active=True)
    )
    if not user:
        raise NotFoundException

    if not user:
        raise NotFoundException(msg="User not found")
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(email_to=user.email, email=email, token=password_reset_token)

    return HTMLResponse(content=email_data.html_content, headers={"subject": email_data.subject})
