from uuid import uuid4
import hashlib
import datetime
from collections import namedtuple

_Record = namedtuple("_Record", "message timestamp hash".split())
hf = hashlib.sha512


class Record(_Record):
    def dump(self):
        return b" ".join((self.timestamp, self.hash, self.message))


def _hash(previous_hash, timestamp, message):
    data = b"".join((previous_hash, timestamp, message))
    return hf(data).digest()


def build_record(parts, previous_hash):
    timestamp = datetime.datetime.now().isoformat().encode("utf-8")
    message = " ".join("=".join(item) for item in parts.items())
    message = message.encode("utf-8")
    hash = _hash(previous_hash, timestamp, message)
    return Record(message, timestamp, hash)


def verify_record(record, previous_hash, current_hash):
    return _hash(previous_hash, record.timestamp, record.message) == current_hash


class Chain:
    def __init__(self, root_hash=None):
        self.records = []
        if root_hash is None:
            self.root_hash = uuid4().bytes
        else:
            self.root_hash = root_hash

    def append(self, **parts):
        if self.records:
            ph = self.records[-1].hash
        else:
            ph = self.root_hash
        rec = build_record(parts=parts, previous_hash=ph)
        self.records.append(rec)
        return len(self.records), rec.hash

    def dump(self):
        return [rec.dump() for rec in self.records]

    @classmethod
    def from_dump(cls, records):
        c = Chain()
        for record in records:
            timestamp, hash, message = record[:19], record[20:84], record[85:]
            c.records.append(Record(timestamp=timestamp, hash=hash, message=message))
        return c

    def verify(self, seq, hash):
        if not self.records[seq].hash == hash:
            print("target record incorrect")
            return False

        for idx, rec in enumerate(self.records[1:], start=1):
            if not verify_record(rec, self.records[idx - 1].hash, rec.hash):
                return False
            ph = rec.hash
        return True
