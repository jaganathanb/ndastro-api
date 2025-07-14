"""Defines the TokenBlacklist model for storing blacklisted tokens in the database."""

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class TokenBlacklist(Base):
    """Represents a blacklisted token entry in the database.

    Attributes:
        id (int): Primary key, unique identifier for the blacklisted token.
        token (str): The token string that has been blacklisted. Must be unique.
        expires_at (datetime): The expiration date and time for the blacklisted token.

    """

    __tablename__ = "token_blacklist"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
