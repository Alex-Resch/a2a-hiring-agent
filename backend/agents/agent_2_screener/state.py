from datetime import datetime
from pydantic import BaseModel


class FileDetails(BaseModel):
    """Details of a file in a GitHub commit."""

    filename: str | None
    status: str | None
    additions: int | None
    deletions: int | None
    changes: int | None
    diff: str | None


class CommitDetails(BaseModel):
    """Details of a GitHub commit."""

    message: str | None
    date_time: datetime | None
    total_changes: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    files_details: list[FileDetails]


class RepoDetails(BaseModel):
    """Details of a GitHub repository."""

    name: str | None
    description: str | None
    language: str | None
    stars: int | None
    commits_details: list[CommitDetails]


class ProfileDetails(BaseModel):
    """Details of a GitHub profile."""

    name: str
    email: str | None
    bio: str | None
    location: str | None
    repos_details: list[RepoDetails] = []


class ProfileScore(BaseModel):
    """Score of a GitHub profile."""

    name: str
    email: str | None
    overall_score: float
    code_quality_score: float
    activity_score: float
    technical_breadth_score: float
    community_impact_score: float
    strengths: list[str]
    weaknesses: list[str]
    reasoning: str


class AgentState(BaseModel):
    """State of the agent."""

    profiles_details: list[ProfileDetails]
    # search_details: dict[str, str]
    scored_profiles: list[ProfileScore] = []
