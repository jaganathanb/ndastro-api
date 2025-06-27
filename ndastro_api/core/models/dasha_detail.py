"""Define the Dasha class, which represents astrological dasha periods.

Include attributes such as name, description, cycle years, and a mapping of planets to their respective periods.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ndastro.libs.planet_enum import Planets


class Dashas(Enum):
    """Enum to hold dasha systems."""

    VIMSHOTTARI = 1
    ASHTOTTARI = 2
    KALACHAKRA = 3

    def __str__(self) -> str:
        """Return the display name of the dasha system."""
        return self.name.capitalize()


class DashaTypes(Enum):
    """Enum to hold dasha types."""

    MAHA = 1
    ANTAR = 2
    PRATYANTAR = 3
    SOOKSHMA = 4

    def __str__(self) -> str:
        """Return the display name of the dasha type."""
        return self.name.capitalize()


@dataclass
class DashaDetail:
    """Defines the DashaSystem class.

    Represents a system of dasha periods with associated attributes such as name, description, and available systems.
    """

    name: str
    """The name of the astrological period."""
    dasha_system: Dashas = Dashas.VIMSHOTTARI
    """The type of dasha system."""
    description: str | None = None
    """A description of the dasha period."""
    cycle_years: int = 0
    """The total number of years in the dasha cycle."""
    planets_period: dict[Planets, int] | None = None
    """A dictionary mapping planet names to their respective periods in the dasha cycle."""
