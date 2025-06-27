"""Provides functions to determine if a planet is in retrograde motion."""

import pathlib
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, cast

from skyfield.api import Loader
from skyfield.searchlib import find_discrete
from skyfield.timelib import Time
from skyfield.toposlib import Topos
from skyfield.units import Angle

from ndastro_api.core.enums.planet_enum import Planets

if TYPE_CHECKING:
    from skyfield.positionlib import Barycentric

# Load ephemeris
load = Loader(pathlib.Path(__file__).parent.parent / "resources" / "data")
eph = load("de440s.bsp")
ts = load.timescale()

# Define Earth
earth = eph["earth"]


class RetrogradeFunction:
    """A class to determine if a planet is in retrograde motion from a given location on Earth.

    Attributes:
        planet_name (str): The name of the planet to observe.
        latitude (float): The latitude of the observer's location.
        longitude (float): The longitude of the observer's location.
        step_days (int): The number of days to step back for comparison (default is 7).

    Methods:
        __call__(t: Time) -> bool:
            Determines if the planet is in retrograde motion at the given time `t`.
            Returns True if the planet is in retrograde motion, otherwise False.

    """

    def __init__(self, planet_name: str, latitude: float, longitude: float) -> None:
        """Initialize a new instance of the retrograde class.

        Args:
            planet_name (str): The name of the planet.
            latitude (float): The latitude coordinate.
            longitude (float): The longitude coordinate.

        """
        self.planet_name = planet_name
        self.latitude = latitude
        self.longitude = longitude
        self.step_days = 7

    def __call__(self, t: Time) -> bool:
        """Determine if the planet is in retrograde motion at a given time.

        This method calculates the ecliptic longitude of the planet at the given time `t`
        and compares it with the ecliptic longitude of the planet at the previous time `t-1`.
        If the longitude decreases, the planet is in retrograde motion.

        Args:
            t (Time): The time at which to check for retrograde motion.

        Returns:
            bool: True if the planet is in retrograde motion, False otherwise.

        """
        observer = (earth + Topos(latitude=self.latitude, longitude=self.longitude)).at(
            t,
        )
        astrometric = cast("Barycentric", observer).observe(eph[self.planet_name]).apparent()
        _, lon_now, _ = astrometric.ecliptic_latlon()  # Get ecliptic coordinates

        observer2 = (earth + Topos(latitude=self.latitude, longitude=self.longitude)).at(t - 1)
        astrometric2 = cast("Barycentric", observer2).observe(eph[self.planet_name]).apparent()
        _, lon_prev, _ = astrometric2.ecliptic_latlon()  # Get ecliptic coordinates

        return cast("float", lon_now.degrees) < cast(
            "float",
            lon_prev.degrees,
        )  # Retrograde if longitude decreases


def __get_retrograde_function(
    planet_name: str,
    latitude: float,
    longitude: float,
) -> RetrogradeFunction:
    """Create a RetrogradeFunction instance for a given planet and location.

    Args:
        planet_name (str): The name of the planet.
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.

    Returns:
        RetrogradeFunction: An instance of RetrogradeFunction for the specified planet and location.

    """
    return RetrogradeFunction(planet_name, latitude, longitude)


def find_retrograde_periods(
    start_date: datetime,
    end_date: datetime,
    planet_name: str,
    latitude: float,
    longitude: float,
) -> list[tuple[datetime, datetime]]:
    """Calculate the retrograde periods for a given planet within a specified date range and location.

    Args:
        start_date (datetime): The start date of the period to check for retrograde motion.
        end_date (datetime): The end date of the period to check for retrograde motion.
        planet_name (str): The name of the planet to check for retrograde motion.
        latitude (float): The latitude of the observation location.
        longitude (float): The longitude of the observation location.

    Returns:
        list[tuple[datetime, datetime]]: A list of tuples, each containing the start and end datetime of a retrograde period.

    """
    # Time range for 2025
    t0 = ts.utc(start_date)
    t1 = ts.utc(end_date)

    # Find times where Venus changes direction
    times, values = find_discrete(
        t0,
        t1,
        __get_retrograde_function(planet_name, latitude, longitude),
    )
    retrograde_periods = []
    in_retrograde = False
    retro_start = None

    for t, retro in zip(times, values):
        if retro:
            if not in_retrograde:
                retro_start = cast("Time", t).utc_datetime()
                in_retrograde = True
        elif in_retrograde:
            retrograde_periods.append((retro_start, t.utc_datetime()))
            in_retrograde = False

    if in_retrograde:
        retrograde_periods.append((retro_start, t1.utc_datetime()))

    return retrograde_periods


def is_planet_in_retrograde(
    check_date: datetime,
    planet_name: str,
    latitude: Angle,
    longitude: Angle,
) -> bool:
    """Check if a planet is in retrograde motion on a specific date.

    Args:
        check_date (datetime): The date to check for retrograde motion.
        planet_name (str): The name of the planet to check.
        latitude (float): The latitude of the observation location.
        longitude (float): The longitude of the observation location.

    Returns:
        bool: True if the planet is in retrograde motion on the given date, otherwise False.

    """
    if planet_name not in [Planets.SUN.code, Planets.MOON.code, Planets.ASCENDANT.code, Planets.EMPTY.code]:
        start_date = check_date - timedelta(days=365)
        end_date = check_date + timedelta(days=365)
        retrograde_periods = find_retrograde_periods(
            start_date,
            end_date,
            planet_name,
            cast("float", latitude.degrees),
            cast("float", longitude.degrees),
        )

        return any(period_start <= check_date <= period_end for period_start, period_end in retrograde_periods)
    return False
