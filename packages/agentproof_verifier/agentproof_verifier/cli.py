from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .core import Command, Verifier, trace_id
from .rules.builtin import rce_protection, ssrf_protection


def build_verifier(secret: str | None = None) -> Verifier:
    kwargs = {}
    if secret:
        kwargs["secret"] = secret.encode("utf-8")
    return Verifier([rce_protection, ssrf_protection], **kwargs)


def cmd_verify(args: argparse.Namespace) -> int:
    data = json.load(sys.stdin) if args.file == "-" else json.loads(Path(args.file).read_text())
    command = Command(
        agent_id=data["agent_id"],
        tool=data["tool"],
        params=data.get("params", {}),
        timestamp=float(data.get("timestamp", time.time())),
        trace_id=data.get("trace_id", trace_id()),
        runtime_context=data.get("runtime_context"),
        issuer=data.get("issuer"),
        audience=data.get("audience"),
    )
    verifier = build_verifier(args.secret)
    print(json.dumps(verifier.issue_receipt(command), indent=2, sort_keys=True))
    return 0


def cmd_demo(_: argparse.Namespace) -> int:
    verifier = build_verifier("demo-secret")
    for label, tool, params in [
        ("ALLOW", "search_web", {"query": "weather in Tokyo"}),
        ("DENY", "shell_exec", {"command": "rm -rf /"}),
    ]:
        receipt = verifier.issue_receipt(Command("demo-agent", tool, params, time.time(), trace_id()))
        check = verifier.verify_receipt(receipt)
        print(f"[{label}] verdict={receipt['verdict']} valid={check['valid']} reason={receipt['block_reason']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="agentproof-verify", description="AgentProof Reference Verifier MVP")
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify", help="Verify a command JSON and emit a signed evidence receipt")
    verify.add_argument("file", help="JSON file, or - for stdin")
    verify.add_argument("--secret", default=None, help="HMAC secret; use env/secret manager in production")
    verify.set_defaults(func=cmd_verify)
    demo = sub.add_parser("demo", help="Run two built-in conformance-style examples")
    demo.set_defaults(func=cmd_demo)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
