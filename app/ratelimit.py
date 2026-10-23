"""Rate limiting (slowapi). Counters are kept in memory, per process."""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Every route gets DEFAULT_RATE_LIMIT; sensitive routes add a stricter one.
from app import config

limiter = Limiter(
    key_func=get_remote_address,  # one bucket per client IP
    default_limits=[config.DEFAULT_RATE_LIMIT],
)
