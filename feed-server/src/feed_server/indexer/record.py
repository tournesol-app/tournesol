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


@dataclass
class AtprotoCompactRecord:
    did: str
    collection: str
    rkey: str
    cid: str
    time_us: int

    @classmethod
    def from_raw(cls, record: dict):
        return cls(
            did=record["did"],
            rkey=record["commit"]["rkey"],
            collection=record["commit"]["collection"],
            cid=record["commit"]["cid"],
            time_us=record["time_us"],
        )

    @property
    def at_uri(self):
        return f"at://{self.did}/{self.collection}/{self.rkey}"

    def serialize(self):
        return COMPRESSOR.compress(
            orjson.dumps(self, option=orjson.OPT_SORT_KEYS),
            mode=COMPRESSOR.FLUSH_FRAME,
        )

    @classmethod
    def deserialize(cls, data: bytes):
        return cls(**orjson.loads(zstd.decompress(data, zstd_dict=ATPROTO_ZSTD_DICT)))

    @property
    def dt(self):
        return datetime.datetime.fromtimestamp(self.time_us / 1e6, tz=datetime.timezone.utc)
