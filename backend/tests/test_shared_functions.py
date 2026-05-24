import httpx
import pytest

from shared import functions


@pytest.mark.anyio
async def test_fetch_sets_headers_and_params():
    """Sets GitHub auth headers and forwards query params."""

    seen = {}

    def fake_transport(request):
        seen["url"] = str(request.url)
        seen["headers"] = dict(request.headers)
        seen["params"] = dict(request.url.params)
        return httpx.Response(200, json={})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(fake_transport)
    ) as client:
        await functions.fetch("/search/users", params={"q": "python"}, client=client)

    assert "/search/users" in seen["url"]
    assert seen["headers"]["authorization"].startswith("Bearer ")
    assert seen["headers"]["accept"] == "application/vnd.github+json"
    assert seen["params"]["q"] == "python"
