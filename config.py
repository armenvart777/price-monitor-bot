import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MIN_PROFIT = int(os.getenv("MIN_PROFIT", 5000))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))  # секунды (5 минут)

DB_PATH = "price_monitor.db"

# Anthropic API для AI-анализа товаров
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Прокси для запросов к маркетплейсам (обход блокировок)
# Форматы: http://user:pass@host:port, socks5://user:pass@host:port
PROXY_URL = os.getenv("PROXY_URL", "")

# Отдельный прокси для WB (если нужен другой IP)
WB_PROXY_URL = os.getenv("WB_PROXY_URL", "")

# Пул User-Agent'ов для ротации (реальные браузеры)
USER_AGENTS = [
    # Chrome 131 Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # Chrome 130 Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    # Chrome 131 Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # Chrome 130 Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    # Firefox 132 Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    # Firefox 131 Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    # Edge 131
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    # Safari 17 Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

def get_random_headers() -> dict:
    """Возвращает заголовки с рандомным User-Agent"""
    import random
    ua = random.choice(USER_AGENTS)
    is_firefox = "Firefox" in ua
    is_safari = "Safari" in ua and "Chrome" not in ua

    headers = {
        "User-Agent": ua,
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
    }

    if is_firefox:
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    elif is_safari:
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    else:
        headers["Accept"] = "application/json, text/plain, */*"
        headers["Sec-Ch-Ua"] = f'"Chromium";v="{ua.split("Chrome/")[1][:3]}", "Not_A Brand";v="24"'
        headers["Sec-Ch-Ua-Mobile"] = "?0"
        headers["Sec-Ch-Ua-Platform"] = '"Windows"' if "Windows" in ua else '"macOS"'

    return headers

# Дефолтные заголовки (для обратной совместимости)
HEADERS = {
    "User-Agent": USER_AGENTS[0],
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
}
