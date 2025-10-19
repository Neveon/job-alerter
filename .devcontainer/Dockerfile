FROM python:3.12-slim

USER root

 RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git unzip xz-utils \
    build-essential pkg-config cmake ninja-build gettext \
    ripgrep fd-find \
    nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Install Neovim (>= 0.9)
# -------------------------------
RUN printf "deb http://deb.debian.org/debian bookworm-backports main\n" \
      > /etc/apt/sources.list.d/backports.list \
 && apt-get update \
 && apt-get -t bookworm-backports install -y neovim \
 && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Install LunarVim (non-interactive)
# NOTE: We don't install system deps via the script since we handled them above.
# -------------------------------
RUN bash -lc 'curl -s https://raw.githubusercontent.com/LunarVim/LunarVim/master/utils/installer/install.sh \
      | bash -s -- --no-install-dependencies --yes'

# Put lvim in PATH explicitly (installer usually does this already)
ENV PATH="/root/.local/bin:${PATH}"

# -------------------------------
# Python env defaults
# -------------------------------
WORKDIR /work
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# -------------------------------
# App Python deps
# -------------------------------
COPY requirements.txt /tmp/requirements.txt
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN python -m pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install -r /tmp/requirements-dev.txt

# -------------------------------
# Prewarm LunarVim plugins & Treesitter
# (Best-effort: won't fail build if a plugin fails to compile.)
# -------------------------------
RUN lvim --headless "+Lazy! sync" +qall || true && \
    lvim --headless "+TSUpdateSync" +qall || true

# Idle so we can exec into it in dev sessions
CMD ["bash", "-lc", "sleep infinity"]
