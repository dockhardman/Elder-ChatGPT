import asyncio
import time


def time_time() -> float:
    """Simple return time.time().

    Returns
    -------
    float
        time.time()

    Notes
    -----
    To avoid from ValueError: no signature found for builtin <built-in function time>.
    """

    return time.time()


async def async_time() -> float:
    """Simple return time.time().

    Returns
    -------
    float
        time.time()
    """

    await asyncio.sleep(0)
    return time.time()
