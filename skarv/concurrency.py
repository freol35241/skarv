import logging
import asyncio
import threading
from typing import Awaitable

logger = logging.getLogger(__name__)

_background_loop = None


def schedule_coroutine(coro: Awaitable) -> asyncio.Future:
    """Schedule a coroutine to run in a background asyncio event loop.

    If the background event loop is not running, it will be started in a new thread.

    Args:
        coro (Awaitable): The coroutine to schedule.

    Returns:
        asyncio.Future: A Future representing the execution of the coroutine.
    """
    global _background_loop

    if _background_loop is None:
        logger.info("Starting asyncio event loop in background thread")
        _background_loop = asyncio.new_event_loop()

        def _initializer():
            asyncio.set_event_loop(_background_loop)
            _background_loop.run_forever()
            logger.info("Background event loop initialized.")

        threading.Thread(target=_initializer, daemon=True).start()

    logger.debug("Scheduling coroutine...")
    return asyncio.run_coroutine_threadsafe(coro, _background_loop)
