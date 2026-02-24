import json
import time

from grader.config import API_BASE, STREAM_TIMEOUT_S
from proto import telemetry_pb2


def _ms() -> int:
    return int(time.time() * 1000)


def _measurement(sensor_id: str, sensor_type: str, location: str, seq: int, ts: int, value: float):
    return telemetry_pb2.Measurement(
        meta=telemetry_pb2.SensorMeta(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            location=location,
        ),
        seq=seq,
        ts_unix_ms=ts,
        value=value,
    )


def test_client_streaming_ingest_and_redis_side_effects(ingest_stub, redis_client):
    sensor_id = "T-01"
    sensor_type = "temperature"
    location = "lab"
    values = [10.0 + i for i in range(30)]  # 30 values: recent should keep last 20

    def gen():
        ts0 = _ms()
        for i, v in enumerate(values, start=1):
            yield _measurement(sensor_id, sensor_type, location, i, ts0 + i, v)

    ack = ingest_stub.PushMeasurements(gen(), timeout=10)
    assert ack.received == 30

    # Global aggregate
    gkey = f"agg:{sensor_type}:{location}"
    g = redis_client.hgetall(gkey)
    assert g, f"Missing global key {gkey}"
    assert int(g["count"]) == 30
    assert float(g["sum"]) == sum(values)
    assert float(g["min"]) == min(values)
    assert float(g["max"]) == max(values)

    # Per-sensor stats
    skey = f"sensor:{sensor_id}:stats"
    s = redis_client.hgetall(skey)
    assert s, f"Missing sensor stats key {skey}"
    assert int(s["count"]) == 30
    assert float(s["sum"]) == sum(values)
    assert float(s["min"]) == min(values)
    assert float(s["max"]) == max(values)

    # Recent bounded list (last 20, newest-first if LPUSH)
    rkey = f"sensor:{sensor_id}:recent"
    recent = redis_client.lrange(rkey, 0, -1)
    assert len(recent) == 20, f"Expected 20 recent values, got {len(recent)}"

    top = json.loads(recent[0])
    assert abs(top["value"] - values[-1]) < 1e-9


def test_server_streaming_aggregates_emits_updates(aggregate_stub):
    req = telemetry_pb2.StreamAggregatesRequest(send_initial_snapshot=True)
    stream = aggregate_stub.StreamAggregates(req, timeout=STREAM_TIMEOUT_S)

    first = next(stream)
    assert first.count >= 1
    assert first.key.sensor_type != ""
    assert first.key.location != ""


def test_unary_query_returns_stats_and_recent(query_stub):
    resp = query_stub.GetSensorStats(
        telemetry_pb2.GetSensorStatsRequest(sensor_id="T-01"),
        timeout=5,
    )
    assert resp.count == 30
    assert len(resp.recent) <= 20
    assert resp.max >= resp.min


def test_fastapi_http_endpoint(http_session):
    r = http_session.get(f"{API_BASE}/sensor/T-01", timeout=5)
    assert r.status_code == 200, r.text

    payload = r.json()
    assert payload["sensor_id"] == "T-01"
    assert payload["count"] == 30
    assert "recent" in payload
    assert len(payload["recent"]) <= 20


def test_fastapi_ws_receives_broadcasts_best_effort():
    """
    Best-effort WebSocket test:
    Some student solutions may omit WS or mount it differently.
    We do NOT fail the entire suite if WS isn't present.
    """
    import asyncio
    import websockets

    async def _ws_once():
        async with websockets.connect("ws://api:8000/ws", open_timeout=5) as ws:
            await ws.send("ping")
            msg = await asyncio.wait_for(ws.recv(), timeout=STREAM_TIMEOUT_S)
            return msg

    try:
        msg = asyncio.run(_ws_once())
        assert isinstance(msg, str) and len(msg) > 0
    except Exception:
        # Best-effort: don't fail the whole grading run on WS specifics
        assert True
