# AgentProof — Reference Verifier

AgentProof is an open-source, experimental reference implementation for verifying AI-agent delegation evidence.

It is intentionally small: the first goal is to let a developer run a command through a verifier, get an explicit allow, deny, or escalate decision, and produce a tamper-evident evidence receipt.

## Why this exists

AI agents increasingly delegate work to tools and other agents.

The security problem is not only whether a token is valid. It is whether an action is still inside the authority that was delegated, and whether that decision can be reconstructed later.

AgentProof provides a small, auditable building block for that problem:

- normalize an agent command
- evaluate pluggable rules
- fail closed on rule errors
- bind the decision to request and runtime context hashes
- emit a tamper-evident evidence receipt
- verify receipt integrity, audience, freshness, and expiry

This repository is a reference MVP for experimentation, development, interoperability, and security testing. It does not claim conformance to a finalized standard.

## Quick Start

### Python

\`\`\`bash
cd packages/agentproof_verifier
python -m pip install -e .
agentproof-verify demo
\`\`\`

Expected output:

\`\`\`text
[ALLOW] verdict=allow valid=True reason=
[DENY] verdict=deny valid=True reason=rce_pattern_detected
\`\`\`

### Node.js

From the repository root:

\`\`\`bash
npm install
npm run demo
\`\`\`

## Verify your own command

Create a file named \`command.json\`:

\`\`\`json
{
  "agent_id": "my-agent",
  "tool": "search_web",
  "params": {
    "query": "example"
  }
}
\`\`\`

Then run:

\`\`\`bash
agentproof-verify verify command.json --secret "demo-secret"
\`\`\`

The verifier returns a receipt containing the decision, hashes, policy/config binding, freshness window, and integrity tag.

## What it verifies

AgentProof focuses on explicit, machine-checkable security decisions:

- agent identity and execution context
- delegated scope
- rule-based security checks
- request and parameter binding
- runtime context binding
- policy/config binding
- receipt integrity
- freshness and expiry
- explicit allow, deny, and escalate outcomes

## Repository layout

\`\`\`text
api/                           OpenAPI definition
docs/                          Design and deployment notes
examples/                      Runnable examples
packages/agentproof_verifier/  Python verifier + CLI
packages/agentproof_sdk_node/  Minimal Node.js SDK primitives
server/                        HTTP verification service
tests/                         Automated tests
vectors/                       Stable verification vectors
.github/                       CI configuration
\`\`\`

## Design principles

1. **Fail closed.** A verifier error is never treated as authorization.
2. **Deterministic inputs.** Canonical JSON and hashes make evidence reproducible.
3. **Explicit decisions.** allow, deny, and escalate are first-class outcomes.
4. **Context-bound evidence.** Receipts bind the decision to request, parameter, runtime, and policy context.
5. **Small reference core.** The implementation is intentionally understandable, auditable, and easy to fork.

## 5-minute security demo

Run the built-in Python demonstration:

\`\`\`bash
cd packages/agentproof_verifier
python -m pip install -e .
agentproof-verify demo
\`\`\`

The demo includes both an allowed command and an intentionally unsafe command so developers can see the verifier distinguish between them.

## Run with Docker

Start the self-hosted verifier service:

\`\`\`bash
cp .env.example .env
docker compose up --build
\`\`\`

Health check:

\`\`\`bash
curl http://localhost:8080/healthz
\`\`\`

Verify a normal command:

\`\`\`bash
curl -s http://localhost:8080/v1/verify \
  -H 'content-type: application/json' \
  -d '{"agent_id":"demo-agent","tool":"search_web","params":{"query":"hello"}}' | jq
\`\`\`

Verify an intentionally unsafe command:

\`\`\`bash
curl -s http://localhost:8080/v1/verify \
  -H 'content-type: application/json' \
  -d '{"agent_id":"demo-agent","tool":"shell_exec","params":{"command":"rm -rf /"}}' | jq
\`\`\`

OpenAPI definition: \`api/openapi.yaml\`

Docker deployment notes: \`docs/docker.md\`

### Docker positioning

The Docker image is a reference verifier and self-test service.

It is intended for local evaluation, CI pipelines, demonstrations, development, and early integrations.

It is not presented as a production security gateway. Before production use, add authentication, authorization, secret management, rate limiting, durable audit storage, isolation, observability, and a deployment-specific trust model.

## Roadmap

- **Level 0:** local signed receipts and stable verification vectors
- **Level 1:** asymmetric receipt signatures and richer bindings
- **Level 2:** isolated verifier process
- **Level 3:** multi-hop delegation chains
- **Level 4:** cross-organization evidence exchange

## Contributing

Bug reports, security findings, compatibility improvements, test vectors, and implementation contributions are welcome.

See \`CONTRIBUTING.md\`.

## Security

Please see \`SECURITY.md\` for security reporting guidance.

## License

Apache-2.0. See \`LICENSE\`.
