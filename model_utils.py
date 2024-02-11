import random


def calculate_sleep_time(retries: int, initial_delay: float, backoff_factor: float,
                         jitter: float, max_delay: float) -> float:
    """
    The function returns the calculated sleep time, which is then used by the continue_conversation function to
    pause execution before attempting another retry. The function calculates the sleep time using the following
    steps:

    1. Calculate the base sleep time by multiplying the `initial_delay` by the `backoff_factor` raised to the power
        of `retries`. This results in an exponential increase in sleep time with each retry.

    2. Add a random jitter value to the base sleep time. The jitter value is calculated as a random float between
        `-jitter * sleep_time and jitter * sleep_time`. This randomization helps avoid the synchronization of
        retries across multiple instances, which could lead to the "thundering herd" problem.

    3. Limit the sleep time to the `max_delay` value. This ensures that the delay between retries does not exceed
        a predefined maximum.

    Calculates the sleep time for a retry attempt using exponential backoff with jitter.

    Parameters
    ----------
    retries : int
        The number of retries that have been attempted so far.
    initial_delay : float
        The initial delay in seconds between retries.
    backoff_factor : float
        The factor by which the delay increases exponentially.
    jitter : float
        The random factor to apply to the sleep time calculation.
    max_delay : float
        The maximum delay in seconds between retries.

    Returns
    -------
    sleep_time : float
        The calculated sleep time in seconds.
    """
    sleep_time = initial_delay * (backoff_factor ** retries)
    sleep_time += random.uniform(-jitter * sleep_time, jitter * sleep_time)
    return min(sleep_time, max_delay)


def log_retries(retries, sleep_time, e_rror):
    """ Logs a message for retry attempts and sleep time.

    Parameters
    ----------
    retries : int
        The number of retries that have been attempted so far.
    sleep_time : float
    The calculated sleep time in seconds.

    """
    retry = f"Retry attempt {retries} failed. Waiting {sleep_time:.2f} seconds before trying again. Error: {e_rror}"
    return retry
