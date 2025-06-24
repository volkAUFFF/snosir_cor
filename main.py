import asyncio
import sqlite3
from datetime import datetime, timedelta
import os
import sys
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from aiogram.types import InputMediaPhoto
import re
import random
import asyncio
from aiosend import CryptoPay, MAINNET
import sqlite3
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Message
from aiogram.utils.keyboard import  InlineKeyboardBuilder
from aiosend import CryptoPay
from aiogram import F
import asyncio
import logging
import aiohttp
import sys
import asyncio
from contextlib import suppress
import logging
import sys
import os
from os import getenv
import sqlite3
import random
import re
import datetime
import time
from aiogram.exceptions import TelegramBadRequest
from typing import Any
from aiogram import types
from aiogram import Router
from aiogram import Bot, Dispatcher, F   
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.types import PreCheckoutQuery, LabeledPrice
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton , InlineKeyboardMarkup , InlineKeyboardButton , CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
from aiogram.types import ChatPermissions
from aiogram.enums import ChatType
from aiogram.methods.send_gift import SendGift
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiosend import CryptoPay




# ===== НАСТРОЙКА ЛОГИРОВАНИЯ =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout)

BOT_TOKEN = os.getenv("BOT_TOKEN") 
CP_TOKEN = os.getenv("CP_TOKEN") 
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 


ADMIN_ID = {285376592, 767154085}   # вариант 2 - кортеж



ADMIN_IDS = {285376592, 767154085}   # вариант 2 - кортеж

WELCOME_PHOTO = "https://i.postimg.cc/VLn67tqY/photo-2025-06-24-14-23-23.jpg"
logger = logging.getLogger(__name__)




# ===== ПРОВЕРКА НАЛИЧИЯ КЛЮЧЕВЫХ ПЕРЕМЕННЫХ =====
if not BOT_TOKEN:
    logging.error("❌ ОШИБКА: Не указан BOT_TOKEN в переменных окружения!")
    sys.exit(1)

if not CP_TOKEN:
    logging.error("❌ ОШИБКА: Не указан CP_TOKEN в переменных окружения!")
    sys.exit(1)

WEB_SERVER_HOST = "0.0.0.0"  
WEB_SERVER_PORT = int(os.getenv("PORT", 8080)) 
WEBHOOK_PATH = "/webhook"
BASE_WEBHOOK_URL = os.getenv("WEBHOOK_URL")  


bot = Bot(BOT_TOKEN)
dp = Dispatcher()
cp = CryptoPay(CP_TOKEN)
user_state = {}
report_data = {}



async def on_startup():
    """Действия при запуске бота"""
    try:
        if BASE_WEBHOOK_URL:
            await bot.set_webhook(
                f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
                drop_pending_updates=True
            )
        
    except Exception as e:
        logging.error(f"🚨 Ошибка при запуске: {e}")
        raise

async def on_shutdown():
    """Действия при выключении бота"""
    try:
        if BASE_WEBHOOK_URL:
            await bot.delete_webhook()
        
        await bot.session.close()
    except Exception as e:
        logging.error(f"🚨 Ошибка при выключении: {e}")

async def keep_alive():
    """Регулярные запросы, чтобы Render не усыплял бота"""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BASE_WEBHOOK_URL or 'http://localhost'}/ping") as resp:
                    logging.info(f"🔁 Keep-alive ping: {resp.status}")
        except Exception as e:
            logging.error(f"🚨 Keep-alive error: {e}")
        await asyncio.sleep(300)

async def ping_handler(request: web.Request):
    """Endpoint для проверки работы бота"""
    return web.Response(text="✅ Bot is alive")

async def setup_webhook():
    """Настройка вебхука"""
    app = web.Application()
    app.router.add_get("/ping", ping_handler)
    
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    return app





def init_db():
    with sqlite3.connect("users.db") as conn:
        # Включаем поддержку внешних ключей
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Создаем таблицу users с явным указанием типов данных
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY NOT NULL,
            username TEXT,
            subscription_until TEXT DEFAULT 'Нет',
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Создаем индекс для быстрого поиска
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id)")
        conn.commit()
        
