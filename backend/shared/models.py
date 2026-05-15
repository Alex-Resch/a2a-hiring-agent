from pydantic import BaseModel

from agents.agent_3_email_agent.state import FreeSlot


class SearchRequest(BaseModel):
    """Search criteria submitted by the recruiter."""

    languages: list[str] = []
    frameworks: list[str] = []
    domains: list[str] = []
    locations: list[str] = []
    experience_levels: list[str] = []
    availability: list[str] = []
    min_years_experience: int = 0
    active_within_months: int = 12
    min_public_repos: int = 0
    min_stars: int = 0


class SelectedProfile(BaseModel):
    """Selected profile identifiers used for scheduling."""

    username: str
    email: str | None = None


class CalendarPhase1Request(BaseModel):
    """Request payload to check busy/free slots."""

    selected_profiles: list[SelectedProfile]
    work_start_hour: int = 9
    work_end_hour: int = 18
    appointment_duration: int = 60


class CalendarPhase2Request(BaseModel):
    """Request payload to schedule an interview slot."""

    selected_profiles: list[SelectedProfile]
    selected_slot: FreeSlot
