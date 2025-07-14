"""API endpoints for user management.

This includes user creation, retrieval, update, deletion, tier management, and rate limit queries for the ndastro-api service.
"""

from __future__ import annotations

from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002 # Required to be imported NOT as type check because openapi needs it

from ndastro_api.api.deps import get_current_superuser, get_current_user
from ndastro_api.core.db.database import async_get_db
from ndastro_api.core.exceptions.http_exceptions import (
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
)
from ndastro_api.core.security import (
    blacklist_token,
    get_password_hash,
    oauth2_scheme,
)
from ndastro_api.crud.tier import crud_tiers
from ndastro_api.crud.users import crud_users
from ndastro_api.schemas.pagination import PaginatedListResponse
from ndastro_api.schemas.tier import TierRead
from ndastro_api.schemas.user import (
    UserCreate,
    UserCreateInternal,
    UserRead,
    UserTierUpdate,
    UserUpdate,
)
from ndastro_api.services.utils import compute_offset, paginated_response

router = APIRouter(tags=["Users"], dependencies=[Depends(get_current_user)])


@router.post("/user", dependencies=[Depends(get_current_superuser)], response_model=UserRead, status_code=201)
async def write_user(user: UserCreate, db: Annotated[AsyncSession, Depends(async_get_db)]) -> UserRead:
    """Create a new user in the database after validating uniqueness of email and username.

    Args:
        user (UserCreate): The user creation data, including email, username, and password.
        db (AsyncSession): The asynchronous database session dependency.

    Returns:
        UserRead: The created user's data in the read schema.

    Raises:
        DuplicateValueException: If the provided email or username already exists in the database.
        NotFoundException: If the user could not be retrieved after creation.

    """
    email_row = await crud_users.exists(db=db, email=user.email)
    if email_row:
        msg = "Email"
        raise DuplicateValueException(msg)

    username_row = await crud_users.exists(db=db, username=user.username)
    if username_row:
        msg = "Username"
        raise DuplicateValueException(msg)

    user_internal_dict = user.model_dump()
    user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
    del user_internal_dict["password"]

    user_internal = UserCreateInternal(**user_internal_dict)
    created_user = await crud_users.create(db=db, object=user_internal)

    user_read = await crud_users.get(db=db, id=created_user.id, schema_to_select=UserRead)
    if user_read is None:
        raise NotFoundException

    return cast("UserRead", user_read)


@router.get("/users", response_model=PaginatedListResponse[UserRead])
async def read_users(db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10) -> dict:
    """Retrieve a paginated list of users from the database.

    Args:
        db (AsyncSession): The asynchronous database session dependency.
        page (int, optional): The page number to retrieve. Defaults to 1.
        items_per_page (int, optional): The number of users per page. Defaults to 10.

    Returns:
        dict: A dictionary containing the paginated list of users and pagination metadata.

    """
    users_data = await crud_users.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/user/me/", response_model=UserRead)
