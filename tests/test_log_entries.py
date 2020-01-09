from hlog import Record, Chain, build_record
from freezegun import freeze_time

EXPECTED_HASH = b"\x18\x9e\x06y\x94\x0c\x0fK\xcd\xd2\x8c.^xNV\xfb\xc6d\xd0%\xfb\xd2q\xfa\xb7\xc8\x0b|\xd9\xff\xaf\x90o\xdb>b\x9c\x8f\xa2g\xc3\xef\x811\xcd@m\xf4\xfeWKUM\x15\xdd\x08\xbc\xadNl\x94\x07\x05"
BASE_TIME = "2012-08-26 00:05:30+00:02"

PRISTINE_CHAIN_HASH = b"\xb5\xe7^Ag\xb4\xf4?\xe1R\x05\x9d\x9d\x138\x8d\x16\xeeS\xac\xb8\xfc{J*\x02\xb6_zW\rm\xdd|\xc1\xfb\xe4YMyT\x0b\xa4\x03\x88C\x10\xea\x05\x86\x01\xad\xda\xcce\xb7\x9d\x93\xf3\xcd\x90\xba@\xe8"


@freeze_time(BASE_TIME)
def test_record_generates_message_from_parts():
    r = build_record(parts={"key1": "value1", "key2": "value2"}, previous_hash=b"")
    assert r.message == b"key1=value1 key2=value2"


@freeze_time(BASE_TIME)
def test_record_generates_hash_from_parts():
    r = build_record(parts={"key1": "value1", "key2": "value2"}, previous_hash=b"0000")

    assert r.hash == EXPECTED_HASH


@freeze_time(BASE_TIME)
def test_record_generates_hash_from_previous_hash():
    r = build_record(parts={"key1": "value1", "key2": "value2"}, previous_hash=b"00000")
    assert r.hash != EXPECTED_HASH


@freeze_time("2012-08-26 00:05:30+00:03")
def test_record_generates_hash_from_parts_and_timestamp():
    r = build_record(parts={"key1": "value1", "key2": "value2"}, previous_hash=b"0000")
    assert r.hash != EXPECTED_HASH


@freeze_time(BASE_TIME)
def test_record_generates_different_hash_from_different_parts():
    r1 = build_record(parts={"key1": "value1", "key2": "value2"}, previous_hash=b"0000")
    r2 = build_record(parts={"key1": "value1", "key2": "value1"}, previous_hash=b"0000")

    assert r1.hash != r2.hash


@freeze_time(BASE_TIME)
def test_chain_creates_records_from_parts():

    c = Chain(root_hash=b"0000")
    c.append(key1="value1", key2="value2")

    assert c.records[-1].hash == EXPECTED_HASH


@freeze_time(BASE_TIME)
def test_pristine_chain_can_be_verified():
    c = Chain(root_hash=b"0000")
    c.append(message="hello")
    c.append(message="wonderful")
    c.append(message="world")
    assert c.verify(seq=2, hash=PRISTINE_CHAIN_HASH)


@freeze_time(BASE_TIME)
def test_chain_cannot_be_amended():
    c = Chain(root_hash=b"0000")
    c.append(message="hello")
    c.append(message="wonderful")
    c.append(message="world")
    c.records[1] = c.records[1]._replace(message=b"message=goodbye")
    assert not c.verify(seq=2, hash=PRISTINE_CHAIN_HASH)


@freeze_time(BASE_TIME)
def test_log_entries_can_be_chained():
    c = Chain(root_hash=b"0000")
    c.append(message="hello")
    c.append(message="wonderful")
    c.append(message="world")

    d = c.dump()

    c2 = Chain.from_dump(d)

    assert c2.verify(seq=2, hash=PRISTINE_CHAIN_HASH)
