import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import (
    add_product, get_active_products, clear_products, get_stats,
    update_min_profit,
)
from price_parser import parse_price_list, format_product_list
from keyboards import (
    main_keyboard, settings_keyboard, confirm_keyboard,
    profit_options_keyboard,
)
from config import MIN_PROFIT, CHECK_INTERVAL

logger = logging.getLogger(__name__)
router = Router()

MAX_MESSAGE_LENGTH = 4000  # Telegram лимит 4096, оставляем запас


class PriceListStates(StatesGroup):
    waiting_price_list = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # Сбрасываем FSM при /start (на случай если пользователь застрял в состоянии)
    await state.clear()
    await message.answer(
        "👋 <b>Мониторинг цен на маркетплейсах</b>\n\n"
        "Я отслеживаю цены на WB, Ozon и Яндекс Маркет.\n"
        "Загрузи прайс-лист — и я уведомлю, когда найду товар дешевле.\n\n"
        "📋 <b>Как пользоваться:</b>\n"
        "1. Нажми «Загрузить прайс» и отправь прайс-лист\n"
        "2. Я буду проверять цены каждые 5 минут\n"
        "3. Если найду выгодную цену — сразу пришлю ссылку\n\n"
        "Минимальная выгода для уведомления: <b>{:,}₽</b>".format(MIN_PROFIT),
        parse_mode="HTML",
        reply_markup=main_keyboard(),
    )


@router.message(F.text == "➕ Загрузить прайс")
async def load_price_list(message: Message, state: FSMContext):
    await state.set_state(PriceListStates.waiting_price_list)
    await message.answer(
        "📝 Отправь прайс-лист в формате:\n\n"
        "<code>Air 256 Black eSim 🇺🇸 76000\n"
        "17 Pro 256 Blue eSim 🇺🇸 102000\n"
        "17 Pro Max 512 Silver eSim 🇯🇵 139500</code>\n\n"
        "Или просто скопируй и отправь весь прайс.",
        parse_mode="HTML",
    )


@router.message(PriceListStates.waiting_price_list)
async def process_price_list(message: Message, state: FSMContext):
    text = message.text
    if not text:
        await message.answer(
            "❌ Отправь прайс-лист текстом.\n"
            "Для отмены нажми /start"
        )
        return

    products = parse_price_list(text)
    if not products:
        await message.answer(
            "❌ Не удалось распознать товары в прайс-листе.\n"
            "Проверь формат и попробуй ещё раз."
        )
        return

    # Очищаем старый прайс перед загрузкой нового
    await clear_products(message.from_user.id)

    # Сохраняем товары в БД
    added = 0
    for p in products:
        await add_product(
            user_id=message.from_user.id,
            name=p["search_query"],
            model=p["model"],
            storage=p["storage"],
            color=p["color"],
            sim_type=p["sim_type"],
            country=p["country"],
            target_price=p["price"],
            min_profit=MIN_PROFIT,
        )
        added += 1

    await state.clear()

    formatted = format_product_list(products)
    full_text = (
        f"✅ <b>Загружено {added} товаров!</b>\n"
        f"{formatted}\n\n"
        f"🔍 Мониторинг запущен. Проверяю цены каждые "
        f"{CHECK_INTERVAL // 60} минут.\n"
        f"💰 Уведомлю если найду дешевле на {MIN_PROFIT:,}₽+"
    )

    # Разбиваем длинное сообщение на части
    if len(full_text) > MAX_MESSAGE_LENGTH:
        # Отправляем подтверждение отдельно
        await message.answer(
            f"✅ <b>Загружено {added} товаров!</b>\n\n"
            f"🔍 Мониторинг запущен. Проверяю цены каждые "
            f"{CHECK_INTERVAL // 60} минут.\n"
            f"💰 Уведомлю если найду дешевле на {MIN_PROFIT:,}₽+",
            parse_mode="HTML",
            reply_markup=main_keyboard(),
        )
        # Отправляем список товаров отдельным сообщением
        product_text = f"📋 <b>Загруженные товары:</b>\n{formatted}"
        # Если и список слишком длинный — разбиваем на части
        while product_text:
            chunk = product_text[:MAX_MESSAGE_LENGTH]
            # Обрезаем по последнему переводу строки чтобы не ломать форматирование
            if len(product_text) > MAX_MESSAGE_LENGTH:
                last_nl = chunk.rfind("\n")
                if last_nl > 100:
                    chunk = product_text[:last_nl]
                    product_text = product_text[last_nl:]
                else:
                    product_text = product_text[MAX_MESSAGE_LENGTH:]
            else:
                product_text = ""
            await message.answer(chunk, parse_mode="HTML")
    else:
        await message.answer(full_text, parse_mode="HTML", reply_markup=main_keyboard())

    logger.info(f"User {message.from_user.id} loaded {added} products")


