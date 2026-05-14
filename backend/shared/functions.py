import httpx

from shared.settings import settings


BASE_URL = "https://api.github.com"


def fetch(url: str, params: dict | None = None) -> httpx.Response:
    return httpx.get(
        BASE_URL + url,
        headers={
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        params=params,
    )
