FROM python:3.13-slim

WORKDIR /app

COPY proto /app/proto
COPY collector /app/collector

RUN pip install --no-cache-dir grpcio grpcio-tools redis

# generated stubs should already be present in proto/ in the template repo
CMD ["python", "-m", "collector.collector_server", "--port", "50051"]
