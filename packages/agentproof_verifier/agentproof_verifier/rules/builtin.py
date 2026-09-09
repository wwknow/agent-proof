from __future__ import annotations

import re
from ..core import Command, RuleResult


def _tag(name):
    def deco(rule):
        rule.rule_name = name
        return rule
    return deco


@_tag("rce_protection")
def rce_protection(command: Command) -> RuleResult:
    """Very small demonstration rule, not a production malware detector."""
    text = str(command.params)
    patterns = [r"\brm\s+-rf\b", r"\bcurl\b.+\|\s*(?:bash|sh)", r"\beval\s*\("]
    matched = next((p for p in patterns if re.search(p, text, re.I)), None)
    if matched:
        return RuleResult("rce_protection", "deny", "rce_pattern_detected")
    return RuleResult("rce_protection", "allow")


@_tag("ssrf_protection")
def ssrf_protection(command: Command) -> RuleResult:
    """Demonstration SSRF guard for obvious localhost/private targets."""
    text = str(command.params).lower()
    blocked = ("127.0.0.1", "localhost", "169.254.169.254", "0.0.0.0")
    if any(host in text for host in blocked):
        return RuleResult("ssrf_protection", "deny", "ssrf_private_target_detected")
    return RuleResult("ssrf_protection", "allow")
