import asyncio
import threading
from typing import Awaitable
from functools import partial


_background_loop = None


def schedule_async_hook(coro: Awaitable):
    global _background_loop

    if _background_loop is None:
        print("Creating background thread")
        _background_loop = asyncio.new_event_loop()

        def _initializer():
            print("Initializing background thread!")
            asyncio.set_event_loop(_background_loop)
            _background_loop.run_forever()

        threading.Thread(target=_initializer, daemon=True).start()

    return asyncio.run_coroutine_threadsafe(coro, _background_loop)


def rate_control(at_most_every=None, at_least_every=None):

    def decorator(callback):
        queue = asyncio.Queue()
        last_emit = 0.0
        last_call = ()

        async def throttle_task():
            nonlocal last_emit, last_call
            while True:
                try:
                    args_kwargs = await asyncio.wait_for(
                        queue.get(), timeout=at_least_every or 3600
                    )
                    now = asyncio.get_event_loop().time()
                    dt = now - last_emit
                    if at_most_every is not None and dt < at_most_every:
                        await asyncio.sleep(at_most_every - dt)
                    last_emit = asyncio.get_event_loop().time()
                    last_call = args_kwargs
                    callback(*(args_kwargs[0]), **(args_kwargs[1]))
                except asyncio.TimeoutError:
                    if last_call:
                        callback(*(last_call[0]), **(last_call[1]))
                        last_emit = asyncio.get_event_loop().time()

        schedule_async_hook(throttle_task()).add_done_callback(
            lambda fut: print(fut.exception())
        )

        def wrapper(*args, **kwargs):
            _background_loop.call_soon_threadsafe(
                partial(queue.put_nowait, (args, kwargs))
            )

        return wrapper

    return decorator
