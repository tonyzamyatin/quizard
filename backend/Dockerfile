FROM python:3.12-alpine

RUN pip install poetry==1.8.3

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-cache

COPY . /app

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]