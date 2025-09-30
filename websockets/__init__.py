import asyncio
from contextlib import asynccontextmanager

from .exceptions import ConnectionClosed, InvalidURI


class _MockWebSocket:
    async def send(self, message):
        await asyncio.sleep(0)

    async def recv(self):
        await asyncio.sleep(0)
        return ""


@asynccontextmanager
async def connect(url, extra_headers=None, subprotocols=None, ssl=None, timeout=None):
    if not isinstance(url, str) or not url:
        raise InvalidURI("Invalid URL")
    ws = _MockWebSocket()
    try:
        yield ws
    finally:
        pass
