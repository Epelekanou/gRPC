import asyncio
import random
import time
from dataclasses import dataclass, field
from typing import Optional, Callable, Awaitable


# -----------------------------
# Sensor reading structure
# -----------------------------
@dataclass
class SensorReading:
    sensor_id: str
    sensor_type: str
    location: str
    seq: int
    ts_unix_ms: int
    value: float


# -----------------------------
# Mock Sensor Class
# -----------------------------
class MockSensor:
    """
    Async industrial sensor.

    Genertaes timestamped random readings at fixed intervals.
    Emission is independent of consumers.
    """

    def __init__(
        self,
        sensor_id: str,
        sensor_type: str,
        location: str,
        interval: float = 1.0,
        generator: Optional[Callable[[], float]] = None        
    ):
        """
        Parameters
        ---------
        sensor_id: str
            Sensor ID/name

        sensor_type: str
            Type of sensor (temperature, humidity, etc.).

        location: str
            Physical or logical location.

        interval: float
            Seconds between readings.

        generator: callable optional
            Custom numeric generator.
            Defaults to uniform random.

        callback: async callabla optional
            Called for each reading (gRPC hook)

        """

        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.location = location
        self.interval = interval
        self.generator = generator or self._default_generator
        self._seq = 0

        self._task: Optional[asyncio.Task] = None
        self._running = False
    
    async def stream(self):
        """
        Async generator of SensorReading
        Runs forever
        """
        while True:
            self._seq += 1

            yield SensorReading(
                sensor_id=self.sensor_id,
                sensor_type=self.sensor_type,
                location=self.location,
                seq=self._seq,
                ts_unix_ms=int(time.time() * 1000),
                value=self.generator()
            )
            await asyncio.sleep(self.interval)


    # -------------------------
    # Default numeric generator
    # -------------------------
    def _default_generator(self) -> float:
        return random.uniform(0, 100)


   