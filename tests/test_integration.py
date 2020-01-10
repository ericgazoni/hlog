from hlog import Chain, build_record


def test_logging_actions():
    c = Chain()

    c.append(message="Alice gives 10.36 euros to Bob", amount=10.36, currency="EUR")
    c.append(message="Bob gives 2 dollars to Alice", amount=2, currency="USD")

    d = c.dump()

    c2 = Chain.from_dump(d)

    used_currencies = set(r.fields["currency"] for r in c2.records)

    assert used_currencies == {"EUR", "USD"}
    assert c2.verify()


def test_tampering_raises_an_exception():
    c = Chain()

    h0 = c.append(message="Alice gives 10.36 euros to Bob", amount=10.36, currency="EUR")
    h1 = c.append(message="Bob gives 2 dollars to Alice", amount=2, currency="USD")
    h2 = c.append(message="Bob gives 1 dollar to Charles", amount=1, currency="USD")
    c.records[1] = build_record({"message": "good"}, previous_hash=c.records[0].hash)

    assert not c.verify(seq=1, hash=h1)
