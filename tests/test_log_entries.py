from hlog import Chain, build_record, ModifiedRecordException
import pytest
from freezegun import freeze_time

EXPECTED_HASH = b'L\xf6;i$\xf5`\x8f\x90M\x8e!S\x94\xe1\xce\xe2F\xec\x80\x8a#E&\x8a\xba\xa9\xe1\x10\xcdw\xb5K\xdcdNY\xbfEqf\x86\x0eU\x1b\x8d\x06\xe4\xe3\x7fY\xdf\xe4\xf9"\xfd\xa3\x84\x88}\xa6\x01\xe32'

BASE_TIME = "2012-08-26 00:05:30+02:00"

PRISTINE_CHAIN_HASH = b"\x9e7\x1c\xf3\x83^\xf4\x8e\x81#z\xca\xb6\x07\xbb\xd4 \xe7\x0f\xf8\x015\xea\x8e\x93\xaa\x15\xd8\x08\xeb\xa2W\xb4i\xd1\x84\x88habC\x83\xcek\xcc\x1a\x1bH\x06\xc86sw\xdd\x84\xc8\xcb\xf4\xe0\xbd\xf1\xa0\xf9\xc0"


@freeze_time(BASE_TIME)
def test_record_generates_message_from_parts():
    r = build_record(fields={"key1": "value1", "key2": "value2"}, previous_hash=b"")
    assert r.message == b"eyJrZXkxIjogInZhbHVlMSIsICJrZXkyIjogInZhbHVlMiJ9"


@freeze_time(BASE_TIME)
def test_record_generates_hash_from_parts():
    r = build_record(
        fields={"key1": "value1", "key2": "value2"}, previous_hash=b"0000", timezone="UTC"
    )
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
    h1 = c.append(key1="value1", key2="value2")

    assert h1 == EXPECTED_HASH


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

    assert c2.records[0].timestamp == b"2012-08-26T08:05:30+10:00"

