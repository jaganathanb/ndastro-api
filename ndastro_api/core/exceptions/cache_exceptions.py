"""Custom exceptions for cache-related errors in the ndastro_api.

Includes errors for cache identification, invalid requests, and missing clients.
"""


class CacheIdentificationInferenceError(Exception):
    """Raised when the cache system cannot infer the resource ID to be cached."""

    def __init__(self, message: str = "Could not infer id for resource being cached.") -> None:
        """Initialize the error with an optional message."""
        self.message = message
        super().__init__(self.message)


class InvalidRequestError(Exception):
    """Raised when an unsupported or invalid request is made to the cache system."""

    def __init__(self, message: str = "Type of request not supported.") -> None:
        """Initialize the error with an optional message."""
        self.message = message
        super().__init__(self.message)


class MissingClientError(Exception):
    """Raised when a required cache client instance is missing or None."""

    def __init__(self, message: str = "Client is None.") -> None:
        """Initialize the error with an optional message."""
        self.message = message
        super().__init__(self.message)
