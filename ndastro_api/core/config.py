"""Configuration settings and utilities for the ndastro API.

This module defines the Settings class for application configuration,
including environment variables, database settings, email settings, and CORS handling.
"""

from __future__ import annotations

import logging
import os
import pathlib
import secrets
import warnings
from typing import Annotated, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_cors(v: str | list[str]) -> list[str] | str:
    """Parse the CORS origins value from environment or config.

    Args:
        v (str | list[str]): The value to parse, typically a string or list.

    Returns:
        list[str] | str: A list of origins or the original value if already a list or string.

    Raises:
        ValueError: If the input cannot be parsed as a list or string.

    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    if isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """Application configuration settings for the ndastro API.

    This class manages environment variables, database settings, email settings, CORS handling,
    and other configuration options required for the application.
    """

    model_config = SettingsConfigDict(
        env_file=f"{pathlib.Path(__file__).resolve().parent.parent}/{os.environ.get('ENV_FILE', '.env')}",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "test", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str,
        BeforeValidator(parse_cors),
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """Return a list of all allowed CORS origins including the frontend host.

        Returns:
            list[str]: A list of origins for CORS configuration.

        """
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST,
        ]

    PROJECT_NAME: str = ""
    SENTRY_DSN: HttpUrl | None = None

    DB_NAME: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_database_uri(self) -> str:
        """Return the SQLAlchemy database URI for the application.

        Returns:
            str: The database URI string.

        """
        return f"sqlite:///{self.DB_NAME}"

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: EmailStr | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        """Return True if email sending is enabled (SMTP host and from email are set).

        Returns:
            bool: True if emails can be sent, False otherwise.

        """
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr = ""
    FIRST_SUPERUSER_PASSWORD: str = ""

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = f'The value of {var_name} is "changethis", for security, please change it, at least for deployments.'
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD",
            self.FIRST_SUPERUSER_PASSWORD,
        )

        return self


settings = Settings()

logger.info("Creating SQLModel engine with database URI: %s", settings.sqlalchemy_database_uri)
