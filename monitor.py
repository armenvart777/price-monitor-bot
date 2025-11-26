from __future__ import annotations

import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError

from config import CHECK_INTERVAL, MIN_PROFIT
from database import get_active_products, add_alert, add_price_history, was_already_notified
from parsers import WildberriesParser, OzonParser, YandexMarketParser
from ai_analyzer import analyze_matches

logger = logging.getLogger(__name__)

wb_parser = WildberriesParser()
ozon_parser = OzonParser()
ym_parser = YandexMarketParser()

ALL_PARSERS = [wb_parser, ozon_parser]
# YM отключён — SmartCaptcha блокирует без headless-браузера


async def check_product(bot: Bot, user_id: int, product: dict) -> int:
    """Check one product across all marketplaces. Returns number of alerts sent."""
    ...


async def run_monitoring(bot: Bot) -> None:
    """Background loop: check all active products every CHECK_INTERVAL seconds."""
    ...


async def close_parsers() -> None:
    for parser in ALL_PARSERS:
        await parser.close()
