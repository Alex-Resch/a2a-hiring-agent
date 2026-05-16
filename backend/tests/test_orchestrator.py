import json
from datetime import datetime, timezone

import pytest

import orchestrator
from agents.agent_3_email_agent.state import FreeSlot
from shared.models import CalendarPhase1Request, SearchRequest, SelectedProfile


class DummyText:
    def __init__(self, text):
        self.text = text


class DummyPart:
    def __init__(self, text):
        self.root = DummyText(text)


class DummyResult:
    def __init__(self, text):
        self.parts = [DummyPart(text)]


class DummyResponse:
    def __init__(self, text):
        self.root = type("Root", (), {"result": DummyResult(text)})()


class DummyResolver:
    def __init__(self, *args, **kwargs):
        pass

    async def get_agent_card(self):
        return object()


class DummyClient:
    responses: list[DummyResponse] = []

    def __init__(self, *args, **kwargs):
        pass

    async def send_message(self, _request):
        if not DummyClient.responses:
            raise AssertionError("No queued response")  # pragma: no cover
        return DummyClient.responses.pop(0)


class FailingClient(DummyClient):
    async def send_message(self, _request):
        raise RuntimeError("boom")


async def collect_events(gen):
    return [event async for event in gen]


@pytest.fixture(autouse=True)
def patch_a2a(monkeypatch):
    DummyClient.responses = []
    monkeypatch.setattr(orchestrator, "A2ACardResolver", DummyResolver)
    monkeypatch.setattr(orchestrator, "A2AClient", DummyClient)


@pytest.fixture
def slot():
    return FreeSlot(
        start=datetime(2026, 5, 15, 9, 0, tzinfo=timezone.utc),
        end=datetime(2026, 5, 15, 10, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def profiles():
    return [SelectedProfile(username="octo", email="o@e.com")]


@pytest.mark.anyio
async def test_run_success():
    """Runs the orchestrator happy path and checks events."""
    raw_profiles = [{"name": "octo", "email": "octo@example.com"}]
    scores = [{"name": "octo", "overall_score": 90}]
    DummyClient.responses = [
        DummyResponse(json.dumps(raw_profiles)),
        DummyResponse(json.dumps(scores)),
    ]

    events = await collect_events(orchestrator.run(SearchRequest()))

    assert events[0]["status"].startswith("Agent 1")
    assert events[1]["profiles"] == raw_profiles
    assert events[2]["status"].startswith("Agent 2")
    assert events[3]["scored_profiles"] == scores


@pytest.mark.anyio
async def test_run_handles_invalid_json():
    """Emits error when Agent 1 returns invalid JSON."""
    DummyClient.responses = [DummyResponse("not-json")]

    events = await collect_events(orchestrator.run(SearchRequest()))

    assert events[-1]["status"] == "Error"
    assert "Agent 1 failed" in events[-1]["error"]


@pytest.mark.anyio
async def test_run_handles_agent2_invalid_json():
    """Emits error when Agent 2 returns invalid JSON."""
    DummyClient.responses = [
        DummyResponse(json.dumps([{"name": "octo", "email": "octo@example.com"}])),
        DummyResponse("not-json"),
    ]

    events = await collect_events(orchestrator.run(SearchRequest()))

    assert events[-1]["status"] == "Error"
    assert "Agent 2 failed" in events[-1]["error"]


@pytest.mark.anyio
async def test_run_calendar_phase1_contract(profiles):
    """Validates calendar phase 1 response contract."""
    payload = {
        "free_slots": [{"start": "2026-01-01T09:00:00+00:00"}],
        "busy_slots": [{"start": "2026-01-01T10:00:00+00:00"}],
    }
    DummyClient.responses = [DummyResponse(json.dumps(payload))]

    events = await collect_events(
        orchestrator.run_calendar_phase1(
            CalendarPhase1Request(selected_profiles=profiles)
        )
    )

    assert events[0]["status"].startswith("Agent 3")
    assert "free_slots" in events[-1]
    assert "busy_slots" in events[-1]


@pytest.mark.anyio
async def test_run_calendar_phase1_handles_invalid_json(profiles):
    """Emits error when calendar agent returns invalid JSON."""
    DummyClient.responses = [DummyResponse("not-json")]

    events = await collect_events(
        orchestrator.run_calendar_phase1(
            CalendarPhase1Request(selected_profiles=profiles)
        )
    )

    assert events[-1]["status"] == "Error"
    assert "Agent 3 failed" in events[-1]["error"]


@pytest.mark.anyio
async def test_run_calendar_phase2_contract(profiles, slot):
    """Validates calendar phase 2 response contract."""
    DummyClient.responses = [DummyResponse("{}")]

    events = await collect_events(orchestrator.run_calendar_phase2(profiles, slot))

    assert events[0]["status"].startswith("Agent 3")
    assert events[-1]["status"] == "Done"


@pytest.mark.anyio
async def test_run_calendar_phase2_handles_send_failure(monkeypatch, profiles, slot):
    """Emits error when calendar agent send fails."""
    monkeypatch.setattr(orchestrator, "A2AClient", FailingClient)

    events = await collect_events(orchestrator.run_calendar_phase2(profiles, slot))

    assert events[-1]["status"] == "Error"
    assert "Agent 3 failed" in events[-1]["error"]
