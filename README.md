# MaintAI

MaintAI is a presentable, policy-grounded maintenance intake copilot. A user describes an operational issue in natural language; the application retrieves relevant internal procedures, calls Gemini for schema-constrained extraction and triage, validates the returned policy citations, and stores the full audit record in PostgreSQL.

> The bundled procedures are fictional demonstration data and are not real safety instructions.

## MVP capabilities

- Natural-language maintenance intake through Streamlit
- FastAPI backend with documented create and history endpoints
- Lightweight retrieval over a bundled internal policy library
- Gemini structured output validated with Pydantic
- Equipment, category, symptoms, severity, safety, and missing-field extraction
- Policy-grounded recommended actions with validated policy IDs
- Human-review routing for risk, uncertainty, or incomplete information
- Gemini model, token usage, latency, retrieval evidence, and error logging
- PostgreSQL persistence with SQLAlchemy and Alembic migrations
- Docker Compose local environment, tests, Ruff linting, and GitHub Actions CI

## Request flow

```text
Natural-language report
        |
        v
Keyword policy retrieval
        |
        v
Relevant policy excerpts + report
        |
        v
Gemini structured extraction
        |
        v
Pydantic and citation validation
        |
        +----> human review when required
        |
        v
PostgreSQL audit record
        |
        v
Streamlit triage and history views
```

This is a lightweight retrieval-augmented generation pattern: the model receives only the procedures selected for the current request rather than an entire policy library.

## Technology

- Python 3.11
- FastAPI
- Streamlit
- Gemini API through the Google Gen AI SDK
- Pydantic
- PostgreSQL
- SQLAlchemy and Alembic
- Docker Compose
- Pytest, Ruff, and GitHub Actions

## Run locally

```powershell
git clone https://github.com/Ahmadishaque/maintai.git
cd maintai
Copy-Item .env.example .env
```

Add your private Gemini API key to `.env`:

```env
GEMINI_API_KEY=your_private_key
DATABASE_URL=postgresql+psycopg://maintai:maintai@localhost:5433/maintai
BACKEND_URL=http://localhost:8000
```

Start the complete stack:

```powershell
docker compose up --build
```

Open:

- Frontend: `http://localhost:8501`
- API documentation: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/health`

PostgreSQL is exposed on host port `5433` to avoid conflicting with an existing local server on port `5432`.

## Interview demo

Submit this sample report:

```text
The cooling pump in Building 3 is vibrating heavily and leaking dark fluid near the rear seal. The issue started this morning.
```

MaintAI will display:

- The structured issue category and equipment type
- Extracted symptoms, severity, and confidence
- Missing information and human-review status
- Recommended actions grounded in retrieved procedures
- Validated policy IDs
- Model name, token counts, latency, and retrieved-policy audit metadata

Then open **Request history** to show that both the original input and AI-generated record were persisted.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check backend and database connectivity |
| `POST` | `/api/v1/requests` | Analyze and persist a maintenance request |
| `GET` | `/api/v1/requests` | List recent requests and their audit records |

## Production considerations demonstrated

The LLM is not given direct database write access. Application code controls persistence, validates the structured response, filters unsupported citations, records operational metadata, and routes uncertain or safety-related results to human review. Automated tests do not call Gemini, preventing API usage during CI.
