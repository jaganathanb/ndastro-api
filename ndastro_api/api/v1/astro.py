"""Astro API endpoints for planetary and astronomy calculations."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, cast

import pytz
from babel.dates import format_datetime
from fastapi import APIRouter, Query, Request
from fastapi.responses import Response
from fastapi_babel import _
from pydantic import BaseModel
from skyfield.units import Angle

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.core.babel_i18n import get_locale
from ndastro_api.core.enums.planet_enum import Planets
from ndastro_api.services.chart_utils import (
    BirthDetails,
    generate_south_indian_chart_svg,
)
from ndastro_api.services.kattams import get_kattams
from ndastro_api.services.position import (
    calculate_lunar_nodes,
    get_sidereal_ascendant_position,
    get_sidereal_planet_positions,
    get_sunrise_sunset,
)
from ndastro_api.services.utils import (
    convert_kattams_to_response_format,
    get_ayanamsa_value,
)

router = APIRouter(prefix="/astro", tags=["Astro"], dependencies=get_conditional_dependencies())


class ChartType(str, Enum):
    """Enumeration for different chart types."""

    SOUTH_INDIAN = "south-indian"
    NORTH_INDIAN = "north-indian"  # For future implementation


class ChartConfig(BaseModel):
    """Configuration for chart generation."""

    chart_type: ChartType = ChartType.SOUTH_INDIAN
    lang: str = "en"
    name: str | None = "ND Astro"
    place: str | None = "Salem"


class ChartRequest(BaseModel):
    """Request model for chart generation."""

    lat: float
    lon: float
    datetime: datetime
    ayanamsa: str
    chart_type: ChartType = ChartType.SOUTH_INDIAN
    name: str = "ND Astro"
    place: str = "Salem"
    lang: str = "en"


class PlanetDetailResponse(BaseModel):
    """Response model for a planet's tropical position."""

    name: str
    """The name of the planet."""

    display_name: str | None = None
    """The localized display name of the planet."""

    short_name: str
    """A unique code representing the planet."""

    latitude: float
    """The latitude of the planet's position."""

    longitude: float
    """The longitude of the planet's position."""

    rasi_occupied: int
    """The rasi (zodiac sign) occupied by the planet"""

    house_posited_at: int
    """The house in which the planet is posited"""

    planet: int
    """The planet associated with this position."""

    distance: float
    """The distance of the planet from a reference point."""

    nirayana_longitude: float
    """The sidereal longitude of the planet, if applicable."""

    advanced_by: float
    """The angle by which the planet has advanced, if applicable."""

    retrograde: bool = False
    """Indicates whether the planet is in retrograde motion."""

    is_ascendant: bool = False
    """Indicates whether the planet is the ascendant."""

    natchaththiram: int
    """The natchaththiram (lunar mansion) occupied by the planet, if applicable."""

    paatham: int
    """The paatham (quarter) of the natchaththiram occupied by the planet, if applicable."""


@router.get("/lunar-nodes")
def get_lunar_nodes(
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(tz=pytz.utc).isoformat(timespec="seconds"),
) -> list[PlanetDetailResponse]:
    """Calculate the positions of Rahu and Kethu (lunar nodes) for a given datetime."""
    results = calculate_lunar_nodes(datetime.fromisoformat(dateandtime))
    return [
        PlanetDetailResponse(
            name=r.planet.name,
            short_name=r.short_name,
            latitude=cast("float", r.latitude.degrees),
            longitude=cast("float", r.longitude.degrees),
            rasi_occupied=r.rasi_occupied.value,
            house_posited_at=r.house_posited_at.value,
            planet=r.planet.value,
            distance=cast("float", r.distance.km) if r.distance else 0.0,
            nirayana_longitude=cast("float", r.nirayana_longitude.degrees) if r.nirayana_longitude else 0.0,
            advanced_by=cast("float", r.advanced_by.degrees) if r.advanced_by else 0.0,
            retrograde=r.retrograde,
            is_ascendant=r.is_ascendant,
            natchaththiram=r.natchaththiram.value if r.natchaththiram else 0,
            paatham=r.paatham if r.paatham else 0,
        )
        for r in results
    ]


class SiderealPositionsRequest(BaseModel):
    """Request model for sidereal planetary positions."""

    lat: float
    lon: float
    datetime: datetime
    ayanamsa: str


