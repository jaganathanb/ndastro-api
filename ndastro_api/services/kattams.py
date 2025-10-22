"""Services for calculating kattams (astrological charts) based on given datetime and location.

This module provides functions to compute kattams using planetary positions, ascendant, and ayanamsa.
"""

from datetime import datetime
from itertools import groupby
from typing import TYPE_CHECKING, cast

from skyfield.units import Angle

from ndastro_api.core.constants import TOTAL_RAASI
from ndastro_api.core.enums.house_enum import Houses
from ndastro_api.core.enums.rasi_enum import Rasis
from ndastro_api.core.models.kattam import Kattam
from ndastro_api.services.position import (
    get_sidereal_ascendant_position,
    get_sidereal_planet_positions,
)

if TYPE_CHECKING:
    from ndastro_api.core.enums.planet_enum import Planets


def get_kattams(lat: Angle, lon: Angle, given_time: datetime, ayanamsa: float) -> list[Kattam]:
    """Return the kattams for the given datetime, latitude, and longitude.

    Args:
        lat (Angle): The latitude of the observer.
        lon (Angle): The longitude of the observer.
        given_time (datetime): The datetime of the observation.
        ayanamsa (float): The ayanamsa value to use for calculations.

    Returns:
        list[Kattam]: A list of kattams.

    """
    ascendant = get_sidereal_ascendant_position(given_time, lat, lon, ayanamsa)
    planets = get_sidereal_planet_positions(lat, lon, given_time, ayanamsa)

    rasis_planets = {k: list(g) for k, g in groupby(sorted(planets, key=lambda x: x.rasi_occupied), lambda x: x.rasi_occupied)}

    kattams: list[Kattam] = []
    rasi_list = list(range(1, TOTAL_RAASI + 1))
    normalized_rasi_list = rasi_list[ascendant.rasi_occupied.value - 1 :] + rasi_list[: ascendant.rasi_occupied.value - 1]
    for idx, rasi_num in enumerate(normalized_rasi_list):
        rasi = Rasis(rasi_num)
        rp = rasis_planets.get(rasi, [])
        kattam = Kattam(
            order=rasi_num,
            owner=cast("Planets", rasi.owner),
            is_ascendant=ascendant.rasi_occupied == rasi,
            planets=rp,
            rasi=rasi,
            house=Houses(idx + 1),
            asc_longitude=ascendant.longitude if ascendant.rasi_occupied == rasi else None,
        )
        kattams.append(kattam)

    kattams.sort(key=lambda x: x.order)

    return kattams
