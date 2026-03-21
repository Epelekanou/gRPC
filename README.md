# Distributed Telemetry System

A real-time distributed telemetry system simulating an industrial IoT facility. Built with gRPC, Redis, FastAPI, and Docker Compose.

## Architecture

```
Sensors → Collector Service → Redis → FastAPI Bridge → WebSocket/HTTP Clients
```

- **Sensors** — Async simulated industrial sensors (temperature, humidity, vibration)
- **Collector** — Central gRPC service that ingests measurements and aggregates data in Redis
- **Redis** — Shared aggregation store for fast distributed data access
- **FastAPI Bridge** — WebSocket and HTTP gateway for real-time dashboard updates

## Features

- Real-time sensor data streaming using gRPC client-streaming RPC
- Live aggregate updates via gRPC server-streaming RPC
- On-demand sensor statistics via gRPC unary RPC
- WebSocket broadcasting for live dashboard updates
- REST API for querying individual sensor stats
- Redis aggregation with min, max, avg, count per sensor type and location
- Full Docker Compose deployment

## Tech Stack

| Technology | Usage |
|---|---|
| Python | Core language |
| gRPC + Protobuf | Microservice communication |
| Redis | Distributed aggregation store |
| FastAPI | HTTP and WebSocket gateway |
| Docker Compose | Service orchestration |
| asyncio | Async programming |

## gRPC Communication Patterns

| Pattern | Where Used |
|---|---|
| Client Streaming | Sensors → Collector (continuous measurements) |
| Server Streaming | Collector → FastAPI (live aggregate updates) |
| Unary RPC | FastAPI → Collector (sensor stats query) |

## Getting Started

### Prerequisites
- Docker Desktop
- Python 3.11+

### Run the System

```bash
docker compose up --build
```

All services will start:
- Collector on port `50051`
- API on port `8000`
- Redis on port `6379`

### Test the API

```bash
# Query a specific sensor
curl http://localhost:8000/sensor/T-BR-01
```

### WebSocket Live Updates

Connect to:
```
ws://localhost:8000/ws
```

You will receive real-time aggregate updates as sensors stream data.

## Project Structure

```
├── proto/
│   └── telemetry.proto        # gRPC service and message definitions
├── collector/
│   └── collector_server.py    # gRPC server with 3 RPC handlers
├── sensor/
│   └── sensor_client.py       # Async sensor simulation + gRPC client
├── api/
│   └── fastapi_bridge.py      # FastAPI WebSocket + HTTP gateway
└── docker-compose.yml         # Multi-service orchestration
```

## API Reference

### GET /sensor/{sensor_id}

Returns aggregated statistics for a specific sensor.

**Example Response:**
```json
{
  "sensor_id": "T-BR-01",
  "count": 150,
  "avg": 73.21,
  "min": 59.50,
  "max": 87.14,
  "recent": [
    {"ts_unix_ms": 1234567890, "value": 72.3},
    {"ts_unix_ms": 1234567891, "value": 74.1}
  ]
}
```

## Real-World Relevance

This architecture is similar to systems used in:
- Industrial IoT and manufacturing monitoring
- Cloud observability platforms (AWS CloudWatch, Google Cloud Monitoring)
- Real-time tracking systems (Uber, Lyft)
- Hospital patient monitoring systems
