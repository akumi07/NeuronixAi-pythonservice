# NeuronixAI AI service

Python 3.12 service built with FastAPI and LangGraph. It routes questions with a small LangGraph graph:
document questions go to the "knowledge" path (which will call the Java RAG API in the backend repo; this
service never rebuilds RAG) and everything else goes to the "general" path. Answers are placeholders for now.

## Requirements
- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## Run
```
uv sync
uv run uvicorn app.main:app --port 8001
```
Health check: `GET http://localhost:8001/health` returns `{"status": "ok"}`.

## Test and lint
```
uv run pytest -q
uv run ruff check .
```

## Layout
- `app/main.py` – FastAPI app (`GET /health`)
- `app/graph.py` – LangGraph graph: router -> knowledge | general
- `tests/` – tests for `/health` and both graph routes

## Rules
- Add dependencies only with `uv add` (dev: `uv add --dev`); commit `pyproject.toml` and `uv.lock` together.
- Never commit `.venv/` or `.env`.
