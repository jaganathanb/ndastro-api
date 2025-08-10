"""Configuration module for ND Astro API.

This module defines settings classes for application, database, cryptography,
caching, rate limiting, and environment configuration, using Pydantic and Starlette.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import cast

from pydantic import SecretStr
from pydantic_settings import BaseSettings
from starlette.config import Config

current_file_dir = Path(__file__).resolve().parent
env_path = current_file_dir.parent / ".env"
config = Config(str(env_path))
config = Config(env_path)


class AppSettings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        APP_NAME (str): The name of the application. Defaults to "ND Astro Rest API".
        APP_DESCRIPTION (str | None): A description of the application. Optional.
        APP_VERSION (str | None): The version of the application. Optional.
        LICENSE_NAME (str | None): The license name for the application. Optional.
        CONTACT_NAME (str | None): The contact person's name for the application. Optional.
        CONTACT_EMAIL (str | None): The contact email address for the application. Optional.

    """

    APP_NAME: str = config("APP_NAME", default="ND Astro Rest API")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default=None)
    LICENSE_NAME: str | None = config("LICENSE", default=None)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: str | None = config("CONTACT_EMAIL", default=None)
    FRONTEND_HOST: str | None = config("FRONTEND_HOST", default="ndastro-ui.onrender.com")
    FRONTENDADMIN_HOST: str | None = config("FRONTENDADMIN_HOST", default="ndastro-pwd-mgnt.onrender.com")
    CORS_ORIGINS: list[str] = config("CORS_ORIGINS", cast=list, default=["*"])
    TOKEN_TYPE: str = config("TOKEN_TYPE", default="bearer")


class CryptSettings(BaseSettings):
    """Configuration settings for cryptographic operations and JWT authentication.

    Attributes:
        SECRET_KEY (SecretStr): The secret key used for cryptographic signing and encryption.
        ALGORITHM (str): The algorithm used for JWT encoding/decoding (default: "HS256").
        ACCESS_TOKEN_EXPIRE_MINUTES (int): The expiration time in minutes for access tokens (default: 30).
        REFRESH_TOKEN_EXPIRE_DAYS (int): The expiration time in days for refresh tokens (default: 7).

    """

    SECRET_KEY: SecretStr = config("SECRET_KEY", cast=SecretStr)
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=7 * 24 * 60)  # Default to 7 days in minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=365)  # Default to 1 year in days


class DatabaseSettings(BaseSettings):
    """Configuration settings for the application's database connection.

    This class should be extended with specific database-related settings
    such as host, port, username, password, and database name. It inherits
    from `BaseSettings` to enable environment variable parsing and validation.

    Attributes:
        (To be defined as needed for database configuration)

    """


class SQLiteSettings(DatabaseSettings):
    """Settings for configuring SQLite database connections.

    Attributes:
        SQLITE_URI (str): The file path or URI to the SQLite database. Defaults to './ndastro_api/resources/data/ndastro_app.db'.
        SQLITE_SYNC_PREFIX (str): The URI prefix used for synchronous SQLite connections. Defaults to 'sqlite:///'.
        SQLITE_ASYNC_PREFIX (str): The URI prefix used for asynchronous SQLite connections using aiosqlite. Defaults to 'sqlite+aiosqlite:///'.

    """

    SQLITE_URI: str = config("SQLITE_URI", default="./ndastro_api/resources/data/ndastro_app.db")
    SQLITE_SYNC_PREFIX: str = config("SQLITE_SYNC_PREFIX", default="sqlite:///")
    SQLITE_ASYNC_PREFIX: str = config("SQLITE_ASYNC_PREFIX", default="sqlite+aiosqlite:///")


