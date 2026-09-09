FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY packages/agentproof_verifier /app/packages/agentproof_verifier
COPY server /app/server
COPY api /app/api

RUN pip install --no-cache-dir --no-deps /app/packages/agentproof_verifier

EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)"

CMD ["python", "-m", "server.server"]