def get_db_path():
    import os
    # На Render используем /tmp/ для временных файлов
    if "RENDER" in os.environ:
        return "/tmp/users.db"
    return "users.db"
def check_and_repair_db():
    try:
        with sqlite3.connect("users.db") as conn:
            # Проверяем существование таблицы
            table_exists = conn.execute("""
                SELECT count(*) FROM sqlite_master 
                WHERE type='table' AND name='users'
            """).fetchone()[0]
            
            if not table_exists:
                logging.warning("Таблица users не найдена, создаем заново")
                init_db()
                
    except Exception as e:
        logging.error(f"Ошибка проверки БД: {e}")
        # Пытаемся восстановить
        try:
            import os
            if os.path.exists("users.db"):
                os.rename("users.db", "users.db.bak")
            init_db()
        except Exception as e:
            logging.critical(f"Не удалось восстановить БД: {e}")
            raise
            

def fix_none_registrations():
    with sqlite3.connect("users.db") as conn:
        conn.execute("UPDATE users SET registered_at=? WHERE registered_at IS NULL", 
                    (datetime.now().isoformat(),))
        conn.commit()

def add_user(uid: int, username: str):
    try:
        with sqlite3.connect("users.db") as conn:
            conn.execute("""
            INSERT OR IGNORE INTO users (user_id, username)
            VALUES (?, ?)
            """, (uid, username))
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка добавления пользователя {uid}: {e}")
        # Пытаемся восстановить БД при ошибке
        check_and_repair_db()






def fix_broken_dates():
    with sqlite3.connect("users.db") as conn:
        # Исправляем None в registered_at
        conn.execute("UPDATE users SET registered_at = datetime('now') WHERE registered_at IS NULL")
        
        # Исправляем некорректные форматы дат
        rows = conn.execute("SELECT user_id, registered_at FROM users").fetchall()
        for uid, reg_date in rows:
            if not reg_date or reg_date in ["None", "Нет", "Неизвестно"]:
                conn.execute("UPDATE users SET registered_at = datetime('now') WHERE user_id = ?", (uid,))
        conn.commit()

def get_user(uid):
    with sqlite3.connect("users.db") as conn:
        row = conn.execute("SELECT username, subscription_until, registered_at FROM users WHERE user_id=?", (uid,)).fetchone()
        return row or ("-", "Нет", "Неизвестно")

def update_sub(uid, days):
    with sqlite3.connect("users.db") as conn:
        # Берём текущее значение подписки, чтобы продлить её, а не перезаписать назад
        row = conn.execute("SELECT subscription_until FROM users WHERE user_id=?", (uid,)).fetchone()
        now = datetime.now()
        if row and row[0] != "Нет":
            try:
                current_until = datetime.fromisoformat(row[0])
                if current_until > now:
                    new_until = current_until + timedelta(days=days)
                else:
                    new_until = now + timedelta(days=days)
            except:
                new_until = now + timedelta(days=days)
        else:
            new_until = now + timedelta(days=days)

        conn.execute("UPDATE users SET subscription_until=? WHERE user_id=?", (new_until.isoformat(), uid))
        conn.commit()

def remove_sub(uid):
    with sqlite3.connect("users.db") as conn:
        conn.execute("UPDATE users SET subscription_until='Нет' WHERE user_id=?", (uid,))
        conn.commit()

# ── Кнопки ────────────────────────────────
def main_menu(is_admin=False):
    kb = InlineKeyboardBuilder()
    kb.button(text="🕹️ Профиль", callback_data="profile")
    kb.button(text="💎 Подписка", callback_data="subscription")
    kb.button(text="❓ Поддержка", callback_data="support")
    kb.button(text="📨 Жалоба", callback_data="report")
    if is_admin:
        kb.button(text="👑 Админ-панель", callback_data="admin")
    kb.adjust(2)
    return kb.as_markup()

def pay_method_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="CryptoBot", callback_data="pay_crypto")
    kb.button(text="По карте", url="t.me/swatdrug")
    return kb.as_markup()

