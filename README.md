# AgentProof — Reference Verifier

AgentProof is an open-source, experimental reference implementation for verifying **AI-agent delegation evidence**.

It is intentionally small: the first goal is to let a developer run a command through a verifier, get an explicit `allow` / `deny` / `escalate` decision, and produce a tamper-evident evidence receipt.

## Why this exists

AI agents increasingly delegate work to tools and other agents. The security problem is not only whether a token is valid; it is whether an action is still inside the authority that was delegated, and whether that decision can be reconstructed later.

AgentProof provides a small, auditable building block for that problem:

- normalize an agent command
- evaluate pluggable rules
- fail closed on rule errors
- bind the decision to request and runtime context hashes
- emit a signed evidence receipt
- verify receipt integrity, audience, freshness, and expiry

This repository is a **reference MVP**, not a claim of conformance to any finalized standard.

## 5-minute demo

### Python

```bash
cd packages/agentproof_verifier
python -m pip install -e .
agentproof-verify demo
```

Expected output:

```text
[ALLOW] verdict=allow valid=True reason=
[DENY] verdict=deny valid=True reason=rce_pattern_detected
```

### Node.js

```bash
npm install
npm run demo
```

## Verify your own command

```json
{
  "agent_id": "my-agent",
  "tool": "search_web",
  "params": {"query": "example"}
}
```

```bash
agentproof-verify verify command.json --secret "demo-secret"
```

The verifier returns a receipt containing the decision, hashes, policy/config binding, freshness window, and an integrity tag.

## Repository layout

```text
packages/agentproof_verifier/   Python verifier + CLI
packages/agentproof_sdk_node/   Minimal Node.js SDK primitives
examples/                       Runnable examples
vectors/                        Stable verification vectors
docs/                           Design and contribution notes
.github/                        CI and issue templates
```

## Design principles

1. **Fail closed.** A verifier error is never treated as authorization.
2. **Deterministic inputs.** Canonical JSON and hashes make evidence reproducible.
3. **Explicit decisions.** `allow`, `deny`, and `escalate` are first-class outcomes.
4. **Evidence is bound to context.** Receipts include request, parameter, runtime, and policy bindings.
5. **Small reference core.** Keep the verifier understandable enough to audit and fork.

## Roadmap

- Level 0: local signed receipts and stable vectors
- Level 1: asymmetric receipt signatures and richer bindings
- Level 2: isolated verifier process
- Level 3: multi-hop delegation chains
- Level 4: cross-organization evidence exchange

## License

Apache-2.0. See `LICENSE`.

## Run with Docker

The fastest self-hosted path is the built-in verifier service.

```bash
cp .env.example .env
docker compose up --build
```

Then open `http://localhost:8080` or check:

```bash
curl http://localhost:8080/healthz
```

Verify a command:

```bash
curl -s http://localhost:8080/v1/verify \\
  -H 'content-type: application/json' \\
  -d '{"agent_id":"demo-agent","tool":"search_web","params":{"query":"hello"}}' | jq
```

An intentionally unsafe example:

```bash
curl -s http://localhost:8080/v1/verify \\
  -H 'content-type: application/json' \\
  -d '{"agent_id":"demo-agent","tool":"shell_exec","params":{"command":"rm -rf /"}}' | jq
```

OpenAPI: `api/openapi.yaml`.

### Docker positioning

This image is a **reference verifier / self-test service**. It is designed for local evaluation, CI, demos, and early integrations. It is not presented as a production security gateway. Before production use, add authentication, authorization, secret management, rate limiting, audit storage, isolation, observability, and a deployment-specific trust model.

## Service API

The HTTP reference service is documented in `api/openapi.yaml`. Deployment notes are in `docs/docker.md`.
