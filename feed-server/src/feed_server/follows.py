import httpx

PUBLIC_APPVIEW_BASE_URL = "https://public.api.bsky.app"
GET_FOLLOWS_PAGE_LIMIT = 100

http_client = httpx.AsyncClient(base_url=PUBLIC_APPVIEW_BASE_URL)


async def get_follows(actor: str) -> list[str]:
    """Return the DIDs of every account ``actor`` follows.

    ``actor`` may be a DID or a handle. Follows are read from the public Bluesky
    AppView, which exposes them paginated; this walks every page.
    """
    followed_dids: list[str] = []
    cursor: str | None = None
    while True:
        params = {"actor": actor, "limit": GET_FOLLOWS_PAGE_LIMIT}
        if cursor:
            params["cursor"] = cursor
        response = await http_client.get(
            "/xrpc/app.bsky.graph.getFollows", params=params, timeout=10.0
        )
        response.raise_for_status()
        data = response.json()
        followed_dids.extend(follow["did"] for follow in data["follows"])
        cursor = data.get("cursor")
        if not cursor:
            return followed_dids
