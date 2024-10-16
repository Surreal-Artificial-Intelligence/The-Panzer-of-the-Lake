from dataclasses import dataclass


@dataclass
class RetryPolicy:
    max_retries: int = 5
    initial_delay: int = 1
    backoff_factor: int = 2
    jitter: float = 0.1
    max_delay: int = 32
