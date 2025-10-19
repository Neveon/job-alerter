FROM python:3.12-slim

# OS deps (only what we need)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Create non-root user that owns /work
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} dev && useradd -m -u ${UID} -g ${GID} dev
WORKDIR /work

# Faster, reproducible pip
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Preinstall dev tools; runtime deps installed via Makefile during first run
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN python -m pip install --upgrade pip && \
    pip install -r /tmp/requirements-dev.txt

USER dev
