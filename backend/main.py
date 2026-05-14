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
    async for event in run(request):
        yield f"data: {json.dumps(event)}\n\n"


@app.post("/search")
async def search(request: SearchRequest):
    return StreamingResponse(event_stream(request), media_type="text/event-stream")


@app.post("/calendar/slots")
async def calendar_slots(request: CalendarPhase1Request):
    async def stream():
        async for event in run_calendar_phase1(request.selected_profiles):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/calendar/schedule")
async def calendar_schedule(request: CalendarPhase2Request):
    async def stream():
        async for event in run_calendar_phase2(
            request.selected_profiles,
            request.selected_slot,
            request.busy_slots,
            request.free_slots,
        ):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
