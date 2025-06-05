import time
from skarv.utilities import call_every


def test_call_every():

    count = 0

    @call_every(0.1)
    def callback():
        nonlocal count
        count += 1

    # Sleep for 1 second
    time.sleep(1)

    # It should have 10 invocations at 0.0, 0.1 ... 0.9 seconds
    assert count == 10


def test_call_every_wait_first():

    count = 0

    @call_every(0.1, wait_first=True)
    def callback():
        nonlocal count
        count += 1

    # Sleep for 1 second
    time.sleep(1)

    # It should have 9 invocations at 0.1, 0.2 ... 0.9 seconds
    assert count == 9
