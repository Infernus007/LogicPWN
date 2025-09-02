from .cache_utils import (
    cached,
    clear_all_caches,
    get_cache_stats,
    response_cache,
    session_cache,
)
from .config_cache import config_cache
from .response_cache import ResponseCache
from .session_cache import SessionCache

# For backward compatibility
__all__ = [
    "response_cache",
    "session_cache",
    "config_cache",
    "get_cache_stats",
    "clear_all_caches",
    "cached",
]
