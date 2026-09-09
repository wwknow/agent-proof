# AgentProof — Reference Verifier

Open-source reference verifier for AI-agent delegation evidence.

> Can this agent perform this action within the authority it was given?

AgentProof evaluates an agent command, returns an explicit allow, deny, or escalate decision, and produces tamper-evident verification evidence.

## Try it in 30 seconds

Clone the repository:

    git clone https://github.com/wwknow/agent-proof.git
    cd agent-proof

Install the verifier:

    cd packages/agentproof_verifier
    python3 -m pip install -e .

Run the built-in security demo:

    agentproof-verify demo

Expected result:

    [ALLOW] verdict=allow valid=True reason=
    [DENY] verdict=deny valid=True reason=rce_pattern_detected

Test the included safe example:

    agentproof-verify verify ../../examples/quickstart/allow.json --secret "demo-secret"

Expected:

    verdict: allow

Test the included unsafe example:

    agentproof-verify verify ../../examples/quickstart/deny.json --secret "demo-secret"

Expected:

    verdict: deny
    block_reason: rce_pattern_detected

These examples are intentionally included so a new developer can clone the repository and observe both an allowed and a blocked action without creating any files.

## What is AgentProof?

AI agents increasingly delegate work to tools and other agents.

Authentication alone does not answer an important security question:

> Is this specific action still inside the authority that was delegated?

AgentProof provides a small, auditable reference implementation for evaluating that decision and producing evidence that can be checked later.

## What it verifies

- agent identity and execution context
- delegated execution scope
- pluggable security rules
- request and parameter bindings
- runtime context bindings
- policy/config bindings
- receipt integrity
- freshness and expiry
- explicit allow, deny, and escalate outcomes

## Test your own command

Create command.json:

    {
      "agent_id": "my-agent",
      "tool": "search_web",
      "params": {
        "query": "example"
      }
    }

Verify it:

    agentproof-verify verify command.json --secret "demo-secret"

The verifier returns evidence containing the decision, hashes, policy/config binding, freshness window, and integrity tag.

## Why this matters

Modern agent systems can look like:

    User
      |
      v
    Agent A
      |
      +---- delegates ----> Agent B
                              |
                              +---- calls ----> Tool / API
                                                  |
                                                  v
                                               Action

The security boundary is no longer only authentication.

The system also needs to answer:

- Who delegated the action?
- What authority was delegated?
- Was that authority exceeded?
- Can the decision be reconstructed later?
- Can another verifier independently validate the evidence?

AgentProof is a reference building block for those checks.

## Repository layout

    api/                           OpenAPI definition
    docs/                          Design and deployment notes
    examples/                      Runnable examples
    packages/agentproof_verifier/  Python verifier + CLI
    packages/agentproof_sdk_node/  Minimal Node.js SDK primitives
    server/                        HTTP verification service
    tests/                         Automated tests
    vectors/                       Stable verification vectors
    .github/                       CI configuration

## Design principles

1. Fail closed. A verifier error is never treated as authorization.
2. Deterministic inputs. Canonical JSON and hashes make evidence reproducible.
3. Explicit decisions. allow, deny, and escalate are first-class outcomes.
4. Context-bound evidence. Receipts bind the decision to request, parameter, runtime, and policy context.
5. Small reference core. The verifier is intentionally understandable, auditable, and easy to fork.

## Node.js SDK

A minimal Node.js implementation is included for integrations that need AgentProof-compatible evidence primitives.

From the repository root:

    npm install
    npm run demo

## Run with Docker

Start the self-hosted verification service:

    cp .env.example .env
    docker compose up --build

Health check:

    curl http://localhost:8080/healthz

Verify an example request:

    curl -s http://localhost:8080/v1/verify -H "content-type: application/json" -d '{"agent_id":"demo-agent","tool":"search_web","params":{"query":"hello"}}'

OpenAPI definition: api/openapi.yaml

Deployment notes: docs/docker.md

### Docker positioning

The Docker image is a reference verifier / self-test service.

It is intended for local evaluation, CI pipelines, demonstrations, development, and early integrations.

It is not presented as a production security gateway. Production deployments should add authentication, authorization, secret management, rate limiting, durable audit storage, isolation, observability, and a deployment-specific trust model.

## Roadmap

- Level 0: local signed receipts and stable verification vectors
- Level 1: asymmetric receipt signatures and richer bindings
- Level 2: isolated verifier process
- Level 3: multi-hop delegation chains
- Level 4: cross-organization evidence exchange

## Contributing

Bug reports, security findings, compatibility improvements, test vectors, and implementation contributions are welcome.

See CONTRIBUTING.md.

## Security

Please see SECURITY.md for security reporting guidance.

## Status

Experimental reference implementation — v0.1.x

This project is intended for development, security testing, interoperability, and community experimentation.

It is not a production security gateway and should not be treated as one without an appropriate deployment-specific security review.

## License

Apache-2.0. See LICENSE.
