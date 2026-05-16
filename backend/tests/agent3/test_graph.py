from datetime import datetime, timezone
from typing import cast

from agents.agent_3_email_agent import graph, nodes
from agents.agent_3_email_agent.state import AgentState, FreeSlot, SelectedProfile


class FakeEventsList:
    def __init__(self, items):
        self._items = items

    def execute(self):
        return {"items": self._items}


class FakeCalendarService:
    def __init__(self, items):
        self._items = items
        self.inserted = []

    def events(self):
        return self

    def list(self, **_kwargs):
        return FakeEventsList(self._items)

    def insert(self, **kwargs):
        self.inserted.append(kwargs)
        return self

    def execute(self):
        return {"id": "event"}


def test_calendar_phase1_graph_runs(monkeypatch):
    """Runs calendar phase 1 graph and returns slots."""
    service = FakeCalendarService([])
    monkeypatch.setattr(nodes, "get_calendar_service", lambda: service)

    state = AgentState(
        selected_profiles=[],
        work_start_hour=9,
        work_end_hour=18,
        appointment_duration=60,
    )

    result = cast(AgentState, graph.calendar_phase1_app.invoke(state))
    assert result.busy_slots is not None
    assert result.free_slots is not None


def test_calendar_phase2_graph_runs(monkeypatch):
    """Runs calendar phase 2 graph and returns events and emails."""
    service = FakeCalendarService([])
    monkeypatch.setattr(nodes, "get_calendar_service", lambda: service)

    class FakeGmail:
        def __init__(self):
            self.sent = []

        def users(self):
            return self

        def messages(self):
            return self

        def send(self, userId, body):
            self.sent.append({"userId": userId, "body": body})
            return self

        def execute(self):
            return {"id": "msg"}

    monkeypatch.setattr(nodes, "get_gmail_service", lambda: FakeGmail())

    slot = FreeSlot(
        start=datetime(2026, 5, 15, 9, 0, tzinfo=timezone.utc),
        end=datetime(2026, 5, 15, 10, 0, tzinfo=timezone.utc),
    )
    state = AgentState(
        selected_profiles=[SelectedProfile(username="octo", email="o@e.com")],
        work_start_hour=9,
        work_end_hour=18,
        appointment_duration=60,
        selected_slot=slot,
    )

    result = cast(AgentState, graph.calendar_phase2_app.invoke(state))
    assert result.created_events is not None
    assert result.emails_sent is not None
