FROM python:3.12-slim AS builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /code/neu

RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir poetry

RUN touch README.md

COPY pyproject.toml pyproject.toml

RUN poetry  install --no-interaction --no-cache --no-root \
    && rm -rf $POETRY_CACHE_DIR


FROM python:3.12-slim AS runtime

ENV VIRTUAL_ENV=/code/neu/.venv \
    PATH="/code/neu/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src src

CMD ["python", "src/main.py" ]
