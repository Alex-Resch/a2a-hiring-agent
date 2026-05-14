from pydantic import BaseModel


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


class CalendarPhase1Request(BaseModel):
    selected_profiles: list[dict]


class CalendarPhase2Request(BaseModel):
    selected_profiles: list[dict]
    selected_slot: dict
    busy_slots: list[dict]
    free_slots: list[dict]