def crypto_sub_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="1 день", callback_data="sub_1")
    kb.button(text="7 дней", callback_data="sub_7")
    kb.button(text="30 дней", callback_data="sub_30")
    kb.button(text="Навсегда", callback_data="sub_forever")
    return kb.adjust(2).as_markup()

def confirm_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да", callback_data="confirm_yes")
    kb.button(text="❌ Нет", callback_data="confirm_no")
    return kb.as_markup()

def admin_panel():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Выдать подписку", callback_data="give_sub")
    kb.button(text="➖ Забрать подписку", callback_data="take_sub")
    return kb.as_markup()

# ── Хэндлеры ──────────────────────────────
@dp.message(CommandStart())
async def cmd_start(m: Message):
    add_user(m.from_user.id, m.from_user.username or "Без username")
    await m.answer_photo(
        photo=WELCOME_PHOTO,
        caption=(
            "🩷 Добро пожаловать в сн0сEр <b>COR Delivery</b>!\n"
            "<i>Хочешь крутые сн*сы? Тогда бери их у нас!</i>\n\n"
            "<i>✏️ Выбери опцию ниже:</i>"
        ),
        reply_markup=main_menu(m.from_user.id in ADMIN_IDS),
        parse_mode=ParseMode.HTML,
    )

@dp.callback_query(F.data == "profile")
async def profile(c: CallbackQuery):
    username, sub_end, reg_date = get_user(c.from_user.id)
    
    # Форматирование даты регистрации
    if reg_date and reg_date not in ["None", "Нет", "Неизвестно"]:
        try:
            # Парсим дату и форматируем по-новому
            reg_dt = datetime.fromisoformat(reg_date)
            reg_text = reg_dt.strftime("%d.%m.%Y %H:%M")
        except:
            # Если ошибка парсинга - используем текущую дату
            reg_text = datetime.now().strftime("%d.%m.%Y %H:%M")
    else:
        # Если дата отсутствует - используем текущую
        reg_text = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Форматирование даты подписки
    if sub_end and sub_end not in ["None", "Нет"]:
        try:
            sub_dt = datetime.fromisoformat(sub_end)
            now = datetime.now()
            sub_text = sub_dt.strftime("%d.%m.%Y %H:%M") if sub_dt > now else "Истекла"
        except:
            sub_text = sub_end
    else:
        sub_text = "Нет активной"

    text = (
        f"<b>🔐 Ваш профиль</b>\n\n"
        f"👤 <b>Юзернейм:</b> <code>@{username}</code>\n"
        f"📛 <b>Имя:</b> <code>{c.from_user.full_name}</code>\n"
        f"🆔 <b>ID:</b> <code>{c.from_user.id}</code>\n\n"
        f"📅 <b>Регистрация:</b> <code>{reg_text} (МСК)</code>\n"
        f"💎 <b>Подписка до:</b> <code>{sub_text}</code>"
    )

    try:
        if c.message.photo:
            await c.message.edit_caption(
                caption=text,
                reply_markup=main_menu(c.from_user.id in ADMIN_IDS),
                parse_mode=ParseMode.HTML
            )
        else:
            await c.message.edit_text(
                text=text,
                reply_markup=main_menu(c.from_user.id in ADMIN_IDS),
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        print(f"[PROFILE ERROR] {e}")



@dp.callback_query(F.data == "subscription")
async def subscription(c: CallbackQuery):
    await c.message.edit_caption(
        "Выберите способ оплаты:",
        reply_markup=pay_method_menu()
    )

@dp.callback_query(F.data == "pay_crypto")
async def pay_crypto(c: CallbackQuery):
    await c.message.edit_caption(
        "Выберите срок подписки:",
        reply_markup=crypto_sub_menu()
    )

@dp.callback_query(F.data.startswith("sub_"))
async def select_sub(c: CallbackQuery):
    user_state[c.from_user.id] = c.data
    await c.message.edit_caption(
        "Вы подтверждаете оплату?",
        reply_markup=confirm_menu()
    )

@dp.callback_query(F.data == "confirm_no")
async def cancel_payment(c: CallbackQuery):
    user_state.pop(c.from_user.id, None)
    await c.message.edit_caption(
        "❌ Отменено",
        reply_markup=main_menu(c.from_user.id in ADMIN_IDS)
    )

@dp.callback_query(F.data == "confirm_yes")
async def confirm_payment(c: CallbackQuery):
    plan = user_state.get(c.from_user.id)
    prices = {"sub_1": 3, "sub_7": 5, "sub_30": 11, "sub_forever": 20}
    days_map = {"sub_1": 1, "sub_7": 7, "sub_30": 30, "sub_forever": 365 * 100}
    price = prices.get(plan, 0)
    duration = days_map.get(plan, 0)

    if price == 0 or duration == 0:
        await c.message.answer("❌ Ошибка выбора тарифа.")
        return

    invoice = await cp.create_invoice(
        amount=price,
        asset="USDT",
        expires_in=600
    )

    user_state[c.from_user.id] = (plan, invoice.invoice_id)

    await c.message.answer(
        f"<b>Счёт на {price}$</b>\nОплатите: {invoice.bot_invoice_url}",
        parse_mode=ParseMode.HTML,
    )

async def check_payments_loop():
    while True:
        try:
            # Получаем только активные инвойсы
            invoices = await cp.get_invoices(status="active")
            
            # Создаем копию словаря для безопасной итерации
            current_states = user_state.copy()
            
            for uid, val in current_states.items():
                if isinstance(val, tuple): 
                    plan, inv_id = val
                    
                    # Ищем соответствующий оплаченный инвойс
                    paid_invoice = next((inv for inv in invoices if inv.invoice_id == inv_id and inv.status == "paid"), None)
                    
                    if paid_invoice:
                        try:
                            days_map = {
                                "sub_1": 1,
                                "sub_7": 7,
                                "sub_30": 30,
                                "sub_forever": 365 * 100
                            }
                            days = days_map.get(plan, 0)
                            
                            if days > 0:
                         
                                update_sub(uid, days)
                                
                                await cp.delete_invoice(inv_id)
                                
                                user_state.pop(uid, None)
                                
                                await bot.send_message(
                                    uid,
                                    "✅ Оплата подтверждена. Подписка активирована!",
                                    reply_markup=main_menu(uid in ADMIN_IDS)
                                )
                                
                                for admin_id in ADMIN_IDS:
                                    await bot.send_message(
                                        admin_id,
                                        f"💰 Новый платеж от @{get_user(uid)[0]}\n"
                                        f"💎 Тариф: {plan.replace('_', ' ')}\n"
                                        f"💵 Сумма: {paid_invoice.amount}$"
                                    )
                        except Exception as e:
                            print(f"[check_payments_loop] Ошибка обработки платежа: {e}")
                            continue

        except Exception as e:
            print(f"[check_payments_loop] Ошибка получения инвойсов: {e}")
        
        await asyncio.sleep(15) 

@dp.callback_query(F.data == "support")
async def support(c: CallbackQuery):
    await c.message.answer(
       f"""<b>🛠 Добро пожаловать, это поддержка COR Delivery</b>

<i>Расскажите, что у вас случилось. Избегайте мета-вопросов, не спамьте и не дублируйте проблему по несколько раз. Опишите вашу проблему ниже:</i>
""", parse_mode='html'
    )
    user_state[c.from_user.id] = "support"

@dp.callback_query(F.data == "report")
async def start_report(c: CallbackQuery):
    _, sub, _ = get_user(c.from_user.id)
    try:
        if sub != "Нет" and datetime.fromisoformat(sub) > datetime.now():
            await c.message.answer(
                "<i>Введите @username нарушителя(пример: @cipratt22292):</i>", parse_mode='html'
            )
            user_state[c.from_user.id] = "report_username"
        else:
            raise ValueError
    except Exception:
        await c.message.edit_caption(
            "<b>❌ У вас нет активной подписки</b>",
            parse_mode='html',
            reply_markup=main_menu(c.from_user.id in ADMIN_IDS)
        )

@dp.callback_query(F.data == "admin")
async def admin_menu(c: CallbackQuery):
    if c.from_user.id in ADMIN_IDS:
        await c.message.edit_caption(
            "👑 Админ-панель",
            reply_markup=admin_panel()
        )
    else:
        await c.message.edit_caption(
            "<b>❌ У вас нет доступа</b>",
            parse_mode='html',
            reply_markup=main_menu(False)
        )

@dp.callback_query(F.data == "give_sub")
async def give_sub(c: CallbackQuery):
    await c.message.answer(
        "Введите ID пользователя, которому хотите выдать подписку:"
    )
    user_state[c.from_user.id] = {"action": "admin_give"}

@dp.callback_query(F.data == "take_sub")
async def take_sub(c: CallbackQuery):
    await c.message.answer(
        "Введите ID пользователя, у которого забрать подписку:"
    )
    user_state[c.from_user.id] = {"action": "admin_take"}

@dp.message()
async def all_text(m: Message):
    uid = m.from_user.id
    state = user_state.get(uid)

    if state == "support":
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, f"🆘 От @{m.from_user.username or 'Без username'}:\n\n{m.text}")
        await m.answer("✅ Ваша заявка отправлена.", reply_markup=main_menu(uid in ADMIN_IDS))
        user_state.pop(uid, None)

    elif state == "report_username":
        report_data[uid] = {"username": m.text}
        user_state[uid] = "report_link"
        await m.answer("<i>Введите ссылку на жалобу:</i>", parse_mode='html')

    elif state == "report_link":
        report_data[uid]["link"] = m.text
        msg = (
            f"📨 Жалоба от @{m.from_user.username or 'Без username'}\n"
            f"👤 На: {report_data[uid]['username']}\n"
            f"🔗 Ссылка: {report_data[uid]['link']}"
        )
        for admin_id in ADMIN_IDS:
            await bot.send_message(admin_id, msg)
        await m.answer("<i>⚡ Идет отправка жалоб...</i>", reply_markup=main_menu(uid in ADMIN_IDS), parse_mode='html')
        import random
        asyncio.sleep(random.randint(20,25))
        await m.answer("<b>🩷 Жалобы успешно отправлены</b>", reply_markup=main_menu(uid in ADMIN_IDS), parse_mode='html')
        user_state.pop(uid, None)
        report_data.pop(uid, None)

    elif isinstance(state, dict) and state.get("action") == "admin_give":
        try:
            target_id = int(m.text)
            user_state[uid] = {"action": "admin_give_days", "target_id": target_id}
            await m.answer("Введите количество дней подписки:")
        except Exception:
            await m.answer("❌ Ошибка. Введите ID числом.")

    elif isinstance(state, dict) and state.get("action") == "admin_give_days":
        try:
            days = int(m.text)
            target_id = state["target_id"]
            update_sub(target_id, days)
            await m.answer(f"✅ Подписка выдана пользователю {target_id} на {days} дней.", reply_markup=main_menu(True))
        except Exception:
            await m.answer("❌ Ошибка. Введите количество дней числом.")
        user_state.pop(uid, None)

    elif isinstance(state, dict) and state.get("action") == "admin_take":
        try:
            target_id = int(m.text)
            remove_sub(target_id)
            await m.answer(f"✅ Подписка забрана у пользователя {target_id}.", reply_markup=main_menu(True))
        except Exception:
            await m.answer("❌ Ошибка. Введите ID числом.")
        user_state.pop(uid, None)

    else:
        await m.answer("❓ Неизвестная команда или сообщение.", reply_markup=main_menu(uid in ADMIN_IDS))



# ===== ЗАПУСК БОТА =====
async def main():
    try:
        # Настройка веб-сервера
        app = await setup_webhook()
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(
            runner,
            host=WEB_SERVER_HOST,
            port=WEB_SERVER_PORT,
            reuse_port=True
        )
        
        await site.start()
        logging.info(f"🌐 Сервер запущен на порту {WEB_SERVER_PORT}")
        
        # Инициализация бота
        await on_startup()
        asyncio.create_task(keep_alive())
        
        # Бесконечный цикл
        while True:
            await asyncio.sleep(3600)
            
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logging.critical(f"💥 Критическая ошибка: {e}")
    finally:
        await on_shutdown()
        if 'runner' in locals():
            await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"💥 Не удалось запустить бота: {e}")
        sys.exit(1)
