"""Module to initialize the database with initial data for ndastro_api."""

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ndastro_api.core.config import settings
from ndastro_api.core.db.database import local_session
from ndastro_api.core.exceptions.http_exceptions import (
    DuplicateValueException,
    NotFoundException,
)
from ndastro_api.core.security import cast, get_password_hash
from ndastro_api.crud.tier import crud_tiers
from ndastro_api.crud.users import crud_users
from ndastro_api.schemas.tier import TierCreateInternal, TierRead
from ndastro_api.schemas.user import UserCreateInternal, UserRead

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_admin_user(session: AsyncSession) -> None:
    """Initialize the database with initial data."""
    db = session

    # Create a default tier if it doesn't exist
    default_tier_name = "system"
    default_tier = await crud_tiers.get(db=db, name=default_tier_name, schema_to_select=None)
    if not default_tier:
        default_tier = await crud_tiers.create(db=db, object=TierCreateInternal(name=default_tier_name))

    email_row = await crud_users.exists(db=db, email=settings.ADMIN_EMAIL)
    if email_row:
        msg = "Email"
        raise DuplicateValueException(msg)

    username_row = await crud_users.exists(db=db, username=settings.ADMIN_USERNAME)
    if username_row:
        msg = "Username"
        raise DuplicateValueException(msg)

    logger.info("Created system tier: %s", default_tier)

    user_internal_dict = {
        "username": settings.ADMIN_USERNAME,
        "email": settings.ADMIN_EMAIL,
        "name": settings.ADMIN_NAME,
        "hashed_password": get_password_hash(settings.ADMIN_PASSWORD),
    }

    user_internal = UserCreateInternal(**user_internal_dict)
    created_user = await crud_users.create(db=db, object=user_internal)

    user_read = cast(UserRead, await crud_users.update(db=db, object={"tier_id": cast(TierRead, default_tier).id, "is_superuser": True}))

    user_read = cast(UserRead, await crud_users.get(db=db, id=created_user.id, schema_to_select=UserRead))
    if user_read is None:
        raise NotFoundException

    logger.info("Created admin user: %s", user_read)


def main() -> None:
    """Asynchronously initializes the application by creating an admin user in the database.

    This function establishes an asynchronous session with the local database and calls
    the `create_admin_user` function to ensure that an admin user exists.

    Returns:
        None

    """

    async def run() -> None:
        async with local_session() as session:
            await create_admin_user(session=session)
            logger.info("Admin user created successfully.")

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
    except DuplicateValueException as e:
        logger.warning("Duplicate value found: %s", e.detail)


if __name__ == "__main__":
    logger.info("Initializing the database with Admin user...")
    main()
    logger.info("Database initialization complete.")
