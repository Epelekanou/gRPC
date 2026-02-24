# 🏭 Distributed Telemetry System Lab

## gRPC Streaming • Redis Aggregation • FastAPI Bridge

---

# 1. Overview

In this lab you will build a **distributed telemetry system** similar to those used in modern industrial facilities, IoT platforms, and observability infrastructures.

The system collects data from simulated industrial sensors, aggregates measurements, and exposes the results for monitoring dashboards.

You will design the communication protocol using **Protocol Buffers**, implement multiple **gRPC communication patterns**, use **Redis as a shared aggregation store**, and expose data through a **FastAPI WebSocket/HTTP gateway**.

This lab emphasizes:

* Distributed system design
* Streaming RPC patterns
* Async programming
* Service orchestration using Docker Compose

---

# 2. Scenario: Smart Industrial Facility

Imagine a smart manufacturing facility equipped with:

* 🌡 Temperature sensors (boiler rooms, labs, warehouses)
* 💧 Humidity sensors (storage areas)
* ⚙ Vibration sensors (assembly lines)
* 🔊 Environmental monitors

Sensors continuously emit telemetry data.

Your system must:

1. Collect sensor measurements in real time.
2. Aggregate measurements centrally.
3. Provide live updates to dashboards.
4. Allow querying individual sensors.
5. Remain scalable and fault-tolerant.

---

# 3. System Architecture

```
Mock Sensors
     │
     │ Client-streaming gRPC
     ▼
Collector Service (stateless)
     │
     │ Redis shared aggregation store
     ▼
Redis
     │
     ├── Server-streaming gRPC → FastAPI Bridge → WebSocket Clients
     └── Unary gRPC → FastAPI Bridge → HTTP Clients
```

---

## Components

### Sensors

Simulated industrial sensors producing measurements asynchronously.

### Collector Service

Central ingestion service that:

* Receives streaming measurements
* Maintains aggregates in Redis
* Streams aggregate updates
* Provides sensor queries

### Redis

Shared aggregation backend.

### FastAPI Bridge

Gateway service that:

* Subscribes to collector streams
* Broadcasts updates via WebSockets
* Exposes HTTP query endpoints

---

# 4. Learning Objectives

After completing this lab you should be able to:

* Define gRPC services using protobuf

* Generate and use Python gRPC stubs

* Implement:

  * Client-streaming RPC
  * Server-streaming RPC
  * Unary RPC

* Use Redis for simple distributed aggregation

* Build asynchronous microservices

* Deploy services using Docker Compose

---

# 5. Protocol Specification (MANDATORY)

Create:

```
proto/telemetry.proto
```

Use **exactly the names and fields as shown in the communication protocol**.
For implementation details [see the protocol definition.](communication-protocol.md)

---

# 6. Required gRPC Services

---

## 6.1 Ingestion Service (Client Streaming)
See also [the protocol definition.](communication-protocol.md)

```proto
service IngestService {
  rpc PushMeasurements(stream Measurement)
      returns (IngestAck);
}
```

Purpose:

* Sensors stream measurements continuously.
* Collector aggregates them.

---

## 6.2 Aggregate Streaming Service (Server Streaming)

```proto
service AggregateService {
  rpc StreamAggregates(StreamAggregatesRequest)
      returns (stream Aggregate);
}

```

Purpose:

* Collector streams aggregate updates.

---

## 6.3 Sensor Query Service (Unary RPC)

```proto
service QueryService {
  rpc GetSensorStats(GetSensorStatsRequest)
      returns (GetSensorStatsResponse);
}
```

Purpose:

* Query statistics for a specific sensor.

---

# 7. Stub Generation

Run:

```bash
python -m grpc_tools.protoc \
  -I . \
  --python_out=. \
  --grpc_python_out=. \
  proto/telemetry.proto
```

This generates:

* `telemetry_pb2.py`
* `telemetry_pb2_grpc.py`

Do **not edit generated files manually.**

---

# 8. Implementation Tasks

---

## Task 1 — Collector Service

Implement three RPC handlers:

---

### A. PushMeasurements

Must:

1. Read streaming measurements.
2. Update Redis global aggregates:

```
agg:{sensor_type}:{location}
```

Fields:

```
count, sum, min, max
```

3. Update per-sensor stats:

```
sensor:{sensor_id}:stats
```

4. Store last 20 values:

```
sensor:{sensor_id}:recent
```

Use:

* `LPUSH`
* `LTRIM 0 19`

Return total received messages.

---

### B. StreamAggregates

Must:

* Periodically read Redis aggregates.
* Stream updated aggregates continuously.
* Continue until client disconnects.

---

### C. GetSensorStats

Must:

* Retrieve per-sensor stats.
* Return last 20 measurements.
* Return NOT_FOUND if sensor missing.

---

## Task 2 — Sensor Client

Implement:

* Async sensors generating measurements.
* Client-streaming RPC to collector.
* Reconnection logic with exponential backoff.

---

## Task 3 — FastAPI Bridge

Must:

### Subscribe to Collector

Call:

```
AggregateService.StreamAggregates
```

Continuously consume stream.

---

### Broadcast via WebSockets

For each aggregate:

* Send update to all connected WebSocket clients.

---

### HTTP Endpoint

Implement:

```
GET /sensor/{sensor_id}
```

Must:

* Call `QueryService.GetSensorStats`
* Return JSON response.

---

# 9. Redis Usage Guidelines

Keep Redis usage simple:

* Hashes for aggregates.
* Lists for recent values.

No advanced Redis features required.

---

# 10. Deployment

Start the system using Docker Compose:

```bash
docker compose up --build
```

All services must start successfully.

---

# 11. Debugging Tips

## Check Redis
Run this from the docker container:
  - Start container:
    ```
    docker start -ia <container_name>
    ```
  - Exit with ctr-c. Then use command below to get a shell on the running container
    ```
    docker exec -it <container_name> sh
    ```

```bash
redis-cli keys *
redis-cli hgetall agg:temperature:lab
```

---

## Check Services

```bash
docker compose logs collector
docker compose logs api
```

---

## Test API

```bash
curl http://localhost:8000/sensor/T-01
```

---

## WebSocket Test

Use browser or test client to connect:

```
ws://localhost:8000/ws
```

---

# 12. Common Mistakes

* Forgetting to regenerate protobuf stubs.
* Mixing blocking and async code.
* Not trimming Redis lists.
* Incorrect proto field names.
* Using blocking gRPC instead of `grpc.aio`.

---

# 13. Deliverables

You must submit:

* Completed `telemetry.proto`
* Collector implementation
* Sensor client implementation
* FastAPI bridge implementation
* Working Docker Compose deployment

---

# 14. Evaluation Criteria

Your solution will be automatically tested for:

* Correct protobuf definitions
* Functioning client-streaming RPC
* Redis aggregation correctness
* Server-streaming aggregate updates
* Unary sensor query correctness
* Working Docker deployment

---

# 15. Real-World Relevance

This architecture resembles:

* Industrial IoT telemetry systems
* Monitoring and observability platforms
* Distributed analytics pipelines
* Real-time event processing backends

You are building a simplified but realistic distributed system.

---

<!-- # 16. Extension Ideas (Optional)

* Load balancing collectors
* Persistent storage beyond Redis
* Authentication
* TLS for gRPC
* Metrics and monitoring integration

--- -->

## End of Lab

Good luck — and enjoy building a real distributed system 🚀