class MySQLSettings(DatabaseSettings):
    """Configuration settings for connecting to a MySQL database.

    Attributes:
        MYSQL_USER (str): The username for the MySQL database connection. Defaults to "username".
        MYSQL_PASSWORD (str): The password for the MySQL database connection. Defaults to "password".
        MYSQL_SERVER (str): The hostname or IP address of the MySQL server. Defaults to "localhost".
        MYSQL_PORT (int): The port number for the MySQL server. Defaults to 5432.
        MYSQL_DB (str): The name of the MySQL database. Defaults to "dbname".
        MYSQL_URI (str): The constructed MySQL URI using the provided user, password, server, port, and database.
        MYSQL_SYNC_PREFIX (str): The prefix for synchronous MySQL connections. Defaults to "mysql://".
        MYSQL_ASYNC_PREFIX (str): The prefix for asynchronous MySQL connections. Defaults to "mysql+aiomysql://".
        MYSQL_URL (str | None): An optional full MySQL connection URL. Defaults to None.

    """

    MYSQL_USER: str = config("MYSQL_USER", default="username")
    MYSQL_PASSWORD: str = config("MYSQL_PASSWORD", default="password")
    MYSQL_SERVER: str = config("MYSQL_SERVER", default="localhost")
    MYSQL_PORT: int = config("MYSQL_PORT", default=5432)
    MYSQL_DB: str = config("MYSQL_DB", default="dbname")
    MYSQL_URI: str = f"{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"
    MYSQL_SYNC_PREFIX: str = config("MYSQL_SYNC_PREFIX", default="mysql://")
    MYSQL_ASYNC_PREFIX: str = config("MYSQL_ASYNC_PREFIX", default="mysql+aiomysql://")
    MYSQL_URL: str | None = config("MYSQL_URL", default=None)


class PostgresSettings(DatabaseSettings):
    """Settings for configuring a PostgreSQL database connection.

    Attributes:
        POSTGRES_USER (str): Username for the PostgreSQL database. Defaults to "postgres".
        POSTGRES_PASSWORD (str): Password for the PostgreSQL database. Defaults to "postgres".
        POSTGRES_SERVER (str): Hostname or IP address of the PostgreSQL server. Defaults to "localhost".
        POSTGRES_PORT (int): Port number for the PostgreSQL server. Defaults to 5432.
        POSTGRES_DB (str): Name of the PostgreSQL database. Defaults to "postgres".
        POSTGRES_SYNC_PREFIX (str): URI prefix for synchronous PostgreSQL connections. Defaults to "postgresql://".
        POSTGRES_ASYNC_PREFIX (str): URI prefix for asynchronous PostgreSQL connections. Defaults to "postgresql+asyncpg://".
        POSTGRES_URI (str): Constructed URI string for connecting to the PostgreSQL database using the provided credentials and server information.
        POSTGRES_URL (str | None): Optional full PostgreSQL connection URL. If not provided, it defaults to None.

    """

    POSTGRES_USER: str = config("POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", default="postgres")
    POSTGRES_SERVER: str = config("POSTGRES_SERVER", default="localhost")
    POSTGRES_PORT: int = config("POSTGRES_PORT", default=5432)
    POSTGRES_DB: str = config("POSTGRES_DB", default="postgres")
    POSTGRES_SYNC_PREFIX: str = config("POSTGRES_SYNC_PREFIX", default="postgresql://")
    POSTGRES_ASYNC_PREFIX: str = config("POSTGRES_ASYNC_PREFIX", default="postgresql+asyncpg://")
    POSTGRES_URI: str = f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    POSTGRES_URL: str | None = config("POSTGRES_URL", default=None)


class FirstUserSettings(BaseSettings):
    """Settings for the initial admin user.

    Attributes:
        ADMIN_NAME (str): The display name of the admin user. Defaults to "admin".
        ADMIN_EMAIL (str): The email address of the admin user. Defaults to "admin@admin.com".
        ADMIN_USERNAME (str): The username for the admin user. Defaults to "admin".
        ADMIN_PASSWORD (str): The password for the admin user. Defaults to "".

    """

    ADMIN_NAME: str = config("ADMIN_NAME", default="admin")
    ADMIN_EMAIL: str = config("ADMIN_EMAIL", default="admin@dapps.com")
    ADMIN_USERNAME: str = config("ADMIN_USERNAME", default="admin")
    ADMIN_PASSWORD: str = config("ADMIN_PASSWORD", default="")


