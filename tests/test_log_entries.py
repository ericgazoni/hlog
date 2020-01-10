from hlog import Chain, build_record, ModifiedRecordException
import pytest
from freezegun import freeze_time

EXPECTED_HASH = b"\xe20\xe3\x9a\xffB\xf0\xd5\x0cg\x95\xae\xfc\xb5H\x86+\xa6\xe0\x85\xbe\xf5VX\x8e\x1bA.A\xcd$\xbf\xc6\xc4\xba2\x04\x87\x14\xb1-?\xd7\x92\x91\xdc3\x15y\x81\xd0\xdc\xd6\x86\xb9\xc9\x87\x13\xb2\xa0\xc8\x1c\xd2!"
BASE_TIME = "2012-08-26 00:05:30+00:02"

PRISTINE_CHAIN_HASH = b"?\x08\x1dKz\xd2\x1d\xe1\x83\x86Z9\x02\xb4\xd4W\x9d\xca\x98\xd4\xa2\xfc\x98\x07\x08\x8dG\x0cX\xc4\x93\xc0\xdd\x83-&\xd8\x12\xd8\xf8&\xc0\x8d\rw@\x02K\xd4K>\x85\x99b]C\x1d\xc3\xae\xda\xd5&u\x93"


@freeze_time(BASE_TIME)
def test_record_generates_message_from_parts():
    r = build_record(fields={"key1": "value1", "key2": "value2"}, previous_hash=b"")
    assert r.message == b"eyJrZXkxIjogInZhbHVlMSIsICJrZXkyIjogInZhbHVlMiJ9"


@freeze_time(BASE_TIME)
def test_record_generates_hash_from_parts():
    r = build_record(fields={"key1": "value1", "key2": "value2"}, previous_hash=b"0000")

    assert r.hash == EXPECTED_HASH


@freeze_time(BASE_TIME)
def test_record_generates_hash_from_previous_hash():
    r = build_record(fields={"key1": "value1", "key2": "value2"}, previous_hash=b"00000")
    assert r.hash != EXPECTED_HASH


@freeze_time("2012-08-26 00:05:30+00:03")
def test_record_generates_hash_from_parts_and_timestamp():
    r = build_record(fields={"key1": "value1", "key2": "value2"}, previous_hash=b"0000")
    assert r.hash != EXPECTED_HASH


@freeze_time(BASE_TIME)
def test_record_generates_different_hash_from_different_parts():
    r1 = build_record(fields={"key1": "value1", "key2": "value2"}, previous_hash=b"0000")
    r2 = build_record(fields={"key1": "value1", "key2": "value1"}, previous_hash=b"0000")

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


@freeze_time(BASE_TIME)
def test_chain_modification_can_be_explained():
    c = Chain(root_hash=b"0000")
    c.append(message="hello")
    c.append(message="wonderful")
    c.append(message="world")
    save_r1 = c.records[1]
    c.records[1] = build_record({"message": "good"}, previous_hash=c.records[0].hash)

    with pytest.raises(ModifiedRecordException) as ex:
        c.verify(raise_on_error=True)
    exc = ex.value
    assert exc.index == 2
    assert exc.message
    assert exc.record == c.records[2]

    with pytest.raises(ModifiedRecordException) as ex:
        c.verify(seq=1, hash=save_r1.hash, raise_on_error=True)
    exc = ex.value
    assert exc.index == 1
    assert exc.message
    assert exc.record == c.records[1]


@freeze_time(BASE_TIME)
def test_logs_can_be_stored_in_a_different_timezone():
    c1 = Chain(timezone="Europe/Brussels")
    c2 = Chain(timezone="Australia/Sydney")

    c1.append(message="hello world")
    c2.append(message="hello world")

    assert c1.records[0].timestamp != c2.records[0].timestamp
