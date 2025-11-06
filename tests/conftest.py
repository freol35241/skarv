import pytest
import skarv


@pytest.fixture(autouse=True)
def clean_skarv():
    """Clean the skarv state between tests to prevent test contamination."""
    yield
    # Clear the vault after each test
    skarv._vault.clear()
    # Clear the subscribers, middlewares, and triggers
    skarv._subscribers.clear()
    skarv._middlewares.clear()
    skarv._triggers.clear()
    # Clear the caches as well
    skarv._find_matching_subscribers.cache_clear()
    skarv._find_matching_middlewares.cache_clear()
    skarv._find_matching_triggers.cache_clear()
