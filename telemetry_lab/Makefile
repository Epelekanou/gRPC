.PHONY: stubs up down logs run_grader grader_clean

stubs:
	python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. proto/telemetry.proto

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=100

run_grader:
	docker compose -f docker-compose.yml -f grader/docker-compose.grader.yml up --build --abort-on-container-exit --exit-code-from grader --no-attach redis --no-attach collector --no-attach api --no-attach sensors

grader_clean:
	docker compose -f docker-compose.yml -f grader/docker-compose.grader.yml down -v

# Run this from project root:
# make stubs -f .\telemetry_lab\Makefile