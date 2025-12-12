# Translation Files Deployment Fix for Render.com

## Problem
The error "No translation file found for domain: 'messages'" occurs because the compiled `.mo` translation files were excluded from git and not being deployed.

## Solution Applied

### 1. ✅ Updated `.gitignore`
Commented out `*.mo` to allow compiled translation files to be committed:
```gitignore
# Translations
# *.mo  # Commented out - .mo files are needed for deployment
*.pot
```

### 2. ✅ Updated `pyproject.toml`
Added explicit inclusion of translation files in the package:
```toml
include = ["ndastro_api/locales/**/*.mo", "ndastro_api/locales/**/*.po"]
```

### 3. ✅ Created `build.sh` for Render.com
Added a build script that:
- Installs dependencies
- Compiles translations during deployment
- Runs database migrations

## Deployment Steps

### For Render.com:

1. **Configure Build Command** in your render.com dashboard:
   ```bash
   chmod +x build.sh && ./build.sh
   ```
   OR if the above doesn't work:
   ```bash
   poetry install --only main && poetry run pybabel compile -d ndastro_api/locales && poetry run alembic upgrade head
   ```

2. **Configure Start Command**:
   ```bash
   poetry run gunicorn ndastro_api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```

3. **Commit and Push** the changes:
   ```bash
   git add .
   git commit -m "Fix: Include translation files for deployment"
   git push
   ```

## Verification

After deployment, test the translations with:

```bash
# Test English (default)
curl https://your-app.onrender.com/api/v1/astro/chart

# Test Tamil
curl -H "Accept-Language: ta" https://your-app.onrender.com/api/v1/astro/chart
```

## Alternative: Compile on Deploy (If build.sh doesn't work)

If Render.com doesn't execute the build.sh script, add this to your render.yaml or dashboard:

```yaml
services:
  - type: web
    name: ndastro-api
    env: python
    buildCommand: poetry install --no-dev && poetry run pybabel compile -d ndastro_api/locales
    startCommand: poetry run gunicorn ndastro_api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

## Files Modified
- `.gitignore` - Allowed .mo files
- `pyproject.toml` - Included locale files in package
- `build.sh` - Created build script for render.com
- Added `.mo` files to git repository

## Current Translation Support
- ✅ English (en)
- ✅ Tamil (ta)
- 🔧 Hindi, Telugu, Kannada, Malayalam (configured but need .mo files compiled)

To add more languages, run:
```bash
poetry run pybabel compile -d ndastro_api/locales
```
