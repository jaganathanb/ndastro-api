"""Custom exception classes for the ndastro_api core module.

This module defines exceptions related to configuration and core functionality.
"""


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
