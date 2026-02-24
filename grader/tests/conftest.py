import pytest
import redis
import requests
import grpc
import time

from proto import telemetry_pb2
from proto import telemetry_pb2_grpc

from grader.config import REDIS_HOST, REDIS_PORT, COLLECTOR_ADDR, API_BASE, READY_TIMEOUT_S
from grader.wait import wait_for_tcp

@pytest.fixture(scope="session")
def redis_client():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
    return r

@pytest.fixture(scope="session")
def collector_channel():
    host, port_s = COLLECTOR_ADDR.split(":")
    wait_for_tcp(host, int(port_s), READY_TIMEOUT_S)
    ch = grpc.insecure_channel(COLLECTOR_ADDR)
    yield ch
    ch.close()

@pytest.fixture(scope="session")
def ingest_stub(collector_channel):
    return telemetry_pb2_grpc.IngestServiceStub(collector_channel)

@pytest.fixture(scope="session")
def aggregate_stub(collector_channel):
    return telemetry_pb2_grpc.AggregateServiceStub(collector_channel)

@pytest.fixture(scope="session")
def query_stub(collector_channel):
    return telemetry_pb2_grpc.QueryServiceStub(collector_channel)


@pytest.fixture(scope="session")
def http_session():
    s = requests.Session()
    # Wait for API port
    wait_for_tcp("api", 8000, READY_TIMEOUT_S)
    
    # Confirm FastAPI is actually responding
    deadline = time.time() + READY_TIMEOUT_S
    last = None
    while time.time() < deadline:
        try:
            r = s.get(f"{API_BASE}/openapi.json", timeout=2)
            if r.status_code == 200:
                return s
            last = (r.status_code, r.text)
        except Exception as e:
            last = str(e)
        time.sleep(0.3)

    raise RuntimeError(f"API not ready at {API_BASE}. Last: {last}")


@pytest.fixture(scope="session", autouse=True)
def _flush_redis(redis_client):
    """
    Flush Redis before suite to make tests deterministic.
    """
    redis_client.flushdb()
    yield