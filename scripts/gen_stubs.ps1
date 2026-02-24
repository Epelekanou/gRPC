python -m grpc_tools.protoc `
  -I . `
  --python_out=. `
  --grpc_python_out=. `
  proto/telemetry.proto

Write-Host "Generated stubs under proto/: telemetry_pb2.py + telemetry_pb2_grpc.py"
