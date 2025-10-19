FROM python:3.12-slim

# force root before any commands (prevents cached USER from prior builds)
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Bake deps into the image (rebuild when requirements change)
COPY requirements.txt /tmp/requirements.txt
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN python -m pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/requirements-dev.txt

# Idle so we can exec into it in dev sessions
CMD ["bash", "-lc", "sleep infinity"]
