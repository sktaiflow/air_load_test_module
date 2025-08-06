FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

WORKDIR /app

# Enable bytecode compilation and set copy mode for better container performance
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies with cache mount and frozen lock
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy application code
COPY locustfile.py ./

# Set non-root user for security
USER nobody

CMD ["locust"]