"""Defines the Dasha class.

Represents an astrological period with associated attributes such as name, description, cycle years, and planets.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import cast

import pytz

from ndastro.gui.models.dasha_detail import DashaTypes
from ndastro.libs.planet_enum import Planets


@dataclass
class Dasha:
    """Represents an astrological period with attributes such as name, description etc."""

    name: str
    """The name of the astrological period."""
    description: str | None = None
    """A description of the dasha period."""
    start_date: datetime | None = None
    """The start date of the dasha period."""
    end_date: datetime | None = None
    """The end date of the dasha period."""
    is_running: bool = False
    """Indicates whether the dasha period is currently running."""
    dasha_type: DashaTypes = DashaTypes.MAHA
    """The type of dasha period."""
    owner: Planets = Planets.SUN
    """The owner planet of the dasha period."""

    @property
    def remaining_period(self) -> timedelta | None:
        """Calculate and return the remaining period of the Dasha as a timedelta.

        Returns:
            timedelta | None: The remaining period as a timedelta, or None if start_date or end_date is not set.

        """
        if self.start_date and self.end_date:
            return cast("datetime", self.end_date) - datetime.now(tz=pytz.timezone("UTC"))
        return None

    def __repr__(self) -> str:
        """Provide a string representation of the Dasha instance."""
        return f"MahaDasha(name={self.name}, dasha_type={self.dasha_type})"
