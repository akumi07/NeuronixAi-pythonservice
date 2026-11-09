# NeuronixAI AI service

Python 3.12 service (FastAPI + LangGraph) for NeuronixAI. A LangGraph router sends document questions to a
"knowledge" node and everything else to a "general" node. Answers are placeholders for now (no LLM calls).

## Related repos
- Backend (Java, Spring Boot, owns RAG): https://github.com/akumi07/NeuronixAI, locally `D:\Neuronix\backend`
- Frontend: https://github.com/akumi07/NeuronixAi-frontend, locally `D:\Neuronix\frontend\NeuronixAi-frontend`
- The Java <-> Python contract lives in the backend repo under `docs/contracts/`. Change it there first, never only here.

## Commands
```
uv sync                                   # install deps into .venv
uv run uvicorn app.main:app --port 8001   # run (GET /health)
uv run pytest -q                          # tests
uv run ruff check .                       # lint
uv run ruff format .                      # format
```
If `uv` is not on PATH, use `py -3.12 -m uv ...`.

## Layout
- `app/main.py` – FastAPI app, `GET /health` -> `{"status": "ok"}`
- `app/graph.py` – LangGraph graph: router -> knowledge | general
- `tests/` – tests for `/health` and both graph routes

## NeuronixAI rules
- One ticket, one branch, one PR: feature/S1-02-short-name.
- Never commit .env, .venv, target/, .DS_Store, keys or tokens.
- Never force-push, rewrite history, or delete shared branches. Never push or merge without asking.
- Flyway: never edit a merged migration; ask for the next V number before creating one.
- Public API contracts don't change without lead approval.
- Python deps only via uv add; commit pyproject.toml and uv.lock together.
- Python never rebuilds RAG; document questions go to the Java RAG API.
- A ticket is done only with evidence: build output, test counts, and anything not run stated.

## Deferred security work (fix before production)
- SEC-01 to SEC-12 from the team plan; the main one is that forgot-password returns an access token.