@router.get("/planets")
def get_sidereal_positions(
    lat: Annotated[float, Query(description="Latitude")] = 12.59,
    lon: Annotated[float, Query(description="Longitude")] = 77.36,
    ayanamsa: Annotated[str, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(tz=pytz.utc).isoformat(timespec="seconds"),
) -> list[PlanetDetailResponse]:
    """Calculate sidereal planetary positions for given latitude, longitude, datetime, and ayanamsa."""
    results = get_sidereal_planet_positions(
        Angle(degrees=lat), Angle(degrees=lon), datetime.fromisoformat(dateandtime), get_ayanamsa_value(ayanamsa, datetime.fromisoformat(dateandtime))
    )
    return [
        PlanetDetailResponse(
            name=r.planet.name,
            short_name=r.short_name,
            latitude=cast("float", r.latitude.degrees),
            longitude=cast("float", r.longitude.degrees),
            rasi_occupied=r.rasi_occupied.value,
            house_posited_at=r.house_posited_at.value,
            planet=r.planet.value,
            distance=cast("float", r.distance.km) if r.distance else 0.0,
            nirayana_longitude=cast("float", r.nirayana_longitude.degrees) if r.nirayana_longitude else 0.0,
            advanced_by=cast("float", r.advanced_by.degrees) if r.advanced_by else 0.0,
            retrograde=r.retrograde,
            is_ascendant=r.is_ascendant,
            natchaththiram=r.natchaththiram.value if r.natchaththiram else 0,
            paatham=r.paatham if r.paatham else 0,
        )
        for r in results
    ]


class AscendantRequest(BaseModel):
    """Request model for ascendant calculation."""

    lat: float
    lon: float
    datetime: datetime
    ayanamsa: str


@router.get("/ascendant", response_model=PlanetDetailResponse)
def get_sidereal_ascendant(
    lat: Annotated[float, Query(description="Latitude")] = 12.59,
    lon: Annotated[float, Query(description="Longitude")] = 77.36,
    ayanamsa: Annotated[str, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(tz=pytz.utc).isoformat(timespec="seconds"),
) -> PlanetDetailResponse:
    """Calculate the sidereal ascendant (lagna) for given latitude, longitude, datetime, and ayanamsa."""
    planet = get_sidereal_ascendant_position(
        datetime.fromisoformat(dateandtime), Angle(degrees=lat), Angle(degrees=lon), get_ayanamsa_value(ayanamsa, datetime.fromisoformat(dateandtime))
    )
    return PlanetDetailResponse(
        name=Planets.ASCENDANT.name,
        short_name=planet.short_name,
        latitude=cast("float", planet.latitude.degrees),
        longitude=cast("float", planet.longitude.degrees),
        rasi_occupied=planet.rasi_occupied.value,
        house_posited_at=planet.house_posited_at.value,
        planet=Planets.ASCENDANT.value,
        distance=cast("float", planet.distance.km) if planet.distance else 0.0,
        nirayana_longitude=cast("float", planet.nirayana_longitude.degrees) if planet.nirayana_longitude else 0.0,
        advanced_by=cast("float", planet.advanced_by.degrees) if planet.advanced_by else 0.0,
        retrograde=planet.retrograde,
        is_ascendant=planet.is_ascendant,
        natchaththiram=planet.natchaththiram.value if planet.natchaththiram else 0,
        paatham=planet.paatham if planet.paatham else 0,
    )


class SunriseSunsetRequest(BaseModel):
    """Request model for sunrise and sunset calculation."""

    lat: float
    lon: float
    datetime: datetime


class SunriseSunsetResponse(BaseModel):
    """Response model for sunrise and sunset calculation."""

    sunrise: str | None
    sunset: str | None


@router.get("/sunrise-sunset", response_model=SunriseSunsetResponse)
def get_sun_rise_set(
    lat: Annotated[float, Query(description="Latitude")] = 12.59,
    lon: Annotated[float, Query(description="Longitude")] = 77.36,
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(tz=pytz.utc).isoformat(timespec="seconds"),
) -> SunriseSunsetResponse:
    """Calculate the sunrise and sunset times for a given location and date."""
    result = get_sunrise_sunset(Angle(degrees=lat), Angle(degrees=lon), datetime.fromisoformat(dateandtime))
    return SunriseSunsetResponse(
        sunrise=result[0].isoformat() if result[0] else None,
        sunset=result[1].isoformat() if result[1] else None,
    )


class KattamRequest(BaseModel):
    """Request model for kattam chart generation."""

    lat: float
    lon: float
    datetime: datetime
    ayanamsa: float


class KattamResponse(BaseModel):
    """Response model for kattam chart."""

    order: int
    is_ascendant: bool
    asc_longitude: float
    owner: int
    rasi: int
    house: int
    planets: list[PlanetDetailResponse] | None


@router.get("/kattams", response_model=list[KattamResponse])
def get_astro_kattams(
    lat: Annotated[float, Query(description="Latitude")] = 12.59,
    lon: Annotated[float, Query(description="Longitude")] = 77.36,
    ayanamsa: Annotated[str, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(tz=pytz.utc).isoformat(timespec="seconds"),
) -> list[KattamResponse]:
    """Generate kattam chart (list of squares) for given lat, lon, datetime, and ayanamsa."""
    kattams = get_kattams(
        Angle(degrees=lat), Angle(degrees=lon), datetime.fromisoformat(dateandtime), get_ayanamsa_value(ayanamsa, datetime.fromisoformat(dateandtime))
    )

    return convert_kattams_to_response_format(kattams, KattamResponse, PlanetDetailResponse)


@router.get("/chart")
def get_astrology_chart_svg(  # noqa: PLR0913
    request: Request,
    lat: Annotated[float, Query(description="Latitude")] = 12.59,
    lon: Annotated[float, Query(description="Longitude")] = 77.36,
    ayanamsa: Annotated[str, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(tz=pytz.utc).isoformat(timespec="seconds"),
    chart_type: Annotated[ChartType, Query(description="Type of astrology chart")] = ChartType.SOUTH_INDIAN,
    name: Annotated[str, Query(description="Name for the chart")] = "ND Astro",
    place: Annotated[str, Query(description="Place of birth")] = "Salem",
    lang: Annotated[str | None, Query(description="Language code for localization")] = None,
    tz: Annotated[str, Query(description="Timezone for the birth location, e.g., 'Asia/Kolkata'")] = "UTC",
) -> Response:
    """Generate astrology chart as SVG image based on chart type.

    Args:
        request: FastAPI request object (for language detection)
        lat: Latitude for birth location
        lon: Longitude for birth location
        ayanamsa: Ayanamsa system to use
        dateandtime: Birth date and time in ISO format
        chart_type: Type of astrology chart ('south-indian' or 'north-indian')
        name: Name for the chart
        place: Place of birth
        lang: Language code for localization
        tz: Timezone for the birth location, e.g., 'Asia/Kolkata'

    Returns:
        Response: SVG image of the astrology chart with Content-Language header

    """
    # Determine the target language using babel's get_locale function
    target_lang = lang or get_locale(request)

    # Get the kattams data using the same logic as the kattams endpoint
    kattams = get_kattams(
        Angle(degrees=lat), Angle(degrees=lon), datetime.fromisoformat(dateandtime), get_ayanamsa_value(ayanamsa, datetime.fromisoformat(dateandtime))
    )

    # Convert to KattamResponse format using the utility function
    kattams_data = convert_kattams_to_response_format(kattams, KattamResponse, PlanetDetailResponse)

    # Create birth details using input parameters
    datetz = datetime.fromisoformat(dateandtime).astimezone(pytz.timezone(tz))
    birth_details = BirthDetails(
        name_abbr=name,
        date=format_datetime(datetz, format=_("DateFormat"), locale=target_lang, tzinfo=pytz.timezone(tz)),
        time=format_datetime(datetz, format=_("TimeFormat"), locale=target_lang, tzinfo=pytz.timezone(tz)),
        place=place,
    )

    # Generate SVG based on chart type using the detected language
    if chart_type == ChartType.SOUTH_INDIAN:
        svg_content = generate_south_indian_chart_svg(kattams_data, birth_details)
        filename = f"south_indian_chart_{target_lang}.svg"
    elif chart_type == ChartType.NORTH_INDIAN:
        # Placeholder for future north indian chart implementation with translation
        coming_soon_text = _("Coming Soon")
        chart_title = _("Birth Chart")
        svg_content = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">'
            f'<text x="200" y="180" text-anchor="middle" font-size="16">{chart_title}</text>'
            f'<text x="200" y="220" text-anchor="middle" font-size="14">{coming_soon_text}</text>'
            "</svg>"
        )
        filename = f"north_indian_chart_{target_lang}.svg"
    else:
        # Default to south indian
        svg_content = generate_south_indian_chart_svg(kattams_data, birth_details, target_lang)
        filename = f"chart_{target_lang}.svg"

    # Return response with proper Content-Language header for i18n
    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={"Content-Disposition": f"inline; filename={filename}", "Content-Language": target_lang},
    )
