import asyncio
import threading
from typing import Awaitable


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


def rate_limit(at_most_every=None, at_least_every=None):

    def decorator(callback):
        queue = asyncio.Queue()
        last_emit = 0.0
        last_call = ()

        async def throttle_task():
            nonlocal last_emit, last_call
            while True:
                try:
                    print("waiting on queue...")
                    args_kwargs = await asyncio.wait_for(queue.get(), timeout=at_least_every or 3600)
                    print("Got item!")
                    now = asyncio.get_event_loop().time()
                    dt = now - last_emit
                    print("dt = ", dt)
                    if dt < at_most_every:
                        print("Sleeping...")
                        await asyncio.sleep(at_most_every - dt)
                    last_emit = asyncio.get_event_loop().time()
                    last_value = args_kwargs
                    print("Calling callback!")
                    callback(*args_kwargs[0], **args_kwargs[1])
                    print("Callback called sucessfully!")
                except asyncio.TimeoutError:
                    if last_value is not None:
                        callback(*last_call[0], **last_call[1])
                        last_emit = asyncio.get_event_loop().time()

        schedule_async_hook(throttle_task()).add_done_callback(print)

        def wrapper(*args, **kwargs):
            print("Putting to queue!")
            queue.put_nowait((args, kwargs))

        return wrapper

    return decorator