import logging
from dataclasses import dataclass
from collections import defaultdict, deque
from threading import Lock
from typing import Dict, Callable, Deque, Any, Set, List

from functools import partial, cache

from zenoh import KeyExpr

from .concurrency import run_in_executor

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Sample:
    key_expr: KeyExpr
    value: Any


@dataclass(frozen=True)
class Subscriber:
    key_expr: KeyExpr
    callback: Callable[[Any], None]
    run_in_threadpool: bool


@dataclass(frozen=True)
class Middleware:
    key_expr: KeyExpr
    operator: Callable[[Any], Any]


_vault: Dict[KeyExpr, Deque[Any]] = defaultdict(partial(deque, maxlen=1))
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
    logger.debug("Putting on %s with %s", key, value)
    ke: KeyExpr = KeyExpr.autocanonize(key)
    logger.debug("Canonized key expression: %s", ke)

    # Pass through middlewares
    for middleware in _find_matching_middlewares(key):
        logger.debug("Applying middleware registered on %s", middleware.key_expr)
        logger.debug("  Input: %s", value)
        value = middleware.operator(value)
        logger.debug("  Output: %s", value)

        if value is None:
            logger.debug("Got None value, breaking early.")
            return

    # Add final value to vault
    with _vault_lock:
        _vault[ke].append(value)

    # Trigger subscribers
    sample = Sample(ke, value)
    for subscriber in _find_matching_subscribers(key):
        logger.debug(
            "Calling %s, subscribed on %s,  with %s",
            subscriber.callback,
            subscriber.key_expr,
            sample,
        )
        if subscriber.run_in_threadpool:
            run_in_executor(subscriber.callback, sample)
        else:
            subscriber.callback(sample)


def subscribe(*keys: str, run_in_threadpool: bool = False):
    logger.debug("Subscribing to: %s", keys)

    # Adding a new subscriber means we need to clear the cache
    _find_matching_subscribers.cache_clear()
    logger.debug("Cleared subscriber cache.")

    def decorator(callback: Callable):
        for key in keys:
            ke = KeyExpr.autocanonize(key)
            logger.debug("Adding internal Subscriber for %s", ke)
            _subscribers.add(Subscriber(ke, callback, run_in_threadpool))

        return callback

    return decorator


def get(key: str):
    logger.debug("Getting for %s", key)
    req_ke = KeyExpr.autocanonize(key)

    with _vault_lock:
        samples = [
            Sample(rep_ke, values[-1])
            for rep_ke, values in _vault.items()
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
