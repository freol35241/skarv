import time
import splice
from splice.middlewares import throttle

import pytest


def test_throttle_middleware():

    count = 0

    @splice.subscribe("throttled")
    def callback(_):
        nonlocal count
        count += 1

    splice.register_middleware("throttled", throttle(at_most_every=0.1))

    start = time.time()

    # Publish at 100Hz during a second
    while time.time() - start < 1:
        splice.put("throttled", 42)
        time.sleep(0.01)

    # It should still only have 10 invocations
    assert count == 10
