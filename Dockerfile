FROM python:3.13-alpine3.22

WORKDIR /app

EXPOSE 8000

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./app/ /app/
COPY ./uv.lock /app/
COPY ./pyproject.toml /app/

CMD ["uv", "run", "-m", "main"]
