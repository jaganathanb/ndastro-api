from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from ndastro_api.core.config import settings
from ndastro_api.core.db import engine, init_db
from ndastro_api.main import app
from ndastro_api.models import User
from ndastro_api.tests.utils.user import authentication_token_from_email
from ndastro_api.tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client,
        email=settings.EMAIL_TEST_USER,
        db=db,
    )
