from hlog import Chain


def test_logging_actions():
    c = Chain()

    c.append(message="Alice gives 10.36 euros to Bob", amount=10.36, currency="EUR")
    c.append(message="Bob gives 2 dollars to Alice", amount=2, currency="USD")

    d = c.dump()

    c2 = Chain.from_dump(d)

    used_currencies = set(r.fields["currency"] for r in c2.records)

    assert used_currencies == {"EUR", "USD"}
