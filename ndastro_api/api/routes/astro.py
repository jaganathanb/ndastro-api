"""Astro API endpoints for planetary and astronomy calculations."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, cast

import pytz
from fastapi import APIRouter, Query
from pydantic import BaseModel
from skyfield.units import Angle

from ndastro_api.core.enums.planet_enum import Planets
from ndastro_api.services.kattams import get_kattams
from ndastro_api.services.position import (
    calculate_lunar_nodes,
    get_sidereal_ascendant_position,
    get_sidereal_planet_positions,
    get_sunrise_sunset,
)
from ndastro_api.services.utils import get_ayanamsa_value

router = APIRouter(prefix="/astro", tags=["astro"])


class PlanetDetailResponse(BaseModel):
    """Response model for a planet's tropical position."""

    name: str
    """The name of the planet."""

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

    return [
        KattamResponse(
            order=k.order,
            is_ascendant=k.is_ascendant,
            asc_longitude=cast("float", k.asc_longitude.degrees) if k.asc_longitude else 0.0,
            owner=k.owner,
            rasi=k.rasi.value,
            house=k.house.value,
            planets=[
                PlanetDetailResponse(
                    name=p.name,
                    short_name=p.short_name,
                    latitude=cast("float", p.latitude.degrees),
                    longitude=cast("float", p.longitude.degrees),
                    rasi_occupied=p.rasi_occupied.value,
                    house_posited_at=p.house_posited_at.value,
                    planet=p.planet.value,
                    distance=cast("float", p.distance.km) if p.distance else 0.0,
                    nirayana_longitude=cast("float", p.nirayana_longitude.degrees) if p.nirayana_longitude else 0.0,
                    advanced_by=cast("float", p.advanced_by.degrees) if p.advanced_by else 0.0,
                    retrograde=p.retrograde,
                    is_ascendant=p.is_ascendant,
                    natchaththiram=p.natchaththiram.value if p.natchaththiram else 0,
                    paatham=p.paatham if p.paatham else 0,
                )
                for p in k.planets or []
            ]
            if k.planets
            else None,
        )
        for k in kattams
    ]
