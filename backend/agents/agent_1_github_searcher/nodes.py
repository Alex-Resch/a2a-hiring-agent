import json
from datetime import datetime, timedelta, timezone

from agents.agent_1_github_searcher.state import (
    AgentState,
    ProfileDetails,
    RepoDetails,
    CommitDetails,
    FileDetails,
)
from shared.functions import fetch


def build_github_query(criteria: dict) -> str:
    """Build a GitHub search query string from structured criteria."""
    parts: list[str] = []

    def add_or_group(tokens: list[str]) -> None:
        """Append a single token or a parenthesized OR-group, skipping empty values to keep query logic stable."""
        clean = [t for t in tokens if t]
        if not clean:
            return
        if len(clean) == 1:
            parts.append(clean[0])
        else:
            parts.append(f"({' OR '.join(clean)})")

    if langs := criteria.get("languages"):
        add_or_group([f"language:{lang}" for lang in langs])

    if locations := criteria.get("locations"):
        add_or_group([f"location:{loc}" for loc in locations])

    if (repos := criteria.get("min_public_repos", 0)) > 0:
        parts.append(f"repos:>={repos}")

    if (min_stars := criteria.get("min_stars", 0)) > 0:
        parts.append(f"stars:>={min_stars}")

    if (active_months := criteria.get("active_within_months", 0)) > 0:
        since = datetime.now(timezone.utc) - timedelta(days=30 * active_months)
        parts.append(f"created:>={since.date().isoformat()}")

    if (min_years := criteria.get("min_years_experience", 0)) > 0:
        add_or_group(
            [
                f'"{min_years} years"',
                f'"{min_years}+ years"',
                f'"{min_years} yrs"',
            ]
        )

    keyword_groups = [
        criteria.get("frameworks", []),
        criteria.get("domains", []),
        criteria.get("experience_levels", []),
        criteria.get("availability", []),
    ]
    for group in keyword_groups:
        add_or_group([f'"{item}"' for item in group])

    return " ".join(parts) or "type:user"


def search_profiles(state: AgentState) -> AgentState:
    """Search GitHub users and store their logins in state."""
    query = build_github_query(json.loads(state.user_input))
    response = fetch("/search/users", params={"q": query, "per_page": 2, "page": 1})

    data = response.json()
    found_profiles = [item["login"] for item in data.get("items", [])]
    return state.model_copy(update={"found_profiles": found_profiles})


def get_profile_details(state: AgentState) -> AgentState:
    """Fetch repo and commit details for found profiles with emails."""
    profile_details: list[ProfileDetails] = []

    for profile in state.found_profiles:
        repos = fetch(f"/users/{profile}/repos", params={"per_page": 1}).json()

        if not isinstance(repos, list):
            continue
        repo_details: list[RepoDetails] = []

        for repo in repos:
            if not isinstance(repo, dict):
                continue

            commits = fetch(
                f"/repos/{profile}/{repo.get('name')}/commits",
                params={"author": profile, "per_page": 1},
            ).json()

            if not isinstance(commits, list):
                continue

            commit_details: list[CommitDetails] = []
            for c in commits:
                if not isinstance(c, dict):
                    continue

                commit_detail_response = fetch(
                    f"/repos/{profile}/{repo.get('name')}/commits/{c.get('sha')}"
                ).json()

                if not isinstance(commit_detail_response, dict):
                    continue

                files = commit_detail_response.get("files", [])

                file_details: list[FileDetails] = []
                for file in files:
                    if not isinstance(file, dict):
                        continue

                    file_detail = FileDetails(
                        filename=file.get("filename"),
                        status=file.get("status"),
                        additions=file.get("additions"),
                        deletions=file.get("deletions"),
                        changes=file.get("changes"),
                        diff=file.get("patch"),
                    )

                    file_details.append(file_detail)

                commit = c.get("commit")
                if not isinstance(commit, dict):
                    continue

                stats = commit_detail_response.get("stats", {})

                commit_detail = CommitDetails(
                    message=commit.get("message"),
                    date_time=commit.get("date"),
                    total_changes=stats.get("total"),
                    total_additions=stats.get("additions"),
                    total_deletions=stats.get("deletions"),
                    files_details=file_details,
                )

                commit_details.append(commit_detail)

            repo_detail = RepoDetails(
                name=repo.get("name"),
                description=repo.get("description"),
                language=repo.get("language"),
                stars=repo.get("stargazers_count"),
                commits_details=commit_details,
            )
            repo_details.append(repo_detail)

        user = fetch(f"/users/{profile}").json()

        profile_detail = ProfileDetails(
            name=user.get("login"),
            email=user.get("email"),
            bio=user.get("bio"),
            location=user.get("location"),
            repos_details=repo_details,
        )
        if profile_detail.email:
            profile_details.append(profile_detail)
    return state.model_copy(update={"profiles_details": profile_details})
