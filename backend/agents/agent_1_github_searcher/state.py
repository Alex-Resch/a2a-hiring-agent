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
    bio: str | None
    location: str | None
    repos_details: list[RepoDetails] = []


class AgentState(BaseModel):
    """State of the agent."""

    user_input: str
    found_profiles: list[str]
    profiles_details: list[ProfileDetails]
