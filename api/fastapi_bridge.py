"""
Responsibilities:

1. Subscribe to collector aggregate stream via gRPC.
2. Broadcast aggregate updates to WebSocket clients.

Currently:
- Uses placeholder data.
- Does NOT connect to collector yet.

Students will implement:
- gRPC streaming client.
- Real broadcast logic.

📘 What the FastAPI Bridge Does (Student Explanation)

The FastAPI bridge connects the telemetry backend with user-facing applications such as dashboards or monitoring tools.

It acts as a gateway between:

The collector service (gRPC backend)

The web clients (HTTP/WebSocket frontend)

This separation is common in real-world telemetry and observability systems because:

gRPC is efficient for internal microservice communication.

Browsers do not natively support standard gRPC streaming.

FastAPI provides a convenient HTTP/WebSocket interface.

Responsibilities of the FastAPI Bridge
1️⃣ Subscribe to Collector Aggregates (gRPC)

The bridge must connect to the collector and call:

AggregateService.StreamAggregates(...)

This is a server-streaming RPC:

The collector continuously sends updated aggregate data.

The FastAPI bridge consumes this stream asynchronously.

This demonstrates how backend services subscribe to live data streams.

2️⃣ Broadcast Data to Web Clients (WebSockets)

Connected WebSocket clients should receive:

Real-time aggregate updates.

No polling required.

Immediate propagation of new telemetry data.

This simulates a live monitoring dashboard.

3️⃣ Provide HTTP API (Optional Extension)

Later, you may implement unary RPC calls:

QueryService.GetSensorStats(...)

This supports:

Sensor drill-down queries

Historical inspection

Dashboard initialization

For now, focus on streaming.
"""
import asyncio
import grpc
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from proto import telemetry_pb2
from proto import telemetry_pb2_grpc

from fastapi import HTTPException

import os

COLLECTOR_ADDR = os.getenv("COLLECTOR_ADDR", "localhost:50051")


# Track Connected websocket clients
connected_clients = set()



# -----------------------------
# Broadcast helper
# -----------------------------
async def broadcast(message: str):
    """
    Send message to all connected WebSocket clients.
    """

    dead_clients = []

    for ws in connected_clients:
        try:
            await ws.send_text(message)
        except Exception:
            dead_clients.append(ws)

    for ws in dead_clients:
        connected_clients.remove(ws)



# -----------------------------
# gRPC streaming subscriber
# -----------------------------
async def subscribe_to_collector():
    print("[FastAPI] Connecting to collector...")

    async with grpc.aio.insecure_channel(COLLECTOR_ADDR) as channel:
        stub = telemetry_pb2_grpc.AggregateServiceStub(channel)

        stream = stub.StreamAggregates(
            telemetry_pb2.StreamAggregatesRequest(
                send_initial_snapshot=True,
                min_update_interval_ms=0,
            )
        )

        async for aggregate in stream:
            avg = aggregate.sum / aggregate.count if aggregate.count else 0

            message = (
                f"type={aggregate.key.sensor_type} "
                f"location={aggregate.key.location} "
                f"count={aggregate.count} "
                f"avg={avg:.2f} "
                f"min={aggregate.min:.2f} "
                f"max={aggregate.max:.2f}"
            )

            print("[FastAPI] broadcasting:", message)
            await broadcast(message)

async def query_sensor_stats(sensor_id: str):
    async with grpc.aio.insecure_channel(COLLECTOR_ADDR) as channel:
        stub = telemetry_pb2_grpc.QueryServiceStub(channel)

        resp = await stub.GetSensorStats(
            telemetry_pb2.GetSensorStatsRequest(sensor_id=sensor_id)
        )

        if resp.count == 0:
            return None
        
        avg = resp.sum / resp.count if resp.count else 0

        return {
            "sensor_id": resp.meta.sensor_id,
            "count": resp.count,
            "avg": avg,
            "min": resp.min,
            "max": resp.max,
            "recent": [
                {
                    "ts_unix_ms": r.ts_unix_ms,
                    "value": r.value,
                }
                for r in resp.recent
            ],
        }



# -----------------------------
# Startup hook
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # start up the streaming service
    asyncio.create_task(subscribe_to_collector())
    yield
    # clean up after app shuts down

app = FastAPI(lifespan=lifespan)


# -----------------------------
# WebSocket endpoint
# -----------------------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.add(ws)
    
    print("WebSocket client connected")

    try:
        while True:
            # keep connection alive (clients usually don't send data)
            await ws.receive_text()
    except WebSocketDisconnect:
        connected_clients.discard(ws)
        print("WebSocket client disconnected")


@app.get("/sensor/{sensor_id}")
async def get_sensor(sensor_id: str):
    data = await query_sensor_stats(sensor_id)

    if data is None:
        raise HTTPException(status_code=404, detail="Sensor not found")

    return data