
FROM python:3.10-slim AS base

WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install \
         --timeout 120 \
         --retries 5 \
         --no-cache-dir \
         -r requirements.txt

COPY src/ .

CMD ["uvicorn", "my_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
