"""Tests for service-auth JWT verification.

A request to the feed server carries the requester's identity as a service-auth
JWT signed by their repo key. ``get_requester_did`` must only return a DID
when the signature is valid and the audience, expiry and lexicon-method claims
match, so that nobody can spoof another account (e.g. to forge "seen" records).
"""

import base64
import json
import time

import pytest
from atproto_crypto.consts import SECP256K1_CURVE_ORDER, SECP256K1_JWT_ALG
from atproto_crypto.did import format_did_key
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

from feed_server import auth
from feed_server.config import FEED_SERVER_DID

GET_FEED_SKELETON = "app.bsky.feed.getFeedSkeleton"
SEND_INTERACTIONS = "app.bsky.feed.sendInteractions"
ISSUER_DID = "did:plc:exampleissuer000000000000"


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


class SigningIdentity:
    """A secp256k1 key pair that mints service-auth JWTs like a user's PDS does."""

    def __init__(self) -> None:
        self._private_key = ec.generate_private_key(ec.SECP256K1())
        compressed_public_key = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.CompressedPoint,
        )
        self.did_key = format_did_key(SECP256K1_JWT_ALG, compressed_public_key)

    def _sign(self, signing_input: bytes) -> bytes:
        der_signature = self._private_key.sign(signing_input, ec.ECDSA(hashes.SHA256()))
        r, s = decode_dss_signature(der_signature)
        if s > SECP256K1_CURVE_ORDER // 2:  # atproto requires the low-S variant
            s = SECP256K1_CURVE_ORDER - s
        return r.to_bytes(32, "big") + s.to_bytes(32, "big")

    def make_jwt(self, payload: dict, tampered_payload: dict | None = None) -> str:
        header = _b64url(json.dumps({"typ": "JWT", "alg": "ES256K"}).encode())
        signed_body = _b64url(json.dumps(payload).encode())
        signature = self._sign(f"{header}.{signed_body}".encode("ascii"))
        # When tampered_payload is set, the visible body no longer matches what was
        # signed, simulating an attacker editing claims after the token was issued.
        body = signed_body if tampered_payload is None else _b64url(json.dumps(tampered_payload).encode())
        return f"{header}.{body}.{_b64url(signature)}"

    def bearer(self, payload: dict, tampered_payload: dict | None = None) -> str:
        return f"Bearer {self.make_jwt(payload, tampered_payload)}"


@pytest.fixture
def identity() -> SigningIdentity:
    return SigningIdentity()


@pytest.fixture(autouse=True)
def resolve_to_identity(identity, monkeypatch):
    """Resolve the issuer DID to the test identity's key, without any network call."""

    async def fake_resolve_atproto_key(did: str, force_refresh: bool = False) -> str:
        assert did == ISSUER_DID
        return identity.did_key

    monkeypatch.setattr(auth._did_resolver, "resolve_atproto_key", fake_resolve_atproto_key)


def valid_payload(**overrides) -> dict:
    payload = {
        "iss": ISSUER_DID,
        "aud": FEED_SERVER_DID,
        "exp": int(time.time()) + 60,
        "lxm": GET_FEED_SKELETON,
    }
    payload.update(overrides)
    return payload


async def test_valid_token_returns_issuer_did(identity):
    requester_did = await auth.get_requester_did(
        identity.bearer(valid_payload()), lexicon_method=GET_FEED_SKELETON
    )
    assert requester_did == ISSUER_DID


async def test_missing_authorization_header_is_anonymous():
    assert await auth.get_requester_did(None, lexicon_method=GET_FEED_SKELETON) is None


async def test_non_bearer_authorization_is_anonymous():
    assert await auth.get_requester_did("Basic abc", lexicon_method=GET_FEED_SKELETON) is None


async def test_malformed_jwt_is_rejected():
    assert await auth.get_requester_did(
        "Bearer not.a-jwt", lexicon_method=GET_FEED_SKELETON
    ) is None


async def test_forged_signature_is_rejected(identity):
    token = identity.make_jwt(valid_payload())
    header, body, signature = token.split(".")
    forged_signature = _b64url(bytes(b ^ 0xFF for b in auth._b64url_decode(signature)))
    forged = f"Bearer {header}.{body}.{forged_signature}"
    assert await auth.get_requester_did(forged, lexicon_method=GET_FEED_SKELETON) is None


async def test_tampered_issuer_is_rejected(identity):
    # Attacker keeps the original (valid) signature but swaps the iss claim.
    bearer = identity.bearer(
        valid_payload(), tampered_payload=valid_payload(iss="did:plc:attacker")
    )
    assert await auth.get_requester_did(bearer, lexicon_method=GET_FEED_SKELETON) is None


async def test_wrong_audience_is_rejected(identity):
    bearer = identity.bearer(valid_payload(aud="did:web:evil.example"))
    assert await auth.get_requester_did(bearer, lexicon_method=GET_FEED_SKELETON) is None


async def test_expired_token_is_rejected(identity):
    bearer = identity.bearer(valid_payload(exp=int(time.time()) - 5))
    assert await auth.get_requester_did(bearer, lexicon_method=GET_FEED_SKELETON) is None


async def test_token_for_another_method_is_rejected(identity):
    # A token obtained for reading the feed must not be replayable to send interactions.
    bearer = identity.bearer(valid_payload(lxm=GET_FEED_SKELETON))
    assert await auth.get_requester_did(bearer, lexicon_method=SEND_INTERACTIONS) is None


async def test_missing_lexicon_method_is_rejected(identity):
    payload = valid_payload()
    del payload["lxm"]
    assert await auth.get_requester_did(
        identity.bearer(payload), lexicon_method=GET_FEED_SKELETON
    ) is None


async def test_signature_reverified_after_key_rotation(identity, monkeypatch):
    # The cached key is stale; verification must retry with a force-refreshed key.
    async def resolve_with_rotation(did: str, force_refresh: bool = False) -> str:
        if not force_refresh:
            return SigningIdentity().did_key  # stale key, signature will not match
        return identity.did_key

    monkeypatch.setattr(auth._did_resolver, "resolve_atproto_key", resolve_with_rotation)

    requester_did = await auth.get_requester_did(
        identity.bearer(valid_payload()), lexicon_method=GET_FEED_SKELETON
    )
    assert requester_did == ISSUER_DID
