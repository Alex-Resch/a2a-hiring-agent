# A2A Hiring Agent Frontend

This contains the frontend for an AI-assisted Github hiring workflow. The UI lets users define search criteria, starts a multi-step agent pipeline, shows ranked candidate profiles, and offers interview scheduling via free calendar slots.

## Product idea in 30 seconds

- You define tech stack, domain, location, and seniority.
- Agent 1 searches GitHub for matching profiles.
- Agent 2 evaluates and ranks the top candidates.
- You select candidates and you can give permission to the programm so it connects to your google calendar to see your free slots.
- Agent 3 schedules the interview and send inventation emails to the selected candidates if their email is public.

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

```bas
npm install
npm run dev
```

## Backend

Be sure to run the backend as the README.md file says in this repo backend folder: [`../backend/README.md`](../backend/README.md).

## Known limitation (showcase)

In `src/pages/resultsPage/useSetFreeSlot.ts`, `selectedProfiles` is currently replaced with mock data. For real end-to-end demos, remove this.
