"""Security utilities for password hashing and JWT token creation/verification.

This module provides functions for hashing passwords, verifying password hashes,
and creating JSON Web Tokens (JWT) for user authentication.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from ndastro_api.core.config import settings

pwd_context = CryptContext(schemes=["sha256_crypt", "md5_crypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(subject: str, expires_delta: timedelta) -> str:
    """Create a JSON Web Token (JWT) for user authentication.

    Parameters
    ----------
    subject : str | Any
        The subject identifier (typically the user ID) to include in the token.
    expires_delta : timedelta
        The duration for which the token will be valid.

    Returns
    -------
    str
        The encoded JWT as a string.

    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plain password matches the given hashed password.

    Parameters
    ----------
    plain_password : str
        The plain text password to verify.
    hashed_password : str
        The hashed password to compare against.

    Returns
    -------
    bool
        True if the password matches the hash, False otherwise.

    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password using the configured password context.

    Parameters
    ----------
    password : str
        The plain text password to hash.

    Returns
    -------
    str
        The hashed password as a string.

    """
    return pwd_context.hash(password)
