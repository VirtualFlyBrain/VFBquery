FROM python:3.11-slim

WORKDIR /app

# Install system deps (some vfb_connect/pandas wheels need these)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer caching)
COPY requirements.txt setup.py pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir aiohttp && \
    pip install --no-cache-dir -e .

EXPOSE 8080

# Tuning via env vars:
#   VFBQUERY_PORT          (default 8080)
#   VFBQUERY_HOST          (default 0.0.0.0)
#   VFBQUERY_WORKERS       (default: CPU count)
#   VFBQUERY_MAX_CONCURRENT (default: workers × 4)

ENTRYPOINT ["python", "-m", "vfbquery.ha_api"]
