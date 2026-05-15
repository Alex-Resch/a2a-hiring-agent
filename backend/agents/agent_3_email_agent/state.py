from datetime import datetime
from pydantic import BaseModel


class EmailSent(BaseModel):
    """Result of sending an email to a profile."""

    profile: str
    status: str
    error_message: str | None = None


class BusySlot(BaseModel):
    """Time window that is already occupied on the calendar."""

    start: datetime
    end: datetime


class FreeSlot(BusySlot):
    """Available time window that can be scheduled."""

    pass


class SelectedProfile(BaseModel):
    """Details of a selected GitHub profile."""

    username: str
    email: str


class AgentState(BaseModel):
    """State of the agent."""

    selected_profiles: list[SelectedProfile]
    busy_slots: list[BusySlot] = []
    free_slots: list[FreeSlot] = []
    selected_slot: FreeSlot | None = None
    emails_sent: list[EmailSent] = []
    created_events: list[dict] = []
