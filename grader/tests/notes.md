### To run grader locally
From repo root:
```
docker compose -f docker-compose.yml -f grader/docker-compose.grader.yml up --build --abort-on-container-exit --exit-code-from grader
```

This will:
    - build and start services
    - run pytest inside grader
    - exit with grader's exit code

Cleanup:
```
docker compose -f docker-compose.yml -f grader/docker-compose.grader.yml down -v
```