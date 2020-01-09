# Principles


- Records are immutable
- Records are ordered
- It must be possible to check `hash(Xi)` for any `i`
- `hash(Xi)` can be sent to anyone as a proof
- `hash(Xi) == hash(X, hash(Xi-1))`
- You do not need X to perform the check?