import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ============ НАСТРОЙКИ ============
BOT_TOKEN = "8873918058:AAErvi7MmR3ZyIEwEndHNcwq1KgizySFToU"
ADMIN_IDS = [8442940149, 7063169118]  # <-- ID админов

WELCOME_TEXT = (
    "👋 Добро пожаловать!\n\n"
    "Здесь ты можешь подать заявку на дуэль "
    "или подать заявку на вступление в клан [SERHI].\n\n"
    "Выбери действие:"
)

DUEL_ASK_ID = "🎯 Отправь свой ID в Standoff 2 :"
DUEL_ASK_TG = "📨 Теперь отправь свой юзернейм в Telegram (например, @username):"
DUEL_DONE = "✅ Заявка на дуэль отправлена! Ожидай ответа."

CLAN_ASK_ID = "🛡 Отправь свой Standoff 2 ID для вступления в клан [SERHI]:"
CLAN_DONE = "✅ Заявка в клан [SERHI] отправлена! Админ свяжется с тобой."

# ==================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ---------- Состояния ----------
class DuelForm(StatesGroup):
    waiting_so_id = State()
    waiting_tg_username = State()


class ClanForm(StatesGroup):
    waiting_so_id = State()


# ---------- Клавиатура ----------
def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Играть дуэль", callback_data="duel")],
        [InlineKeyboardButton(text="🛡 Вступить в клан [SERHI]", callback_data="clan")],
    ])


# ---------- /start ----------
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())


# ---------- Кнопка "Дуэль" ----------
@dp.callback_query(F.data == "duel")
async def cb_duel(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(DUEL_ASK_ID)
    await state.set_state(DuelForm.waiting_so_id)
    await call.answer()


@dp.message(DuelForm.waiting_so_id)
async def duel_get_id(message: Message, state: FSMContext):
    await state.update_data(so_id=message.text)
    await message.answer(DUEL_ASK_TG)
    await state.set_state(DuelForm.waiting_tg_username)


@dp.message(DuelForm.waiting_tg_username)
async def duel_get_tg(message: Message, state: FSMContext):
    data = await state.get_data()
    so_id = data.get("so_id")
    tg_username = message.text
    await state.clear()

    await message.answer(DUEL_DONE, reply_markup=main_menu())

    # Отправляем заявку всем админам
    text = (
        "⚔️ Новая заявка на ДУЭЛЬ\n\n"
        f"👤 От: {message.from_user.full_name} "
        f"(tg://user?id={message.from_user.id}"
        f"🎮 Standoff 2 ID: {so_id}\n"
        f"📨 Telegram: {tg_username}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            logging.warning(f"Не удалось отправить админу {admin_id}: {e}")


# ---------- Кнопка "Клан" ----------
@dp.callback_query(F.data == "clan")
async def cb_clan(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(CLAN_ASK_ID)
    await state.set_state(ClanForm.waiting_so_id)
    await call.answer()


@dp.message(ClanForm.waiting_so_id)
async def clan_get_id(message: Message, state: FSMContext):
    so_id = message.text
    await state.clear()

    await message.answer(CLAN_DONE, reply_markup=main_menu())

    text = (
        "🛡 Новая заявка в КЛАН [SERHI]\n\n"
        f"👤 От: {message.from_user.full_name} "
        f"'tg://user?id={message.from_user.id}\n"
        f"🎮 Standoff 2 ID: {so_id}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            logging.warning(f"Не удалось отправить админу {admin_id}: {e}")


# ---------- Команда /admin (для проверки что ты админ) ----------
@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У тебя нет доступа.")
        return
    await message.answer("✅ Ты админ. Все новые заявки будут приходить сюда автоматически.")


# ---------- Запуск ----------
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())