import json

from agents.agent_1_github_searcher.state import (
    AgentState,
    ProfileDetails,
    RepoDetails,
    CommitDetails,
    FileDetails,
)
from shared.functions import fetch


def build_github_query(criteria: dict) -> str:
    parts = []

    if langs := criteria.get("languages"):
        parts.append(" OR ".join(f"language:{lang}" for lang in langs))

    for loc in criteria.get("locations", []):
        parts.append(f"location:{loc}")

    if (repos := criteria.get("min_public_repos", 0)) > 0:
        parts.append(f"repos:>={repos}")

    return " ".join(parts) or "type:user"


def search_profiles(state: AgentState) -> AgentState:
    query = build_github_query(json.loads(state.user_input))
    response = fetch("/search/users", params={"q": query, "per_page": 2, "page": 1})

    data = response.json()
    found_profiles = [item["login"] for item in data.get("items", [])]
    return state.model_copy(update={"found_profiles": found_profiles})


def get_profile_details(state: AgentState) -> AgentState:
    """Add DocString later"""
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
        profile_details.append(profile_detail)
    return state.model_copy(update={"profiles_details": profile_details})
