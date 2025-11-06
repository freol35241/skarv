import time
import asyncio
import logging
import warnings
from typing import Callable

from ..concurrency import schedule_coroutine


logger = logging.getLogger(__name__)


def call_every(
    seconds: float,
    wait_first: bool = False,
):
    """Decorator to repeatedly call a function every specified number of seconds.

    Args:
        seconds (float): The interval in seconds between calls.
        wait_first (bool, optional): If True, wait for the interval before the first call. Defaults to False.

    Returns:
        Callable: A decorator that schedules the function to be called periodically.
    """

    def timed_task_decorator(func: Callable) -> Callable:

        is_coroutine = asyncio.iscoroutinefunction(func)

        async def timer():

            if wait_first:
                await asyncio.sleep(seconds)

            while True:
                t_0 = time.time()

                try:
                    if is_coroutine:
                        await func()
                    else:
                        await asyncio.get_event_loop().run_in_executor(None, func)
                except Exception:  # pylint: disable=broad-except
                    logger.exception(f"call_every: Exception in {func}")

                remainder = seconds - (time.time() - t_0)

                if remainder < 0:
                    warnings.warn(
                        f"Function {func} has an execution time the exceeds"
                        f" the requested execution interval of {seconds}s!",
                        UserWarning,
                    )

                await asyncio.sleep(max(remainder, 0))

        # Put `timer` on the event loop on service startup
        schedule_coroutine(timer())
        return func

    return timed_task_decorator
