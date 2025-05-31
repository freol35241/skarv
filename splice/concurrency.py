import time
import atexit
import logging
import asyncio
import threading
from functools import wraps, partial
from typing import Awaitable, Callable, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, Future

logger = logging.getLogger(__name__)

_background_loop = None


def schedule_coroutine(coro: Awaitable) -> asyncio.Future:
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


_executor = ThreadPoolExecutor()
atexit.register(_executor.shutdown)


def run_in_executor(func: Callable, *args, **kwargs):

    def _done_callback(fut: Future):
        try:
            fut.result()
        except Exception:
            logger.exception("Exception raised in task run in executor")

    _executor.submit(func, *args, **kwargs).add_done_callback(_done_callback)
