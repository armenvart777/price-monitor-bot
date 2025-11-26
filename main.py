import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database import init_db
from handlers import router
from monitor import run_monitoring, close_parsers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        logger.error("BOT_TOKEN not set in .env file!")
        return

    await init_db()
    logger.info("Database initialized")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    # Запускаем мониторинг цен в фоне
    monitoring_task = asyncio.create_task(run_monitoring(bot))

    logger.info("Bot started!")
    try:
        await dp.start_polling(bot)
    finally:
        # Корректное завершение
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass

        # Закрываем aiohttp сессии парсеров
        await close_parsers()
        logger.info("Parser sessions closed")

        await bot.session.close()
        logger.info("Bot session closed")


if __name__ == "__main__":
    asyncio.run(main())
