import datetime
import pathlib
from dataclasses import dataclass

import orjson
from backports import zstd

# From https://github.com/bluesky-social/jetstream/blob/main/pkg/models/zstd_dictionary
ATPROTO_ZSTD_DICT_LOCATION = pathlib.Path(__file__).parent / "zstd_dictionary"
ATPROTO_ZSTD_DICT = zstd.ZstdDict(ATPROTO_ZSTD_DICT_LOCATION.read_bytes())
COMPRESSOR = zstd.ZstdCompressor(
    zstd_dict=ATPROTO_ZSTD_DICT,
    options={
        zstd.CompressionParameter.dict_id_flag: 0,
    },
)


REPOST_COLLECTION = "app.bsky.feed.repost"


@dataclass
class AtprotoCompactRecord:
    did: str
    collection: str
    rkey: str
    cid: str
    time_us: int
    # For reposts: the original post that was reposted, referenced by both its
    # at-uri and cid. The uri is the post to surface (and gives its author); the
    # cid is used to link the repost to that post when ranking.
    repost_subject_uri: str | None = None
    repost_subject_cid: str | None = None

    @classmethod
    def from_raw(cls, record: dict):
        collection = record["commit"]["collection"]
        repost_subject_uri = None
        repost_subject_cid = None
        if collection == REPOST_COLLECTION:
            subject = record["commit"].get("record", {}).get("subject", {})
            repost_subject_uri = subject.get("uri")
            repost_subject_cid = subject.get("cid")
        return cls(
            did=record["did"],
            rkey=record["commit"]["rkey"],
            collection=collection,
            cid=record["commit"]["cid"],
            time_us=record["time_us"],
            repost_subject_uri=repost_subject_uri,
            repost_subject_cid=repost_subject_cid,
        )

    @property
    def is_repost(self) -> bool:
        return self.collection == REPOST_COLLECTION

    @property
    def at_uri(self):
        return f"at://{self.did}/{self.collection}/{self.rkey}"

    def serialize(self):
        # Drop unset fields (the repost-only ones on a plain post) to keep the
        # stored footprint minimal.
        present_fields = {key: value for key, value in self.__dict__.items() if value is not None}
        return COMPRESSOR.compress(
            orjson.dumps(present_fields, option=orjson.OPT_SORT_KEYS),
            mode=COMPRESSOR.FLUSH_FRAME,
        )

    @classmethod
    def deserialize(cls, data: bytes):
        return cls(**orjson.loads(zstd.decompress(data, zstd_dict=ATPROTO_ZSTD_DICT)))

    @property
    def dt(self):
        return datetime.datetime.fromtimestamp(self.time_us / 1e6, tz=datetime.timezone.utc)
