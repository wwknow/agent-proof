import time
from agentproof_verifier import Command, Verifier, rce_protection, ssrf_protection, trace_id


def make():
    return Command("test-agent", "search_web", {"query": "weather"}, time.time(), trace_id())


def test_allow_receipt_roundtrip():
    v = Verifier([rce_protection, ssrf_protection], secret=b"x" * 32)
    r = v.issue_receipt(make())
    assert r["verdict"] == "allow"
    assert v.verify_receipt(r)["valid"]


def test_deny_rce():
    v = Verifier([rce_protection], secret=b"x" * 32)
    c = Command("a", "shell_exec", {"command": "rm -rf /"}, time.time(), trace_id())
    r = v.issue_receipt(c)
    assert r["verdict"] == "deny"
    assert r["block_reason"] == "rce_pattern_detected"


def test_tamper_is_detected():
    v = Verifier([rce_protection], secret=b"x" * 32)
    r = v.issue_receipt(make())
    r["tool"] = "evil_tool"
    assert not v.verify_receipt(r)["valid"]
