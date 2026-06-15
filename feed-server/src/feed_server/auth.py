import base64
import binascii
import json
import logging

logger = logging.getLogger(__name__)

BEARER_PREFIX = "Bearer "


def get_requester_did(authorization_header: str | None) -> str | None:
    """Return the DID of the account requesting a feed, or ``None`` if unknown.

    Bluesky sends the requester's identity as a JWT in the ``Authorization``
    header; the issuer (``iss``) claim is their DID.

    WARNING: the JWT signature is NOT verified here, so the returned DID is not
    trustworthy and must not gate access to anything sensitive. This only decodes
    the payload, which is enough while we experiment with personalised feeds.
    """
    if not authorization_header or not authorization_header.startswith(BEARER_PREFIX):
        return None

    token = authorization_header[len(BEARER_PREFIX):].strip()
    segments = token.split(".")
    if len(segments) != 3:
        return None

    payload_segment = segments[1]
    padding = "=" * (-len(payload_segment) % 4)
    try:
        payload = json.loads(base64.urlsafe_b64decode(payload_segment + padding))
    except (binascii.Error, ValueError):
        logger.warning("Could not decode requester JWT payload", exc_info=True)
        return None

    return payload.get("iss")
