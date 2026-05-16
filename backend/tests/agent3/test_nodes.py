import pytest
from datetime import datetime, timedelta, timezone

from agents.agent_3_email_agent import nodes
from agents.agent_3_email_agent.state import (
    AgentState,
    BusySlot,
    FreeSlot,
    SelectedProfile,
)


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


class FailingGmail:
    def users(self):
        return self

    def messages(self):
        return self

    def send(self, userId, body):
        raise RuntimeError("boom")


@pytest.fixture
def slot():
    return FreeSlot(
        start=datetime(2026, 5, 15, 9, 0, tzinfo=timezone.utc),
        end=datetime(2026, 5, 15, 10, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def base_state():
    return dict(
        selected_profiles=[SelectedProfile(username="octo", email="o@e.com")],
        work_start_hour=9,
        work_end_hour=18,
        appointment_duration=60,
    )


def test_check_busy_slots_filters_events(monkeypatch):
    """Filters all-day events and keeps dateTime slots."""
    items = [
        {
            "start": {"dateTime": "2026-01-01T09:00:00+00:00"},
            "end": {"dateTime": "2026-01-01T10:00:00+00:00"},
        },
        {"start": {"date": "2026-01-01"}, "end": {"date": "2026-01-01"}},
    ]
    monkeypatch.setattr(
        nodes, "get_calendar_service", lambda: FakeCalendarService(items)
    )

    state = AgentState(
        selected_profiles=[],
        work_start_hour=9,
        work_end_hour=18,
        appointment_duration=60,
    )
    result = nodes.check_busy_slots(state)

    assert len(result.busy_slots) == 1
    assert result.busy_slots[0].start.isoformat().startswith("2026-01-01T09:00:00")


def test_get_free_slots_returns_duration():
    """Produces slots matching the configured duration."""
    now = datetime.now(timezone.utc)
    busy = [BusySlot(start=now + timedelta(hours=1), end=now + timedelta(hours=2))]
    state = AgentState(
        selected_profiles=[],
        work_start_hour=9,
        work_end_hour=18,
        appointment_duration=60,
        busy_slots=busy,
    )

    result = nodes.get_free_slots(state)

    assert result.free_slots
    for s in result.free_slots:
        assert s.end - s.start == timedelta(minutes=60)


def test_create_appointment_records_events(monkeypatch, slot, base_state):
    """Creates calendar events for selected profiles."""
    service = FakeCalendarService([])
    monkeypatch.setattr(nodes, "get_calendar_service", lambda: service)

    result = nodes.create_appointment(AgentState(**base_state, selected_slot=slot))

    assert result.created_events
    assert service.inserted[0]["body"]["summary"].startswith("Interview with")


def test_create_appointment_requires_slot(monkeypatch, base_state):
    """Raises when no slot is selected for appointment creation."""
    monkeypatch.setattr(nodes, "get_calendar_service", lambda: FakeCalendarService([]))

    with pytest.raises(ValueError, match="No Free Slot"):
        nodes.create_appointment(AgentState(**base_state, selected_slot=None))


def test_build_email_message_contains_username(slot):
    """Embeds the username into the email body."""
    message = nodes.build_email_message("octo", slot)

    assert "octo" in message.get_payload()


def test_send_interview_invitations_sends(monkeypatch, slot, base_state):
    """Sends an invitation email for each selected profile."""
    service = FakeGmail()
    monkeypatch.setattr(nodes, "get_gmail_service", lambda: service)

    result = nodes.send_interview_invitations(
        AgentState(**base_state, selected_slot=slot)
    )

    assert result.emails_sent[0].status == "sent"


def test_send_interview_invitations_failure(monkeypatch, slot, base_state):
    """Records a failed email send when the service errors."""
    monkeypatch.setattr(nodes, "get_gmail_service", lambda: FailingGmail())

    result = nodes.send_interview_invitations(
        AgentState(**base_state, selected_slot=slot)
    )

    assert result.emails_sent[0].status == "failed"
    assert result.emails_sent[0].error_message is not None
    assert "boom" in result.emails_sent[0].error_message


def test_send_interview_invitations_requires_slot(monkeypatch, base_state):
    """Raises when no slot is selected before sending emails."""
    monkeypatch.setattr(nodes, "get_gmail_service", lambda: FakeGmail())

    with pytest.raises(ValueError, match="No Free Slot"):
        nodes.send_interview_invitations(AgentState(**base_state, selected_slot=None))
