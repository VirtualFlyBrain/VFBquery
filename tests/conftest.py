"""Shared test helpers.

``run`` lives here because three test modules need it and `pytest-asyncio` is
not a dependency of this package. Adding one to run a handful of coroutines
would put a plugin in the way of the CI install for no coverage in return; a
fresh loop per test is four lines and has no version to keep in step.
"""
import asyncio


def run(coro):
    """Run one coroutine on a fresh loop, and close the loop afterwards.

    Fresh rather than shared: several of these tests leave a deliberately
    cancelled request behind, and a loop reused across tests would carry that
    into the next one as a stray task.
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
