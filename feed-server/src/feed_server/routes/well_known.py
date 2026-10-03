from fastapi import APIRouter
from feed_server.config import FEED_SERVER_DID, FEED_SERVER_HOSTNAME

router = APIRouter()


@router.get("/.well-known/did.json")
async def well_known_did():
    return {
        "@context": ["https://www.w3.org/ns/did/v1"],
        "id": FEED_SERVER_DID,
        "service": [
            {
                "id": "#bsky_fg",
                "type": "BskyFeedGenerator",
                "serviceEndpoint": f"https://{FEED_SERVER_HOSTNAME}",
            }
        ],
    }
