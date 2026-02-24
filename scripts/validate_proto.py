"""
Proto validation helper for telemetry lab.

This script validates:

- Generated protobuf stubs exist
- Required services exist
- RPC methods exist and are callable
- Required messages/fields exist

It does NOT require a running gRPC server.
"""

import sys
import grpc

try:
    from proto import telemetry_pb2
    from proto import telemetry_pb2_grpc
except Exception as e:
    print("❌ Could not import generated stubs.")
    print("Did you run protoc?")
    print(e)
    sys.exit(1)


def check(condition, msg):
    if condition:
        print(f"✅ {msg}")
    else:
        print(f"❌ {msg}")
        sys.exit(1)


print("\n=== Creating Dummy Channel ===")

try:
    # Dummy channel – no server needed
    channel = grpc.insecure_channel("localhost:0")
    print("✅ Channel created")
except Exception as e:
    print("❌ Failed creating channel:", e)
    sys.exit(1)


print("\n=== Instantiating Stubs ===")

try:
    ingest_stub = telemetry_pb2_grpc.IngestServiceStub(channel)
    agg_stub = telemetry_pb2_grpc.AggregateServiceStub(channel)
    query_stub = telemetry_pb2_grpc.QueryServiceStub(channel)
    print("✅ Stubs instantiated")
except Exception as e:
    print("❌ Stub instantiation failed:", e)
    sys.exit(1)


print("\n=== Checking RPC Methods ===")

check(hasattr(ingest_stub, "PushMeasurements"),
      "PushMeasurements RPC exists")

check(hasattr(agg_stub, "StreamAggregates"),
      "StreamAggregates RPC exists")

check(hasattr(query_stub, "GetSensorStats"),
      "GetSensorStats RPC exists")


print("\n=== Checking Message Types ===")

required_messages = [
    "SensorMeta",
    "Measurement",
    "AggregateKey",
    "Aggregate",
    "RecentValue",
    "GetSensorStatsRequest",
    "GetSensorStatsResponse",
]

for msg in required_messages:
    check(hasattr(telemetry_pb2, msg), f"{msg} exists")


print("\n=== Checking Critical Fields ===")

check(
    hasattr(telemetry_pb2.Measurement(), "value"),
    "Measurement.value field exists"
)

check(
    hasattr(telemetry_pb2.Aggregate(), "count"),
    "Aggregate.count field exists"
)

check(
    hasattr(telemetry_pb2.GetSensorStatsResponse(), "recent"),
    "GetSensorStatsResponse.recent field exists"
)

print("\n🎉 Proto validation passed.")
print("You can proceed with implementation.")