# The Studio Linux image: Manim, LaTeX to SVG, and the web build and capture.
# Blender EEVEE is not here. It needs a GPU and runs on the operator's PC.
#
# The same package list is installed in the Managed Agents cloud sandbox
# (see environment.yaml) and is the base for the E2B and Docker fallbacks.
#
#   docker build -t studio-env environments/studio
#
FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

# Manim's native dependencies, a TeX set with dvisvgm, ffmpeg, and Node for the web app.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential pkg-config \
        libcairo2-dev libpango1.0-dev \
        ffmpeg \
        texlive-latex-base texlive-latex-extra texlive-fonts-recommended \
        texlive-science dvisvgm \
        curl ca-certificates git xz-utils \
    && curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Typst: fast equations with no TeX step. The release binary matches the CPU.
ARG TYPST_VERSION=0.15.1
RUN arch="$(uname -m)" \
    && curl -fsSL "https://github.com/typst/typst/releases/download/v${TYPST_VERSION}/typst-${arch}-unknown-linux-musl.tar.xz" \
       | tar -xJ --strip-components=1 -C /usr/local/bin "typst-${arch}-unknown-linux-musl/typst"

# Versions are pinned here until the lock files of milestone 2 replace them.
RUN pip install "manim==0.22.1" "sympy" "numpy" "pydantic>=2" "playwright"

# The browser that captures three.js frames.
RUN python -m playwright install --with-deps chromium

WORKDIR /workspace
