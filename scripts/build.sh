#!/usr/bin/env bash
set -euo pipefail

echo "=== Building Taiwan Parenting Subsidy Site ==="

# Navigate to project root
cd "$(dirname "$0")/.."

# 1. Validate data
echo "[1/6] Validating data..."
python manage.py validate_data

# 2. Export JSON
echo "[2/6] Exporting JSON data..."
python manage.py export_json

# 3. Build Tailwind CSS
echo "[3/6] Building CSS..."
npm run build:css

# 4. Collect static files
echo "[4/6] Collecting static files..."
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py collectstatic --noinput

# 5. Generate static HTML
echo "[5/6] Generating static HTML..."
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py distill-local --force output/

# 6. Copy static files to output
echo "[6/6] Copying static files..."
cp -r staticfiles/ output/static/ 2>/dev/null || true

echo "=== Build complete! Output in ./output/ ==="
