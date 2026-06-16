# MaintAI

MaintAI is a policy-grounded maintenance intake assistant. It is being built as a production-style example of how an enterprise application can combine natural-language intake, structured data, internal procedures, and auditable LLM calls.

## Current milestone

The application currently supports:

- A Streamlit maintenance intake form
- FastAPI create and list endpoints
- PostgreSQL persistence through SQLAlchemy
- Alembic database migrations
- Docker Compose for local development
- Input validation, health checks, tests, and CI

Gemini-based field extraction and policy retrieval will be added in subsequent milestones.

## Architecture

```text
Streamlit frontend
        |
        v
FastAPI backend
        |
        v
PostgreSQL

Future request flow:
Natural-language issue -> Gemini extraction -> validation -> policy retrieval -> grounded response
```

## Run locally

```powershell
git clone https://github.com/Ahmadishaque/maintai.git
cd maintai
Copy-Item .env.example .env
docker compose up --build
```

Open:

- Frontend: `http://localhost:8501`
- API documentation: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/health`

PostgreSQL is exposed on host port `5433` to avoid conflicting with an existing local PostgreSQL server on port `5432`.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check backend and database connectivity |
| `POST` | `/api/v1/requests` | Create a maintenance request |
| `GET` | `/api/v1/requests` | List recent maintenance requests |

## Development roadmap

1. Persist natural-language maintenance requests
2. Extract structured fields with Gemini
3. Add policy-document ingestion and retrieval
4. Generate grounded recommendations with citations
5. Track token usage, latency, and human-review decisions
