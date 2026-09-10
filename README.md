# AgentProof

**AgentProof by WWKnow**

**Open-source evidence verification for AI agent actions.**

AgentProof is a lightweight, self-hosted reference verifier for AI-agent actions.

It evaluates an agent's proposed tool action, returns an explicit **allow / deny / escalate** decision, and produces a tamper-evident evidence receipt that can be inspected and verified later.

The core idea is simple:

> AI-agent actions should not only execute — the decision to allow, deny, or escalate them should produce verifiable evidence.

AgentProof is currently an **experimental open-source reference implementation** intended for developers, researchers, agent-framework authors, and security teams exploring verifiable AI-agent execution.

---

## Why AgentProof?

AI agents increasingly call tools that can:

- execute shell commands
- access internal or external URLs
- modify files
- call APIs
- interact with databases
- trigger business workflows
- invoke other agents

Traditional application logs tell you what happened after execution.

AgentProof focuses on a different question:

> **What evidence existed when the action was evaluated, what decision was made, and can that decision record still be verified afterward?**

A typical flow looks like this:

```text
AI Agent
   |
   | proposed tool action
   v
AgentProof Verifier
   |
   +--> evaluate rules / evidence
   |
   +--> allow
   +--> deny
   +--> escalate
   |
   v
Evidence Receipt
   |
   v
Tool Execution / Enforcement
```

This makes AgentProof useful as a small building block for agent runtimes, tool gateways, policy systems, audit pipelines, and future multi-agent evidence infrastructure.

---

## Current release

**v0.1.1**

The current release includes:

- Python verification core
- `agentproof-verify` CLI
- Node.js SDK/example integration
- HTTP verification service
- self-hosted Web Verifier
- Docker support
- OpenAPI definition
- built-in RCE protection
- built-in SSRF protection
- allow / deny / escalate decisions
- evidence receipt generation
- HMAC-SHA256 receipt integrity verification
- CI tests and Docker smoke testing
- basic test vectors

AgentProof is intentionally small at this stage.

The goal of v0.1.x is to validate the verification and evidence workflow with real integrations before expanding the architecture.

---

# 5-minute quickstart

## Python

Clone the repository:

```bash
git clone https://github.com/wwknow/agent-proof.git
cd agent-proof
```

Install the verifier:

```bash
cd packages/agentproof_verifier
python -m pip install -e .
```

Run the built-in demo:

```bash
agentproof-verify demo
```

The demo sends example agent actions through the verifier and returns explicit verification decisions together with evidence receipts.

---

## Node.js

From the repository root:

```bash
npm install
npm run demo
```

The Node.js example demonstrates how an agent-side application can send actions through the AgentProof verification workflow.

---

# Web Verifier

AgentProof v0.1.1 includes a lightweight self-hosted browser interface.

From the repository root, start the reference server:

```bash
python server/server.py
```

Then open:

```text
http://127.0.0.1:8080/
```

The Web Verifier lets you submit example agent actions and inspect the resulting decision.

For example:

```text
search_web
```

with a normal query can produce:

```text
allow
```

while an obviously dangerous shell action such as:

```text
rm -rf /
```

can produce:

```text
deny
```

with a block reason such as:

```text
rce_pattern_detected
```

The Web Verifier is self-hosted and does not require an external AgentProof service.

---

# Verify an AI-agent action

A verification request represents an action an agent wants to perform.

Example:

```json
{
  "agent_id": "demo-agent",
  "tool": "search_web",
  "params": {
    "query": "open source AI agent security"
  },
  "trace_id": "demo-trace"
}
```

AgentProof evaluates the request and produces one of three verdicts:

```text
allow
deny
escalate
```

### allow

The available evidence and configured rules permit the action.

### deny

One or more rules reject the action.

### escalate

The action requires additional evidence, policy evaluation, or human/system review before execution.

---

# Example: blocked action

An action such as:

```json
{
  "agent_id": "demo-agent",
  "tool": "shell_exec",
  "params": {
    "command": "rm -rf /"
  },
  "trace_id": "dangerous-example"
}
```

can be rejected by the built-in RCE protection rule.

Example result:

```text
verdict: deny
block_reason: rce_pattern_detected
```

The reference implementation also includes basic SSRF protection for obvious localhost, private-network, and metadata-service targets.

The built-in rules are intentionally small and are examples of enforcement logic rather than a complete production security policy.

---

# Evidence receipts

Every verification decision can produce an evidence receipt.

A receipt can contain fields such as:

```text
evidence_version
verdict
timestamp
tool
params_hash
rule_summary
verified_at
block_reason
request_hash
response_hash
runtime_context_hash
action
config_hash
issuer
audience
nonce
sequence
issued_at
expires_at
max_clock_skew
receipt
```

