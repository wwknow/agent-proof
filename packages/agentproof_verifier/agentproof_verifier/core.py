from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from typing import Any, Callable

VERDICTS = {"allow", "deny", "escalate"}
RECEIPT_VERSION = "0.1-mvp"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_hex(value: Any, *, truncate: int | None = None) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return digest[:truncate] if truncate else digest


def trace_id() -> str:
    return hashlib.sha256(str(time.time_ns()).encode()).hexdigest()[:16]


@dataclass(frozen=True)
class Command:
    agent_id: str
    tool: str
    params: dict[str, Any]
    timestamp: float
    trace_id: str
    request_hash: str | None = None
    response_hash: str | None = None
    runtime_context: dict[str, Any] | None = None
    action: str | None = None
    issuer: str | None = None
    audience: str | None = None

    @property
    def params_hash(self) -> str:
        return sha256_hex(self.params, truncate=16)


@dataclass(frozen=True)
class RuleResult:
    rule_name: str
    verdict: str
    reason: str = ""
    latency_ms: float = 0.0


Rule = Callable[[Command], RuleResult]


@dataclass
class Verifier:
    rules: list[Rule]
    policy_version: str = "mvp-1"
    policy_floor: str = "baseline"
    issuer: str = "local:agentproof-verifier"
    audience: str = "local:executor"
    secret: bytes = field(default_factory=lambda: secrets.token_bytes(32))
    receipt_ttl_seconds: float = 60.0

    def config(self) -> dict[str, Any]:
        return {
            "rules": [getattr(r, "rule_name", r.__name__) for r in self.rules],
            "policy_version": self.policy_version,
            "policy_floor": self.policy_floor,
            "issuer": self.issuer,
            "audience": self.audience,
        }

    def config_hash(self) -> str:
        return "sha256:" + sha256_hex(self.config())

    def evaluate(self, command: Command) -> tuple[str, list[RuleResult]]:
        results: list[RuleResult] = []
        for rule in self.rules:
            started = time.perf_counter()
            try:
                result = rule(command)
            except Exception as exc:  # fail closed
                result = RuleResult(getattr(rule, "rule_name", rule.__name__), "deny", "rule_error")
            elapsed = (time.perf_counter() - started) * 1000
            results.append(RuleResult(result.rule_name, result.verdict, result.reason, elapsed))
        verdicts = {r.verdict for r in results}
        if "deny" in verdicts:
            return "deny", results
        if "escalate" in verdicts:
            return "escalate", results
        return "allow", results

    def issue_receipt(self, command: Command) -> dict[str, Any]:
        normalized = normalize_command(command)
        verdict, results = self.evaluate(normalized)
        now = time.time()
        expires = now + self.receipt_ttl_seconds
        summary = "|".join(f"{r.rule_name}={r.verdict}" for r in results)
        reason = next((r.reason for r in results if r.verdict == "deny" and r.reason), "")
        receipt = {
            "evidence_version": RECEIPT_VERSION,
            "trace_id": normalized.trace_id,
            "verdict": verdict,
            "timestamp": normalized.timestamp,
            "tool": normalized.tool,
            "params_hash": normalized.params_hash,
            "rule_summary": summary,
            "verified_at": now,
            "block_reason": reason,
            "request_hash": normalized.request_hash,
            "response_hash": normalized.response_hash,
            "runtime_context_hash": (
                "sha256:" + sha256_hex(normalized.runtime_context)
                if normalized.runtime_context is not None else ""
            ),
            "action": normalized.action or f"evidence:tool-invoke:{normalized.tool}:{normalized.params_hash}",
            "config_hash": self.config_hash(),
            "issuer": normalized.issuer or self.issuer,
            "audience": normalized.audience or self.audience,
            "nonce": secrets.token_hex(16),
            "sequence": 0,
            "issued_at": now,
            "expires_at": expires,
            "max_clock_skew": 30.0,
        }
        receipt["receipt"] = self._sign(receipt)
        return receipt

    def _sign(self, receipt: dict[str, Any]) -> str:
        payload = canonical_json({k: v for k, v in receipt.items() if k not in {"receipt", "signature"}})
        return hmac.new(self.secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()[:32]

    def verify_receipt(self, receipt: dict[str, Any], *, expected_audience: str | None = None, now: float | None = None) -> dict[str, Any]:
        errors: list[str] = []
        required = ["trace_id", "verdict", "timestamp", "tool", "params_hash", "rule_summary", "receipt", "issued_at", "expires_at", "issuer", "audience", "nonce", "config_hash"]
        for field_name in required:
            if field_name not in receipt:
                errors.append(f"missing:{field_name}")
        if receipt.get("verdict") not in VERDICTS:
            errors.append("invalid:verdict")
        if expected_audience is not None and receipt.get("audience") != expected_audience:
            errors.append("audience_mismatch")
        current = time.time() if now is None else now
        skew = float(receipt.get("max_clock_skew", 30.0))
        if isinstance(receipt.get("issued_at"), (int, float)) and current < receipt["issued_at"] - skew:
            errors.append("not_yet_valid")
        if isinstance(receipt.get("expires_at"), (int, float)) and current > receipt["expires_at"] + skew:
            errors.append("expired")
        expected = self._sign(receipt) if not errors else None
        if expected is not None and not hmac.compare_digest(expected, str(receipt.get("receipt", ""))):
            errors.append("invalid_signature")
        return {"valid": not errors, "errors": errors, "verdict": receipt.get("verdict")}


def normalize_command(command: Command) -> Command:
    if not command.agent_id or len(command.agent_id.encode()) > 512:
        raise ValueError("agent_id invalid")
    if not command.tool or len(command.tool.encode()) > 512:
        raise ValueError("tool invalid")
    canonical_json(command.params)
    params_hash = sha256_hex(command.params)
    request_hash = command.request_hash or ("sha256:" + sha256_hex({"tool": command.tool, "params": command.params, "agent_id": command.agent_id}))
    return Command(
        agent_id=command.agent_id,
        tool=command.tool,
        params=command.params,
        timestamp=float(command.timestamp),
        trace_id=command.trace_id,
        request_hash=request_hash,
        response_hash=command.response_hash,
        runtime_context=command.runtime_context,
        action=command.action or f"evidence:tool-invoke:{command.tool}:{params_hash}",
        issuer=command.issuer,
        audience=command.audience,
    )
