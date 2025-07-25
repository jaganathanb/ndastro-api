from fastapi.testclient import TestClient
from sqlmodel import Session

from ndastro_api.core.config import settings
from ndastro_api.core.exceptions import UserIdNotSetError
from ndastro_api.models import User, UserCreate, UserUpdate
from ndastro_api.services import users
from ndastro_api.tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *,
    client: TestClient,
    email: str,
    password: str,
) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    return {"Authorization": f"Bearer {auth_token}"}


def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    return users.create_user(session=db, user_create=user_in)


def authentication_token_from_email(
    *,
    client: TestClient,
    email: str,
    db: Session,
) -> dict[str, str]:
    """Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = users.get_user_by_email(session=db, email=email)
    if not user:
        user_in_create = UserCreate(email=email, password=password)
        user = users.create_user(session=db, user_create=user_in_create)
    else:
        user_in_update = UserUpdate(password=password, email=email)
        if not user.id:
            raise UserIdNotSetError(user_id=user.id)
        user = users.update_user(session=db, db_user=user, user_in=user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)
