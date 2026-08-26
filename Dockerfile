FROM python:3.11-slim

WORKDIR /app

# Install system deps (some vfb_connect/pandas wheels need these)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Build numpy from source with no fixed SIMD baseline. The PyPI wheels for
# numpy >= 2.4 are compiled for x86-64-v2 (SSE4.2/POPCNT) and refuse to import
# on the VFB Rancher/k8s hosts, whose QEMU "qemu64" CPU model does not expose
# those flags. cpu-baseline=none keeps every SIMD path as a runtime-dispatched
# option (X86_V2/V3/V4 are still used where the CPU has them), so there is no
# speed cost on modern hosts. Installed first so pip treats the numpy
# requirement from vfb_connect/pandas as already satisfied.
ARG NUMPY_SPEC=numpy
RUN pip install --no-cache-dir --no-binary numpy \
        -Csetup-args=-Dcpu-baseline=none "${NUMPY_SPEC}"

# Install Python deps first (layer caching)
COPY requirements.txt setup.py pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir aiohttp && \
    pip install --no-cache-dir -e .

EXPOSE 8080

# Tuning via env vars:
#   VFBQUERY_PORT            (default 8080)
#   VFBQUERY_HOST            (default 0.0.0.0)
#   VFBQUERY_WORKERS         (default: 10)
#   VFBQUERY_MAX_CONCURRENT  (default: workers × 2)
#   VFBQUERY_MAX_QUEUE_DEPTH (default: 200, 0 = unlimited)
#   VFBQUERY_CACHE_TTL       (default: 300 seconds)
#   VFBQUERY_SOLR_WRITE_TIMEOUT (default: 30 seconds)

ENTRYPOINT ["python", "-m", "vfbquery.ha_api"]
