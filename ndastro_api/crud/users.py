"""CRUD operations for User model using FastCRUD.

This module defines the CRUDUser class and an instance for handling user-related database operations.
"""

from fastcrud import FastCRUD

from ndastro_api.models.user import User
from ndastro_api.schemas.user import (
    UserCreateInternal,
    UserDelete,
    UserRead,
    UserUpdate,
    UserUpdateInternal,
)

CRUDUser = FastCRUD[User, UserCreateInternal, UserUpdate, UserUpdateInternal, UserDelete, UserRead]
crud_users = CRUDUser(User)
