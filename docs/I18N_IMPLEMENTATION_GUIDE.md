# FastAPI Internationalization (i18n) Implementation Guide

This guide shows you how to implement internationalization in your FastAPI astrology API.

## 1. Setup Instructions

### Install Required Packages

```bash
pip install babel fastapi-babel
# or if using poetry:
poetry add babel fastapi-babel
```

### Optional: Advanced Setup with Babel

If you want to use the full Babel system for more advanced translations:

```bash
# Initialize babel configuration
pybabel extract -F babel.cfg -k _l -o messages.pot .

# Create language-specific translation files
pybabel init -i messages.pot -d ndastro_api/translations -l hi
pybabel init -i messages.pot -d ndastro_api/translations -l ta
pybabel init -i messages.pot -d ndastro_api/translations -l te

# Update existing translations
pybabel update -i messages.pot -d ndastro_api/translations

# Compile translations
pybabel compile -d ndastro_api/translations
```

## 2. Integration with Your FastAPI App

### Update main.py to include i18n middleware:

```python
from fastapi import FastAPI
from ndastro_api.middlewares import I18nMiddleware

app = FastAPI(title="ND Astro API")

# Add internationalization middleware
app.add_middleware(I18nMiddleware)

# Include your routers
app.include_router(astro_router, prefix="/api/v1")
```

## 3. Using Internationalization in API Endpoints

### Method 1: Using Query Parameter (Current Implementation)
Your current `/chart` endpoint already accepts a `lang` parameter, which is perfect!

```python
@router.get("/chart")
def get_astrology_chart_svg(
    # ... other parameters ...
    lang: Annotated[str, Query(description="Language for chart labels")] = "en",
) -> Response:
    # The lang parameter can be used directly with translation functions
    translated_title = get_astro_translation("chart_title", lang)
```

### Method 2: Using Request Object for Automatic Language Detection

```python
from fastapi import Request
from ndastro_api.middlewares import get_request_language

@router.get("/chart-auto")
def get_astrology_chart_svg_auto(
    request: Request,
    # ... other parameters ...
) -> Response:
    # Automatically get language from request (middleware)
    lang = get_request_language(request)
    translated_title = get_astro_translation("chart_title", lang)
```

## 4. API Usage Examples

### Using Query Parameter
```bash
# English (default)
GET /api/v1/astro/chart?lat=12.59&lon=77.36&name=John&place=Mumbai

# Hindi
GET /api/v1/astro/chart?lat=12.59&lon=77.36&name=John&place=Mumbai&lang=hi

# Tamil
GET /api/v1/astro/chart?lat=12.59&lon=77.36&name=John&place=Mumbai&lang=ta
```

### Using Accept-Language Header
```bash
curl -H "Accept-Language: hi,en;q=0.9" \
  "http://localhost:8000/api/v1/astro/chart?lat=12.59&lon=77.36&name=John&place=Mumbai"
```

## 5. Translation Functions Available

```python
from ndastro_api.core.simple_i18n import (
    get_astro_translation,
    translate_planet_name,
    translate_rasi_name
)

# General astrology translations
title = get_astro_translation("chart_title", "hi")  # "ज्योतिष चार्ट"

# Planet name translations
sun_name = translate_planet_name("Sun", "hi")  # "सूर्य"

# Rasi (zodiac sign) translations
aries_name = translate_rasi_name("Aries", "ta")  # "மேடம்"
```

## 6. Supported Languages

- `en`: English (default)
- `hi`: Hindi (हिन्दी)
- `ta`: Tamil (தமிழ்)
- `te`: Telugu (తెలుగు)
- `kn`: Kannada (ಕನ್ನಡ)
- `ml`: Malayalam (മലയാളം)

## 7. Extending Translations

To add new translations, update the `ASTRO_TRANSLATIONS` dictionary in `ndastro_api/core/simple_i18n.py`:

```python
ASTRO_TRANSLATIONS = {
    "en": {
        "new_term": "English Translation",
        # ... existing translations
    },
    "hi": {
        "new_term": "हिन्दी अनुवाद",
        # ... existing translations
    },
    # Add other languages...
}
```

## 8. Response Headers

The middleware automatically sets the `Content-Language` header in responses:

```
Content-Language: hi
```

This helps clients understand which language was used for the response.

## 9. Error Handling

If an unsupported language is requested, the system falls back to English:

```python
# If user requests 'fr' (French), it falls back to 'en'
translation = get_astro_translation("sun", "fr")  # Returns "Sun" (English)
```

## 10. Advanced Usage in Chart Generation

You can integrate translations directly into your chart generation:

```python
def generate_south_indian_chart_svg(kattams_data, birth_details, lang="en"):
    # Translate chart elements
    chart_title = get_astro_translation("chart_title", lang)
    
    # Translate planet names in the chart
    for kattam in kattams_data:
        if kattam.planets:
            for planet in kattam.planets:
                planet.translated_name = translate_planet_name(planet.name, lang)
    
    # Use translated text in SVG generation...
```

This implementation provides a solid foundation for internationalization in your astrology API!