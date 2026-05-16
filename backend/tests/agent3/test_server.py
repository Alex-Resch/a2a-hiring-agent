import json
from datetime import datetime, timezone
import pytest
from typing import cast

from a2a.server.agent_execution import RequestContext
from a2a.server.events import EventQueue
from agents.agent_3_email_agent import server
from agents.agent_3_email_agent.state import EmailSent, FreeSlot, BusySlot


class DummyContext:
    def __init__(self, user_input):
        self._user_input = user_input

    def get_user_input(self):
        return self._user_input


class DummyEventQueue:
    def __init__(self):
        self.events = []

    async def enqueue_event(self, event):
        self.events.append(event)


@pytest.mark.anyio
async def test_executor_phase1(monkeypatch):
    """Serializes phase 1 results with free and busy slots."""
    slot = FreeSlot(
        start=datetime(2026, 5, 15, 9, 0, tzinfo=timezone.utc),
        end=datetime(2026, 5, 15, 10, 0, tzinfo=timezone.utc),
    )
    busy = BusySlot(
        start=datetime(2026, 5, 15, 11, 0, tzinfo=timezone.utc),
        end=datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc),
    )

    monkeypatch.setattr(server, "new_agent_text_message", lambda text: {"text": text})
    monkeypatch.setattr(
        server.calendar_phase1_app,
        "invoke",
        lambda _payload: {"free_slots": [slot], "busy_slots": [busy]},
    )

    executor = server.CalendarAgentExecutor()
    context = DummyContext(user_input=json.dumps({"selected_profiles": []}))
    queue = DummyEventQueue()

    await executor.execute(
        cast(RequestContext, cast(object, context)),
        cast(EventQueue, cast(object, queue)),
    )

    payload = json.loads(queue.events[0]["text"])
    assert payload["free_slots"][0]["start"].startswith("2026-05-15T09:00:00")


@pytest.mark.anyio
async def test_executor_phase2(monkeypatch):
    """Serializes phase 2 results with events and emails."""
    sent = [EmailSent(profile="octo", status="sent")]
    monkeypatch.setattr(server, "new_agent_text_message", lambda text: {"text": text})
    monkeypatch.setattr(
        server.calendar_phase2_app,
        "invoke",
        lambda _payload: {"created_events": [{"id": "1"}], "emails_sent": sent},
    )

    executor = server.CalendarAgentExecutor()
    context = DummyContext(
        user_input=json.dumps({"selected_slot": {"start": "x", "end": "y"}})
    )
    queue = DummyEventQueue()

    await executor.execute(
        cast(RequestContext, cast(object, context)),
        cast(EventQueue, cast(object, queue)),
    )

    payload = json.loads(queue.events[0]["text"])
    assert payload["created_events"][0]["id"] == "1"
    assert payload["emails_sent"][0]["status"] == "sent"


@pytest.mark.anyio
async def test_executor_cancel_raises():
    """Rejects cancel requests with an exception."""
    executor = server.CalendarAgentExecutor()
    context = DummyContext(user_input="")
    queue = DummyEventQueue()

    with pytest.raises(Exception):
        await executor.cancel(
            cast(RequestContext, cast(object, context)),
            cast(EventQueue, cast(object, queue)),
        )
