from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мой прайс"), KeyboardButton(text="➕ Загрузить прайс")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="⚙️ Настройки")],
        ],
        resize_keyboard=True,
    )


def settings_keyboard(min_profit: int, interval: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"💰 Мин. выгода: {min_profit:,}₽",
            callback_data="set_min_profit"
        )],
        [InlineKeyboardButton(
            text=f"⏱ Интервал: {interval // 60} мин",
            callback_data="info_interval"
        )],
        [InlineKeyboardButton(text="🗑 Очистить прайс", callback_data="clear_products")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")],
    ])


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}"),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel"),
        ]
    ])


def profit_options_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="3 000₽", callback_data="profit_3000"),
            InlineKeyboardButton(text="5 000₽", callback_data="profit_5000"),
        ],
        [
            InlineKeyboardButton(text="7 000₽", callback_data="profit_7000"),
            InlineKeyboardButton(text="10 000₽", callback_data="profit_10000"),
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_settings")],
    ])
