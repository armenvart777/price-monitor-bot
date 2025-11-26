from __future__ import annotations

import logging
from config import get_random_headers

logger = logging.getLogger(__name__)

YM_SEARCH_URL = "https://market.yandex.ru/search"
RATE_LIMIT_COOLDOWN = 1200


class YandexMarketParser:
    def __init__(self):
        self.name = "Яндекс Маркет"
        self._session = None
        self.rate_limited = False
        self._cooldown_until = 0

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _fetch_html(self, url: str, params: dict = None,
                          max_retries: int = 2) -> str | None:
        ...

    async def search(self, query: str, limit: int = 20) -> list:
        """Поиск товаров на Яндекс Маркет"""
        ...

    def _parse_html(self, html: str, limit: int) -> list:
        ...
