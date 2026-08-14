FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY static ./static
COPY app ./app
COPY agents-cli-manifest.yaml ./
RUN python -m pip install --no-cache-dir .

ENV PYTHONPATH=/app/src
EXPOSE 8080
CMD ["sh", "-c", "python -m uvicorn recovery_mesh.api:app --host 0.0.0.0 --port ${PORT}"]
