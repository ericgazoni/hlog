import base64
import arrow  # type: ignore
import hashlib
import json
from collections import namedtuple
from typing import Sequence, List, Tuple
from uuid import uuid4

_Record = namedtuple("_Record", ("message", "timestamp", "hash"))
hf = hashlib.sha512


class ModifiedRecordException(Exception):
    def __init__(self, *args, **kwargs):
        self.index = kwargs.pop("index")
        self.record = kwargs.pop("record")
        super().__init__(*args, **kwargs)
        self.message = "Signature of record #{}, created on {} does not match its content".format(
            self.index, self.record.timestamp
        )


class Record(_Record):
    def dump(self):
        return b" ".join((self.timestamp, base64.b64encode(self.hash), self.message))

    @property
    def fields(self):
        return json.loads(base64.b64decode(self.message).decode("utf-8"))


def _hash(previous_hash, timestamp, message):
    data = b"".join((previous_hash, timestamp, message))
    return hf(data).digest()


def build_record(fields: dict, previous_hash: bytes, timezone: str = None) -> Record:
    timestamp = arrow.now(timezone).isoformat().encode("utf-8")
    message = base64.b64encode(json.dumps(fields).encode("utf-8"))
    hash = _hash(previous_hash, timestamp, message)
    return Record(message, timestamp, hash)


def verify_record(record: Record, previous_hash: bytes, current_hash: bytes) -> bool:
    return _hash(previous_hash, record.timestamp, record.message) == current_hash


class Chain:
    def __init__(self, root_hash: bytes = None, timezone: str = "UTC"):
        self.records: List[Record] = []
        self.timezone = timezone
        if root_hash is None:
            self.root_hash = uuid4().bytes
        else:
            self.root_hash = root_hash

    def append(self, **fields: Sequence[object]) -> bytes:
        if self.records:
            ph = self.records[-1].hash
        else:
            ph = self.root_hash
        rec = build_record(fields=fields, previous_hash=ph, timezone=self.timezone)
        self.records.append(rec)
        return rec.hash

    def dump(self) -> Tuple[bytes]:
        return tuple(rec.dump() for rec in self.records)

    @classmethod
    def from_dump(cls, records: Sequence[bytes]):
        c = Chain()
        for record in records:
            timestamp, hash, message = record.split(b" ")
            c.records.append(
                Record(timestamp=timestamp, hash=base64.b64decode(hash), message=message)
            )
        return c

    def verify(self, seq: int = None, hash: bytes = None, raise_on_error: bool = False) -> bool:
        if seq is not None and hash is not None:
            if not self.records[seq].hash == hash:
                if raise_on_error:
                    raise ModifiedRecordException(index=seq, record=self.records[seq])
                else:
                    return False

        for idx, rec in enumerate(self.records[1:], start=1):
            if not verify_record(rec, self.records[idx - 1].hash, rec.hash):
                if raise_on_error:
                    raise ModifiedRecordException(index=idx, record=rec)
                else:
                    return False
            ph = rec.hash
        return True
