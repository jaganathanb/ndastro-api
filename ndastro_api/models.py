"""Data models for users and authentication schemas used in the ndastro API."""

from __future__ import annotations

import os
import uuid

from pydantic import EmailStr  # noqa: TC002
from sqlmodel import Field, SQLModel


# Shared properties
class UserBase(SQLModel):
    """Base model for user data, containing shared properties.

    Attributes
    ----------
    email : EmailStr
        The user's email address.
    is_active : bool
        Indicates if the user is active.
    is_superuser : bool
        Indicates if the user has superuser privileges.
    full_name : str | None
        The user's full name.

    """

    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    """Model for creating a new user via the API.

    Attributes
    ----------
    password : str
        The user's password (min 8, max 40 characters).

    """

    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    """Model for registering a new user.

    Attributes
    ----------
    email : EmailStr
        The user's email address.
    password : str
        The user's password (min 8, max 40 characters).
    full_name : str | None
        The user's full name (optional).

    """

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    """Model for updating user information.

    Attributes
    ----------
    password : str | None
        The user's password (optional, min 8, max 40 characters).

    """

    password: str | None = Field(default=None, min_length=8, max_length=40)
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]


class UserUpdateMe(SQLModel):
    """Model for updating the current user's information.

    Attributes
    ----------
    full_name : str | None
        The user's full name (optional).
    email : EmailStr | None
        The user's email address (optional).

    """

    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """Model for updating a user's password.

    Attributes
    ----------
    current_password : str
        The user's current password (min 8, max 40 characters).
    new_password : str
        The new password to set (min 8, max 40 characters).

    """

    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    """Database model for a user.

    Attributes
    ----------
    id : str
        The unique identifier for the user.
    hashed_password : str
        The hashed password of the user.

    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=32)
    hashed_password: str


# Properties to return via API, id is always required
class UserPublic(UserBase):
    """Model for returning public user information via the API.

    Attributes
    ----------
    id : str
        The unique identifier for the user.

    """

    id: str


class UsersPublic(SQLModel):
    """Model for returning a list of public user information and the total count.

    Attributes
    ----------
    data : list[UserPublic]
        The list of public user information.
    count : int
        The total number of users.

    """

    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    """Generic message model.

    Attributes
    ----------
    message : str
        The message content.

    """

    message: str


# JSON payload containing access token
class Token(SQLModel):
    """Model representing a JSON payload containing an access token.

    Attributes
    ----------
    access_token : str
        The access token string.
    token_type : str
        The type of the token (default is "bearer").

    """

    access_token: str
    token_type: str = os.environ.get("TOKEN_TYPE", "bearer")


# Contents of JWT token
class TokenPayload(SQLModel):
    """Model representing the payload of a JWT token.

    Attributes
    ----------
    sub : str | None
        The subject identifier (typically the user ID) contained in the token.

    """

    sub: str | None = None


class NewPassword(SQLModel):
    """Model for setting a new password using a token.

    Attributes
    ----------
    token : str
        The password reset token.
    new_password : str
        The new password to set (min 8, max 40 characters).

    """

    token: str
    new_password: str = Field(min_length=8, max_length=40)


class UserSetting(SQLModel, table=True):
    """Model for storing user-specific settings as key-value pairs."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=32)
    section: str = Field(max_length=64)
    key: str = Field(max_length=64)
    value: str = Field(max_length=255)
