Start a redis service using docker:
```
docker run -d --name redis -p 6379:6379 redis
```

In a terminal run:
```
python -m sensor.sensor_client
```
from the project root.

In a second terminal start the collector service:
```
python -m collector.collector_server
```

In a third terminal start the FastAPI bridge:
```
uvicorn api.fastapi_bridge:app --reload --port 8000
```
All from project root.

You can the open the index.html in /web directory 
and see some live updates. 