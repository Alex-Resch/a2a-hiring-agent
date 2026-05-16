import json
import pytest

from agents.agent_1_github_searcher import nodes
from agents.agent_1_github_searcher.state import AgentState
from tests.conftest import DummyResponse


def test_build_github_query_defaults_to_type_user():
    """Defaults to the type:user query when no criteria are set."""
    assert nodes.build_github_query({}) == "type:user"


def test_build_github_query_combines_criteria():
    """Combines multiple criteria into a single GitHub search query."""
    query = nodes.build_github_query(
        {
            "languages": ["python", "go"],
            "locations": ["berlin"],
            "min_public_repos": 3,
            "min_stars": 10,
            "active_within_months": 1,
            "min_years_experience": 5,
            "frameworks": ["django"],
        }
    )

    assert "(language:python OR language:go)" in query
    assert "location:berlin" in query
    assert "repos:>=3" in query
    assert "stars:>=10" in query
    assert "created:>=" in query
    assert '"5 years"' in query
    assert '"django"' in query


def test_search_profiles_uses_fetch(monkeypatch):
    """Calls fetch with a query and stores returned logins."""

    def fake_fetch(_url, params=None):
        assert params and "q" in params
        return DummyResponse({"items": [{"login": "octocat"}]})

    monkeypatch.setattr(nodes, "fetch", fake_fetch)

    state = AgentState(
        user_input=json.dumps({}), found_profiles=[], profiles_details=[]
    )
    result = nodes.search_profiles(state)

    assert result.found_profiles == ["octocat"]


def test_get_profile_details_filters_missing_email(monkeypatch):
    """Keeps only profiles with email and builds nested details."""

    def fake_fetch(url, params=None):
        if url.endswith("/repos"):
            return DummyResponse(
                [
                    {
                        "name": "repo",
                        "description": "d",
                        "language": "py",
                        "stargazers_count": 5,
                    }
                ]
            )
        if "/commits/" in url:
            return DummyResponse(
                {
                    "files": [
                        {
                            "filename": "a.py",
                            "status": "modified",
                            "additions": 2,
                            "deletions": 1,
                            "changes": 3,
                            "patch": "+x",
                        }
                    ],
                    "stats": {"total": 3, "additions": 2, "deletions": 1},
                }
            )
        if url.endswith("/commits"):
            return DummyResponse(
                [{"sha": "abc", "commit": {"message": "m", "date": "2026-01-01"}}]
            )
        if url.endswith("/users/octocat"):
            return DummyResponse(
                {
                    "login": "octocat",
                    "email": "octo@example.com",
                    "bio": "bio",
                    "location": "earth",
                }
            )
        if url.endswith("/users/noemail"):
            return DummyResponse(
                {"login": "noemail", "email": None, "bio": "bio", "location": "mars"}
            )
        return DummyResponse({"items": []})  # pragma: no cover

    monkeypatch.setattr(nodes, "fetch", fake_fetch)

    state = AgentState(
        user_input=json.dumps({}),
        found_profiles=["octocat", "noemail"],
        profiles_details=[],
    )
    result = nodes.get_profile_details(state)

    assert len(result.profiles_details) == 1
    profile = result.profiles_details[0]
    assert profile.name == "octocat"
    assert (
        profile.repos_details[0].commits_details[0].files_details[0].filename == "a.py"
    )


_HAPPY_REPOS = [
    {"name": "repo", "description": "d", "language": "py", "stargazers_count": 5}
]
_HAPPY_COMMITS = [{"sha": "abc", "commit": {"message": "m", "date": "2026-01-01"}}]
_HAPPY_COMMIT_DETAIL = {
    "files": [],
    "stats": {"total": 0, "additions": 0, "deletions": 0},
    "commit": {"message": "m", "date": "2026-01-01"},
}


@pytest.mark.parametrize(
    "profile,bad_url,bad_response,expect_in",
    [
        ("bad_repos", "/repos", DummyResponse({"unexpected": True}), False),
        ("bad_repo_item", "/repos", DummyResponse(["not-a-dict"]), True),
        ("bad_commits", "/commits", DummyResponse({"unexpected": True}), True),
        ("bad_commit_item", "/commits", DummyResponse(["not-a-dict"]), True),
        (
            "bad_commit_meta",
            "/commits",
            DummyResponse([{"sha": "abc", "commit": "not-a-dict"}]),
            True,
        ),
        ("bad_commit_detail", "/commits/", DummyResponse(["not-a-dict"]), True),
        (
            "bad_file_item",
            "/commits/",
            DummyResponse(
                {
                    "files": ["not-a-dict"],
                    "stats": {"total": 0, "additions": 0, "deletions": 0},
                    "commit": {"message": "m", "date": "2026-01-01"},
                }
            ),
            True,
        ),
        (
            "bad_commit",
            "/commits/",
            DummyResponse(
                {
                    "files": [],
                    "stats": {"total": 0, "additions": 0, "deletions": 0},
                    "commit": "not-a-dict",
                }
            ),
            True,
        ),
    ],
)
def test_get_profile_details_handles_unexpected_shapes(
    monkeypatch, profile, bad_url, bad_response, expect_in
):
    """Skips unexpected response shapes without crashing."""

    def fake_fetch(url, params=None):
        if bad_url == "/commits/" and "/commits/" in url:
            return bad_response
        if bad_url != "/commits/" and url.endswith(bad_url):
            return bad_response
        if url.endswith("/repos"):
            return DummyResponse(_HAPPY_REPOS)
        if url.endswith("/commits"):
            return DummyResponse(_HAPPY_COMMITS)
        if "/commits/" in url:
            return DummyResponse(_HAPPY_COMMIT_DETAIL)
        if url.endswith(f"/users/{profile}"):
            return DummyResponse({"login": profile, "email": "x@example.com"})
        return DummyResponse({})  # pragma: no cover

    monkeypatch.setattr(nodes, "fetch", fake_fetch)

    state = AgentState(
        user_input=json.dumps({}),
        found_profiles=[profile],
        profiles_details=[],
    )
    result = nodes.get_profile_details(state)
    names = {p.name for p in result.profiles_details}

    if expect_in:
        assert profile in names
    else:
        assert profile not in names
