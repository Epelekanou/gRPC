import asyncio
import threading
import time

import grpc
import pytest

from proto import telemetry_pb2
from proto import telemetry_pb2_grpc

# -----------------------------
# Fake collector implementation
# -----------------------------
class FakeIngestService(telemetry_pb2_grpc.IngestServiceServicer):
    def __init__(self):
        self.received = []
    
    async def PushMeasurements(self, request_iterator, context):
        async for m in request_iterator:
            self.received.append(m)
        
        return telemetry_pb2.IngestAck(received=len(self.received))

# -----------------------------
# Helper: start Fake collector
# -----------------------------
async def start_fake_collector(servicer, port=50099):
    server = grpc.aio.server()
    telemetry_pb2_grpc.add_IngestServiceServicer_to_server(servicer, server)

    server.add_insecure_port(f"[::]:{port}")
    await server.start()

    return server

# -----------------------------
# Actual Test
# -----------------------------
@pytest.mark.asyncio
async def test_sensor_client_streams_measurements():
    """
    Validates that the student's sensor client:

    - connects to PushMeasurements()
    - sends Measurement messages
    - includes metadata correctly
    - increments sequence numbers
    """
    # Import student sensor code dynamically
    # so failures surface clearly.
    from sensor.mock_sensor import MockSensor
    from sensor.sensor_client import send_sensor

    servicer = FakeIngestService()
    server = await start_fake_collector(servicer)

    # Force sensor client to connect to fake collector
    import sensor.sensor_client as sc
    sc.COLLECTOR_ADDRS = ["localhost:50099"]

    # Create a deterministic sensor
    sensor = MockSensor(
        sensor_id="myTEST-01",
        sensor_type="temperature",
        location="lab2",
        interval=0.05,
        generator=lambda: 42.0,
    )

    # Run sensor briefly
    task = asyncio.create_task(send_sensor(sensor))
    await asyncio.sleep(3.0)
    task.cancel()

    await server.stop(grace=5.0)

    # Assertions
    assert len(servicer.received) > 5, "Sensor sent too few measurements"

    first = servicer.received[0]

    assert first.meta.sensor_id == "myTEST-01"
    assert first.meta.sensor_type == "temperature"
    assert first.meta.location == "lab2"
    assert first.value == 42.0

    # Sequence monotonicity check
    seqs = [m.seq for m in servicer.received]
    assert seqs == sorted(seqs), "Sequence numbers not increasing"