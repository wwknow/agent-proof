# Security Policy

Please report suspected vulnerabilities privately before opening a public issue.

This MVP is experimental. Its local HMAC mode does not provide strong verifier/operator separation, and replay persistence is intentionally outside the minimal local demo. Production deployments should use isolated verification, managed key material, explicit freshness/replay controls, and an independent review of rule semantics.
