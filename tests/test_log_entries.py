from hlog import Chain, build_record
from freezegun import freeze_time

EXPECTED_HASH = b"\x1ajV\xfaN\xda\xbb\xbcr\x06|W\xa2\x10\x00S)\x91\xd5\x92\x9d\x04\x94\xf8\xe4-\x98\x9b\xadX\x92\x8c\xab\xc3\xfc\x8d\x7fy\xaejK}iZ\xa8\xed9\xba\x1b\xbe\xd0\\\xcd\x84h\xcc\xff\xd3\xbc\x88]\xfc=\x1e"
BASE_TIME = "2012-08-26 00:05:30+00:02"

PRISTINE_CHAIN_HASH = b"\x1fXx\ts\xdb\x83\xcfn\xd4\xe2o\xcb\xf3\xb3)]\x11\xbf}\xca\xef\x7fU\xf88\x83\xf7\xb3\x8a\xbf\xbb\x8e\xa8\xc4\x9e\xcf\x08\x0c\xae5\x93\xad\xf7\x1d864\x91\xd7MgS\xd3\xdaY/\xd2\xa1\xf1\xc9$\xc4\x9d"


@freeze_time(BASE_TIME)
def test_record_generates_message_from_parts():
    r = build_record(parts={"key1": "value1", "key2": "value2"}, previous_hash=b"")
    assert r.message == b"eyJrZXkxIjogInZhbHVlMSIsICJrZXkyIjogInZhbHVlMiJ9"


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
