# AgentBench — AI Evaluation Platform (MVP)

FastAPI backend that benchmarks deterministic baseline strategies against test cases, records per-case accuracy and latency, and stores experiment history in SQLite.

> **Scope:** This is a starter evaluation backend, **not yet a real LLM-agent benchmarking platform**. Real LLM provider integrations, RAG, React, PostgreSQL and multi-step agent evaluation are future work.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. POST the contents of `examples/run.json` to `/experiments`, then GET `/experiments`.

## Docker and tests

```bash
docker compose up --build
python -m pytest -q
```

## Features

- Experiment submission with echo, lowercase and reverse baseline strategies
- Per-case expected/actual comparisons, pass/fail and latency
- Persistent experiment history and detail endpoints
- FastAPI Swagger UI, Docker, unit tests

## Roadmap

- [ ] LLM provider adapters and real agent tasks
- [ ] React/TypeScript dashboard
- [ ] PostgreSQL persistence
- [ ] RAG and tool-use evaluation

Use synthetic/public data only; never commit API keys.

## React dashboard (local)

Run the Python API on port 8000. In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite development server proxies `/api` to FastAPI. The UI submits baseline evaluations and displays history. `app/adapters.py` contains an opt-in OpenAI-compatible chat-completions adapter, but it is **not yet connected to the benchmark API**. Real agent/tool-use evaluation remains future work.

## LLM evaluation (opt-in)

The `/experiments` endpoint now accepts `strategy: "llm"` and a `model` identifier. Set `OPENAI_API_KEY` in the backend environment before running a real request; each test case sends its prompt to the configured chat-completions provider. Example request:

```json
{"name":"provider-smoke-test","strategy":"llm","model":"YOUR_AVAILABLE_MODEL","cases":[{"prompt":"Reply with the word hello","expected":"hello"}]}
```

This requires a valid provider account and may incur API charges. Tests use a mocked provider and require no API key. **Exact-string accuracy is a limited baseline metric, not a reliable evaluation of agent reasoning, tool use, or task completion.** No production provider calls have been verified here.
