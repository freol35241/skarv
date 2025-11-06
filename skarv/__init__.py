import logging
from threading import Lock
from dataclasses import dataclass
from functools import cache
from typing import Dict, Callable, Any, Set, List, Union

from zenoh import KeyExpr

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Sample:
    """A data sample consisting of a key expression and its associated value.

    Attributes:
        key_expr (KeyExpr): The key expression associated with the sample.
        value (Any): The value of the sample.
    """

    key_expr: KeyExpr
    value: Any


@dataclass(frozen=True)
class Subscriber:
    """A subscriber that listens to updates for a specific key expression.

    Attributes:
        key_expr (KeyExpr): The key expression to subscribe to.
        callback (Callable[[Any], None]): The callback function to invoke when a matching sample is published.
    """

    key_expr: KeyExpr
    callback: Callable[[Any], None]


@dataclass(frozen=True)
class Middleware:
    """A middleware operator that processes values for a specific key expression.

    Attributes:
        key_expr (KeyExpr): The key expression the middleware applies to.
        operator (Callable[[Any], Any]): The operator function to process the value.
    """

    key_expr: KeyExpr
    operator: Callable[[Any], Any]


@dataclass(frozen=True)
class Trigger:
    """A trigger that executes a callback when a matching key expression is published.

    Attributes:
        key_expr (KeyExpr): The key expression to trigger on.
        callback (Callable[[], None]): The callback function to invoke when a matching sample is published.
    """

    key_expr: KeyExpr
    callback: Callable[[], None]


_vault: Dict[KeyExpr, Any] = dict()
_vault_lock = Lock()

_subscribers: Set[Subscriber] = set()
_middlewares: Set[Middleware] = set()
_triggers: Set[Trigger] = set()


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


@cache
def _find_matching_triggers(key: str) -> List[Trigger]:
    return [trigger for trigger in _triggers if trigger.key_expr.intersects(key)]


def put(key: str, value: Any):
    """Store a value for a given key, passing it through any registered middlewares and notifying subscribers.

    Args:
        key (str): The key to associate with the value.
        value (Any): The value to store.
    """
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

    # Trigger triggers
    for trigger in _find_matching_triggers(key):
        trigger.callback()


def subscribe(*keys: str):
    """Decorator to subscribe a callback to one or more keys.

    Args:
        *keys (str): One or more keys to subscribe to.

    Returns:
        Callable: A decorator that registers the callback as a subscriber.
    """
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


def trigger(*keys: str):
    """Decorator to trigger a callback when one or more keys are published.

    Args:
        *keys (str): One or more keys to trigger on.

    Returns:
        Callable: A decorator that registers the callback as a trigger.
    """
    logger.debug("Adding trigger for: %s", keys)

    # Adding a new trigger means we need to clear the cache
    _find_matching_triggers.cache_clear()
    logger.debug("Cleared trigger cache.")

    def decorator(callback: Callable):
        for key in keys:
            ke = KeyExpr.autocanonize(key)
            logger.debug("Adding internal Trigger for %s", ke)
            _triggers.add(Trigger(ke, callback))

        return callback

    return decorator


def get(key: str) -> Union[Sample, List[Sample], None]:
    """Retrieve sample(s) whose keys intersect with the given key.

    For key expressions without wildcards, returns a single Sample or None.
    For key expressions with wildcards, returns a list of matching samples.

    Args:
        key (str): The key to search for.

    Returns:
        Union[Sample, List[Sample], None]: For non-wildcard keys, returns a single Sample or None if not found.
                                            For wildcard keys, returns a list of matching samples.
    """
    logger.debug("Getting for %s", key)
    req_ke = KeyExpr.autocanonize(key)

    with _vault_lock:
        samples = [
            Sample(rep_ke, value)
            for rep_ke, value in _vault.items()
            if req_ke.intersects(rep_ke)
        ]

    # Return single sample for non-wildcard keys, list for wildcard keys
    has_wildcards = "*" in key or "$" in key
    if has_wildcards:
        return samples
    else:
        return samples[0] if samples else None


def register_middleware(key: str, operator: Callable[[Any], Any]):
    """Register a middleware operator for a given key.

    Args:
        key (str): The key to associate with the middleware.
        operator (Callable[[Any], Any]): The operator function to process values.
    """
    logger.debug("Registering middleware on %s", key)
    ke = KeyExpr.autocanonize(key)
    _middlewares.add(Middleware(ke, operator))
    _find_matching_middlewares.cache_clear()


__all__ = [
    "Sample",
    "put",
    "subscribe",
    "trigger",
    "get",
    "register_middleware",
]
