# Docker deployment

AgentProof ships a small self-hosted HTTP verifier. It is intentionally dependency-free at runtime and packaged into a Python slim image.

## Local

```bash
cp .env.example .env
docker compose up --build
```

Endpoints:

- `GET /healthz` — liveness/health
- `GET /v1/info` — verifier metadata and config hash
- `POST /v1/verify` — evaluate a command and return a receipt + verification result

## Production hardening

The reference image is not a hardened multi-tenant security gateway. Put it behind your own authentication and network controls. Replace the demo secret, use an external secret manager, restrict ingress, add rate limits, persist evidence in your own controlled store, and define the trust policy for your deployment.
