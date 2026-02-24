FROM python:3.13-slim

WORKDIR /app

COPY proto /app/proto
COPY sensor /app/sensor

RUN pip install --no-cache-dir grpcio grpcio-tools

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "sensor.sensor_client"]
