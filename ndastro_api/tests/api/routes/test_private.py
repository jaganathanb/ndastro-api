import httpx
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from ndastro_api.core.config import settings
from ndastro_api.models import User


def test_create_user(client: TestClient, db: Session, superuser_token_headers: dict[str, str]) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/private/users/",
        json={
            "email": "hello@hello.com",
            "password": "password123",
            "full_name": "Hello World",
        },
        headers=superuser_token_headers,
    )

    assert r.status_code == httpx.codes.OK

    data = r.json()

    user = db.exec(select(User).where(User.id == data["id"])).first()

    assert user
    assert user.email == "hello@hello.com"
    assert user.full_name == "Hello World"
