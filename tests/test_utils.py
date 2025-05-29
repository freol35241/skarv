import time
import splice

import pytest


def test_maximum_rate_control():

    count = 0

    @splice.rate_control(at_most_every=0.1)
    def callback():
        nonlocal count
        count += 1

    start = time.time()

    # Call function 100 times during 1 second
    while time.time() - start < 1:
        callback()
        time.sleep(0.01)

    # It should still only have 10 invocations
    assert count == 10


def test_minimum_rate_control():

    count = 0

    @splice.rate_control(at_least_every=0.1)
    def callback():
        nonlocal count
        count += 1

    # We need to call it once so that we know about the call signature
    callback()

    # Dont call the function explicitly during a second
    time.sleep(1)

    # It should still have 10 invocations
    assert count == 10
