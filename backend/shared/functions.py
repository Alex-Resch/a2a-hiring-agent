import httpx

from shared.settings import settings


BASE_URL = "https://api.github.com"


async def fetch(
    url: str,
    client: httpx.AsyncClient,
    params: dict | None = None,
) -> httpx.Response:
    """Fetch a GitHub API endpoint asynchronously with auth headers applied."""
    return await client.get(
        BASE_URL + url,
        headers={
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        params=params,
    )
