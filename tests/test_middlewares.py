import time
import skarv
from skarv.middlewares import throttle, average, weighted_average, differentiate, batch

import pytest


def test_throttle_middleware():

    throttler = throttle(at_most_every=0.1)

    start = time.time()

    output = []

    # Call at 100Hz during a second
    while time.time() - start < 1:
        output.append(throttler(42))
        time.sleep(0.01)

    # It should still only have 10 invocations
    assert output.count(42) == 10


def test_average_middleware():

    averager = average(2)

    assert averager(2) == 2
    assert averager(4) == 3
    assert averager(5) == 4.5
    assert averager(15) == 10


def test_weighted_average_middleware():

    weighted_averager = weighted_average(no_of_samples=3)

    assert weighted_averager(2) == 2
    assert weighted_averager(4) == pytest.approx(4 * 2 / 3 + 2 * 1 / 3)
    assert weighted_averager(6) == pytest.approx(6 * 3 / 6 + 4 * 2 / 6 + 2 * 1 / 6)


def test_differentiate_middleware():

    differentiator = differentiate()

    assert differentiator(1) is None
    assert differentiator(1) == 0
    time.sleep(1)
    assert differentiator(2) == pytest.approx(1, rel=0.05)


def test_batch_middleware():

    batcher = batch(2)

    assert batcher(1) is None
    assert batcher(1) == (1, 1)
    assert batcher(2) == None
    assert batcher(3) == (2, 3)
