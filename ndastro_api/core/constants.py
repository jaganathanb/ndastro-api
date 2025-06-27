"""Constants and utility classes for astronomical calculations.

This module defines Unicode symbols, ayanamsa values, and other constants
used throughout the ndastro API for astronomical computations.
"""

from typing import Final


class SYMBOLS:
    """Unicode symbols used in astronomy."""

    DEGREE_SYMBOL = "\u00b0"
    MINUTE_SYMBOL = "\u2032"
    SECOND_SYMBOL = "\u2033"
    RETROGRADE_SYMBOL = "℞"
    ASENDENT_SYMBOL = "L"


class AYANAMSA:
    """Different Ayanamsas for the system."""

    CENTURY_19: Final[int] = 1900
    CENTURY_20: Final[int] = 2000
    CENTURY_21: Final[int] = 2100

    AYANAMSA_AT_J2000 = 22.460148
    DEG_PER_JCENTURY = 1.396042
    DEG_PER_SQUARE_JCENTURY = 0.000308

    LAHIRI = 24.12

    def __init__(self, name: str) -> None:
        """Set current active ayanamsa.

        Args:
            name (str): Name of the current active ayanams.

        """
        self._name = name

    @property
    def name(self) -> str:
        """Name of the active ayanamsa."""
        return self._name

    @property
    def value(self) -> float:
        """Return value of the active ayanamsa.

        Returns:
            value (float): Ayanamsa value

        """
        match self.name:
            case "lahiri":
                return self.LAHIRI
            case _:
                return self.LAHIRI

    @value.setter
    def value(self, val: float) -> None:
        match self.name:
            case "lahiri":
                self.LAHIRI = val
            case _:
                self.LAHIRI = 24


DEGREE_MAX = 360
DEGREES_PER_RAASI = 30
TOTAL_RAASI = 12
TOTAL_NAKSHATRAS = 27
TOTAL_PADAM = 4
DEGREES_PER_NAKSHATRA = 13.333333333333334
DEGREES_PER_PADAM = 3.3333333333333335

KATTAM_RASI_MAP = [12, 1, 2, 3, 11, 4, 10, 5, 9, 8, 7, 6]

LOCALES = [("English", "en"), ("Tamil", "ta")]
THEMES = [("Light", "light"), ("Dark", "dark")]