@router.message(F.text == "📋 Мой прайс")
async def show_price_list(message: Message):
    products = await get_active_products(message.from_user.id)
    if not products:
        await message.answer(
            "📋 Прайс-лист пуст.\n"
            "Нажми «Загрузить прайс» чтобы добавить товары.",
        )
        return

    # Берём актуальную мин. выгоду из БД (не глобальную)
    user_min_profit = products[0].get("min_profit", MIN_PROFIT)

    header = f"📋 <b>Ваш прайс-лист ({len(products)} товаров):</b>\n\n"
    footer = f"\n\n🔍 Мониторинг активен\n💰 Мин. выгода: {user_min_profit:,}₽"

    # Разбиваем на части чтобы не превысить лимит Telegram (4096 символов)
    current_msg = header
    for i, p in enumerate(products, 1):
        line = (
            f"{i}. <b>{p['name']}</b> {p['color']} — "
            f"<b>{p['target_price']:,}₽</b>\n"
        )
        if len(current_msg) + len(line) > MAX_MESSAGE_LENGTH:
            await message.answer(current_msg, parse_mode="HTML")
            current_msg = ""
        current_msg += line

    current_msg += footer
    await message.answer(current_msg, parse_mode="HTML")


@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message):
    stats = await get_stats(message.from_user.id)

    # Берём актуальную мин. выгоду из БД
    products = await get_active_products(message.from_user.id)
    user_min_profit = products[0].get("min_profit", MIN_PROFIT) if products else MIN_PROFIT

    await message.answer(
        f"📊 <b>Статистика</b>\n\n"
        f"📱 Товаров на мониторинге: <b>{stats['active_products']}</b>\n"
        f"🔔 Всего уведомлений: <b>{stats['total_alerts']}</b>\n"
        f"⏱ Интервал проверки: <b>{CHECK_INTERVAL // 60} мин</b>\n"
        f"💰 Мин. выгода: <b>{user_min_profit:,}₽</b>",
        parse_mode="HTML",
    )


@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: Message):
    # Берём актуальную мин. выгоду из БД
    products = await get_active_products(message.from_user.id)
    user_min_profit = products[0].get("min_profit", MIN_PROFIT) if products else MIN_PROFIT

    await message.answer(
        "⚙️ <b>Настройки мониторинга</b>",
        parse_mode="HTML",
        reply_markup=settings_keyboard(user_min_profit, CHECK_INTERVAL),
    )


@router.callback_query(F.data == "info_interval")
async def info_interval(callback: CallbackQuery):
    await callback.answer(
        f"Интервал проверки: {CHECK_INTERVAL // 60} мин. "
        "Изменить можно в .env (CHECK_INTERVAL)",
        show_alert=True,
    )


@router.callback_query(F.data == "set_min_profit")
async def set_min_profit(callback: CallbackQuery):
    await callback.message.edit_text(
        "💰 Выбери минимальную выгоду для уведомления:",
        reply_markup=profit_options_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("profit_"))
async def apply_profit(callback: CallbackQuery):
    value = int(callback.data.split("_")[1])
    await update_min_profit(callback.from_user.id, value)
    await callback.message.edit_text(
        f"✅ Минимальная выгода установлена: <b>{value:,}₽</b>",
        parse_mode="HTML",
        reply_markup=settings_keyboard(value, CHECK_INTERVAL),
    )
    await callback.answer()


@router.callback_query(F.data == "clear_products")
async def clear_products_confirm(callback: CallbackQuery):
    await callback.message.edit_text(
        "🗑 Очистить весь прайс-лист? Мониторинг будет остановлен.",
        reply_markup=confirm_keyboard("clear"),
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_clear")
async def clear_products_do(callback: CallbackQuery):
    await clear_products(callback.from_user.id)
    await callback.message.edit_text("✅ Прайс-лист очищен.")
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery):
    await callback.message.edit_text("❌ Отменено.")
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery):
    # Берём актуальную мин. выгоду из БД
    products = await get_active_products(callback.from_user.id)
    user_min_profit = products[0].get("min_profit", MIN_PROFIT) if products else MIN_PROFIT

    await callback.message.edit_text(
        "⚙️ <b>Настройки мониторинга</b>",
        parse_mode="HTML",
        reply_markup=settings_keyboard(user_min_profit, CHECK_INTERVAL),
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        # Сообщение может быть слишком старым для удаления (>48ч)
        pass
    await callback.message.answer("👌", reply_markup=main_keyboard())
    await callback.answer()
