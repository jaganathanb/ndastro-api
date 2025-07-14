"""Defines the Tier model representing subscription or service tiers in the system."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ndastro_api.core.db.database import Base


class Tier(Base):
    """Represents a subscription or service tier in the system.

    Attributes:
        id (int): Unique identifier for the tier. Primary key.
        name (str): Unique name of the tier.
        created_at (datetime): Timestamp when the tier was created (timezone-aware).
        updated_at (datetime | None): Timestamp when the tier was last updated (timezone-aware), or None if never updated.

    """

    __tablename__ = "tier"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
