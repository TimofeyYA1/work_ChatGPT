FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir . && playwright install --with-deps chromium

ENV DATA_DIR=/app/data \
    HEADLESS=true

VOLUME ["/app/data"]
CMD ["vfs-france-monitor"]
