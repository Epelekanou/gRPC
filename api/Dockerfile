FROM python:3.13-slim

WORKDIR /app

COPY proto /app/proto
COPY api /app/api

RUN pip install --no-cache-dir fastapi "uvicorn[standard]" grpcio grpcio-tools

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.fastapi_bridge:app", "--host", "0.0.0.0", "--port", "8000"]
