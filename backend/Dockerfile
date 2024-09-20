# Dockerfile
# See the Quizard-Notion page "Docker-Poetry" for explanations regarding this Docker Build

#syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS builder

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV POETRY_VERSION=1.7.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH

RUN pip install poetry==$POETRY_VERSION

WORKDIR /app

RUN adduser --uid 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

RUN touch README.md
COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --only main && rm -rf $POETRY_CACHE_DIR

FROM python:${PYTHON_VERSION}-slim AS runtime
WORKDIR /app
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group
COPY --from=builder /app/.venv .venv
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
# Only copy essential files
COPY --chown=appuser:appuser pyproject.toml poetry.lock ./
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser assets/ ./assets/
COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh
USER appuser

# Make entrypoint.sh executable
RUN chmod +x /app/entrypoint.sh

# Use entrypoint.sh for handling service logic
ENTRYPOINT ["/app/entrypoint.sh"]