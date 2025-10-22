"""Utility functions for astronomical calculations and planetary positions.

This module provides helper functions for degree normalization, DMS conversion,
and filtering planetary positions by rasi, using constants and models from ndastro_api.
"""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Any, cast

from fastapi_babel import _
from skyfield.api import Loader

from ndastro_api.core.constants import DEGREE_MAX, TOTAL_RAASI
from ndastro_api.services.ayanamsa import get_lahiri_ayanamsa

if TYPE_CHECKING:
    from datetime import datetime


load = Loader(pathlib.Path(__file__).parent.parent / "resources" / "data")
eph = load("de440s.bsp")
ts = load.timescale()


def sign(num: int) -> int:
    """Return the sign of the given number.

    Args:
        num (int): The number to get the sign from.

    Returns:
        int: -1 if the number is negative, otherwise 1.

    """
    return -1 if num < 0 else 1


def dms_to_decimal(degrees: int, minutes: int, seconds: float) -> float:
    """Convert degrees, minutes, and seconds to decimal degrees.

    Args:
        degrees (int): The degrees part.
        minutes (int): The minutes part.
        seconds (float): The seconds part.

    Returns:
        float: The decimal degrees.

    """
    return degrees + minutes / 60 + seconds / 3600


def normalize_degree(degree: float) -> float:
    """Normalize the degree to be within 0-360.

    Args:
        degree (float): The degree to normalize.

    Returns:
        float: The normalized degree.

    """
    if degree < 0:
        return DEGREE_MAX + degree
    while degree > DEGREE_MAX:
        degree -= DEGREE_MAX
    return degree


def normalize_rasi_house(position: int) -> int:
    """Normalize the rasi position to be within 1-12.

    Args:
        position (int): The rasi position to normalize.

    Returns:
        int: The normalized rasi position.

    """
    if position < 0:
        return TOTAL_RAASI + position
    while position > TOTAL_RAASI:
        position -= TOTAL_RAASI
    return position


def get_ayanamsa_value(ayanamsa: str, date: datetime) -> float:
    """Convert the ayanamsa string to a float value.

    Args:
        ayanamsa (str): The ayanamsa string to convert.
        date (datetime): The date for which to calculate the ayanamsa.

    Returns:
        float: The float value of the ayanamsa.

    """
    match ayanamsa.lower():
        case "lahiri":
            return get_lahiri_ayanamsa(date)
        case _:
            return 0.0  # Default to 0.0 if no match found


def compute_offset(page: int, items_per_page: int) -> int:
    """Compute the offset for pagination based on page and items per page."""
    return max((page - 1) * items_per_page, 0)


def paginated_response(*, crud_data: Any, page: int, items_per_page: int) -> dict[str, Any]:  # noqa: ANN401
    """Build a paginated response dictionary for list endpoints.

    Args:
        crud_data: An object or list containing the data to paginate. If an object, it should have 'items' and optionally 'total' attributes.
        page (int): The current page number (1-based).
        items_per_page (int): The number of items per page.

    Returns:
        dict: A dictionary containing:
            - items: The list of items for the current page.
            - total: The total number of items.
            - page: The current page number.
            - items_per_page: The number of items per page.
            - next_page: The next page number, or None if there is no next page.
            - prev_page: The previous page number, or None if there is no previous page.

    """
    """Build a paginated response dict for list endpoints."""
    items = crud_data.get("data", [])
    total_count = crud_data.get("total_count", 0)

    return {
        "items": items,
        "total": total_count,
        "total_count": total_count,
        "has_more": (page * items_per_page) < total_count,
        "page": page,
        "items_per_page": items_per_page,
    }


def convert_kattams_to_response_format(kattams: list, kattam_response_class: type, planet_detail_response_class: type) -> list:
    """Convert kattams service response to KattamResponse format.

    This utility function handles the conversion of raw kattam data from the service
    to the standardized KattamResponse format used by API endpoints.

    Args:
        kattams: List of raw kattam objects from the service
        kattam_response_class: The KattamResponse class to use for conversion
        planet_detail_response_class: The PlanetDetailResponse class to use for conversion

    Returns:
        List of objects in KattamResponse format

    """
    return [
        kattam_response_class(
            order=k.order,
            is_ascendant=k.is_ascendant,
            asc_longitude=cast("float", k.asc_longitude.degrees) if k.asc_longitude is not None else 0.0,
            owner=k.owner,
            rasi=k.rasi.value,
            house=k.house.value,
            planets=[
                planet_detail_response_class(
                    name=p.name,
                    short_name=p.short_name,
                    display_name=_(p.short_name[:2]),
                    latitude=cast("float", p.latitude.degrees),
                    longitude=cast("float", p.longitude.degrees),
                    rasi_occupied=p.rasi_occupied.value,
                    house_posited_at=p.house_posited_at.value,
                    planet=p.planet.value,
                    distance=cast("float", p.distance.km) if p.distance else 0.0,
                    nirayana_longitude=cast("float", p.nirayana_longitude.degrees) if p.nirayana_longitude else 0.0,
                    advanced_by=cast("float", p.advanced_by.degrees) if p.advanced_by else 0.0,
                    retrograde=p.retrograde,
                    is_ascendant=p.is_ascendant,
                    natchaththiram=p.natchaththiram.value if p.natchaththiram else 0,
                    paatham=p.paatham if p.paatham else 0,
                )
                for p in k.planets or []
            ]
            if k.planets
            else None,
        )
        for k in kattams
    ]
