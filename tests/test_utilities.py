import time
import skarv
from skarv.utilities import call_every
from skarv.utilities.zenoh import mirror
from unittest.mock import MagicMock, Mock


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


def test_mirror_subscription():
    # Create a mock zenoh session
    mock_session = Mock()
    mock_subscriber = Mock()
    mock_session.declare_subscriber = Mock(return_value=mock_subscriber)
    mock_session.get = Mock(return_value=[])

    # Call mirror with unique key to avoid test contamination
    mirror(mock_session, "zenoh/test_subscription", "skarv/test_subscription")

    # Verify subscriber was created
    mock_session.declare_subscriber.assert_called_once()
    call_args = mock_session.declare_subscriber.call_args
    assert call_args[0][0] == "zenoh/test_subscription"

    # Get the callback function that was passed
    callback = call_args[0][1]

    # Create a mock sample
    mock_sample = Mock()
    mock_sample.payload = b"test_payload"

    # Call the callback
    callback(mock_sample)

    # Verify the value was put into skarv
    result = skarv.get("skarv/test_subscription")
    assert result is not None
    assert result.value == b"test_payload"


def test_mirror_initial_value():
    # Create a mock zenoh session with an initial value
    mock_session = Mock()
    mock_session.declare_subscriber = Mock()

    # Create a mock response with initial value
    mock_response = Mock()
    mock_response.ok = Mock()
    mock_response.ok.payload = b"initial_value"
    mock_session.get = Mock(return_value=[mock_response])

    # Call mirror with unique key to avoid test contamination
    mirror(mock_session, "zenoh/test_initial", "skarv/test_initial")

    # Verify get was called on zenoh
    mock_session.get.assert_called_once_with("zenoh/test_initial")

    # Verify the initial value was put into skarv
    result = skarv.get("skarv/test_initial")
    assert result is not None
    assert result.value == b"initial_value"


def test_mirror_no_overwrite():
    # Put an existing value in skarv with unique key
    skarv.put("skarv/test_no_overwrite", b"existing_value")

    # Create a mock zenoh session with an initial value
    mock_session = Mock()
    mock_session.declare_subscriber = Mock()

    # Create a mock response
    mock_response = Mock()
    mock_response.ok = Mock()
    mock_response.ok.payload = b"new_value"
    mock_session.get = Mock(return_value=[mock_response])

    # Call mirror - should not overwrite existing value
    mirror(mock_session, "zenoh/test_no_overwrite", "skarv/test_no_overwrite")

    # Verify the existing value was not overwritten
    result = skarv.get("skarv/test_no_overwrite")
    assert result is not None
    assert result.value == b"existing_value"
