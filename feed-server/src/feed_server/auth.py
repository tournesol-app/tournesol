import base64
import binascii
import json
import logging
import time

from atproto_crypto.verify import verify_signature
from atproto_identity.cache.in_memory_cache import AsyncDidInMemoryCache
from atproto_identity.did.resolver import AsyncDidResolver

from .config import FEED_SERVER_DID

logger = logging.getLogger(__name__)

BEARER_PREFIX = "Bearer "

_did_resolver = AsyncDidResolver(cache=AsyncDidInMemoryCache())


async def get_requester_did(
    authorization_header: str | None, lexicon_method: str
) -> str | None:
    """Return the verified DID of the account making the request, or ``None``.

    Bluesky sends the requester's identity as a service-auth JWT in the
    ``Authorization`` header: the ``iss`` claim is the requester's DID and the
    token is signed by their repo key. We verify the signature against the
    issuer's DID document and check the audience, expiry and lexicon-method
    claims, so the returned DID can be trusted.

    ``None`` means the request is unauthenticated or the token was invalid.
    """
    token = _bearer_token(authorization_header)
    if token is None:
        return None

    try:
        payload, signing_input, signature = _parse_jwt(token)
    except (ValueError, binascii.Error):
        logger.warning("Could not decode requester JWT", exc_info=True)
        return None

    issuer = payload.get("iss")
    if not issuer:
        return None

    audience = payload.get("aud")
    if audience != FEED_SERVER_DID:
        logger.warning("Rejecting JWT: audience %r does not match %r", audience, FEED_SERVER_DID)
        return None

    expiration = payload.get("exp")
    if not isinstance(expiration, (int, float)) or time.time() > expiration:
        logger.warning("Rejecting JWT from %s: missing or expired exp claim", issuer)
        return None

    method = payload.get("lxm")
    if method != lexicon_method:
        logger.warning(
            "Rejecting JWT from %s: lexicon method %r does not match %r",
            issuer, method, lexicon_method,
        )
        return None

    if not await _signature_is_valid(issuer, signing_input, signature):
        logger.warning("Rejecting JWT: invalid signature for issuer %s", issuer)
        return None

    return issuer


async def _signature_is_valid(issuer: str, signing_input: bytes, signature: bytes) -> bool:
    # Retry once with a fresh DID document in case verification failed because
    # the issuer recently rotated their signing key, mirroring atproto's own
    # verifyJwt behaviour.
    for force_refresh in (False, True):
        try:
            signing_key = await _did_resolver.resolve_atproto_key(
                issuer, force_refresh=force_refresh
            )
        except Exception:
            logger.warning("Could not resolve signing key for %s", issuer, exc_info=True)
            return False
        try:
            if verify_signature(signing_key, signing_input, signature):
                return True
        except Exception:
            logger.warning("Could not verify JWT signature for %s", issuer, exc_info=True)
            return False
    return False


def _bearer_token(authorization_header: str | None) -> str | None:
    if not authorization_header or not authorization_header.startswith(BEARER_PREFIX):
        return None
    return authorization_header[len(BEARER_PREFIX):].strip()


def _parse_jwt(token: str) -> tuple[dict, bytes, bytes]:
    segments = token.split(".")
    if len(segments) != 3:
        raise ValueError("JWT must have three segments")
    payload = json.loads(_b64url_decode(segments[1]))
    signing_input = f"{segments[0]}.{segments[1]}".encode("ascii")
    signature = _b64url_decode(segments[2])
    return payload, signing_input, signature


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)
