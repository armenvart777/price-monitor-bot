import aiosqlite
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # WAL mode для лучшей работы при конкурентном доступе
        await db.execute("PRAGMA journal_mode=WAL")

        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                model TEXT,
                storage TEXT,
                color TEXT,
                sim_type TEXT,
                country TEXT,
                target_price INTEGER NOT NULL,
                min_profit INTEGER DEFAULT 5000,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                marketplace TEXT NOT NULL,
                found_name TEXT,
                found_price INTEGER NOT NULL,
                profit INTEGER NOT NULL,
                url TEXT,
                notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                marketplace TEXT NOT NULL,
                price INTEGER NOT NULL,
                url TEXT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # Индексы для быстрых запросов
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_user_active
            ON products(user_id, active)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_product_marketplace
            ON price_alerts(product_id, marketplace, notified_at)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_product
            ON price_history(product_id, marketplace)
        """)

        await db.commit()


async def add_product(user_id: int, name: str, model: str, storage: str,
                      color: str, sim_type: str, country: str,
                      target_price: int, min_profit: int = 5000) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO products (user_id, name, model, storage, color,
               sim_type, country, target_price, min_profit)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, name, model, storage, color, sim_type, country,
             target_price, min_profit)
        )
        await db.commit()
        return cursor.lastrowid


async def get_active_products(user_id: int = None) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if user_id is not None:
            cursor = await db.execute(
                "SELECT * FROM products WHERE active = 1 AND user_id = ?",
                (user_id,)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM products WHERE active = 1"
            )
        return [dict(row) for row in await cursor.fetchall()]


async def deactivate_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE products SET active = 0 WHERE id = ?", (product_id,)
        )
        await db.commit()


async def clear_products(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE products SET active = 0 WHERE user_id = ?", (user_id,)
        )
        await db.commit()


async def add_alert(product_id: int, marketplace: str, found_name: str,
                    found_price: int, profit: int, url: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO price_alerts
               (product_id, marketplace, found_name, found_price, profit, url)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (product_id, marketplace, found_name, found_price, profit, url)
        )
        await db.commit()


async def add_price_history(product_id: int, marketplace: str,
                            price: int, url: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO price_history (product_id, marketplace, price, url)
               VALUES (?, ?, ?, ?)""",
            (product_id, marketplace, price, url)
        )
        await db.commit()


async def was_already_notified(product_id: int, marketplace: str,
                                found_price: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """SELECT id FROM price_alerts
               WHERE product_id = ? AND marketplace = ? AND found_price = ?
               AND notified_at > datetime('now', '-1 hour')""",
            (product_id, marketplace, found_price)
        )
        return await cursor.fetchone() is not None


async def update_min_profit(user_id: int, min_profit: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE products SET min_profit = ? WHERE user_id = ? AND active = 1",
            (min_profit, user_id)
        )
        await db.commit()


async def get_stats(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM products WHERE user_id = ? AND active = 1",
            (user_id,)
        )
        active = (await cursor.fetchone())[0]

        cursor = await db.execute(
            """SELECT COUNT(*) FROM price_alerts pa
               JOIN products p ON pa.product_id = p.id
               WHERE p.user_id = ?""",
            (user_id,)
        )
        alerts = (await cursor.fetchone())[0]

        return {"active_products": active, "total_alerts": alerts}
