"""Astrology translations for Babel extraction."""

from ndastro_api.core.babel_i18n import translate

# Planet names for translation
PLANET_NAMES = {
    "sun": translate("Sun"),
    "moon": translate("Moon"),
    "mercury": translate("Mercury"),
    "venus": translate("Venus"),
    "mars": translate("Mars"),
    "jupiter": translate("Jupiter"),
    "saturn": translate("Saturn"),
    "rahu": translate("Rahu"),
    "kethu": translate("Kethu"),
    "ascendant": translate("Ascendant"),
    "su": translate("SU"),
    "mo": translate("MO"),
    "me": translate("ME"),
    "ve": translate("VE"),
    "ma": translate("MA"),
    "ju": translate("JU"),
    "sa": translate("SA"),
    "ra": translate("RA"),
    "ke": translate("KE"),
    "as": translate("AS"),
}

# Zodiac sign names for translation
RASI_NAMES = {
    "aries": translate("Aries"),
    "taurus": translate("Taurus"),
    "gemini": translate("Gemini"),
    "cancer": translate("Cancer"),
    "leo": translate("Leo"),
    "virgo": translate("Virgo"),
    "libra": translate("Libra"),
    "scorpio": translate("Scorpio"),
    "sagittarius": translate("Sagittarius"),
    "capricorn": translate("Capricorn"),
    "aquarius": translate("Aquarius"),
    "pisces": translate("Pisces"),
}

# Chart UI elements for translation
CHART_LABELS = {
    "birth_chart": translate("Birth Chart"),
    "planet": translate("Planet"),
    "sign": translate("Sign"),
    "house": translate("House"),
    "degree": translate("Degree"),
    "chart_for": translate("Chart for {name}"),
    "birth_details": translate("Birth Details"),
    "date_of_birth": translate("Date"),
    "time_of_birth": translate("Time"),
    "place_of_birth": translate("Place"),
    "latitude": translate("Latitude"),
    "longitude": translate("Longitude"),
    "timezone": translate("Timezone"),
}
