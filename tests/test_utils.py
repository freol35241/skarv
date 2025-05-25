import time
from splice.utils import rate_limit

import pytest

@pytest.mark.skip
def test_maximum_rate_limit():

    count = 0

    @rate_limit(at_most_every=0.1)
    def callback():
        nonlocal count
        count += 1

    start = time.time()

    while (time.time() - start < 1):
        callback()
        time.sleep(0.01)

    assert count == 10
