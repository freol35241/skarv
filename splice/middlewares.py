import time
from typing import Callable, Any


def throttle(at_most_every: float) -> Callable[[Any], Any]:

    last_call_time = 0.0

    def _throttler(value: Any) -> Any | None:
        nonlocal last_call_time

        now = time.time()

        # Should we throttle?
        if (now - last_call_time) < at_most_every:
            return None

        last_call_time = now
        return value

    return _throttler
