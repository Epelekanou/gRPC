# Protocol Buffers Contract Specification (You must follow exactly)

Create a file:

* `proto/telemetry.proto`

At the top, your file must declare:

* `syntax = "proto3";`
* `package telemetry.v1;`

These lines must appear before message/service definitions.

---

## 1) Core Data Model

### Message: `SensorMeta`

This message is embedded in multiple other messages and must contain exactly these fields **with these numbers**:

1. `sensor_id` (type: `string`)

   * stable sensor identifier (example: `"T-01"`, `"H-WH-02"`)

2. `sensor_type` (type: `string`)

   * example values: `"temperature"`, `"humidity"`, `"vibration"`

3. `location` (type: `string`)

   * example values: `"boiler_room"`, `"warehouse"`, `"lab"`

✅ The message name must be exactly `SensorMeta`.

---

### Message: `Measurement`

This is the unit of data produced by sensors and streamed into collectors.

Fields (must match **names + numbers + types**):

1. `meta` (type: `SensorMeta`)
   * This is the **SensorMeta** message defined above. In protocol buffers we can nest Messages.
2. `seq` (type: `uint64`)

   * sequence number per sensor (starts at 1, increments)
3. `ts_unix_ms` (type: `int64`)

   * timestamp in unix epoch milliseconds
4. `value` (type: `double`)

✅ The message name must be exactly `Measurement`.

---

## 2) Aggregations

We keep aggregation simple and global.

### Message: `AggregateKey`

This identifies the grouping key of aggregated statistics.

Fields:

1. `sensor_type` (type: `string`)
2. `location` (type: `string`)

✅ Name must be exactly `AggregateKey`.

---

### Message: `Aggregate`

This is what the collector streams to the dashboard layer.

Fields (must match exactly):

1. `key` (type: `AggregateKey`)
2. `count` (type: `uint64`)
3. `sum` (type: `double`)
4. `min` (type: `double`)
5. `max` (type: `double`)
6. `updated_unix_ms` (type: `int64`)

   * when this aggregate snapshot was produced

✅ Name must be exactly `Aggregate`.

---

## 3) Services and RPC Signatures (Autograder-sensitive)

The autograder expects these **service names** and **RPC method names** exactly.
Case, spelling, and request/response types must match.

---

### Service 1: `IngestService`

**Purpose:** sensors push measurements to collector.

RPC:

* Method name: `PushMeasurements`
* Signature must be:

```proto
rpc PushMeasurements(stream Measurement) returns (IngestAck);
```

Define message `IngestAck` with:

1. `received` (type: `uint64`)

   * number of measurements processed (best effort)

✅ Names must be: `IngestService`, `PushMeasurements`, `IngestAck`, `received`

---

### Service 2: `AggregateService`

**Purpose:** consumers (e.g., FastAPI) subscribe to aggregate updates.

RPC:

* Method name: `StreamAggregates`
* Signature must be:

```proto
rpc StreamAggregates(StreamAggregatesRequest) returns (stream Aggregate);
```

Define message `StreamAggregatesRequest` with fields:

1. `keys` (type: `repeated AggregateKey`)

   * if empty, means “stream all keys”
2. `send_initial_snapshot` (type: `bool`)

   * if true, emit current known aggregates immediately
3. `min_update_interval_ms` (type: `uint32`)

   * optional rate limiting for updates

✅ Names must be exactly: `AggregateService`, `StreamAggregates`, `StreamAggregatesRequest`

---

### Service 3: `QueryService`

**Purpose:** query per-sensor statistics on demand.

RPC:

* Method name: `GetSensorStats`
* Signature must be:

```proto
rpc GetSensorStats(GetSensorStatsRequest) returns (GetSensorStatsResponse);
```

Define `GetSensorStatsRequest`:

1. `sensor_id` (type: `string`)

✅ Name must be exactly `GetSensorStatsRequest`.

---

## 4) “Recent values” support (last N samples)

To support showing the last 10–20 measurements per sensor, define:

### Message: `RecentValue`

Fields:

1. `ts_unix_ms` (type: `int64`)
2. `value` (type: `double`)

✅ Name must be exactly `RecentValue`.

---

### Message: `GetSensorStatsResponse`

Fields (must match exactly):

1. `meta` (type: `SensorMeta`)
2. `count` (type: `uint64`)
3. `sum` (type: `double`)
4. `min` (type: `double`)
5. `max` (type: `double`)
6. `updated_unix_ms` (type: `int64`)
7. `recent` (type: `repeated RecentValue`)

✅ Name must be exactly `GetSensorStatsResponse`.
✅ Field numbers must be exactly 1..7 as above.
⚠️ In Protocol Buffers, the repeated keyword is used to define a field that can contain multiple values of the same type rather than just one. It works like a list or array, allowing zero or more entries to be included in a message while preserving their order. This is commonly used when sending collections of data (such as multiple recent values or messages) inside another protobuf message, making the schema flexible without needing separate numbered fields.

---

# 5) Stub Generation (must be done after proto changes)

After writing `proto/telemetry.proto`, generate Python stubs:

```bash
python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. proto/telemetry.proto
```

This should produce:

* `proto/telemetry_pb2.py`
* `proto/telemetry_pb2_grpc.py`

If your proto changes, you must regenerate these files or the services won’t match.

You can make a rough validation of your proto file and generated stubsby running the validate_proto script in scripts
```
python -m scripts.validate_proto
``` 

---

# 6) Common mistakes that cause autograder failure

* Renaming `telemetry.v1` package or changing service names
* Changing RPC method names (`PushMeasurements`, `StreamAggregates`, `GetSensorStats`)
* Changing message names or field numbers
* Using the wrong stream direction (e.g., unary instead of streaming)
* Forgetting to regenerate stubs after editing the `.proto`

