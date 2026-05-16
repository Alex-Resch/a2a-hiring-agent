import json

from agents.agent_1_github_searcher import graph
from agents.agent_1_github_searcher.state import AgentState
from tests.conftest import DummyResponse


def test_graph_runs_end_to_end(monkeypatch):
    """Runs the agent graph end-to-end with mocked fetches."""

    def fake_fetch(url, params=None):
        if url == "/search/users":
            return DummyResponse({"items": [{"login": "octocat"}]})
        if "/commits/" in url:
            return DummyResponse(
                {"files": [], "stats": {"total": 0, "additions": 0, "deletions": 0}}
            )
        if url.endswith("/commits"):
            return DummyResponse(
                [{"sha": "abc", "commit": {"message": "m", "date": "2026-01-01"}}]
            )
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
        if url.endswith("/users/octocat"):
            return DummyResponse({"login": "octocat", "email": "octo@example.com"})
        return DummyResponse({})  # pragma: no cover

    monkeypatch.setattr("agents.agent_1_github_searcher.nodes.fetch", fake_fetch)

    state = AgentState(
        user_input=json.dumps({}), found_profiles=[], profiles_details=[]
    )

    result = graph.app.invoke(state)
    assert result.profiles_details  # type: ignore[union-attr]
    assert result.profiles_details[0].email == "octo@example.com"  # type: ignore[union-attr]
