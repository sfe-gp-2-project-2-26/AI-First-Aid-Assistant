FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml ./
COPY src ./src

RUN uv pip install --system --no-cache -e .

ENV PYTHONPATH=/app/src

EXPOSE 3000

CMD ["uvicorn", "first_aid_rag.main:app", "--host", "0.0.0.0", "--port", "3000"]
