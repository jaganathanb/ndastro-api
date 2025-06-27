"""Module to hold planet postion related data classes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skyfield.units import Angle

    from ndastro_api.core.enums.house_enum import Houses
    from ndastro_api.core.enums.planet_enum import Planets
    from ndastro_api.core.enums.rasi_enum import Rasis
    from ndastro_api.core.models.planet_position import PlanetDetail


@dataclass
class Kattam:
    """Holds data for each square (kattam/கட்டம்) on the chart."""

    order: int
    is_ascendant: bool
    asc_longitude: Angle | None
    owner: Planets
    rasi: Rasis
    house: Houses
    planets: list[PlanetDetail] | None
