Agent Workflow scaffold
======================

Overview
--------

This directory provides a scaffold for a secure, modular chat agent system:

- `auth.py` — JWT-like token creation/verification, simple user store
- `supervisor.py` — intent classification and routing logic
- `agents/` — DomainAgent, EmailAgent, PaymentAgent, ContentAgent (stubs)
- `tools.py` — stateless tool registry and example tools
- `verifier.py` — validates agent/tool outputs
- `memory.py` — in-memory session and long-term memory stubs (replace with a vector DB: Pinecone, Chroma, Milvus, or similar)
- `logger.py` — structured JSON logging
- `app.py` — FastAPI app exposing auth, session, chat and webhook endpoints

Getting started
---------------

Install dependencies (recommended in a virtualenv):

```bash
pip install fastapi uvicorn pydantic
```

Run the server:

```bash
uvicorn workflows.agent_system.app:app --reload --port 8080
```

Next steps (production hardening)
--------------------------------

- Replace the in-memory stores with a proper Postgres + vector DB (Pinecone / Chroma / Milvus).
- Use a real JWT library and rotate secrets via env vars.
- Implement OAuth exchange using real provider endpoints.
- Add webhook signature verification for Stripe and email providers.
- Wire agents to real tools (Stripe SDK, SendGrid, GoDaddy REST API).
- Add OpenTelemetry instrumentation for observability.
