"""Mixins for SQLAlchemy models providing UUID primary keys, timestamp fields, and soft deletion support."""

from __future__ import annotations

import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """A mixin class that adds a UUID primary key column to a SQLAlchemy model.

    Attributes:
        uuid (uuid_pkg.UUID): The primary key column, automatically assigned a UUID value.
            - Uses Python's uuid4 for default value generation.
            - Uses PostgreSQL's gen_random_uuid() for server-side default.

    """

    uuid: Mapped[uuid_pkg.UUID] = mapped_column(UUID, primary_key=True, default=uuid_pkg.uuid4, server_default=text("gen_random_uuid()"))


class TimestampMixin:
    """A mixin class that adds timestamp fields to a SQLAlchemy model.

    Attributes:
        created_at (datetime): The timestamp when the record was created. Automatically set to the current UTC time on creation.
        updated_at (datetime | None): The timestamp when the record was last updated. Automatically updated to the current UTC time on modification.

    """

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC), server_default=text("current_timestamp(0)"))
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, onupdate=datetime.now(UTC), server_default=text("current_timestamp(0)")
    )


class SoftDeleteMixin:
    """A mixin class that adds soft deletion support to SQLAlchemy models.

    Attributes:
        deleted_at (datetime | None): Timestamp indicating when the record was soft deleted. None if not deleted.
        is_deleted (bool): Flag indicating whether the record is considered deleted.

    """

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
