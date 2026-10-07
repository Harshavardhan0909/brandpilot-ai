# BrandPilot AI — Agentic Branded Content Studio

A learning-focused production-style prototype that turns brand guidelines and a campaign brief into brand-aware marketing content.

## What it demonstrates

- FastAPI REST API
- SQLite persistence
- PDF/text brand-guideline ingestion
- Lightweight RAG retrieval using TF-IDF (no paid API required)
- Provider abstraction for image generation
- Rule-based brand compliance evaluation
- Revision workflow with bounded retries
- Streamlit demo UI
- MCP-style tool layer for future AI-client integration

## Quick start

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the API.

In another terminal:

```bash
streamlit run frontend/streamlit_app.py
```

## Demo flow

1. Create a brand with `POST /brands`.
2. Add a guideline document with `POST /brands/{brand_id}/guidelines`.
3. Create a campaign with `POST /campaigns`.
4. Run it with `POST /campaigns/{campaign_id}/run`.
5. Inspect the generated content and compliance score.

The default image provider is a deterministic mock provider, so the project runs without image-generation credentials. Replace it later with a real provider through `app/providers/image_provider.py`.

## Project structure

```text
app/
  api/          HTTP routes
  agents/       Campaign workflow
  database/     SQLite schema and repositories
  providers/    LLM/image provider seams
  rag/          Guideline ingestion and retrieval
  schemas/      Request/response models
frontend/       Streamlit demo
data/           Sample guideline text
tests/          Automated tests
```

## Design decisions

This is intentionally an MVP. The workflow is explicit and bounded rather than an uncontrolled autonomous agent. RAG retrieval, content planning, image generation and evaluation are separate seams so each can be tested and replaced independently.

## Tests

```bash
pytest -q
ruff check .
```

## Roadmap

- Replace TF-IDF with ChromaDB or pgvector
- Add LangGraph orchestration
- Add a real image-generation provider adapter
- Add Redis/Celery for long jobs
- Add authentication, object storage and observability
- Add a full MCP server transport
