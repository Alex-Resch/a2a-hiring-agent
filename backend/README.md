# A2A Hiring Agent (Backend)

A local multi-agent backend that searches GitHub profiles, scores candidates, and schedules interview slots via Google Calendar and Gmail. It exposes an orchestrator API (SSE) and three A2A agent services.

## Architecture

- **Orchestrator API (FastAPI)**: Streams progress and results via Server-Sent Events (SSE).
- **Agent 1 (GitHub Searcher)**: Searches GitHub users and fetches limited profile/repo/commit details.
- **Agent 2 (Screener)**: Scores profiles using an LLM (Gemini via LiteLLM + Instructor).
- **Agent 3 (Calendar/Email)**: Finds free slots in Google Calendar and sends interview emails.

Default ports:
- Orchestrator: `http://localhost:8000`
- Agent 1: `http://localhost:8001`
- Agent 2: `http://localhost:8002`
- Agent 3: `http://localhost:8003`

## Requirements

- Python `>=3.11`
- GitHub API token
- LLM API key (used by Agent 2)
- Google OAuth credentials for Calendar + Gmail (used by Agent 3)

Create a local `.env` (do not commit it):

```dotenv
GITHUB_TOKEN=your_github_token
LLM_PROVIDER_API_KEY=your_llm_api_key  # e.g. GEMINI_API_KEY
```

Place your Google OAuth client in `credentials.json` (local only). The OAuth flow creates `token.json`. These files contain sensitive credentials and should never be committed.

## Setup

Create a virtual environment and install dependencies:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Generate Google OAuth token (opens a local browser flow):

```sh
python auth.py
```

## Run the services

Start the three agents (each in its own terminal):

```sh
python agents/agent_1_github_searcher/server.py
python agents/agent_2_screener/server.py
python agents/agent_3_email_agent/server.py
```

Start the orchestrator API:

```sh
uvicorn main:app --reload --host localhost --port 8000
```

## API (SSE)

All endpoints stream `text/event-stream` responses with lines like:

```
data: {"status": "...", ...}
```

### `POST /search`
Search GitHub and score candidates.

**Request body**:

```json
{
  "languages": ["python"],
  "locations": ["germany"],
  "min_public_repos": 5,
  "frameworks": [],
  "domains": [],
  "experience_levels": [],
  "availability": [],
  "min_years_experience": 0,
  "active_within_months": 12,
  "min_stars": 0
}
```

**Example**:

```sh
curl -N -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"languages":["python"],"locations":["germany"],"min_public_repos":5}'
```

### `POST /calendar/slots`
Find free calendar slots for selected profiles.

**Request body**:

```json
{
  "selected_profiles": [
    {"username": "octocat", "email": "octocat@example.com"}
  ]
}
```

**Example**:

```sh
curl -N -X POST http://localhost:8000/calendar/slots \
  -H "Content-Type: application/json" \
  -d '{"selected_profiles":[{"username":"octocat","email":"octocat@example.com"}]}'
```

### `POST /calendar/schedule`
Schedule an interview for a chosen slot.

**Request body**:

```json
{
  "selected_profiles": [
    {"username": "octocat", "email": "octocat@example.com"}
  ],
  "selected_slot": {
    "start": "2026-05-15T09:00:00+00:00",
    "end": "2026-05-15T10:00:00+00:00"
  }
}
```

**Example**:

```sh
curl -N -X POST http://localhost:8000/calendar/schedule \
  -H "Content-Type: application/json" \
  -d '{"selected_profiles":[{"username":"octocat","email":"octocat@example.com"}],"selected_slot":{"start":"2026-05-15T09:00:00+00:00","end":"2026-05-15T10:00:00+00:00"}}'
```

## Notes and current limitations

- GitHub query uses all request fields; some are mapped heuristically (keyword search, created-date approximation, and stars qualifier support depends on GitHub user search behavior).
- GitHub fetch is intentionally shallow: first 2 users, 1 repo per user, 1 commit per repo.
- Only profiles with a public email address are kept.
- Calendar availability is computed for the next 7 days, UTC, with work hours 09:00–18:00 and 60-minute slots.
- Agent 2 uses `gemini/gemini-2.5-flash` via LiteLLM + Instructor.

## Local artifacts

`credentials.json` and `token.json` are local-only files. Treat them as secrets and keep them out of version control.
