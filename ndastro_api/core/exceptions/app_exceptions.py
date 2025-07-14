"""Custom exception classes for common error scenarios in ndastro_api.core.exceptions."""

from starlette import status

from ndastro_api.core.exceptions.http_exceptions import CustomException


class RedisClientNotInitializedError(Exception):
    """Raised when the Redis client is not initialized."""

    def __init__(self, message: str = "Redis client is not initialized.") -> None:
        """Initialize the error with an optional message."""
        self.message = message
        super().__init__(self.message)


class EmailConfigurationError(Exception):
    """Exception raised when email configuration variables are missing."""

    def __init__(self) -> None:
        """Initialize EmailConfigurationError with a default message."""
        super().__init__("No provided configuration for email variables")


class UserIdNotSetError(Exception):
    """Exception raised when a user ID is not set."""

    def __init__(self, user_id: str) -> None:
        """Initialize UserIdNotSetError with the given user_id."""
        super().__init__(f"User id not set: {user_id}")


class RefreshTokenMissingInvalidException(CustomException):
    """Exception raised when a refresh token is missing or invalid."""

    def __init__(self) -> None:
        """Initialize RefreshTokenMissingInvalidException with a 401 Unauthorized error."""
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing or invalid.")
