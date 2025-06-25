"""Routes for private user management in the ndastro API.

This module provides endpoints for creating private users and related operations.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from ndastro_api.api.deps import SessionDep
from ndastro_api.core.security import get_password_hash
from ndastro_api.models import User, UserPublic

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    """Schema for creating a private user.

    Attributes
    ----------
    email : str
        The email address of the user.
    password : str
        The password for the user account.
    full_name : str
        The full name of the user.

    """

    email: str
    password: str
    full_name: str


@router.post("/users/")
def create_user(user_in: PrivateUserCreate, session: SessionDep) -> UserPublic:
    """Create a new user."""
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserPublic.model_validate(user)
