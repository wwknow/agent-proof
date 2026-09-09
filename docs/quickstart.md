# Quickstart

## Python

```bash
cd packages/agentproof_verifier
python -m pip install -e .
agentproof-verify demo
```

## Verify JSON

Create `command.json`:

```json
{
  "agent_id": "demo-agent",
  "tool": "search_web",
  "params": {"query": "example"}
}
```

Run:

```bash
agentproof-verify verify command.json --secret demo-secret
```

## Node.js

```bash
npm install
npm run demo
```
