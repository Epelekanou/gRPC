#!/usr/bin/env bash
set -euo pipefail

echo "[grader] Starting tests..."
pytest -v /grader/grader/tests
