import types

from agents.agent_2_screener import nodes
from agents.agent_2_screener.state import AgentState, ProfileDetails, ProfileScore


def test_build_user_prompt_includes_criteria():
    """Includes profile content and criteria in the prompt."""
    state = AgentState(user_input="python", profiles_details=[])
    prompt = nodes.build_user_prompt("profile", state)

    assert "profile" in prompt
    assert "python" in prompt


def test_score_profiles_sets_email(monkeypatch):
    """Copies the profile email onto the scored result."""

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
    result = nodes.score_profiles(state)

    assert len(result["scored_profiles"]) == 1
    assert result["scored_profiles"][0].email == "o@e.com"
