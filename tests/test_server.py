import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

from server.server import Handler


def test_server_health_and_verify():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{httpd.server_port}"
    try:
        with urllib.request.urlopen(base + "/healthz", timeout=2) as response:
            assert response.status == 200
            assert json.load(response)["ok"] is True
        payload = json.dumps({
            "agent_id": "test-agent",
            "tool": "shell_exec",
            "params": {"command": "rm -rf /"},
        }).encode()
        request = urllib.request.Request(
            base + "/v1/verify", data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            body = json.load(response)
            assert response.status == 200
            assert body["receipt"]["verdict"] == "deny"
            assert body["verification"]["valid"] is True
    finally:
        httpd.shutdown()
        thread.join(timeout=2)
