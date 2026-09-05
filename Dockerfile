# Runs the pipeline anywhere, with the versions it was actually developed against.
FROM python:3.12-slim

WORKDIR /app

# Dependencies first, so a code edit does not invalidate the pip layer.
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY src/ ./src/
COPY sql/ ./sql/
COPY tests/ ./tests/
COPY pyproject.toml ./

ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    NSE_DATA_DIR=/data \
    NSE_DB_PATH=/data/nse.db

# The image ships no data. The .asc feeds are 580MB and are mounted at run time:
#   docker run --rm -v "$PWD/data:/data" nse-pipeline
VOLUME ["/data"]

CMD ["python", "-m", "nse_pipeline.build"]
