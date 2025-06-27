"""Module to hold planet postion related data classes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ndastro_api.core.enums.planet_enum import Planets

if TYPE_CHECKING:
    from skyfield.units import Angle, Distance

    from ndastro_api.core.enums.house_enum import Houses
    from ndastro_api.core.enums.nakshatra_enum import Natchaththirams
    from ndastro_api.core.enums.rasi_enum import Rasis


@dataclass
class PlanetDetail:
    """Represents the position of a planet with various attributes.

    Attributes:
        name (str): The name of the planet.
        short_name (str): A unique code representing the planet.
        latitude (Angle): The latitude of the planet's position.
        longitude (Angle): The longitude of the planet's position.
        distance (Distance): The distance of the planet from a reference point.
        s_longitude (Angle | None): The sidereal longitude of the planet, if applicable.
        posited_at (Houses | None): The house in which the planet is posited, if applicable.
        advanced_by (Angle | None): The angle by which the planet has advanced, if applicable.
        retrograde (bool): Indicates whether the planet is in retrograde motion.
        rasi_occupied (Rasis | None): The rasi (zodiac sign) occupied by the planet, if applicable.
        is_ascendant (bool): Indicates whether the planet is the ascendant.
        planet (Planets): The planet associated with this position.
        nakshatra (Natchaththirams | None): The natchaththiram (lunar mansion) occupied by the planet, if applicable.
        paatham (int | None): The paatham (quarter) of the nakshatra occupied by the planet, if applicable.

    """

    name: str
    """The name of the planet."""

    short_name: str
    """A unique code representing the planet."""

    latitude: Angle
    """The latitude of the planet's position."""

    longitude: Angle
    """The longitude of the planet's position."""

    rasi_occupied: Rasis
    """The rasi (zodiac sign) occupied by the planet"""

    house_posited_at: Houses
    """The house in which the planet is posited"""

    planet: Planets = Planets.EMPTY
    """The planet associated with this position."""

    distance: Distance | None = None
    """The distance of the planet from a reference point."""

    nirayana_longitude: Angle | None = None
    """The sidereal longitude of the planet, if applicable."""

    advanced_by: Angle | None = None
    """The angle by which the planet has advanced, if applicable."""

    retrograde: bool = False
    """Indicates whether the planet is in retrograde motion."""

    is_ascendant: bool = False
    """Indicates whether the planet is the ascendant."""

    natchaththiram: Natchaththirams | None = None
    """The natchaththiram (lunar mansion) occupied by the planet, if applicable."""

    paatham: int | None = None
    """The paatham (quarter) of the natchaththiram occupied by the planet, if applicable."""
