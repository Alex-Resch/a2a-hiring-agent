import json
from typing import cast
import pytest

from a2a.server.agent_execution import RequestContext
from a2a.server.events import EventQueue
from agents.agent_2_screener import server
from agents.agent_2_screener.state import ProfileScore


class DummyContext:
    def __init__(self, user_input):
        self._user_input = user_input

    def get_user_input(self):
        return self._user_input


class DummyEventQueue:
    def __init__(self):
        self.events = []

    async def enqueue_event(self, event):
        self.events.append(event)


@pytest.mark.anyio
async def test_executor_emits_scores(monkeypatch):
    """Emits serialized scores in the event queue."""

    def fake_invoke(_state):
        return {
            "scored_profiles": [
                ProfileScore(
                    name="octo",
                    email="o@e.com",
                    overall_score=90,
                    code_quality_score=20,
                    activity_score=20,
                    technical_breadth_score=25,
                    community_impact_score=25,
                    strengths=["tests"],
                    weaknesses=["none"],
                    reasoning="ok",
                )
            ]
        }

    monkeypatch.setattr(server, "new_agent_text_message", lambda text: {"text": text})
    monkeypatch.setattr(server.app, "invoke", fake_invoke)

    payload = json.dumps(
        {
            "profiles": [
                {
                    "name": "octo",
                    "email": "o@e.com",
                    "bio": None,
                    "location": None,
                    "repos_details": [],
                }
            ],
            "user_input": "python",
        }
    )
    executor = server.GithubScreenerExecutor()
    context = DummyContext(user_input=payload)
    queue = DummyEventQueue()

    await executor.execute(
        cast(RequestContext, cast(object, context)),
        cast(EventQueue, cast(object, queue)),
    )

    assert len(queue.events) == 1
    payload = json.loads(queue.events[0]["text"])
    assert payload[0]["overall_score"] == 90


@pytest.mark.anyio
async def test_executor_cancel_raises():
    """Rejects cancel requests with an exception."""
    executor = server.GithubScreenerExecutor()
    context = DummyContext(user_input="")
    queue = DummyEventQueue()

    with pytest.raises(Exception):
        await executor.cancel(
            cast(RequestContext, cast(object, context)),
            cast(EventQueue, cast(object, queue)),
        )
