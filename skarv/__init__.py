import logging
from threading import Lock
from dataclasses import dataclass
from functools import cache
from typing import Dict, Callable, Any, Set, List

from zenoh import KeyExpr

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Sample:
    key_expr: KeyExpr
    value: Any


@dataclass(frozen=True)
class Subscriber:
    key_expr: KeyExpr
    callback: Callable[[Any], None]


@dataclass(frozen=True)
class Middleware:
    key_expr: KeyExpr
    operator: Callable[[Any], Any]


_vault: Dict[KeyExpr, Any] = dict()
_vault_lock = Lock()

_subscribers: Set[Subscriber] = set()
_middlewares: Set[Middleware] = set()


@cache
def _find_matching_subscribers(key: str) -> List[Subscriber]:
    return [
        subscriber for subscriber in _subscribers if subscriber.key_expr.intersects(key)
    ]


@cache
def _find_matching_middlewares(key: str) -> List[Middleware]:
    return [
        middleware for middleware in _middlewares if middleware.key_expr.intersects(key)
    ]


def put(key: str, value: Any):
    ke: KeyExpr = KeyExpr.autocanonize(key)

    # Pass through middlewares
    for middleware in _find_matching_middlewares(key):
        value = middleware.operator(value)

        if value is None:
            return

    # Add final value to vault
    with _vault_lock:
        _vault[ke] = value

    # Trigger subscribers
    sample = Sample(ke, value)
    for subscriber in _find_matching_subscribers(key):
        subscriber.callback(sample)


def subscribe(*keys: str):
    logger.debug("Subscribing to: %s", keys)

    # Adding a new subscriber means we need to clear the cache
    _find_matching_subscribers.cache_clear()
    logger.debug("Cleared subscriber cache.")

    def decorator(callback: Callable):
        for key in keys:
            ke = KeyExpr.autocanonize(key)
            logger.debug("Adding internal Subscriber for %s", ke)
            _subscribers.add(Subscriber(ke, callback))

        return callback

    return decorator


def get(key: str) -> List[Sample]:
    logger.debug("Getting for %s", key)
    req_ke = KeyExpr.autocanonize(key)

    with _vault_lock:
        samples = [
            Sample(rep_ke, value)
            for rep_ke, value in _vault.items()
            if req_ke.intersects(rep_ke)
        ]

    return samples


def register_middleware(key: str, operator: Callable[[Any], Any]):
    logger.debug("Registering middleware on %s", key)
    ke = KeyExpr.autocanonize(key)
    _middlewares.add(Middleware(ke, operator))
    _find_matching_middlewares.cache_clear()


__all__ = [
    "Sample",
    "put",
    "subscribe",
    "get",
    "register_middleware",
]
