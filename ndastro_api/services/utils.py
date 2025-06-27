"""Utility functions for astronomical calculations and planetary positions.

This module provides helper functions for degree normalization, DMS conversion,
and filtering planetary positions by rasi, using constants and models from ndastro_api.
"""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

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
