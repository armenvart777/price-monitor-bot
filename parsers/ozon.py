from __future__ import annotations

import asyncio
import time
import aiohttp
import logging
import re

from config import get_random_headers, PROXY_URL

try:
    from aiohttp_socks import ProxyConnector
except ImportError:
    ProxyConnector = None

logger = logging.getLogger(__name__)

OZON_API_URL = "https://api.ozon.ru/composer-api.bx/page/json/v2"
OZON_ITEM_URL = "https://www.ozon.ru"
RATE_LIMIT_COOLDOWN = 1800


class OzonParser:
    def __init__(self):
        self.name = "Ozon"
        self._session = None
        self.rate_limited = False
        self._cooldown_until = 0

    async def _new_session(self) -> aiohttp.ClientSession:
        ...

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _fetch_with_retry(self, url: str, params: dict = None,
                                max_retries: int = 3) -> tuple[int, str | None]:
        ...

    async def search(self, query: str, limit: int = 20) -> list:
        """Поиск товаров на Ozon по названию"""
        ...

    async def _search_api(self, query: str, limit: int, api_url: str) -> list:
        ...

    def _parse_search_results(self, data: dict, limit: int) -> list:
        ...

    def _parse_item(self, item: dict) -> dict | None:
        ...

    def _extract_price_from_text(self, text: str) -> int | None:
        if not text:
            return None
        digits = re.sub(r"[^\d]", "", text)
        if digits:
            price = int(digits)
            if 30000 <= price <= 500000:
                return price
        return None
