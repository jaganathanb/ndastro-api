"""FastAPI-Babel internationalization configuration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from fastapi_babel import BabelConfigs, BabelMiddleware, _

if TYPE_CHECKING:
    from fastapi import FastAPI, Request

# Supported languages
LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలुગు (Telugu)",
    "kn": "ಕನ್ನಡ (Kannada)",
    "ml": "മലയാളം (Malayalam)",
}

# Default language
DEFAULT_LOCALE = "en"

# Babel configuration
configs = BabelConfigs(
    ROOT_DIR=str(Path(__file__).parent.parent.parent),
    BABEL_DEFAULT_LOCALE=DEFAULT_LOCALE,
    BABEL_TRANSLATION_DIRECTORY=str(Path(__file__).parent.parent / "locales"),
)


def get_locale(request: Request) -> str:
    """Get locale from request.

    Priority:
    1. 'lang' query parameter
    2. Accept-Language header
    3. Default locale

    Args:
        request: FastAPI request object

    Returns:
        Language code

    """
    # Check query parameter first
    if "lang" in request.query_params:
        lang = request.query_params["lang"]
        if lang in LANGUAGES:
            return lang

    # Check Accept-Language header
    accept_language = request.headers.get("Accept-Language", "")
    if accept_language:
        # Parse Accept-Language header (simplified)
        for lang_entry in accept_language.split(","):
            lang_code = lang_entry.split(";")[0].strip().split("-")[0]
            if lang_code in LANGUAGES:
                return lang_code

    return DEFAULT_LOCALE


def init_babel(app: FastAPI) -> None:
    """Initialize Babel with FastAPI app.

    Args:
        app: FastAPI application instance

    """
    app.add_middleware(BabelMiddleware, babel_configs=configs, locale_selector=get_locale)


# Translation helper functions
def translate(key: str) -> str:
    """Translate a key using current locale.

    Args:
        key: Translation key

    Returns:
        Translated string

    """
    return _(key)
