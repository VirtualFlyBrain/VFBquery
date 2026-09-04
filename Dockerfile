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

# The term_info fallback (src/vfbquery/term_info_fallback.py) rebuilds a
# missing vfb_json document by running the bulk indexer's own query, so the
# indexer has to be importable. It is not a package: the `precompute live
# query results` Jenkins job clones it, clones VFB_json_schema alongside,
# copies the schema's src into src/vfb and puts the checkout on PYTHONPATH.
# Do exactly that, so what runs here is what runs in the bulk job.
#
# Pin by passing --build-arg INDEXER_REF=<sha>; the default tracks master the
# way the Jenkins job does. Both resolved SHAs are baked into the image so
# /status can report which schema built a given document.
ARG INDEXER_REF=master
ARG JSON_SCHEMA_REF=master
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*
RUN git clone --quiet https://github.com/VirtualFlyBrain/VFB_json_schema_indexer.git /opt/vfb_indexer && \
    git -C /opt/vfb_indexer checkout --quiet "${INDEXER_REF}" && \
    git clone --quiet https://github.com/VirtualFlyBrain/VFB_json_schema.git /opt/vfb_json_schema && \
    git -C /opt/vfb_json_schema checkout --quiet "${JSON_SCHEMA_REF}" && \
    mkdir -p /opt/vfb_indexer/src/vfb && \
    cp -r /opt/vfb_json_schema/src/* /opt/vfb_indexer/src/vfb/ && \
    printf 'VFB_INDEXER_SHA=%s\nVFB_JSON_SCHEMA_SHA=%s\n' \
        "$(git -C /opt/vfb_indexer rev-parse --short HEAD)" \
        "$(git -C /opt/vfb_json_schema rev-parse --short HEAD)" > /opt/vfb_versions.env && \
    cat /opt/vfb_versions.env && \
    rm -rf /opt/vfb_indexer/.git /opt/vfb_json_schema
# jsonschema and tqdm are the indexer's own runtime deps that VFBquery does
# not already have (requests and vfb_connect it does).
RUN pip install --no-cache-dir jsonschema tqdm
ENV PYTHONPATH=/opt/vfb_indexer

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

#   VFB_JSON_SCHEMA_SHA      (set from the build; stamped into rebuilt documents)

ENTRYPOINT ["python", "-m", "vfbquery.ha_api"]
