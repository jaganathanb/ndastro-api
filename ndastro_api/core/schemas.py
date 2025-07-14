"""Schemas and data models for the ndastro API core components.

This module defines Pydantic models and mixins for health checks, UUIDs, timestamps,
persistent deletion, authentication tokens, and token blacklisting.
"""

from __future__ import annotations

import uuid as uuid_pkg
from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_serializer


class HealthCheck(BaseModel):
    """Represents the health check information for the API.

    Attributes:
        name (str): The name of the service or component being checked.
        version (str): The current version of the service.
        description (str): A brief description of the service's health status.

    """

    name: str
    version: str
    description: str


# -------------- mixins --------------
class UUIDSchema(BaseModel):
    """Schema for representing a universally unique identifier (UUID).

    Attributes:
        uuid (uuid_pkg.UUID): A UUID field that is automatically generated using uuid_pkg.uuid4 by default.

    """

    uuid: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4)


class TimestampSchema(BaseModel):
    """Schema for timestamp fields, including creation and update times.

    Attributes:
        created_at (datetime): The timestamp when the object was created. Defaults to the current UTC time (without tzinfo).
        updated_at (datetime | None): The timestamp when the object was last updated. Optional.

    Methods:
        serialize_dt(created_at, _info): Serializes the 'created_at' datetime to an ISO 8601 string, or returns None if not set.
        serialize_updated_at(updated_at, _info): Serializes the 'updated_at' datetime to an ISO 8601 string, or returns None if not set.

    """

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: datetime | None = Field(default=None)

    @field_serializer("created_at")
    def serialize_dt(self, created_at: datetime | None) -> str | None:
        """Serialize a datetime object to an ISO 8601 formatted string.

        Args:
            created_at (datetime | None): The datetime object to serialize. If None, returns None.
            _info (Any): Additional information (unused).

        Returns:
            str | None: The ISO 8601 formatted string representation of the datetime, or None if input is None.

        """
        if created_at is not None:
            return created_at.isoformat()

        return None

    @field_serializer("updated_at")
    def serialize_updated_at(self, updated_at: datetime | None) -> str | None:
        """Serialize a datetime object to an ISO 8601 formatted string.

        Args:
            updated_at (datetime | None): The datetime object to serialize. If None, no serialization is performed.
            _info (Any): Additional information (unused).

        Returns:
            str | None: The ISO 8601 formatted string representation of the datetime if provided, otherwise None.

        """
        if updated_at is not None:
            return updated_at.isoformat()

        return None


class PersistentDeletion(BaseModel):
    """Represents a model for tracking persistent deletion state.

    Attributes:
        deleted_at (datetime | None): The timestamp when the deletion occurred. Defaults to None.
        is_deleted (bool): Indicates whether the object is marked as deleted. Defaults to False.

    Methods:
        serialize_dates(deleted_at, _info): Serializes the 'deleted_at' datetime to an ISO 8601 string, or returns None if not set.

    """

    deleted_at: datetime | None = Field(default=None)
    is_deleted: bool = False

    @field_serializer("deleted_at")
    def serialize_dates(self, deleted_at: datetime | None) -> str | None:
        """Serialize a datetime object to an ISO 8601 formatted string.

        Args:
            deleted_at (datetime | None): The datetime object to serialize. If None, no serialization is performed.
            _info (Any): Additional information (unused).

        Returns:
            str | None: The ISO 8601 formatted string representation of the datetime if provided, otherwise None.

        """
        if deleted_at is not None:
            return deleted_at.isoformat()

        return None


class Token(BaseModel):
    """Represents an authentication token.

    Attributes:
        access_token (str): The JWT or access token string.
        token_type (str): The type of the token (e.g., "bearer").

    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token data containing the username or email extracted from a token.

    Attributes:
        username_or_email (str): The username or email address associated with the token.

    """

    username_or_email: str


class TokenBlacklistBase(BaseModel):
    """Base schema for representing a blacklisted token.

    Attributes:
        token (str): The token string that has been blacklisted.
        expires_at (datetime): The expiration date and time of the blacklisted token.

    """

    token: str
    expires_at: datetime


class TokenBlacklistRead(TokenBlacklistBase):
    """Represents a read-only view of a blacklisted token, including its unique identifier.

    Attributes:
        id (int): The unique identifier of the blacklisted token.

    """

    id: int


class TokenBlacklistCreate(TokenBlacklistBase):
    """Schema for creating a new token blacklist entry.

    Inherits from:
        TokenBlacklistBase: Base schema containing common fields for token blacklist entries.

    This class can be extended to include additional fields or validation logic specific to token blacklist creation.
    """


class TokenBlacklistUpdate(TokenBlacklistBase):
    """Schema for updating entries in the token blacklist.

    Inherits all fields from TokenBlacklistBase. This class can be extended to add or override fields specific to update operations.
    """
