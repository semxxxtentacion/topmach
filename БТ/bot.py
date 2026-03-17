# bot.py
import logging
import random
import string
import aiohttp
import re
import json
import idna
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    ContextTypes, CallbackQueryHandler
)

# ==== Константы ====
TOKEN = '7962163111:AAHDBFyXAYILqVinNOziAONkAnD4dvDDans'
ADD_CODE_URL = 'https://xn--80aaxohchw2d.xn--p1ai/add_code.php'
UPDATE_STATUS_URL = 'https://xn--80aaxohchw2d.xn--p1ai/update_status.php'
ADMIN_CHAT_IDS = [7660312786, 1714559515]  # ← оба админа
COUNTER_FILE = Path("counter.txt")

# ==== Логирование ====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==== Генерация одноразового кода ====
def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def escape_markdown(text):
    return re.sub(r'([_\*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def get_next_application_number():
    if not COUNTER_FILE.exists():
        COUNTER_FILE.write_text("1")
        return 1
    try:
        current = int(COUNTER_FILE.read_text().strip())
        COUNTER_FILE.write_text(str(current + 1))
        return current
    except Exception as e:
        logger.error(f"Ошибка счётчика заявок: {e}")
        COUNTER_FILE.write_text("1")
        return 1

# ==== Команда /start ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = generate_code()
    user = update.effective_user

    telegram_id = user.id
    first_name = user.first_name or ""
    username = user.username or ""

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(ADD_CODE_URL, json={
                'telegram_id': telegram_id,
                'code': code,
                'name': first_name,
                'username': username
            }) as resp:
                if resp.status == 200:
                    escaped_code = escape_markdown(code)
                    await update.message.reply_text(
                        f"Ваш код: `{escaped_code}`",
                        parse_mode="MarkdownV2"
                    )
                else:
                    logger.warning(f"Ошибка при отправке кода: HTTP {resp.status}")
                    await update.message.reply_text("❌ Ошибка при сохранении кода.")
        except Exception as e:
            logger.error(f"Ошибка отправки: {e}")
            await update.message.reply_text("❌ Произошла ошибка.")

# ==== Отправка заявки администратору ====
async def notify_admin(
    telegram_id, site, keywords=None,
    region=None, audit=None, keywords_selection=None,
    google=None, yandex=None
):
    def checkmark(value):
        return "✅" if str(value).strip().lower() == "true" else "❌"

    def sanitize(value):
        return value.strip() if isinstance(value, str) and value.strip() else "—"

    region = sanitize(region)
    audit = checkmark(audit)
    keywords_selection = checkmark(keywords_selection)
    google = checkmark(google)
    yandex = checkmark(yandex)

    if not site or not site.strip():
        return
    if not telegram_id:
        return

    site = re.sub(r'^https?://', '', site.strip(), flags=re.IGNORECASE).strip('/')
    try:
        punycode_site = idna.encode(site).decode()
    except idna.IDNAError:
        punycode_site = re.sub(r'[^a-zA-Z0-9.-]', '', site)

    safe_site = punycode_site[:50]
    app_number = get_next_application_number()

    print(f"DEBUG CALLBACK_DATA: accept:{telegram_id}:{safe_site}")

    try:
        user = await app.bot.get_chat(int(telegram_id))
        name = user.first_name or "—"
        username = f"@{user.username}" if user.username else "—"
    except Exception as e:
        logger.warning(f"Не удалось получить имя/юзернейм: {e}")
        name = "—"
        username = "—"

    if keywords and isinstance(keywords, str):
        keywords_list = [word.strip() for word in keywords.splitlines() if word.strip()]
        formatted_keywords = "\n".join([f"{i+1}. {kw}" for i, kw in enumerate(keywords_list)]) if keywords_list else "—"
    else:
        formatted_keywords = "—"

    keyboard = [
        [InlineKeyboardButton("✅ Принять в работу", callback_data=f"accept:{telegram_id}:{safe_site}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject:{telegram_id}:{safe_site}")]
    ]

    text = (
        f"🆕 Заявка №{app_number}:\n"
        f"👤 ID: {telegram_id}\n"
        f"📛 Имя: {name}\n"
        f"🔗 Никнейм: {username}\n"
        f"🌐 Сайт: {site}\n"
        f"📍 Регион: {region}\n"
        f"🔍 Аудит сайта: {audit}\n"
        f"🧠 Подбор ключей: {keywords_selection}\n"
        f"🌐 Google: {google}\n"
        f"🌐 Yandex: {yandex}\n"
        f"🔑 Ключевые слова:\n{formatted_keywords}"
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    for admin_id in ADMIN_CHAT_IDS:
        await app.bot.send_message(chat_id=admin_id, text=text, reply_markup=reply_markup)

# ==== Обработка кнопок ====
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        action, telegram_id, site = query.data.split(":")
    except ValueError:
        await query.edit_message_text("❌ Неверный формат данных кнопки.")
        logger.error(f"Некорректный callback_data: {query.data}")
        return

    status = {
        "accept": "Принят в работу",
        "reject": "Отклонён"
    }.get(action)

    if not status:
        await query.edit_message_text("❌ Неизвестное действие.")
        return

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(UPDATE_STATUS_URL, json={
                'telegram_id': telegram_id,
                'site': site,
                'status': status
            }) as resp:
                if resp.status != 200:
                    logger.warning(f"Ошибка при отправке статуса: HTTP {resp.status}")
        except Exception as e:
            logger.error(f"Ошибка запроса: {e}")

    original_text = query.message.text
    updated_text = f"{original_text}\n\n📝 Статус: {status}"
    await query.edit_message_text(updated_text)

# ==== Запуск ====
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))

if __name__ == '__main__':
    print("✅ Бот запущен.")
    app.run_polling()
