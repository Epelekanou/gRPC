import os

# Inside docker-compose network, use service names:
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

COLLECTOR_ADDR = os.getenv("COLLECTOR_ADDR", "collector:50051")  # gRPC
API_BASE = os.getenv("API_BASE", "http://api:8000")              # HTTP

# Timeouts / waits
READY_TIMEOUT_S = float(os.getenv("READY_TIMEOUT_S", "20"))
STREAM_TIMEOUT_S = float(os.getenv("STREAM_TIMEOUT_S", "8"))
