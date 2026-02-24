"""
This file will:
    Create multiple sensors
    Each opens its own gRPC stream
    Stream forever
"""
"""
📘 What This Sensor Client Does (Student Explanation)
This program simulates a set of industrial sensors that continuously send telemetry data to a central data collection service.
Each sensor represents a physical measurement device located somewhere in an industrial facility (for example, temperature sensors in a boiler room or vibration sensors on an assembly line). These sensors periodically generate measurements such as temperature, humidity, or vibration intensity.

The MockSensor class produces an asynchronous stream of readings. Each reading contains:
    A unique sensor identifier (sensor_id)
    The sensor type (temperature, humidity, etc.)
    The physical location (warehouse, lab, etc.)
    A timestamp
    A simulated measurement value

The program selects a small random subset of sensors (currently 5) and runs them concurrently using Python’s asyncio. Each sensor continuously generates readings at its own sampling rate.
Normally, these readings would be streamed to a collector service using gRPC client-streaming RPC. 
However, in this scaffold version, the actual gRPC call has been removed so that the program can run independently while you implement the communication layer.

Your task later in the lab will be to:
Define the gRPC service in the .proto file.
Generate Python stubs.
Replace the placeholder code with the actual gRPC client streaming call.
"""

import random
import asyncio
import grpc

from proto import telemetry_pb2
from proto import telemetry_pb2_grpc

from sensor.mock_sensor import MockSensor
from sensor.sensor_helper import (
    temp_boiler_room,
    temp_warehouse,
    temp_assembly_line,
    temp_lab,
    humidity_boiler_room,
    humidity_warehouse,
    humidity_assembly_line,
    humidity_lab,
    vibration_boiler_room,
    vibration_warehouse,
    vibration_assembly_line,
    vibration_lab,
    GENERATOR_MAP
)

import os

# COLLECTOR_ADDRS = ["collector:50051","localhost:50052",]
collector_addrs_str = os.getenv("COLLECTOR_ADDRS", "localhost:50051,localhost:50052")

COLLECTOR_ADDRS = [addr.strip() for addr in collector_addrs_str.split(",") if addr.strip()]

async def send_sensor(sensor: MockSensor):
    backoff = 1

    while True:
        addr = random.choice(COLLECTOR_ADDRS)
        try:
            async with grpc.aio.insecure_channel(addr) as channel:
                # ------------------------------------------------------------------
                # TEMPORARY PLACEHOLDER (NO gRPC YET)
                #
                # This block simply consumes the sensor stream locally so that the
                # program runs without contacting a collector service.
                #
                # You should replace this with a real gRPC call
                # 
                # 1. Use the gRPC channel created above
                # 2. Create the IngestServiceStub
                # 3. Stream Measurement messages using:
                #   await stub.PushMeasuremets(request_generator())
                # ------------------------------------------------------------------

                print(f"[{sensor.sensor_id}] placeholder connection -> {addr}")

                async for reading in sensor.stream():
                    print(
                        f"[{reading.sensor_id}] "
                        f"{reading.sensor_type}@{reading.location} "
                        f"value={reading.value:.2f} "
                        f"ts={reading.ts_unix_ms}"
                    )

                    # Simulate network delay / batching
                    await asyncio.sleep(0.1)

        except grpc.aio.AioRpcError as e:
            print(f"[{sensor.sensor_id}] disconnected from {addr}:", e.code())
        
        # Exponential backoff with jitter
        sleep_time = backoff + random.uniform(0, 0.5)
        print(f"[{sensor.sensor_id}] retrying in {sleep_time:.1f}s")
        
        await asyncio.sleep(sleep_time)
        backoff = min(backoff * 2, 30)



