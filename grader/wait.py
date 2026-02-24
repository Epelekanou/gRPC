import socket
import time


def wait_for_tcp(host: str, port: int, timeout_s: float) -> None:
    deadline = time.time() + timeout_s
    last_err = None
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return
        except OSError as e:
            last_err = e
            time.sleep(0.3)
    raise TimeoutError(f"Timed out waiting for TCP {host}:{port}. Last error: {last_err}")