async def read_users_me(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    """Retrieve the current authenticated user's information.

    Args:
        current_user (dict): The currently authenticated user, injected by dependency.

    Returns:
        dict: The current user's information.

    """
    return current_user


@router.get("/user/{username}", response_model=UserRead)
async def read_user(username: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> UserRead:
    """Retrieve a user by username from the database.

    Args:
        username (str): The username of the user to retrieve.
        db (AsyncSession): The asynchronous database session dependency.

    Returns:
        UserRead: The user data matching the given username.

    Raises:
        NotFoundException: If no user with the specified username is found.

    """
    db_user = await crud_users.get(db=db, username=username, is_deleted=False, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException

    return cast("UserRead", db_user)


@router.patch("/user/{username}")
async def patch_user(
    values: UserUpdate,
    username: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """Update the details of an existing user.

    This endpoint allows an authenticated user to update their own username and/or email.
    It performs the following checks:
    - Verifies that the user exists.
    - Ensures the current user is authorized to update the specified user.
    - Checks for duplicate usernames or emails before updating.

    Args:
        values (UserUpdate): The new values for the user (username and/or email).
        username (str): The username of the user to update.
        current_user (dict): The currently authenticated user, injected by dependency.
        db (AsyncSession): The database session, injected by dependency.

    Returns:
        dict[str, str]: A message indicating the user was updated.

    Raises:
        NotFoundException: If the user does not exist.
        ForbiddenException: If the current user is not authorized to update this user.
        DuplicateValueException: If the new username or email already exists.

    """
    db_user = await crud_users.get(db=db, username=username, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException

    db_user = cast("UserRead", db_user)
    if db_user.username != current_user["username"]:
        raise ForbiddenException

    if values.username != db_user.username:
        existing_username = await crud_users.exists(db=db, username=values.username)
        if existing_username:
            msg = "Username"
            raise DuplicateValueException(msg)

    if values.email != db_user.email:
        existing_email = await crud_users.exists(db=db, email=values.email)
        if existing_email:
            msg = "Email"
            raise DuplicateValueException(msg)

    await crud_users.update(db=db, object=values, username=username)
    return {"message": "User updated"}


@router.delete("/user/{username}", dependencies=[Depends(get_current_superuser)])
async def erase_user(
    username: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict[str, str]:
    """Asynchronously deletes a user account and blacklists the current authentication token.

    Args:
        username (str): The username of the user to be deleted.
        current_user (dict): The currently authenticated user, injected by dependency.
        db (AsyncSession): The asynchronous database session, injected by dependency.
        token (str): The current user's authentication token, injected by dependency.

    Returns:
        dict[str, str]: A message indicating successful deletion of the user.

    Raises:
        NotFoundException: If the user with the specified username does not exist.
        ForbiddenException: If the current user is not authorized to delete the specified user.

    """
    db_user = await crud_users.get(db=db, username=username, schema_to_select=UserRead)
    if not db_user:
        raise NotFoundException

    if username != current_user["username"]:
        raise ForbiddenException

    await crud_users.delete(db=db, username=username)
    await blacklist_token(token=token, db=db)
    return {"message": "User deleted"}


@router.delete("/db_user/{username}", dependencies=[Depends(get_current_superuser)])
async def erase_db_user(
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict[str, str]:
    """Asynchronously deletes a user from the database and blacklists their authentication token.

    Args:
        username (str): The username of the user to be deleted.
        db (AsyncSession): The asynchronous database session dependency.
        token (str): The authentication token of the user, obtained via OAuth2.

    Returns:
        dict[str, str]: A message indicating successful deletion of the user.

    Raises:
        NotFoundException: If the user with the specified username does not exist in the database.

    """
    db_user = await crud_users.exists(db=db, username=username)
    if not db_user:
        raise NotFoundException

    await crud_users.db_delete(db=db, username=username)
    await blacklist_token(token=token, db=db)
    return {"message": "User deleted from the database"}


@router.get("/user/{username}/tier")
async def read_user_tier(username: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict | None:
    """Retrieve the tier information for a user identified by username.

    Args:
        username (str): The username of the user whose tier information is to be retrieved.
        db (AsyncSession): The asynchronous database session dependency.

    Returns:
        dict | None: A dictionary containing user and tier information, or None if the user has no tier.

    Raises:
        NotFoundException: If the user or the tier does not exist.

    """
    db_user = await crud_users.get(db=db, username=username, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException

    db_user = cast("UserRead", db_user)
    if db_user.tier_id is None:
        return None

    db_tier = await crud_tiers.get(db=db, id=db_user.tier_id, schema_to_select=TierRead)
    if not db_tier:
        raise NotFoundException

    db_tier = cast("TierRead", db_tier)

    user_dict = db_user.model_dump()
    tier_dict = db_tier.model_dump()

    for key, value in tier_dict.items():
        user_dict[f"tier_{key}"] = value

    return user_dict


@router.patch("/user/{username}/tier", dependencies=[Depends(get_current_superuser)])
async def patch_user_tier(
    username: str,
    values: UserTierUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """Update the tier of a user identified by username.

    Args:
        username (str): The username of the user whose tier is to be updated.
        values (UserTierUpdate): An object containing the new tier information.
        db (AsyncSession): The asynchronous database session dependency.

    Returns:
        dict[str, str]: A message indicating the user's tier was updated.

    Raises:
        NotFoundException: If the user or the specified tier does not exist.

    """
    db_user = await crud_users.get(db=db, username=username, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException

    db_user = cast("UserRead", db_user)
    db_tier = await crud_tiers.get(db=db, id=values.tier_id, schema_to_select=TierRead)
    if db_tier is None:
        raise NotFoundException

    await crud_users.update(db=db, object=values.model_dump(), username=username)
    return {"message": f"User {db_user.name} Tier updated"}
