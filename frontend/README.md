# A2A Hiring Agent Frontend

Short description
This repository contains the frontend for an AI-assisted hiring workflow. The UI lets users define search criteria, starts a multi-step agent pipeline, shows ranked candidate profiles, and offers interview scheduling via free calendar slots. The backend is not part of this repo.

## Product idea in 30 seconds

- You define tech stack, domain, location, and seniority.
- Agent 1 searches GitHub for matching profiles.
- Agent 2 evaluates and ranks the top candidates.
- You select candidates and request free interview slots.
- Optional: Agent 3 schedules the interview.

## Features

- Multi-step search form with tabs (Tech Stack, Domain & Location, Experience, Filters)
- Live status updates via streaming responses (Agent 1/2/3 progress)
- Results list with score ring, sub-scores, strengths/weaknesses, and reasoning
- Candidate selection and scheduling flow with config modal
- Tailwind/DaisyUI styling and compact layout

## Tech stack

- React 19 + TypeScript
- Vite
- React Router
- React Hook Form
- Tailwind CSS + DaisyUI
- lucide-react icons

## Requirements

- Node.js (LTS recommended)
- A running backend at `http://localhost:8000`

## Local setup

```bash
npm install
npm run dev
```

## Backend contract (expected)

The UI expects streaming responses in the format `data: {json}` (SSE-like).
The base URL is currently hardcoded in `src/shared/functions.ts`.

- `POST /search`
    - Request: `SearchFormData`
    - Response (streaming): `StreamResponse` with `status` and `scored_profiles`

- `POST /calendar/slots`
    - Request: `CalendarPhase1Request`
    - Response (streaming): `StreamResponse` with `status` and `free_slots`

- `POST /calendar/schedule`
    - Request: `CalendarPhase2Request`
    - Response (streaming): `StreamResponse` with `status`

Example streaming chunk:

```text
data: {"status":"Agent 1 is searching..."}
```

Key models are defined in `src/shared/models.ts` and `src/shared/types.ts`.

## Key project areas

- `src/pages/mainPage/MainPage.tsx`: search form and agent status
- `src/pages/resultsPage/ResultsPage.tsx`: ranking and selection
- `src/pages/resultsPage/FreeSlotsModal.tsx`: slot selection
- `src/shared/functions.ts`: `streamFetch` SSE parsing

## Backend

Be sure to run the backend as the README.md file says in this repo backend folder: [`../backend/README.md`](../backend/README.md).

## Known limitation (showcase)

In `src/pages/resultsPage/useSetFreeSlot.ts`, `selectedProfiles` is currently replaced with mock data. For real end-to-end demos, remove this or adapt it to the backend.

## Scripts

```bash
npm run dev
npm run build
npm run preview
npm run lint
```

## Contributing

PRs and issues are welcome. Please describe the problem you are solving and how it was tested.

## License

No license specified. If you want this to be open source, add an appropriate license file.
