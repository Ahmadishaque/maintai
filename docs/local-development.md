# Local development

## Requirements

- Git
- Docker Desktop
- Docker Compose
- A Gemini API key stored in a local `.env` file

## Start the project

```powershell
git clone https://github.com/Ahmadishaque/maintai.git
cd maintai
Copy-Item .env.example .env
docker compose up --build
```

Add your private Gemini key to `.env` before the LLM milestone. Do not commit `.env`.

Open the frontend at `http://localhost:8501` and the API documentation at `http://localhost:8000/docs`.

PostgreSQL is exposed at `localhost:5433` to avoid conflicting with a local server on port 5432.

## Stop the project

```powershell
docker compose down
```
