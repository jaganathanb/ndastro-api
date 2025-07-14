"""Custom HTTP exception classes for the ndastro_api application.

This module defines application-specific exceptions that extend standard HTTP exceptions
from fastcrud, providing more descriptive error handling for API endpoints.
"""

from fastcrud.exceptions.http_exceptions import (
    BadRequestException,
    CustomException,
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
    RateLimitException,
    UnauthorizedException,
)


class ResourceNotFoundException(NotFoundException):
    """Raised when a requested resource is not found in the system."""

    def __init__(self, message: str = "Requested resource not found.") -> None:
        """Initialize the error with an optional message."""
        self.message = message
        super().__init__(self.message)


class InvalidInputException(BadRequestException):
    """Raised when the input provided to an API endpoint is invalid."""

    def __init__(self, message: str = "Invalid input provided.") -> None:
        """Initialize the error with an optional message."""
        self.message = message
        super().__init__(self.message)


class PermissionDeniedException(ForbiddenException):
    """Raised when a user does not have permission to access a resource."""

    def __init__(self, message: str = "Permission denied for the requested operation.") -> None:
        """Initialize the error with an optional message."""
        self.message = message
        super().__init__(self.message)


class RateLimitExceededException(RateLimitException):
    """Raised when a user exceeds the allowed rate limit for API requests."""

    def __init__(self, message: str = "Rate limit exceeded. Please try again later.") -> None:
        """Initialize the error with an optional message."""
        self.message = message
        super().__init__(self.message)


class DuplicateResourceException(DuplicateValueException):
    """Raised when trying to create a resource that already exists."""

    def __init__(self, message: str = "Resource already exists.") -> None:
        """Initialize the error with an optional message."""
        self.message = message
        super().__init__(self.message)


class UnauthorizedAccessException(UnauthorizedException):
    """Raised when a user attempts to access a resource without proper authentication."""

    def __init__(self, message: str = "Unauthorized access. Please log in.") -> None:
        """Initialize the error with an optional message."""
        self.message = message
        super().__init__(self.message)


class CustomAPIException(CustomException):
    """A custom exception for the ndastro_api application.

    This exception can be used to handle specific errors that do not fit into the standard HTTP exceptions.
    """

    def __init__(self, message: str = "An error occurred in the ndastro_api application.") -> None:
        """Initialize the error with an optional message."""
        self.message = message
        super().__init__()
