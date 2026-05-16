import json
import pytest
from typing import cast

from a2a.server.agent_execution import RequestContext
from a2a.server.events import EventQueue
from agents.agent_1_github_searcher import server
from agents.agent_1_github_searcher.state import ProfileDetails


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
async def test_executor_emits_profiles(monkeypatch):
    """Emits serialized profiles in the event queue."""

    def fake_invoke(_state):
        return {
            "profiles_details": [
                ProfileDetails(
                    name="octo",
                    email="o@e.com",
                    bio=None,
                    location=None,
                    repos_details=[],
                )
            ]
        }

    monkeypatch.setattr(server, "new_agent_text_message", lambda text: {"text": text})
    monkeypatch.setattr(server.app, "invoke", fake_invoke)

    executor = server.GithubSearcherExecutor()
    context = DummyContext(user_input=json.dumps({}))
    queue = DummyEventQueue()

    await executor.execute(
        cast(RequestContext, cast(object, context)),
        cast(EventQueue, cast(object, queue)),
    )

    assert len(queue.events) == 1
    payload = json.loads(queue.events[0]["text"])
    assert payload[0]["name"] == "octo"


@pytest.mark.anyio
async def test_executor_cancel_raises():
    """Rejects cancel requests with an exception."""
    executor = server.GithubSearcherExecutor()
    context = DummyContext(user_input="")
    queue = DummyEventQueue()

    with pytest.raises(Exception):
        await executor.cancel(
            cast(RequestContext, cast(object, context)),
            cast(EventQueue, cast(object, queue)),
        )
