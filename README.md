# a2a-hiring-agent

A multi-agent hiring assistant built on the [A2A (Agent2Agent) protocol](https://github.com/a2aproject/a2a-python). Three independent agents work together to find developers on GitHub, screen them with an LLM and schedule interviews — each agent runs as its own service and is called by an orchestrator over A2A.

## What it does

1. **Search** – You describe the profile you are looking for (languages, location, minimum public repos, …). Agent 1 searches GitHub and collects profile, repository and commit details.
2. **Screen** – Agent 2 scores every candidate with an LLM and returns a structured assessment.
3. **Schedule** – For the candidates you pick, Agent 3 checks your Google Calendar for free slots, creates the interview event and sends the invitation via Gmail.

Progress and results are streamed to a React frontend via Server-Sent Events.

## Architecture

```
React frontend ──SSE──▶ Orchestrator (FastAPI, :8000)
                              │  A2A
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   Agent 1 (:8001)     Agent 2 (:8002)     Agent 3 (:8003)
   GitHub search       LLM screening       Calendar + Gmail
```

| Component | Responsibility | Built with |
|---|---|---|
| Orchestrator | Coordinates the agents, streams progress | FastAPI, A2A client, SSE |
| Agent 1 – GitHub Searcher | Finds users and fetches profile, repo and commit data | LangGraph, GitHub API |
| Agent 2 – Screener | Scores candidates, structured output | LangGraph, LiteLLM, Instructor |
| Agent 3 – Calendar/Email | Finds free slots, books the interview, sends the invite | LangGraph, Google Calendar API, Gmail API |
| Frontend | Search form, candidate list, slot picker | React, TypeScript, Vite, Tailwind CSS |

Each agent is a LangGraph graph exposed as an A2A server, so agents can be replaced or reused independently.

## Getting started

Requirements: Python 3.11+, Node.js, a GitHub token, an LLM API key and a Google OAuth client for Calendar and Gmail.

```sh
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
python auth.py            # one-time Google OAuth flow, creates token.json

# each in its own terminal
python agents/agent_1_github_searcher/server.py
python agents/agent_2_screener/server.py
python agents/agent_3_email_agent/server.py
uvicorn main:app --reload --port 8000
```

```sh
cd frontend
npm install
npm run dev
```

Configuration (`.env`), the SSE API and current limitations are documented in [backend/README.md](backend/README.md).

## Tests

```sh
cd backend
pytest
```

Unit tests cover each agent, the orchestrator and the API.

## Notes

- `credentials.json`, `token.json` and `.env` contain secrets and must never be committed.
- The GitHub search is intentionally shallow (few users, one repo each) to stay within API rate limits.
