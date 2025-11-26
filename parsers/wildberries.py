from __future__ import annotations

import asyncio
import logging
import os
from config import get_random_headers

logger = logging.getLogger(__name__)

WB_SEARCH_URL = "https://search.wb.ru/exactmatch/ru/common/v7/search"
WB_ITEM_URL = "https://www.wildberries.ru/catalog/{article}/detail.aspx"
RATE_LIMIT_COOLDOWN = 7200

WB_PROXY_URL = os.getenv("WB_PROXY_URL", "")


class WildberriesParser:
    def __init__(self):
        self.name = "Wildberries"
        self._session = None
        self.rate_limited = False
        self._cooldown_until = 0

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _fetch(self, url: str, params: dict = None) -> dict | None:
        ...

    async def search(self, query: str, limit: int = 20) -> list:
        """Поиск товаров на Wildberries по запросу"""
        ...

    def _parse_results(self, data: dict, limit: int) -> list:
        ...

    def _extract_price(self, product: dict) -> int | None:
        ...
