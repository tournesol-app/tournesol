import logging

from atproto_core.exceptions import AtProtocolError
from atproto_identity.cache.in_memory_cache import AsyncDidInMemoryCache
from atproto_identity.did.resolver import AsyncDidResolver
from atproto_server.auth.jwt import verify_jwt_async

from .config import FEED_SERVER_DID

logger = logging.getLogger(__name__)

BEARER_PREFIX = "Bearer "
DID_KEY_PREFIX = "did:key:"
CLOCK_LEEWAY_SECONDS = 10

_did_resolver = AsyncDidResolver(
    cache=AsyncDidInMemoryCache(
        stale_ttl=24 * 60 * 60,  # 24 hours
        max_ttl=8 * 24 * 60 * 60,  # 8 days
    )
)


async def get_requester_did(authorization_header: str | None, lexicon_method: str) -> str | None:
    """Return the verified DID of the account making the request, or ``None``.

    Bluesky sends the requester's identity as a service-auth JWT in the
    ``Authorization`` header: the ``iss`` claim is the requester's DID and the
    token is signed by their repo key. ``verify_jwt_async`` checks the
    signature against the issuer's DID document, plus the audience and expiry;
    we additionally require the expiry and lexicon-method claims.

    ``None`` means the request is unauthenticated or the token was invalid.
    """
    token = _bearer_token(authorization_header)
    if token is None:
        return None

    # TODO: the service-auth spec also asks receivers to use the ``jti`` nonce
    # to prevent replays (remember seen values until the token's ``exp``).
    # For now replays are only bounded by the token's short lifetime.
    try:
        payload = await verify_jwt_async(
            token, _get_signing_key, own_did=FEED_SERVER_DID, leeway=CLOCK_LEEWAY_SECONDS
        )
    except AtProtocolError as e:
        logger.warning("Rejecting requester JWT: %s", e)
        return None
    except Exception:
        # e.g. a did:web host serving a malformed DID document: the resolver
        # only wraps HTTP errors, so parsing errors surface here.
        logger.warning("Unexpected error while verifying requester JWT", exc_info=True)
        return None

    if payload.exp is None:
        logger.warning("Rejecting JWT from %s: missing exp claim", payload.iss)
        return None

    method = getattr(payload, "lxm", None)
    if method != lexicon_method:
        logger.warning(
            "Rejecting JWT from %s: lexicon method %r does not match %r",
            payload.iss,
            method,
            lexicon_method,
        )
        return None

    return payload.iss


async def _get_signing_key(issuer: str, force_refresh: bool) -> str:
    # The resolver returns a did:key as its own signing key, so anyone could mint
    # a valid token for a fresh identity. A did:key is never an atproto account.
    if issuer.startswith(DID_KEY_PREFIX):
        raise AtProtocolError(f"did:key issuer is not an atproto account: {issuer}")
    return await _did_resolver.resolve_atproto_key(issuer, force_refresh=force_refresh)


def _bearer_token(authorization_header: str | None) -> str | None:
    if not authorization_header or not authorization_header.startswith(BEARER_PREFIX):
        return None
    return authorization_header[len(BEARER_PREFIX) :].strip()
