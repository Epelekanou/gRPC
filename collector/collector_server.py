"""
Collector Service — Central telemetry aggregation service.

Exposes three gRPC services:
1️⃣  IngestService     — Client Streaming RPC  (sensors → collector)
2️⃣  AggregateService  — Server Streaming RPC  (collector → FastAPI)
3️⃣  QueryService      — Unary RPC             (FastAPI → collector)
"""
import asyncio
import time
from collections import defaultdict

import grpc

from proto import telemetry_pb2
from proto import telemetry_pb2_grpc

import redis.asyncio as redis
import argparse
import json
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)


# -----------------------------
# Redis aggregation store
# -----------------------------
class AggregationStoreAsync:
    async def update(self, measurement):
        type_loc_key = f"agg:{measurement.meta.sensor_type}:{measurement.meta.location}"
        sensor_stats_key = f"sensor:{measurement.meta.sensor_id}:stats"
        sensor_recent_key = f"sensor:{measurement.meta.sensor_id}:recent"

        async with redis_client.pipeline(transaction=True) as pipe:
            while True:
                try:
                    await pipe.watch(type_loc_key, sensor_stats_key)

                    # --- GLOBAL AGGREGATION ---
                    global_current = await pipe.hgetall(type_loc_key)
                    g_count = int(global_current.get("count", 0)) + 1
                    g_sum = float(global_current.get("sum", 0)) + measurement.value
                    g_min = min(float(global_current.get("min", measurement.value)), measurement.value)
                    g_max = max(float(global_current.get("max", measurement.value)), measurement.value)

                    # --- PER SENSOR STATS ---
                    sensor_current = await pipe.hgetall(sensor_stats_key)
                    s_count = int(sensor_current.get("count", 0)) + 1
                    s_sum = float(sensor_current.get("sum", 0)) + measurement.value
                    s_min = min(float(sensor_current.get("min", measurement.value)), measurement.value)
                    s_max = max(float(sensor_current.get("max", measurement.value)), measurement.value)

                    recent_entry = json.dumps({
                        "ts": measurement.ts_unix_ms,
                        "value": measurement.value
                    })

                    pipe.multi()

                    pipe.hset(type_loc_key, mapping={
                        "count": g_count,
                        "sum": g_sum,
                        "min": g_min,
                        "max": g_max,
                    })

                    pipe.hset(sensor_stats_key, mapping={
                        "count": s_count,
                        "sum": s_sum,
                        "min": s_min,
                        "max": s_max,
                    })

                    pipe.lpush(sensor_recent_key, recent_entry)
                    pipe.ltrim(sensor_recent_key, 0, 19)

                    await pipe.execute()
                    break

                except redis.WatchError:
                    continue

    async def snapshot(self):
        keys = await redis_client.keys("agg:*")
        result = {}
        for key in keys:
            data = await redis_client.hgetall(key)
            result[key] = data
        return result


store = AggregationStoreAsync()


# ----------------------------------------------------------
# 1️⃣ Client-streaming ingestion service
# ----------------------------------------------------------
class IngestService(telemetry_pb2_grpc.IngestServiceServicer):

    async def PushMeasurements(self, request_iterator, context):
        received = 0
        async for measurement in request_iterator:
            received += 1
            await store.update(measurement)
        return telemetry_pb2.IngestAck(received=received)


# ----------------------------------------------------------
# 2️⃣ Server-streaming aggregate service
# ----------------------------------------------------------
class AggregateService(telemetry_pb2_grpc.AggregateServiceServicer):

    async def StreamAggregates(self, request, context):
        while True:
            snapshot = await store.snapshot()

            for key, v in snapshot.items():
                if not v:
                    continue
                parts = key.split(":")
                sensor_type = parts[1]
                location = parts[2]

                yield telemetry_pb2.Aggregate(
                    key=telemetry_pb2.AggregateKey(
                        sensor_type=sensor_type,
                        location=location,
                    ),
                    count=int(v["count"]),
                    sum=float(v["sum"]),
                    min=float(v["min"]),
                    max=float(v["max"]),
                    updated_unix_ms=int(time.time() * 1000),
                )

            await asyncio.sleep(2)


# ----------------------------------------------------------
# 3️⃣ Unary query service
# ----------------------------------------------------------
class QueryService(telemetry_pb2_grpc.QueryServiceServicer):

    async def GetSensorStats(self, request, context):
        sensor_id = request.sensor_id
        stats_key = f"sensor:{sensor_id}:stats"
        recent_key = f"sensor:{sensor_id}:recent"

        stats = await redis_client.hgetall(stats_key)

        if not stats:
            await context.abort(grpc.StatusCode.NOT_FOUND, f"Sensor {sensor_id} not found")
            return

        recent_raw = await redis_client.lrange(recent_key, 0, 19)
        recent_values = []
        for r in recent_raw:
            entry = json.loads(r)
            recent_values.append(telemetry_pb2.RecentValue(
                ts_unix_ms=int(entry["ts"]),
                value=float(entry["value"]),
            ))

        return telemetry_pb2.GetSensorStatsResponse(
            meta=telemetry_pb2.SensorMeta(
                sensor_id=sensor_id,
                sensor_type="unknown",
                location="unknown",
            ),
            count=int(stats["count"]),
            sum=float(stats["sum"]),
            min=float(stats["min"]),
            max=float(stats["max"]),
            updated_unix_ms=int(time.time() * 1000),
            recent=recent_values,
        )


# -----------------------------
# Periodic stats printer
# -----------------------------
async def stats_printer():
    while True:
        await asyncio.sleep(5)
        snap = await store.snapshot()

        print("\n===== REDIS AGGREGATES =====")
        for key, v in snap.items():
            if not v:
                continue
            count = int(v["count"])
            sum_v = float(v["sum"])
            avg = sum_v / count if count else 0
            print(
                f"{key} count={count} avg={avg:.2f} "
                f"min={float(v['min']):.2f} max={float(v['max']):.2f}"
            )
        print("============================\n")


# -----------------------------
# Server bootstrap
# -----------------------------
async def serve(port: int):
    server = grpc.aio.server()

    telemetry_pb2_grpc.add_IngestServiceServicer_to_server(
        IngestService(), server
    )

    telemetry_pb2_grpc.add_AggregateServiceServicer_to_server(
        AggregateService(), server
    )

    telemetry_pb2_grpc.add_QueryServiceServicer_to_server(
        QueryService(), server
    )

    server.add_insecure_port(f"[::]:{port}")

    await server.start()
    print(f"Collector running on :{port}")

    asyncio.create_task(stats_printer())

    await server.wait_for_termination()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=50051)
    args = ap.parse_args()
    preferred_port = args.port
    asyncio.run(serve(preferred_port))
