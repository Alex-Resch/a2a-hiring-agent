import httpx

from shared import functions


def test_fetch_sets_headers_and_params(monkeypatch):
    """Sets GitHub auth headers and forwards query params."""

    seen = {}

    def fake_get(url, headers=None, params=None):
        seen["url"] = url
        seen["headers"] = headers
        seen["params"] = params
        return "ok"

    monkeypatch.setattr(httpx, "get", fake_get)

    result = functions.fetch("/search/users", params={"q": "python"})

    assert result == "ok"
    assert seen["url"].endswith("/search/users")
    assert seen["headers"]["Authorization"].startswith("Bearer ")
    assert seen["headers"]["Accept"] == "application/vnd.github+json"
    assert seen["params"]["q"] == "python"
