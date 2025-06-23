import time
import operator
from threading import Lock
from functools import cache
from collections import deque
from typing import Callable, Any, Union, Sequence

Numeric = Union[int, float]


def throttle(at_most_every: float) -> Callable[[Any], Any | None]:
    """Create a throttling middleware that allows values through at most once every specified interval.

    Args:
        at_most_every (float): Minimum interval in seconds between allowed values.

    Returns:
        Callable[[Any], Any | None]: Middleware function that returns the value or None if throttled.
    """
    lock = Lock()
    last_call_time = 0.0

    def _throttler(value: Any) -> Any | None:
        nonlocal last_call_time

        with lock:

            now = time.time()

            # Should we throttle?
            if (now - last_call_time) < at_most_every:
                return None

            last_call_time = now
            return value

    return _throttler


def average(no_of_samples: int) -> Callable[[Numeric], Numeric]:
    """Create a middleware that computes the moving average over a window of samples.

    Args:
        no_of_samples (int): Number of samples to average over.

    Returns:
        Callable[[Numeric], Numeric]: Middleware function that returns the moving average.
    """
    lock = Lock()
    window = deque(maxlen=no_of_samples)

    def _averager(value: Numeric) -> Numeric:
        nonlocal window

        with lock:

            window.append(value)

            return sum(window) / len(window)

    return _averager


@cache
def _get_weights(no_of_samples: int) -> Sequence[float]:
    sum_of_smaller_integers = (no_of_samples - 1) * (no_of_samples / 2) + no_of_samples
    return [number / sum_of_smaller_integers for number in range(no_of_samples, 0, -1)]


def weighted_average(no_of_samples: int) -> Callable[[Numeric], Numeric]:
    """Create a middleware that computes a weighted moving average over a window of samples.

    Args:
        no_of_samples (int): Number of samples to use for the weighted average.

    Returns:
        Callable[[Numeric], Numeric]: Middleware function that returns the weighted moving average.
    """
    lock = Lock()
    window = deque(maxlen=no_of_samples)

    def _averager(value: Numeric) -> Numeric:
        nonlocal window

        with lock:

            window.appendleft(value)

            return sum(map(operator.mul, window, _get_weights(len(window))))

    return _averager


def differentiate() -> Callable[[Numeric], Numeric | None]:
    """Create a middleware that computes the numerical derivative of the input values.

    Returns:
        Callable[[Numeric], Numeric | None]: Middleware function that returns the derivative or None for the first value.
    """
    lock = Lock()
    last_value = None
    last_time = None

    def _differentiator(value: Numeric) -> Numeric | None:
        nonlocal last_value, last_time

        with lock:

            if last_value is None:
                last_value = value
                last_time = time.time()
                return None

            now = time.time()

            derivative = (value - last_value) / (now - last_time)

            last_value = value
            last_time = now

            return derivative

    return _differentiator


def batch(size: int) -> Callable[[Any], Sequence[Any] | None]:
    """Create a middleware that batches input values and outputs them as a sequence when the batch size is reached.

    Args:
        size (int): The number of values to collect before emitting a batch.

    Returns:
        Callable[[Any], Sequence[Any] | None]: Middleware function that returns a batch or None if not enough values have been collected.
    """
    lock = Lock()
    batch = []

    def _batcher(value: Any) -> Sequence[Any] | None:

        with lock:
            batch.append(value)

            if len(batch) >= size:
                output = tuple(batch)
                batch.clear()
                return output

            return None

    return _batcher
