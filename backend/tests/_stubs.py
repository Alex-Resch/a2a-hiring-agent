import sys
import types
from typing import Any


def _ensure_module(name: str) -> Any:
    module = sys.modules.get(name)
    if module is not None:
        return module

    if "." in name:
        parent_name, child_name = name.rsplit(".", 1)
        parent_module = _ensure_module(parent_name)
        module = types.ModuleType(name)
        setattr(parent_module, child_name, module)
    else:
        module = types.ModuleType(name)

    sys.modules[name] = module
    return module


def install_dependency_stubs() -> None:
    langgraph_graph = _ensure_module("langgraph.graph")

    class _StateGraph:
        def __init__(self, _state_type):
            self._nodes = {}
            self._edges = {}
            self._entry = None

        def add_node(self, name, func):
            self._nodes[name] = func

        def set_entry_point(self, name):
            self._entry = name

        def add_edge(self, src, dst):
            self._edges.setdefault(src, []).append(dst)

        def compile(self):
            graph = self

            class _App:
                def invoke(self, state):
                    current = graph._entry
                    data = state
                    while True:
                        if current is langgraph_graph.END:
                            return data
                        if current not in graph._nodes:
                            return data
                        node = graph._nodes[current]
                        result = node(data)
                        if isinstance(result, dict):
                            if hasattr(data, "model_copy"):
                                data = getattr(data, "model_copy")(update=result)
                            elif isinstance(data, dict):
                                merged = dict(data)
                                merged.update(result)
                                data = merged
                            else:
                                data = result
                        else:
                            data = result

                        next_nodes = graph._edges.get(current, [])
                        if not next_nodes:
                            return data
                        next_node = next_nodes[0]
                        if next_node is langgraph_graph.END:
                            return data
                        current = next_node

            return _App()

    langgraph_graph.StateGraph = _StateGraph
    langgraph_graph.END = object()

    class _Dummy:
        def __init__(self, *args, **kwargs):
            pass

    class _Role:
        user = "user"

    class _A2ACardResolver:
        def __init__(self, *args, **kwargs):
            pass

        async def get_agent_card(self):
            return object()

    a2a_client = _ensure_module("a2a.client")
    a2a_client.A2AClient = _Dummy
    a2a_client.A2ACardResolver = _A2ACardResolver

    a2a_types = _ensure_module("a2a.types")
    a2a_types.Role = _Role
    for _name in (
        "MessageSendParams",
        "SendMessageRequest",
        "Message",
        "Part",
        "TextPart",
        "AgentCard",
        "AgentCapabilities",
        "AgentSkill",
    ):
        setattr(a2a_types, _name, _Dummy)

    class _A2AStarletteApplication:
        def __init__(self, *args, **kwargs):
            pass

        def build(self):
            return None

    for _module_name, _attr, _value in [
        ("a2a.server.agent_execution", "AgentExecutor", object),
        ("a2a.server.agent_execution", "RequestContext", object),
        ("a2a.server.apps", "A2AStarletteApplication", _A2AStarletteApplication),
        ("a2a.server.events", "EventQueue", object),
        ("a2a.server.request_handlers", "DefaultRequestHandler", _Dummy),
        ("a2a.server.tasks", "InMemoryTaskStore", _Dummy),
    ]:
        setattr(_ensure_module(_module_name), _attr, _value)

    def _new_agent_text_message(text):
        return {"text": text}

    a2a_utils = _ensure_module("a2a.utils")
    a2a_utils.new_agent_text_message = _new_agent_text_message

    instructor = _ensure_module("instructor")
    instructor.from_litellm = lambda _completion: types.SimpleNamespace(
        chat=types.SimpleNamespace(
            completions=types.SimpleNamespace(create=lambda *args, **kwargs: None)
        )
    )

    litellm = _ensure_module("litellm")
    litellm.completion = object()

    googleapiclient_discovery = _ensure_module("googleapiclient.discovery")
    googleapiclient_discovery.build = lambda *args, **kwargs: object()

    class _Credentials:
        valid = True
        expired = False
        refresh_token = None

        @classmethod
        def from_authorized_user_file(cls, *args, **kwargs):
            return cls()

        def refresh(self, *args, **kwargs):
            return None

        def to_json(self):
            return "{}"

    class _InstalledAppFlow:
        @classmethod
        def from_client_secrets_file(cls, *args, **kwargs):
            return cls()

        def run_local_server(self, *args, **kwargs):
            return _Credentials()

    google_auth_oauthlib_flow = _ensure_module("google_auth_oauthlib.flow")
    google_auth_oauthlib_flow.InstalledAppFlow = _InstalledAppFlow

    google_auth_transport_requests = _ensure_module("google.auth.transport.requests")
    google_auth_transport_requests.Request = object

    google_oauth2_credentials = _ensure_module("google.oauth2.credentials")
    google_oauth2_credentials.Credentials = _Credentials
