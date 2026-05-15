import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from orchestrator import run, run_calendar_phase1, run_calendar_phase2
from shared.models import SearchRequest, CalendarPhase1Request, CalendarPhase2Request


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def event_stream(request):
    """Stream events from the main search orchestrator as SSE."""
    async for event in run(request):
        yield f"data: {json.dumps(event)}\n\n"


@app.post("/search")
async def search(request: SearchRequest):
    """Start profile search and return an SSE stream."""
    return StreamingResponse(event_stream(request), media_type="text/event-stream")


@app.post("/calendar/slots")
async def calendar_slots(request: CalendarPhase1Request):
    """Stream available interview slots for selected profiles."""

    async def stream():
        async for event in run_calendar_phase1(request):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/calendar/schedule")
async def calendar_schedule(request: CalendarPhase2Request):
    """Schedule interviews for a chosen slot and stream status."""

    async def stream():
        async for event in run_calendar_phase2(
            request.selected_profiles,
            request.selected_slot,
        ):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
