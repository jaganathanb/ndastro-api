"""Defines the User model for the ndastro_api, representing users and their attributes in the database."""

from __future__ import annotations

import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ndastro_api.core.db.database import Base


class User(Base):
    """Represents a user in the system.

    Attributes:
        id (int): Primary key, auto-incremented unique identifier for the user.
        name (str): The user's full name.
        username (str): Unique username for the user, indexed for fast lookup.
        email (str): Unique email address for the user, indexed for fast lookup.
        hashed_password (str): The user's hashed password.
        profile_image_url (str): URL to the user's profile image. Defaults to a placeholder URL.
        uuid (uuid_pkg.UUID): Universally unique identifier for the user. Primary key and unique.
        created_at (datetime): Timestamp when the user was created (timezone-aware).
        updated_at (datetime | None): Timestamp when the user was last updated (timezone-aware).
        deleted_at (datetime | None): Timestamp when the user was deleted (timezone-aware).
        is_deleted (bool): Indicates if the user is marked as deleted. Indexed.
        is_superuser (bool): Indicates if the user has superuser privileges.
        tier_id (int | None): Foreign key referencing the user's tier. Indexed.

    """

    __tablename__ = "user"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    profile_image_url: Mapped[str] = mapped_column(String, default="https://profileimageurl.com")
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, unique=True)  # not primary_key
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    tier_id: Mapped[int | None] = mapped_column(ForeignKey("tier.id"), index=True, default=None, init=False)
