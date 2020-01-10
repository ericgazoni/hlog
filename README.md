# HashLog
[![Coverage Status](https://coveralls.io/repos/github/ericgazoni/hlog/badge.svg?branch=master)](https://coveralls.io/github/ericgazoni/hlog?branch=master)

# Principles

- Records are immutable
- Records are ordered
- It must be possible to check `hash(Xi)` for any `i`
- `hash(Xi)` can be sent to anyone as a proof
- `hash(Xi) == hash(X, hash(Xi-1))`
- You do not need X to perform the check

# Installation

    $ pip install hlog

# Usage

## Getting started

```python
# create a chain
c = Chain()

# send some messages
c.append(message="Alice gives 10.36 euros to Bob", amount=10.36, currency="EUR")
c.append(message="Bob gives 2 dollars to Alice", amount=2, currency="USD")

# you can loop through the chain records
used_currencies = set(r.fields["currency"] for r in c.records)

# call verify() to ensure records have not been modified
c.verify()
```

## Raising an exception during validation

```python
c.verify(raise_on_error=True)
```
Verify will raise a `ModifiedRecordException`. It has 3 interesting attributes:

- `index`: the index in the chain where validation starts to fail
- `message`: a user-friendly message to indicate the error
- `record`: the `Record` object itself

## Dumping

```python
c = Chain()
c.append(message="hello")
c.append(message="wonderful")
c.append(message="world")

rows = c.dump()
```
`rows` is a `tuple` of `bytes`, each item being one record of the chain.

## Restoring from a dump

If you want to reconstruct your chain based on a file or database records, you can use `Chain.from_dump()`
```python
c = Chain()
c.append(message="hello")
c.append(message="wonderful")
c.append(message="world")

d = c.dump()

c2 = Chain.from_dump(d)

c2.verify()
```