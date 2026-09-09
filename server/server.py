from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from agentproof_verifier.core import Command, Verifier, trace_id
from agentproof_verifier.rules.builtin import rce_protection, ssrf_protection

HOST = os.getenv("AGENTPROOF_HOST", "0.0.0.0")
PORT = int(os.getenv("AGENTPROOF_PORT", "8080"))
SECRET = os.getenv("AGENTPROOF_SECRET", "demo-secret").encode("utf-8")
ISSUER = os.getenv("AGENTPROOF_ISSUER", "local:agentproof")
AUDIENCE = os.getenv("AGENTPROOF_AUDIENCE", "local:executor")

VERIFIER = Verifier(
    [rce_protection, ssrf_protection],
    secret=SECRET,
    issuer=ISSUER,
    audience=AUDIENCE,
)


def json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "AgentProof/0.2"

    def _send(self, status: int, body: Any, content_type: str = "application/json") -> None:
        payload = body if isinstance(body, bytes) else json_bytes(body)
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 1_048_576:
            raise ValueError("body must be between 1 byte and 1 MiB")
        raw = self.rfile.read(length)
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object")
        return data

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self._send(200, {"ok": True, "service": "agentproof"})
            return
        if self.path == "/v1/info":
            self._send(200, {
                "service": "agentproof",
                "version": "0.2.0",
                "verifier": "reference-mvp",
                "policy_version": VERIFIER.policy_version,
                "config_hash": VERIFIER.config_hash(),
            })
            return
        if self.path == "/":
            html = """<!doctype html><html><head><meta charset='utf-8'><title>AgentProof</title><meta name='viewport' content='width=device-width,initial-scale=1'></head><body><main style='max-width:760px;margin:40px auto;font-family:system-ui'><h1>AgentProof</h1><p>Reference verifier for AI-agent delegation evidence.</p><p>POST a command JSON to <code>/v1/verify</code>.</p><pre>curl -X POST http://localhost:8080/v1/verify \\
  -H 'content-type: application/json' \\
  -d '{"agent_id":"demo-agent","tool":"search_web","params":{"query":"hello"}}'</pre><p>Health: <a href='/healthz'>/healthz</a> · Info: <a href='/v1/info'>/v1/info</a></p></main></body></html>"""
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
            return
        self._send(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/verify":
            self._send(404, {"error": "not_found"})
            return
        try:
            data = self._read_json()
            command = Command(
                agent_id=str(data["agent_id"]),
                tool=str(data["tool"]),
                params=data.get("params", {}),
                timestamp=float(data.get("timestamp", time.time())),
                trace_id=str(data.get("trace_id", trace_id())),
                runtime_context=data.get("runtime_context"),
                request_hash=data.get("request_hash"),
                response_hash=data.get("response_hash"),
                action=data.get("action"),
                issuer=data.get("issuer"),
                audience=data.get("audience"),
            )
            receipt = VERIFIER.issue_receipt(command)
            checked = VERIFIER.verify_receipt(
                receipt,
                expected_audience=data.get("expected_audience"),
            )
            self._send(200, {"receipt": receipt, "verification": checked})
        except KeyError as exc:
            self._send(400, {"error": "missing_field", "field": str(exc).strip("'")})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self._send(400, {"error": "invalid_request", "detail": str(exc)})
        except Exception:
            self._send(500, {"error": "internal_error"})

    def log_message(self, fmt: str, *args: object) -> None:
        print("[agentproof] " + (fmt % args))


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"AgentProof listening on http://{HOST}:{PORT}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