The purpose of the receipt is to bind the verification decision to important execution context.

For example:

```text
request
   |
   +--> request_hash
   |
runtime context
   |
   +--> runtime_context_hash
   |
policy configuration
   |
   +--> config_hash
   |
   v
verification decision
   |
   v
evidence receipt
```

This allows another component to check whether the evidence record has been modified and whether it corresponds to the expected verification context.

---

# Receipt integrity

AgentProof v0.1.1 uses **HMAC-SHA256** to protect receipt integrity.

The current implementation therefore provides a **tamper-evident integrity mechanism between parties that share the configured secret**.

It should not be interpreted as:

- an asymmetric digital signature
- cryptographic non-repudiation
- proof that a specific independent organization signed the receipt

Those properties require stronger trust separation and asymmetric cryptography.

Future versions may add signing mechanisms such as **Ed25519** for cross-domain verification and stronger issuer separation.

---

# Fail-closed verification

AgentProof follows a fail-closed design principle.

A verification failure should not silently become permission to execute an action.

Conceptually:

```text
no valid verification
        |
        v
do not automatically execute
```

Rule evaluation failures are also treated conservatively by the reference verifier.

This is important for agent systems because verification infrastructure should not become an accidental bypass path.

---

# HTTP API

The reference server exposes:

```text
GET  /healthz
GET  /v1/info
POST /v1/verify
GET  /
GET  /app.js
```

Check health:

```bash
curl http://127.0.0.1:8080/healthz
```

Check service information:

```bash
curl http://127.0.0.1:8080/v1/info
```

Example verification request:

```bash
curl -X POST http://127.0.0.1:8080/v1/verify -H "Content-Type: application/json" -d '{"agent_id":"demo-agent","tool":"search_web","params":{"query":"open source AI"},"trace_id":"demo-trace"}'
```

Example dangerous request:

```bash
curl -X POST http://127.0.0.1:8080/v1/verify -H "Content-Type: application/json" -d '{"agent_id":"demo-agent","tool":"shell_exec","params":{"command":"rm -rf /"},"trace_id":"dangerous-example"}'
```

The OpenAPI definition is available at:

```text
api/openapi.yaml
```

---

# Docker

AgentProof can also run as a container.

From the repository root:

```bash
docker compose up --build
```

The reference service listens on container port:

```text
8080
```

The Docker configuration supports environment variables including:

```text
AGENTPROOF_SECRET
AGENTPROOF_ISSUER
AGENTPROOF_AUDIENCE
```

See:

```text
docs/docker.md
```

for Docker-specific documentation.

---

# Python verifier

The Python implementation lives in:

```text
packages/agentproof_verifier/
```

It contains the main verification logic, including:

```text
Command
   |
   v
rule evaluation
   |
   v
allow / deny / escalate
   |
   v
receipt generation
   |
   v
receipt verification
```

The package also provides the CLI:

```text
agentproof-verify
```

At this stage the Python package is distributed from the source repository for development and evaluation.

A formal public package-distribution strategy can be introduced separately as the project matures.

---

# Node.js SDK

The Node.js implementation lives in:

```text
packages/agentproof_sdk_node/
```

It provides a lightweight integration path for JavaScript/Node-based AI-agent applications.

The current SDK is part of the repository's development and demonstration workflow.

Formal npm publication is intentionally separate from the v0.1.1 source release.

---

# Built-in rules

AgentProof currently contains lightweight reference rules.

## RCE protection

The built-in RCE rule detects obvious dangerous command patterns such as shell-destructive commands and common direct execution patterns.

Example:

```text
rm -rf /
```

can be denied with:

```text
rce_pattern_detected
```

## SSRF protection

The SSRF rule detects obvious requests targeting locations such as:

```text
localhost
loopback addresses
private network ranges
metadata service targets
```

These rules demonstrate how verification policies can participate in the evidence workflow.

They are not intended to represent comprehensive RCE or SSRF defenses.

---

# Verification model

The reference implementation works conceptually as follows:

```text
Agent / Application
        |
        v
Verification Request
        |
        v
AgentProof
        |
        +-------------------+
        |                   |
        v                   v
   Built-in Rules      Evidence Context
        |                   |
        +---------+---------+
                  |
                  v
          Verification Decision
                  |
          +-------+-------+
          |       |       |
        allow    deny   escalate
                  |
                  v
           Evidence Receipt
                  |
                  v
           Receipt Verification
```

AgentProof is deliberately designed so the verification layer can later be separated from the agent runtime itself.

---

# Repository structure

