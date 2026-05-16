import httpx
import pytest
from pydantic import BaseModel

from tests import _stubs


def test_ensure_module_creates_and_reuses():
    """Creates modules and reuses existing instances."""
    module = _stubs._ensure_module("example.module")
    again = _stubs._ensure_module("example.module")

    assert module is again
    assert module.__name__ == "example.module"
    assert _stubs._ensure_module("example")


def test_install_dependency_stubs_exposes_helpers():
    _stubs.install_dependency_stubs()

    import sys
    from langgraph.graph import StateGraph, END
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from a2a.utils import new_agent_text_message

    a2a_client_mod = sys.modules["a2a.client"]
    A2AClient = a2a_client_mod.A2AClient
    A2ACardResolver = a2a_client_mod.A2ACardResolver
    A2AStarletteApplication = sys.modules["a2a.server.apps"].A2AStarletteApplication

    assert StateGraph is not None
    assert END is not None
    assert A2AStarletteApplication().build() is None
    assert new_agent_text_message("x") == {"text": "x"}

    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", [])
    creds = flow.run_local_server(port=0)
    assert creds.to_json() == "{}"

    creds = Credentials.from_authorized_user_file("token.json", [])
    assert creds.refresh(None) is None

    assert isinstance(A2AClient(), A2AClient)
    resolver = A2ACardResolver()
    assert hasattr(resolver, "get_agent_card")


def test_stategraph_branches():
    """Covers stub StateGraph branch behavior."""
    from langgraph.graph import StateGraph, END

    class _State(BaseModel):
        done: bool = False

    _state = _State()

    graph = StateGraph(_State)
    graph.add_node("start", lambda state: {"done": True})
    graph.set_entry_point("start")
    result = graph.compile().invoke(_state)
    assert result.done is True  # type: ignore[union-attr]

    graph2 = StateGraph(_State)
    graph2.add_node("start", lambda state: {"done": True})
    graph2.set_entry_point("start")
    graph2.add_edge("start", END)
    result2 = graph2.compile().invoke(_state)
    assert result2.done is True  # type: ignore[union-attr]

    graph3 = StateGraph(_State)
    graph3.set_entry_point(END)
    assert graph3.compile().invoke(_state) == _state

    graph4 = StateGraph(_State)
    graph4.set_entry_point("missing")
    assert graph4.compile().invoke(_state) == _state

    # elif isinstance(data, dict): Pfad
    graph5 = StateGraph(_State)
    graph5.add_node("start", lambda state: {"done": True})
    graph5.set_entry_point("start")
    result5 = graph5.compile().invoke({"done": False})  # type: ignore[arg-type]
    assert result5["done"] is True

    # else: Pfad – node gibt kein dict zurück
    graph6 = StateGraph(_State)
    graph6.add_node("start", lambda state: "fertig")
    graph6.set_entry_point("start")
    result6 = graph6.compile().invoke({"done": False})  # type: ignore[arg-type]
    assert result6 == "fertig"

    graph7 = StateGraph(_State)
    graph7.add_node("start", lambda state: {"done": True})
    graph7.set_entry_point("start")
    result7 = graph7.compile().invoke(object())  # type: ignore[arg-type]
    assert result7 == {"done": True}


@pytest.mark.anyio
async def test_resolver_get_agent_card():
    """Returns a placeholder card from the stub resolver."""
    from a2a.client import A2ACardResolver

    async with httpx.AsyncClient() as client:
        resolver = A2ACardResolver(httpx_client=client, base_url="http://test")
        card = await resolver.get_agent_card()

        assert card is not None
