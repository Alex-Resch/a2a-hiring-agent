from pydantic import BaseModel

from agents.agent_3_email_agent.state import FreeSlot


class SearchRequest(BaseModel):
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
    username: str
    email: str | None = None


class CalendarPhase1Request(BaseModel):
    selected_profiles: list[SelectedProfile]


class CalendarPhase2Request(BaseModel):
    selected_profiles: list[SelectedProfile]
    selected_slot: FreeSlot
