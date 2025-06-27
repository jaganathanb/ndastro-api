"""Module to define ayanamsa related definations."""

import datetime

from skyfield.api import load

from ndastro_api.core.constants import AYANAMSA

# Load Skyfield's timescale
ts = load.timescale()


def get_lahiri_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Lahiri Ayanamsa for a given date."""
    # Constants in the Lahiri Ayanamsa formula
    c0 = AYANAMSA.AYANAMSA_AT_J2000  # Constant term
    c1 = AYANAMSA.DEG_PER_JCENTURY  # Linear term (degrees per Julian century)
    c2 = AYANAMSA.DEG_PER_SQUARE_JCENTURY  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def calculate_b6(date: tuple[int, int, int]) -> float:
    """Calculate B6 parameter for Julian Date."""
    # Calculate Julian Date using Skyfield
    t = ts.utc(*date)
    jd = t.tt  # Julian Date in Terrestrial Time
    # Compute B6 parameter
    return (jd - get_days_since_julian(AYANAMSA.CENTURY_19)) / get_days_in_julian_century(AYANAMSA.CENTURY_20, AYANAMSA.CENTURY_21)


def get_days_in_julian_century(start_year: int, end_year: int) -> float:
    """Calculate the number of days in a Julian century."""
    # Define the start of a Julian century
    start = ts.tt(start_year, 1, 1, 12)  # J2000.0 epoch (2451545.0 JD)

    # Define the end of the Julian century (100 Julian years later)
    end = ts.tt(end_year, 1, 1, 12)  # 2100 January 1, 12:00 TT

    # Calculate the Julian Dates
    jd_start = start.tt  # Julian Date at J2000.0
    jd_end = end.tt  # Julian Date at 2100 January 1

    # Compute the number of days in the century
    return jd_end - jd_start


def get_days_since_julian(century: int) -> float:
    """Calculate the number of days in a Julian century given."""
    # Define the start of a Julian century
    start = ts.tt(century, 1, 1, 12)  # J2000.0 epoch (2451545.0 JD)

    return start.tt
