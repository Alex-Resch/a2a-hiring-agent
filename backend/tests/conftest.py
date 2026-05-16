import json
from tests._stubs import install_dependency_stubs

install_dependency_stubs()


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def extract_sse_events(body: str) -> list[dict]:
    events: list[dict] = []
    for line in body.splitlines():
        if line.startswith("data: "):
            events.append(json.loads(line[len("data: ") :]))
    return events
