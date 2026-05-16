import httpx
import pytest

import main
from tests.conftest import extract_sse_events


@pytest.mark.anyio
async def test_search_streams_events(monkeypatch):
    """Streams search SSE events and validates payloads."""

    async def fake_run(_request):
        yield {"status": "Agent 1 is searching GitHub profiles..."}
        yield {"status": "Done", "scored_profiles": [{"name": "octo"}]}

    monkeypatch.setattr(main, "run", fake_run)

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/search",
            json={"languages": ["python"], "locations": ["germany"]},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    events = extract_sse_events(response.text)
    assert events[0]["status"].startswith("Agent 1")
    assert events[-1]["scored_profiles"][0]["name"] == "octo"


@pytest.mark.anyio
async def test_calendar_slots_streams_events(monkeypatch):
    """Streams calendar slots SSE events and validates payloads."""

    async def fake_run(_request):
        yield {"status": "Agent 3 is checking calendar..."}
        yield {
            "status": "Free slots found",
            "free_slots": [{"start": "2026-01-01T09:00:00+00:00"}],
            "busy_slots": [],
        }

    monkeypatch.setattr(main, "run_calendar_phase1", fake_run)

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/calendar/slots",
            json={"selected_profiles": [{"username": "octo", "email": "o@e.com"}]},
        )

    assert response.status_code == 200
    events = extract_sse_events(response.text)
    assert events[0]["status"] == "Agent 3 is checking calendar..."
    assert "free_slots" in events[-1]


@pytest.mark.anyio
async def test_calendar_schedule_streams_events(monkeypatch):
    """Streams calendar schedule SSE events and validates payloads."""

    async def fake_run(_profiles, _slot):
        yield {"status": "Agent 3 is scheduling appointment..."}
        yield {"status": "Done"}

    monkeypatch.setattr(main, "run_calendar_phase2", fake_run)

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/calendar/schedule",
            json={
                "selected_profiles": [{"username": "octo", "email": "o@e.com"}],
                "selected_slot": {
                    "start": "2026-05-15T09:00:00+00:00",
                    "end": "2026-05-15T10:00:00+00:00",
                },
            },
        )

    assert response.status_code == 200
    events = extract_sse_events(response.text)
    assert events[0]["status"].startswith("Agent 3")
    assert events[-1]["status"] == "Done"
