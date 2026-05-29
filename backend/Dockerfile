FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY data ./data
RUN printf '%s\n' '#!/bin/sh' 'exec uv run python -m app.seed.docker_bootstrap_cli "$@"' > /usr/local/bin/salary-bootstrap \
    && chmod +x /usr/local/bin/salary-bootstrap

EXPOSE 8000

CMD ["sh", "-c", "uv run alembic upgrade head && salary-bootstrap && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