```text
agent-proof/
├── api/
│   └── openapi.yaml
├── docs/
│   ├── docker.md
│   ├── quickstart.md
│   └── open-source-strategy.md
├── examples/
│   └── basic/
│       └── demo.mjs
├── packages/
│   ├── agentproof_verifier/
│   │   ├── agentproof_verifier/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── agentproof_sdk_node/
│       ├── src/
│       └── package.json
├── server/
│   └── server.py
├── tests/
│   └── test_server.py
├── vectors/
│   └── basic.jsonl
├── web/
│   ├── index.html
│   └── app.js
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── SECURITY.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

# Design principles

## 1. Explicit decisions

Every evaluated action should resolve to an explicit decision:

```text
allow
deny
escalate
```

## 2. Evidence by default

A security decision should produce evidence that can be inspected later.

## 3. Fail closed

Missing or failed verification should not silently become permission to execute.

## 4. Context binding

Receipts should bind important information such as:

```text
request
response
runtime context
configuration
issuer
audience
freshness
```

## 5. Small reference implementation

The implementation is intentionally compact enough for developers to inspect, understand, modify, and integrate.

## 6. Self-hosted first

The core verifier does not require a hosted AgentProof control plane.

## 7. Extensible architecture

The current project is a foundation for future work including richer policy engines, external verification services, stronger cryptography, multi-hop evidence, and interoperability.

---

# Security scope

AgentProof v0.1.1 is an **experimental reference implementation**.

It should not currently be treated as a complete security boundary for high-risk production systems.

Important limitations include:

- built-in RCE detection is intentionally lightweight
- built-in SSRF detection is intentionally lightweight
- policy coverage is not comprehensive
- HMAC requires shared-secret trust
- HMAC does not provide asymmetric-signature semantics
- production authentication and authorization are deployment concerns
- production secret management is outside the current reference implementation
- production isolation, monitoring, rate limiting, and operational hardening require additional work
- integration security depends on the surrounding agent runtime and enforcement architecture

AgentProof is designed to make these areas easier to reason about, not to claim that v0.1.1 solves all of them.

Security issues should be reported according to:

```text
SECURITY.md
```

---

# What AgentProof is not

AgentProof is not currently:

- a hosted SaaS security gateway
- a complete sandbox
- a complete RCE prevention engine
- a complete SSRF firewall
- an autonomous-agent framework
- a replacement for authentication or authorization
- a claim of formal security verification
- a production PKI
- an asymmetric signing infrastructure

It is a reference implementation of an **agent-action verification and evidence workflow**.

---

# Where it can fit

AgentProof can sit between an agent and the tools it wants to invoke.

Examples include:

```text
LLM Agent
   |
AgentProof
   |
Shell / Browser / API / Database
```

or:

```text
Agent Framework
      |
      v
Tool Gateway
      |
      v
AgentProof Verifier
      |
      v
Policy Decision + Evidence
      |
      v
Execution
```

or eventually:

```text
Agent A
   |
Evidence
   |
Agent B
   |
Evidence
   |
External Service
```

The last model requires additional protocol and trust work and is part of the longer-term direction rather than a v0.1.1 production claim.

---

# Roadmap

Development will remain incremental and driven by real integration feedback.

Potential future work includes:

- richer policy and rule interfaces
- user-defined rules
- stronger receipt verification
- Ed25519 receipt signatures
- key rotation
- issuer trust models
- out-of-process verification
- challenge / additional-evidence workflows
- multi-hop evidence propagation
- cross-organization verification
- conformance test vectors
- additional SDKs
- framework adapters
- production deployment guidance
- observability integrations
- external policy-engine integrations

Roadmap items are exploratory and may change.

---

# Project philosophy

AgentProof does not try to build an entire agent platform.

Its focus is narrower:

> **Verify the action, make the decision explicit, and preserve evidence of why that decision was made.**

That narrow scope is intentional.

It allows AgentProof to potentially integrate with many different agent frameworks and execution environments instead of becoming another closed runtime.

---

# Contributing

Contributions and real-world integration feedback are welcome.

See:

```text
CONTRIBUTING.md
```

Useful contributions include:

- new verification rules
- test vectors
- attack cases
- agent-framework integrations
- SDK improvements
- documentation improvements
- receipt-verification tooling
- deployment experiments
- interoperability experiments

One of the most useful early tests is simple:

> Can a developer who has never seen AgentProof clone it, run the demo, verify a safe and unsafe action, and understand the evidence receipt within five minutes?

---

# Open-source status

AgentProof is developed openly as:

**AgentProof by WWKnow**

Repository:

```text
https://github.com/wwknow/agent-proof
```

The `WWKnow` identity is used to distinguish this project from unrelated projects that may also use the name AgentProof.

The project name remains **AgentProof**.

---

# License

See:

```text
LICENSE
```

for the repository license.

---

## AgentProof by WWKnow

**Verify the action. Preserve the evidence.**
