3) Run autograder locally (one command)

From repo root:
```
docker compose -f docker-compose.yml -f grader/docker-compose.grader.yml up --build --abort-on-container-exit --exit-code-from grader --no-attach redis --no-attach collector --no-attach api --no-attach sensors

```

This will:
    - build and start services
    - run pytest inside grader
    - exit with grader’s exit code (perfect for CI)

Cleanup:
```
docker compose -f docker-compose.yml -f grader/docker-compose.grader.yml down -v
```