async def main():
    sensors = [
        MockSensor("T-BR-01", "temperature", "boiler_room", 0.5, temp_boiler_room),
        MockSensor("T-BR-02", "temperature", "boiler_room", 0.7, temp_boiler_room),
        MockSensor("H-WH-01", "humidity", "warehouse", 1.2, humidity_warehouse),
        MockSensor("T-WH-03", "temperature", "warehouse", 1.1, temp_warehouse),
        MockSensor("T-WH-04", "temperature", "warehouse", 0.9, temp_warehouse),
        MockSensor("V-AL-01", "vibration", "assembly_line", 0.3, vibration_assembly_line),
        MockSensor("T-L-05", "temperature", "lab", 1.5, temp_lab),
        MockSensor("T-AL-06", "temperature", "assembly_line", 1.1, temp_assembly_line),
        MockSensor("T-AL-07", "temperature", "assembly_line", 1.2, temp_assembly_line),
        MockSensor("T-AL-08", "temperature", "assembly_line", 0.9, temp_assembly_line),
        MockSensor("T-AL-09", "temperature", "assembly_line", 1.0, temp_assembly_line),
        MockSensor("T-AL-10", "temperature", "assembly_line", 1.01, temp_assembly_line),

        MockSensor("H-BR-03", "humidity", "boiler_room", 0.4, humidity_boiler_room),
        MockSensor("T-BR-04", "temperature", "boiler_room", 0.8, temp_boiler_room),
        MockSensor("T-BR-05", "temperature", "boiler_room", 0.6, temp_boiler_room),
        MockSensor("V-BR-02", "vibration", "boiler_room", 0.2, vibration_boiler_room),
        MockSensor("T-WH-05", "temperature", "warehouse", 1.0, temp_warehouse),
        MockSensor("H-WH-02", "humidity", "warehouse", 1.3, humidity_warehouse),
        MockSensor("V-WH-01", "vibration", "warehouse", 0.5, vibration_warehouse),
        MockSensor("V-WH-02", "vibration", "warehouse", 0.6, vibration_warehouse),
        MockSensor("T-WH-06", "temperature", "warehouse", 1.2, temp_warehouse),
        MockSensor("T-WH-07", "temperature", "warehouse", 0.95, temp_warehouse),

        MockSensor("T-L-06", "temperature", "lab", 1.4, temp_lab),
        MockSensor("H-L-01", "humidity", "lab", 1.1, humidity_lab),
        MockSensor("V-L-01", "vibration", "lab", 0.2, vibration_lab),
        MockSensor("T-L-07", "temperature", "lab", 1.6, temp_lab),
        MockSensor("T-L-08", "temperature", "lab", 1.3, temp_lab),
        MockSensor("H-L-02", "humidity", "lab", 1.0, humidity_lab),
        MockSensor("T-L-09", "temperature", "lab", 1.45, temp_lab),
        MockSensor("V-L-02", "vibration", "lab", 0.25, vibration_lab),
        MockSensor("T-L-10", "temperature", "lab", 1.5, temp_lab),
        MockSensor("H-AL-01", "humidity", "assembly_line", 0.8, humidity_assembly_line),

        MockSensor("T-AL-11", "temperature", "assembly_line", 1.22, temp_assembly_line),
        MockSensor("T-AL-12", "temperature", "assembly_line", 1.15, temp_assembly_line),
        MockSensor("V-AL-02", "vibration", "assembly_line", 0.35, vibration_assembly_line),
        MockSensor("V-AL-03", "vibration", "assembly_line", 0.4, vibration_assembly_line),
        MockSensor("H-AL-02", "humidity", "assembly_line", 0.9, humidity_assembly_line),
        MockSensor("T-AL-13", "temperature", "assembly_line", 0.97, temp_assembly_line),
        MockSensor("T-AL-14", "temperature", "assembly_line", 1.03, temp_assembly_line),
        MockSensor("T-AL-15", "temperature", "assembly_line", 1.08, temp_assembly_line),
        MockSensor("V-AL-04", "vibration", "assembly_line", 0.33, vibration_assembly_line),
        MockSensor("H-AL-03", "humidity", "assembly_line", 0.85, humidity_assembly_line),

        # Boiler room extras
        MockSensor("T-BR-06", "temperature", "boiler_room", 0.58, temp_boiler_room),
        MockSensor("H-BR-04", "humidity", "boiler_room", 0.48, humidity_boiler_room),
        MockSensor("V-BR-03", "vibration", "boiler_room", 0.28, vibration_boiler_room),
        MockSensor("T-BR-07", "temperature", "boiler_room", 0.62, temp_boiler_room),
        MockSensor("T-BR-08", "temperature", "boiler_room", 0.73, temp_boiler_room),
        MockSensor("H-BR-05", "humidity", "boiler_room", 0.55, humidity_boiler_room),
        MockSensor("T-BR-09", "temperature", "boiler_room", 0.67, temp_boiler_room),
        MockSensor("V-BR-04", "vibration", "boiler_room", 0.31, vibration_boiler_room),
        MockSensor("T-BR-10", "temperature", "boiler_room", 0.69, temp_boiler_room),
        MockSensor("H-BR-06", "humidity", "boiler_room", 0.6, humidity_boiler_room),

        # Warehouse expanded
        MockSensor("T-WH-08", "temperature", "warehouse", 1.1, temp_warehouse),
        MockSensor("T-WH-09", "temperature", "warehouse", 0.88, temp_warehouse),
        MockSensor("H-WH-03", "humidity", "warehouse", 1.25, humidity_warehouse),
        MockSensor("H-WH-04", "humidity", "warehouse", 1.15, humidity_warehouse),
        MockSensor("V-WH-03", "vibration", "warehouse", 0.57, vibration_warehouse),
        MockSensor("V-WH-04", "vibration", "warehouse", 0.62, vibration_warehouse),
        MockSensor("T-WH-10", "temperature", "warehouse", 1.02, temp_warehouse),
        MockSensor("H-WH-05", "humidity", "warehouse", 1.05, humidity_warehouse),
        MockSensor("T-WH-11", "temperature", "warehouse", 1.08, temp_warehouse),
        MockSensor("V-WH-05", "vibration", "warehouse", 0.55, vibration_warehouse),

        # Lab expanded
        MockSensor("T-L-11", "temperature", "lab", 1.45, temp_lab),
        MockSensor("H-L-03", "humidity", "lab", 1.07, humidity_lab),
        MockSensor("V-L-03", "vibration", "lab", 0.22, vibration_lab),
        MockSensor("T-L-12", "temperature", "lab", 1.52, temp_lab),
        MockSensor("H-L-04", "humidity", "lab", 1.12, humidity_lab),
        MockSensor("T-L-13", "temperature", "lab", 1.48, temp_lab),
        MockSensor("V-L-04", "vibration", "lab", 0.27, vibration_lab),
        MockSensor("T-L-14", "temperature", "lab", 1.56, temp_lab),
        MockSensor("H-L-05", "humidity", "lab", 1.08, humidity_lab),
        MockSensor("T-L-15", "temperature", "lab", 1.50, temp_lab),

        # Assembly line completion
        MockSensor("T-AL-16", "temperature", "assembly_line", 1.07, temp_assembly_line),
        MockSensor("T-AL-17", "temperature", "assembly_line", 1.09, temp_assembly_line),
        MockSensor("H-AL-04", "humidity", "assembly_line", 0.92, humidity_assembly_line),
        MockSensor("V-AL-05", "vibration", "assembly_line", 0.38, vibration_assembly_line),
        MockSensor("T-AL-18", "temperature", "assembly_line", 1.12, temp_assembly_line),
        MockSensor("T-AL-19", "temperature", "assembly_line", 1.00, temp_assembly_line),
        MockSensor("T-AL-20", "temperature", "assembly_line", 1.05, temp_assembly_line),
        MockSensor("H-AL-05", "humidity", "assembly_line", 0.88, humidity_assembly_line),
        MockSensor("V-AL-06", "vibration", "assembly_line", 0.36, vibration_assembly_line),
        MockSensor("T-AL-21", "temperature", "assembly_line", 1.14, temp_assembly_line),
    ]

    sensors = random.sample(population=sensors, k=5)
    tasks = [asyncio.create_task(send_sensor(s)) for s in sensors]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())