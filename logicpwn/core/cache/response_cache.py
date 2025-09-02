"""
HTTP response cache for LogicPwn.
"""

from typing import Any, Optional

from .cache_manager import CacheManager


class ResponseCache:
    def __init__(self, max_size: int = 500, default_ttl: int = 300):
        self.cache_manager = CacheManager(max_size, default_ttl)

    def get_response(
        self,
        url: str,
        method: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Optional[Any]:
        key = self._generate_response_key(url, method, params, headers)
        return self.cache_manager.get(key)

    def set_response(
        self,
        url: str,
        method: str,
        response: Any,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        ttl: Optional[int] = None,
    ) -> None:
        key = self._generate_response_key(url, method, params, headers)
        metadata = {"url": url, "method": method, "params": params, "headers": headers}
        self.cache_manager.set(key, response, ttl, metadata)

    def _generate_response_key(
        self, url: str, method: str, params: Optional[dict], headers: Optional[dict]
    ) -> str:
        key_data = f"{url}:{method}:{params}:{headers}"
        return self.cache_manager._generate_key(key_data)
