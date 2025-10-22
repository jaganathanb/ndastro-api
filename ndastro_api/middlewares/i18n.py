"""FastAPI middleware for internationalization support."""

from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware

from ndastro_api.core.babel_i18n import DEFAULT_LOCALE, LANGUAGES

if TYPE_CHECKING:
    from fastapi import Request


class I18nMiddleware(BaseHTTPMiddleware):
    """Middleware to handle internationalization for FastAPI requests."""

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001, ANN201
        """Process request and inject language information."""
        # Get language from various sources in order of preference:
        # 1. Query parameter 'lang'
        # 2. Header 'Accept-Language'
        # 3. Default language

        language = DEFAULT_LOCALE

        # Check query parameter first
        if "lang" in request.query_params:
            lang_param = request.query_params["lang"]
            if lang_param in LANGUAGES:
                language = lang_param

        # Check Accept-Language header if no query param
        elif "Accept-Language" in request.headers:
            accept_lang = request.headers["Accept-Language"]
            # Parse Accept-Language header (simplified)
            for lang_entry in accept_lang.split(","):
                lang_code = lang_entry.split(";")[0].strip().split("-")[0]
                if lang_code in LANGUAGES:
                    language = lang_code
                    break

        # Store language in request state for use in route handlers
        request.state.language = language

        # Add language header to response
        response = await call_next(request)
        response.headers["Content-Language"] = language

        return response


def get_request_language(request: Request) -> str:
    """Get the language for the current request.

    Args:
        request: FastAPI request object

    Returns:
        Language code for the request

    """
    return getattr(request.state, "language", DEFAULT_LOCALE)
