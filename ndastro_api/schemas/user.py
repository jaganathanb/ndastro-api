"""Schemas for user-related data models in the ndastro_api application."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ndastro_api.core.schemas import (
    PersistentDeletion,
    TimestampSchema,
    UUIDSchema,
)

if TYPE_CHECKING:
    from datetime import datetime


class UserBase(BaseModel):
    """Base schema for user information (name, username, email)."""

    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"])]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]


class UserSchema(TimestampSchema, UserBase, UUIDSchema, PersistentDeletion):
    """Full user schema including profile image, password hash, superuser flag, and tier."""

    profile_image_url: Annotated[str, Field(default="https://www.profileimageurl.com")]
    hashed_password: str
    is_superuser: bool = False
    tier_id: int | None = None


class UserRead(BaseModel):
    """Schema for reading user information (public fields only)."""

    id: int

    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"])]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]
    profile_image_url: str
    tier_id: int | None


class UserCreate(UserBase):
    """Schema for creating a new user (with password)."""

    model_config = ConfigDict(extra="forbid")

    password: Annotated[str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])]


class UserCreateInternal(UserBase):
    """Internal schema for creating a user with a hashed password."""

    hashed_password: str


class UserUpdate(BaseModel):
    """Schema for updating user information (all fields optional)."""

    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(min_length=2, max_length=30, examples=["User Userberg"], default=None)]
    username: Annotated[str | None, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userberg"], default=None)]
    email: Annotated[EmailStr | None, Field(examples=["user.userberg@example.com"], default=None)]
    profile_image_url: Annotated[
        str | None,
        Field(pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", examples=["https://www.profileimageurl.com"], default=None),
    ]


class UserUpdateInternal(UserUpdate):
    """Schema for internal user update, including updated_at timestamp."""

    updated_at: datetime


class UserTierUpdate(BaseModel):
    """Schema for updating a user's tier."""

    tier_id: int


class UserDelete(BaseModel):
    """Schema for soft-deleting a user (is_deleted and deleted_at)."""

    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


class UserRestoreDeleted(BaseModel):
    """Schema for restoring a soft-deleted user."""

    is_deleted: bool