class TestSettings(BaseSettings):
    """TestSettings is a configuration class for managing test-specific settings."""

    TEST_DATABASE_URI: str = config("TEST_DATABASE_URI", default="./test.db")
    TEST_DATABASE_SYNC_PREFIX: str = config("TEST_DATABASE_SYNC_PREFIX", default="sqlite:///")
    TEST_DATABASE_ASYNC_PREFIX: str = config("TEST_DATABASE_ASYNC_PREFIX", default="sqlite+aiosqlite:///")
    TEST_DATABASE_URL: str | None = config("TEST_DATABASE_URL", default=None)


class ClientSideCacheSettings(BaseSettings):
    """ClientSideCacheSettings is a configuration class for managing client-side caching settings."""

    CLIENT_CACHE_MAX_AGE: int = config("CLIENT_CACHE_MAX_AGE", default=60)


class CRUDAdminSettings(BaseSettings):
    """CRUDAdminSettings is a configuration class for managing CRUD Admin settings."""

    CRUD_ADMIN_ENABLED: bool = config("CRUD_ADMIN_ENABLED", default=True)
    CRUD_ADMIN_MOUNT_PATH: str = config("CRUD_ADMIN_MOUNT_PATH", default="/admin")

    CRUD_ADMIN_ALLOWED_IPS_LIST: list[str] | None = None
    CRUD_ADMIN_ALLOWED_NETWORKS_LIST: list[str] | None = None
    CRUD_ADMIN_MAX_SESSIONS: int = config("CRUD_ADMIN_MAX_SESSIONS", default=10)
    CRUD_ADMIN_SESSION_TIMEOUT: int = config("CRUD_ADMIN_SESSION_TIMEOUT", default=1440)
    SESSION_SECURE_COOKIES: bool = config("SESSION_SECURE_COOKIES", default=True)

    CRUD_ADMIN_TRACK_EVENTS: bool = config("CRUD_ADMIN_TRACK_EVENTS", default=True)
    CRUD_ADMIN_TRACK_SESSIONS: bool = config("CRUD_ADMIN_TRACK_SESSIONS", default=True)


class EnvironmentOption(Enum):
    """Enumeration for different environment options."""

    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseType(Enum):
    """Enumeration for different database types."""

    SQLITE = "sqlite"
    POSTGRES = "postgres"
    MYSQL = "mysql"


class EnvironmentSettings(BaseSettings):
    """Settings for the application's environment configuration."""

    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default=EnvironmentOption.LOCAL)
    DATABASE_TYPE: DatabaseType = config("DATABASE_TYPE", default=DatabaseType.SQLITE)


class EmailSettings(BaseSettings):
    """Settings for email configuration."""

    EMAILS_ENABLED: bool = config("EMAILS_ENABLED", default=False)
    EMAILS_FROM_NAME: str = config("EMAILS_FROM_NAME", default="ND Astro by DApps")
    EMAILS_FROM_EMAIL: str = config("EMAILS_FROM_EMAIL", default="ndastro@dhuruvah.in")
    SMTP_HOST: str = config("SMTP_HOST", default="smtppro.zoho.in")
    SMTP_PORT: int = config("SMTP_PORT", default=465)
    SMTP_TLS: bool = config("SMTP_TLS", default=False)
    SMTP_SSL: bool = config("SMTP_SSL", default=True)
    SMTP_USER: str | None = config("SMTP_USER", default="ndastro@dhuruvah.in")
    SMTP_PASSWORD: SecretStr | None = cast("SecretStr", config("SMTP_PASSWORD", default=None))
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = config("EMAIL_RESET_TOKEN_EXPIRE_HOURS", default=24)
    EMAIL_TEST_RECIPIENT: str | None = config("EMAIL_TEST_RECIPIENT", default=None)


class Settings(
    AppSettings,
    PostgresSettings,
    MySQLSettings,
    SQLiteSettings,
    CryptSettings,
    FirstUserSettings,
    TestSettings,
    ClientSideCacheSettings,
    CRUDAdminSettings,
    EnvironmentSettings,
    EmailSettings,
):
    """Main settings class that aggregates all configuration settings for the application."""


settings = Settings()
"""Global settings instance for the application."""
