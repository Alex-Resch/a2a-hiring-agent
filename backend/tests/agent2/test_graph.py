import types
from typing import cast

from agents.agent_2_screener import graph, nodes
from agents.agent_2_screener.state import AgentState, ProfileDetails, ProfileScore


def test_graph_runs_end_to_end(monkeypatch):
    """Runs the screener graph end-to-end with a mocked LLM call."""

    def fake_create(*_args, **_kwargs):
        return ProfileScore(
            name="octo",
            email="",
            overall_score=90,
            code_quality_score=20,
            activity_score=20,
            technical_breadth_score=25,
            community_impact_score=25,
            strengths=["tests"],
            weaknesses=["none"],
            reasoning="ok",
        )

    dummy_chat = types.SimpleNamespace(
        completions=types.SimpleNamespace(create=fake_create)
    )
    monkeypatch.setattr(nodes.client, "chat", dummy_chat)

    state = AgentState(
        user_input="python",
        profiles_details=[
            ProfileDetails(
                name="octo", email="o@e.com", bio=None, location=None, repos_details=[]
            )
        ],
    )

    result = cast(AgentState, graph.app.invoke(state))
    assert result.scored_profiles
    assert result.scored_profiles[0].overall_score == 90
