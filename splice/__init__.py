from dataclasses import dataclass
from collections import defaultdict, deque
from typing import Dict, Callable, Deque, Any, Set

from functools import partial

from zenoh import KeyExpr


@dataclass(frozen=True)
class Sample:
    key_expr: KeyExpr
    value: Any

@dataclass(frozen=True)
class _Subscriber:
    key_expr: KeyExpr
    callback: Callable

_vault: Dict[KeyExpr, Deque[Any]] = defaultdict(partial(deque, maxlen=1))
_subscribers: Set[_Subscriber] = set()


def put(key: str, value: Any):

    ke: KeyExpr = KeyExpr.autocanonize(key)

    _vault[ke].append(value)

    # Trigger subscribers
    sample = Sample(ke, value)
    for subscriber in _subscribers:
        if ke.intersects(subscriber.key_expr):
            subscriber.callback(sample)

def subscribe(*keys: str):

    def decorator(callback: Callable):
        for key in keys:
            ke = KeyExpr.autocanonize(key)
            _subscribers.add(_Subscriber(ke, callback))

        return callback

    return decorator

def get(key: str):
    req_ke = KeyExpr.autocanonize(key)
    return [
        Sample(rep_ke, values[-1]) for rep_ke, values in _vault.items() if req_ke.intersects(rep_ke)
    ]



